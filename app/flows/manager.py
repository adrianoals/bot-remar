from app.services.google_sheets_service import GoogleSheetsService
from app.services.mega_api import MegaApiService
from app.services.supabase_service import SupabaseService
from app.templates.messages import (
    WELCOME_MESSAGE,
    DONATION_TYPE_MENU,
    DONATION_CATEGORY_MENU,
    DONATION_ITEM_CONDITION,
    DONATION_ASK_NAME,
    DONATION_CONFIRM_NAME,
    DONATION_ASK_ADDRESS,
    DONATION_CONFIRM_ADDRESS,
    DONATION_ASK_PHONE,
    DONATION_CONFIRM_PHONE,
    DONATION_ASK_EMAIL,
    DONATION_CONFIRM_EMAIL,
    DONATION_ASK_TIME,
    DONATION_ASK_PHOTO,
    DONATION_PHOTO_NOT_RECEIVED,
    DONATION_ASK_MORE_PHOTOS,
    DONATION_CONFIRMATION,
    DONATION_VALUE_MESSAGE,
    SERVICES_MENU,
    SERVICES_CONTACT,
    FRETES_MENU,
    FRETES_CONTACT,
    ACOLHIMENTO_WELCOME,
    ACOLHIMENTO_CONTACT,
    LOJAS_MENU,
    LOJAS_CONTACT,
    ERROR_INVALID_OPTION,
)
import logging
from typing import Optional, Dict, Any
import re
import json
import ast

logger = logging.getLogger(__name__)


class FlowManager:
    def __init__(self):
        self.mega_api = MegaApiService()
        self.supabase = SupabaseService()
        self.sheets = GoogleSheetsService()

    @staticmethod
    def _normalize_wa_id(raw: str) -> str:
        """Normaliza identificador WhatsApp mantendo apenas dígitos."""
        return re.sub(r"\D", "", (raw or "").strip())

    @staticmethod
    def _parse_fotos(value: Any) -> list[str]:
        """
        Normaliza o campo fotos para lista de URLs.
        Aceita: list, dict (imagem1/imagem2), JSON string, string com \n ou string única.
        """
        if value is None:
            return []
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, dict):
            return [str(v).strip() for v in value.values() if str(v).strip()]
        if not isinstance(value, str):
            return [str(value).strip()] if str(value).strip() else []

        raw = value.strip()
        if not raw:
            return []

        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(raw)
                if isinstance(parsed, list):
                    return [str(v).strip() for v in parsed if str(v).strip()]
                if isinstance(parsed, dict):
                    return [str(v).strip() for v in parsed.values() if str(v).strip()]
            except Exception:
                continue

        if "\n" in raw:
            return [p.strip() for p in raw.split("\n") if p.strip()]
        return [raw]

    def extract_text_content(self, message: Dict[str, Any]) -> str:
        """Extrai o conteúdo de texto de uma mensagem."""
        if not message:
            return ""
        
        # Mensagem de conversa simples
        if "conversation" in message:
            return message["conversation"]
        # Mensagem de texto estendida
        elif "extendedTextMessage" in message:
            return message["extendedTextMessage"].get("text", "")
        # Mensagem efêmera
        elif "ephemeralMessage" in message:
            ephem = message["ephemeralMessage"].get("message", {})
            if "extendedTextMessage" in ephem:
                return ephem["extendedTextMessage"].get("text", "")
        # Resposta de lista
        elif "listResponseMessage" in message:
            return message["listResponseMessage"].get("singleSelectReply", {}).get("selectedRowId", "")
        return ""

    async def handle_message(self, data: dict):
        """Recebe o payload do webhook e decide o que fazer."""
        try:
            logger.info("=" * 60)
            logger.info("PROCESSANDO MENSAGEM")
            logger.info("=" * 60)
            logger.info(f"Data recebida: {data}")
            
            # O payload da MegaAPI vem na raiz, não dentro de "body"
            # Formato: { "key": {...}, "message": {...}, "pushName": "...", etc }
            message = data.get("message", {})
            key = data.get("key", {})
            remote_jid = key.get("remoteJid", "")
            from_me = key.get("fromMe", False)
            is_group = data.get("isGroup", False)
            push_name = data.get("pushName", "")
            message_type = data.get("messageType", "")

            logger.info(f"Message: {message}")
            logger.info(f"Key: {key}")
            logger.info(f"remoteJid: {remote_jid}")
            logger.info(f"pushName: {push_name}")
            logger.info(f"messageType: {message_type}")
            logger.info(f"fromMe: {from_me}, isGroup: {is_group}")

            # Ignorar mensagens de confirmação (ack) - não são mensagens reais
            if message_type == "message.ack":
                logger.info("⚠️ Mensagem ignorada: messageType = 'message.ack' (confirmação)")
                return

            # Ignorar mensagens próprias ou de grupos
            if from_me:
                logger.info("⚠️ Mensagem ignorada: fromMe = True (mensagem própria)")
                return
            if is_group:
                logger.info("⚠️ Mensagem ignorada: isGroup = True (mensagem de grupo)")
                return

            wa_id = self._normalize_wa_id(remote_jid.split("@")[0] if remote_jid else "")
            logger.info(f"✅ wa_id extraído (remoteJid): {wa_id}")
            
            if not wa_id:
                logger.error("❌ ERRO: wa_id está vazio! remoteJid não encontrado ou inválido")
                logger.error(f"remote_jid completo: {remote_jid}")
                return

            # Destino das respostas: preferir número real (senderPn) para a MegaAPI entregar no mesmo chat
            sender_pn = (key.get("senderPn") or "").strip()
            sender_wa_id = self._normalize_wa_id(sender_pn.split("@")[0] if sender_pn else "")
            reply_to = sender_wa_id or wa_id
            # Chave usada no Supabase (estado da conversa): preferir também o telefone real
            db_wa_id = reply_to or wa_id
            if reply_to != wa_id:
                logger.info(f"📱 reply_to (senderPn): {reply_to}")
                logger.info(f"💾 db_wa_id (Supabase): {db_wa_id}  | wa_id original (remoteJid): {wa_id}")
            else:
                logger.info(f"📱 reply_to: {reply_to} (sem senderPn no payload)")
                logger.info(f"💾 db_wa_id (Supabase): {db_wa_id}")
            
            text_content = self.extract_text_content(message).strip()
            logger.info(f"✅ Texto extraído: '{text_content}'")

            # Verificar comandos de admin
            if text_content.startswith("/"):
                await self.handle_admin_command(db_wa_id, text_content, push_name, reply_to)
                return

            # Buscar estado atual do usuário
            logger.info(f"🔍 Buscando estado do usuário: {db_wa_id}")
            user_state = self.supabase.get_user_state(db_wa_id)
            logger.info(f"📊 Estado encontrado: {user_state}")
            
            # Atualizar data e horário a cada mensagem (como no n8n)
            # Isso garante que sempre temos a última interação registrada
            if user_state:
                from datetime import datetime
                logger.info("🔄 Atualizando data e horário...")
                self.supabase.create_or_update_user(db_wa_id, {
                    "data": datetime.now().strftime('%Y-%m-%d'),
                    "horario": datetime.now().strftime('%H:%M:%S')
                })
                logger.info("✅ Data e horário atualizados")
            
            # Se não tem estado ou é comando de início, começar fluxo
            if not user_state or text_content.lower() in ["oi", "ola", "olá", "começar", "inicio", "início"]:
                logger.info("🚀 Iniciando novo fluxo (usuário novo ou comando de início)")
                await self.handle_initial_state(db_wa_id, push_name, reply_to)
                return

            estado = user_state.get("estado", "inicio")

            # Roteamento principal por estado (Switch2)
            if estado == "reset":
                # Estado de reset/amortecimento: qualquer mensagem reinicia o fluxo sem erro
                logger.info("🔄 Estado RESET: Reiniciando fluxo silenciosamente")
                await self.handle_initial_state(db_wa_id, push_name, reply_to)
                return

            if estado == "inicio" or estado == "inicio0":
                await self.handle_menu_principal(db_wa_id, text_content, reply_to)
            elif estado == "doacao":
                await self.handle_doacao_tipo(db_wa_id, text_content, reply_to)
            elif estado.startswith("doacao_item_"):
                await self.handle_doacao_item(db_wa_id, text_content, estado, message, reply_to)
            elif estado == "acolhimento":
                await self.handle_acolhimento(db_wa_id, text_content, reply_to)
            elif estado == "lojas":
                await self.handle_lojas(db_wa_id, text_content, reply_to)
            elif estado == "servico":
                await self.handle_servicos(db_wa_id, text_content, reply_to)
            elif estado == "fretes":
                await self.handle_fretes(db_wa_id, text_content, reply_to)
            else:
                # Estado desconhecido, voltar ao início
                await self.handle_initial_state(db_wa_id, push_name, reply_to)

        except Exception as e:
            logger.error(f"Erro no processamento: {e}", exc_info=True)

    async def handle_admin_command(self, wa_id: str, command: str, push_name: str, reply_to: str):
        """Trata comandos de administrador."""
        to = reply_to or wa_id
        if "/chat" in command.lower():
            await self.mega_api.send_text(to, "Modo chat manual ativado.")
        elif "/nochat" in command.lower():
            self.supabase.update_state(wa_id, "inicio")
            await self.mega_api.send_text(to, "Modo automático ativado.")

    async def handle_initial_state(self, wa_id: str, push_name: str, reply_to: Optional[str] = None):
        """Handle estado inicial - seleção de estado geográfico (Switch3)."""
        to = (reply_to or wa_id).strip()
        logger.info(f"📝 Salvando dados iniciais - wa_id: {wa_id}, nome: {push_name}")
        
        try:
            self.supabase.create_or_update_user(wa_id, {
                "estado": "inicio",
                "nome": push_name or ""
            })
            logger.info(f"✅ Dados salvos no banco: wa_id=+{wa_id}, nome={push_name}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar dados iniciais: {e}", exc_info=True)
        
        try:
            logger.info(f"📤 Enviando mensagem de boas-vindas (menu principal) para {to}")
            result = await self.mega_api.send_text(to, WELCOME_MESSAGE)
            if result:
                logger.info("✅ Mensagem enviada com sucesso")
            else:
                logger.error("❌ Falha ao enviar mensagem (retorno None)")
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}", exc_info=True)

    async def handle_menu_principal(self, wa_id: str, text_content: str, reply_to: Optional[str] = None):
        """Handle menu principal (Switch4)."""
        to = (reply_to or wa_id).strip()
        logger.info(f"📋 Processando menu principal - texto: '{text_content}'")
        
        if text_content == "1":
            logger.info("📦 Opção 1 selecionada: Doação")
            self.supabase.update_state(wa_id, "doacao")
            await self.mega_api.send_text(to, DONATION_TYPE_MENU)
        elif text_content == "2":
            logger.info("🏠 Opção 2 selecionada: Acolhimento")
            self.supabase.update_state(wa_id, "acolhimento")
            await self.mega_api.send_text(to, ACOLHIMENTO_WELCOME)
        elif text_content == "3":
            logger.info("🛒 Opção 3 selecionada: Lojas")
            self.supabase.update_state(wa_id, "lojas")
            await self.mega_api.send_text(to, LOJAS_MENU)
        elif text_content == "4":
            logger.info("🔧 Opção 4 selecionada: Serviços")
            self.supabase.update_state(wa_id, "servico")
            await self.mega_api.send_text(to, SERVICES_MENU)
        elif text_content == "5":
            logger.info("🚚 Opção 5 selecionada: Fretes")
            self.supabase.update_state(wa_id, "fretes")
            await self.mega_api.send_text(to, FRETES_MENU)
        elif text_content == "0":
            logger.info("🔄 Opção 0 selecionada: Voltar ao início")
            await self.handle_initial_state(wa_id, "", reply_to)
        else:
            logger.info(f"⚠️ Opção inválida: '{text_content}'. Mostrando mensagem de erro e menu")
            await self.mega_api.send_text(to, ERROR_INVALID_OPTION)
            await self.mega_api.send_text(to, WELCOME_MESSAGE)

    async def handle_doacao_tipo(self, wa_id: str, text_content: str, reply_to: Optional[str] = None):
        """Handle tipo de doação (Switch5)."""
        to = (reply_to or wa_id).strip()
        if text_content == "1":
            await self.mega_api.send_text(to, DONATION_VALUE_MESSAGE)
            self.supabase.update_state(wa_id, "reset")
            try:
                conv = self.supabase.get_user_state(wa_id)
                if conv:
                    self.sheets.append_doacao_valor(conv, telefone=reply_to or to)
            except Exception as e:
                logger.warning(f"Google Sheets (doação valor): {e}")
        elif text_content == "2":
            await self.mega_api.send_text(to, DONATION_CATEGORY_MENU)
            self.supabase.update_state(wa_id, "doacao_item_1")
        elif text_content == "0":
            await self.mega_api.send_text(to, WELCOME_MESSAGE)
            self.supabase.update_state(wa_id, "inicio")
        else:
            await self.mega_api.send_text(to, ERROR_INVALID_OPTION)
            await self.mega_api.send_text(to, DONATION_TYPE_MENU)

    async def handle_doacao_item(self, wa_id: str, text_content: str, estado: str, message: Dict[str, Any], reply_to: Optional[str] = None):
        """Handle fluxo completo de doação de itens."""
        to = (reply_to or wa_id).strip()
        estado_num = int(estado.split("_")[-1]) if estado.split("_")[-1].isdigit() else 0

        # Verificar se é imagem
        media_data = self.mega_api.extract_media_data(message)
        is_image = media_data and media_data.get("messageType") == "image"

        # doacao_item_1: Seleção de categoria
        if estado_num == 1:
            categorias = {
                "1": "Móveis",
                "2": "Utensílios",
                "3": "Eletroeletrônicos",
                "4": "Roupas",
                "5": "Itens variados"
            }
            if text_content in categorias:
                tipo_doacao = categorias[text_content]
                self.supabase.create_doacao(wa_id, tipo_doacao)
                await self.mega_api.send_text(to, DONATION_ITEM_CONDITION)
                self.supabase.update_state(wa_id, "doacao_item_2")
            elif text_content == "0":
                await self.mega_api.send_text(to, DONATION_TYPE_MENU)
                self.supabase.update_state(wa_id, "doacao")
            else:
                await self.mega_api.send_text(to, ERROR_INVALID_OPTION)
                await self.mega_api.send_text(to, DONATION_CATEGORY_MENU)

        # doacao_item_2: Estado dos itens
        elif estado_num == 2:
            estados_doacao = {
                "1": "Novo",
                "2": "Usado em bom estado",
                "3": "Usado com marcas de uso",
                "4": "Com defeito (ou misto: alguns bons, outros com defeito)",
                "5": "Não sei dizer",
            }
            if text_content in estados_doacao:
                self.supabase.update_doacao(wa_id, {"estado_doacao": estados_doacao[text_content]})
                await self.mega_api.send_text(to, DONATION_ASK_NAME)
                self.supabase.update_state(wa_id, "doacao_item_3")
            elif text_content == "0":
                await self.mega_api.send_text(to, DONATION_CATEGORY_MENU)
                self.supabase.update_state(wa_id, "doacao_item_1")
            else:
                await self.mega_api.send_text(to, ERROR_INVALID_OPTION)
                await self.mega_api.send_text(to, DONATION_ITEM_CONDITION)

        # doacao_item_3: Solicitação de nome
        elif estado_num == 3:
            if text_content and len(text_content) > 2:
                self.supabase.create_or_update_user(wa_id, {"mensagem_temp": text_content})
                await self.mega_api.send_text(to, DONATION_CONFIRM_NAME.format(nome=text_content))
                self.supabase.update_state(wa_id, "doacao_item_4")
            else:
                await self.mega_api.send_text(to, DONATION_ASK_NAME)

        # doacao_item_4: Confirmação de nome
        elif estado_num == 4:
            if text_content == "1":
                user_state = self.supabase.get_user_state(wa_id)
                nome = user_state.get("mensagem_temp", "") if user_state else ""
                if not nome:
                    await self.mega_api.send_text(to, DONATION_ASK_NAME)
                    self.supabase.update_state(wa_id, "doacao_item_3")
                    return
                # n8n: doacoes.nome_responsavel
                self.supabase.update_doacao(wa_id, {"nome_responsavel": nome})
                await self.mega_api.send_text(to, DONATION_ASK_ADDRESS)
                self.supabase.update_state(wa_id, "doacao_item_5")
            elif text_content == "0":
                await self.mega_api.send_text(to, WELCOME_MESSAGE)
                self.supabase.update_state(wa_id, "inicio")
            else:
                self.supabase.create_or_update_user(wa_id, {"mensagem_temp": text_content})
                await self.mega_api.send_text(to, DONATION_CONFIRM_NAME.format(nome=text_content))

        # doacao_item_5: Solicitação de endereço
        elif estado_num == 5:
            if text_content and len(text_content) > 10:
                self.supabase.create_or_update_user(wa_id, {"mensagem_temp": text_content})
                await self.mega_api.send_text(to, DONATION_CONFIRM_ADDRESS.format(endereco=text_content))
                self.supabase.update_state(wa_id, "doacao_item_6")
            else:
                await self.mega_api.send_text(to, DONATION_ASK_ADDRESS)

        # doacao_item_6: Confirmação de endereço
        elif estado_num == 6:
            if text_content == "1":
                user_state = self.supabase.get_user_state(wa_id)
                endereco = user_state.get("mensagem_temp", "") if user_state else ""
                if endereco:
                    # n8n: doacoes.endereco_retirada
                    self.supabase.update_doacao(wa_id, {"endereco_retirada": endereco})
                    await self.mega_api.send_text(to, DONATION_ASK_PHONE)
                    self.supabase.update_state(wa_id, "doacao_item_7")
                else:
                    await self.mega_api.send_text(to, DONATION_ASK_ADDRESS)
                    self.supabase.update_state(wa_id, "doacao_item_5")
            elif text_content == "0":
                await self.mega_api.send_text(to, WELCOME_MESSAGE)
                self.supabase.update_state(wa_id, "inicio")
            else:
                self.supabase.create_or_update_user(wa_id, {"mensagem_temp": text_content})
                await self.mega_api.send_text(to, DONATION_CONFIRM_ADDRESS.format(endereco=text_content))

        # doacao_item_7: Solicitação de WhatsApp
        elif estado_num == 7:
            if text_content and len(text_content) >= 10:
                self.supabase.create_or_update_user(wa_id, {"mensagem_temp": text_content})
                await self.mega_api.send_text(to, DONATION_CONFIRM_PHONE.format(telefone=text_content))
                self.supabase.update_state(wa_id, "doacao_item_8")
            else:
                await self.mega_api.send_text(to, DONATION_ASK_PHONE)

        # doacao_item_8: Confirmação de WhatsApp
        elif estado_num == 8:
            if text_content == "1":
                user_state = self.supabase.get_user_state(wa_id)
                telefone = user_state.get("mensagem_temp", "") if user_state else ""
                if telefone:
                    # n8n: doacoes.telefone_whatsapp
                    self.supabase.update_doacao(wa_id, {"telefone_whatsapp": telefone})
                    await self.mega_api.send_text(to, DONATION_ASK_EMAIL)
                    self.supabase.update_state(wa_id, "doacao_item_9")
                else:
                    await self.mega_api.send_text(to, DONATION_ASK_PHONE)
                    self.supabase.update_state(wa_id, "doacao_item_7")
            elif text_content == "0":
                await self.mega_api.send_text(to, WELCOME_MESSAGE)
                self.supabase.update_state(wa_id, "inicio")
            else:
                self.supabase.create_or_update_user(wa_id, {"mensagem_temp": text_content})
                await self.mega_api.send_text(to, DONATION_CONFIRM_PHONE.format(telefone=text_content))

        # doacao_item_9: Confirmação de email, depois horário, depois foto
        elif estado_num == 9:
            doacao = self.supabase.get_latest_doacao(wa_id)
            
            if not doacao:
                await self.mega_api.send_text(to, ERROR_INVALID_OPTION)
                self.supabase.update_state(wa_id, "inicio")
                return
            
            user_state = self.supabase.get_user_state(wa_id)
            
            # 1) Primeiro: confirmar/salvar email
            if not doacao.get("email"):
                if text_content == "1":
                    email = user_state.get("mensagem_temp", "") if user_state else ""
                    if email and "@" in email:
                        self.supabase.update_doacao(wa_id, {"email": email})
                        # Depois do email, perguntar horário preferencial
                        await self.mega_api.send_text(to, DONATION_ASK_TIME)
                    else:
                        await self.mega_api.send_text(to, DONATION_ASK_EMAIL)
                elif "@" in text_content:
                    self.supabase.create_or_update_user(wa_id, {"mensagem_temp": text_content})
                    await self.mega_api.send_text(to, DONATION_CONFIRM_EMAIL.format(email=text_content))
                elif text_content == "0":
                    await self.mega_api.send_text(to, WELCOME_MESSAGE)
                    self.supabase.update_state(wa_id, "inicio")
                else:
                    self.supabase.create_or_update_user(wa_id, {"mensagem_temp": text_content})
                    await self.mega_api.send_text(to, DONATION_CONFIRM_EMAIL.format(email=text_content))
            # 2) Depois: horário preferencial (Manhã / Tarde / Noite)
            elif not doacao.get("horario_preferencial"):
                if text_content in ["1", "2", "3"]:
                    mapa_horario = {"1": "Manhã", "2": "Tarde", "3": "Noite"}
                    horario = mapa_horario[text_content]
                    self.supabase.update_doacao(wa_id, {"horario_preferencial": horario})
                    # Após escolher horário, pedir a primeira foto
                    await self.mega_api.send_text(to, DONATION_ASK_PHOTO)
                elif text_content == "0":
                    await self.mega_api.send_text(to, WELCOME_MESSAGE)
                    self.supabase.update_state(wa_id, "inicio")
                else:
                    # Resposta inválida para horário → perguntar novamente
                    await self.mega_api.send_text(to, DONATION_ASK_TIME)
            # 3) Fluxo de fotos (uma ou várias)
            elif is_image:
                media_data = self.mega_api.extract_media_data(message)
                if media_data:
                    try:
                        import tempfile
                        import os
                        import uuid
                        
                        file_ext = media_data.get("mimetype", "image/jpeg").split("/")[-1]
                        if file_ext == "jpeg":
                            file_ext = "jpg"
                        temp_file = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.{file_ext}")
                        
                        success = await self.mega_api.download_and_save_media(media_data, temp_file)
                        if success:
                            file_name = f"{wa_id}/{uuid.uuid4()}.{file_ext}"
                            media_url = self.supabase.upload_media(
                                temp_file,
                                bucket="whatsapp_media",
                                file_name=file_name,
                                content_type=media_data.get("mimetype"),
                            )
                            
                            if media_url:
                                doacao_atual = self.supabase.get_latest_doacao(wa_id)
                                fotos_raw = doacao_atual.get("fotos") if doacao_atual else None
                                fotos = self._parse_fotos(fotos_raw)
                                if media_url not in fotos:
                                    fotos.append(media_url)

                                # Quando o campo é TEXT no banco, persistimos JSON string para manter múltiplas URLs.
                                # Quando é JSON/JSONB e já retorna lista, mantém como lista.
                                fotos_to_save: Any = fotos if isinstance(fotos_raw, list) else json.dumps(fotos, ensure_ascii=False)
                                self.supabase.update_doacao(wa_id, {"fotos": fotos_to_save})
                                logger.info(f"Foto salva para {wa_id}: {media_url}")
                            
                            try:
                                os.remove(temp_file)
                            except Exception:
                                pass
                    except Exception as e:
                        logger.error(f"Erro ao processar foto de {wa_id}: {e}")
                
                await self.mega_api.send_text(to, DONATION_ASK_MORE_PHOTOS)
            elif text_content == "1":
                await self.mega_api.send_text(to, DONATION_ASK_PHOTO)
            elif text_content == "2":
                await self.mega_api.send_text(to, DONATION_CONFIRMATION)
                self.supabase.update_state(wa_id, "reset")
                try:
                    doacao = self.supabase.get_latest_doacao(wa_id)
                    if doacao:
                        self.sheets.append_doacao_item(doacao, telefone=reply_to or to)
                except Exception as e:
                    logger.warning(f"Google Sheets (doação item): {e}")
            elif text_content == "0":
                await self.mega_api.send_text(to, WELCOME_MESSAGE)
                self.supabase.update_state(wa_id, "inicio")
            else:
                await self.mega_api.send_text(to, ERROR_INVALID_OPTION)
                await self.mega_api.send_text(to, DONATION_ASK_MORE_PHOTOS)

    async def handle_acolhimento(self, wa_id: str, text_content: str, reply_to: Optional[str] = None):
        """Handle fluxo de acolhimento."""
        to = (reply_to or wa_id).strip()
        if text_content == "1":
            await self.mega_api.send_text(to, ACOLHIMENTO_CONTACT)
            self.supabase.update_state(wa_id, "reset")
            try:
                conv = self.supabase.get_user_state(wa_id)
                if conv:
                    self.sheets.append_acolhimento(conv, telefone=reply_to or to)
            except Exception as e:
                logger.warning(f"Google Sheets (acolhimento): {e}")
        elif text_content == "2":
            await self.mega_api.send_text(to, WELCOME_MESSAGE)
            self.supabase.update_state(wa_id, "inicio")
        else:
            await self.mega_api.send_text(to, ERROR_INVALID_OPTION)
            await self.mega_api.send_text(to, ACOLHIMENTO_WELCOME)

    async def handle_lojas(self, wa_id: str, text_content: str, reply_to: Optional[str] = None):
        """Handle fluxo de lojas."""
        to = (reply_to or wa_id).strip()
        if text_content == "1":
            await self.mega_api.send_text(to, LOJAS_CONTACT)
            self.supabase.update_state(wa_id, "reset")
            try:
                conv = self.supabase.get_user_state(wa_id)
                if conv:
                    self.sheets.append_lojas(conv, telefone=reply_to or to)
            except Exception as e:
                logger.warning(f"Google Sheets (lojas): {e}")
        elif text_content == "2":
            await self.mega_api.send_text(to, WELCOME_MESSAGE)
            self.supabase.update_state(wa_id, "inicio")
        else:
            await self.mega_api.send_text(to, ERROR_INVALID_OPTION)
            await self.mega_api.send_text(to, LOJAS_MENU)

    async def handle_servicos(self, wa_id: str, text_content: str, reply_to: Optional[str] = None):
        """Handle fluxo de serviços."""
        to = (reply_to or wa_id).strip()
        if text_content == "1":
            await self.mega_api.send_text(to, SERVICES_CONTACT)
            self.supabase.update_state(wa_id, "reset")
            try:
                conv = self.supabase.get_user_state(wa_id)
                if conv:
                    self.sheets.append_servico(conv, telefone=reply_to or to)
            except Exception as e:
                logger.warning(f"Google Sheets (serviço): {e}")
        elif text_content == "2":
            await self.mega_api.send_text(to, WELCOME_MESSAGE)
            self.supabase.update_state(wa_id, "inicio")
        else:
            await self.mega_api.send_text(to, ERROR_INVALID_OPTION)
            await self.mega_api.send_text(to, SERVICES_MENU)

    async def handle_fretes(self, wa_id: str, text_content: str, reply_to: Optional[str] = None):
        """Handle fluxo de fretes."""
        to = (reply_to or wa_id).strip()
        if text_content == "1":
            await self.mega_api.send_text(to, FRETES_CONTACT)
            self.supabase.update_state(wa_id, "reset")
            try:
                conv = self.supabase.get_user_state(wa_id)
                if conv:
                    self.sheets.append_fretes(conv, telefone=reply_to or to)
            except Exception as e:
                logger.warning(f"Google Sheets (fretes): {e}")
        elif text_content == "2":
            await self.mega_api.send_text(to, WELCOME_MESSAGE)
            self.supabase.update_state(wa_id, "inicio")
        else:
            await self.mega_api.send_text(to, ERROR_INVALID_OPTION)
            await self.mega_api.send_text(to, FRETES_MENU)
