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

logger = logging.getLogger(__name__)


class FlowManager:
    def __init__(self):
        self.mega_api = MegaApiService()
        self.supabase = SupabaseService()

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

            wa_id = remote_jid.split("@")[0] if remote_jid else ""
            logger.info(f"✅ wa_id extraído: {wa_id}")
            
            if not wa_id:
                logger.error("❌ ERRO: wa_id está vazio! remoteJid não encontrado ou inválido")
                logger.error(f"remote_jid completo: {remote_jid}")
                return
            
            text_content = self.extract_text_content(message).strip()
            logger.info(f"✅ Texto extraído: '{text_content}'")

            # Verificar comandos de admin
            if text_content.startswith("/"):
                await self.handle_admin_command(wa_id, text_content, push_name)
                return

            # Buscar estado atual do usuário
            logger.info(f"🔍 Buscando estado do usuário: {wa_id}")
            user_state = self.supabase.get_user_state(wa_id)
            logger.info(f"📊 Estado encontrado: {user_state}")
            
            # Atualizar data e horário a cada mensagem (como no n8n)
            # Isso garante que sempre temos a última interação registrada
            if user_state:
                from datetime import datetime
                logger.info("🔄 Atualizando data e horário...")
                self.supabase.create_or_update_user(wa_id, {
                    "data": datetime.now().strftime('%Y-%m-%d'),
                    "horario": datetime.now().strftime('%H:%M:%S')
                })
                logger.info("✅ Data e horário atualizados")
            
            # Se não tem estado ou é comando de início, começar fluxo
            if not user_state or text_content.lower() in ["oi", "ola", "olá", "começar", "inicio", "início"]:
                logger.info("🚀 Iniciando novo fluxo (usuário novo ou comando de início)")
                await self.handle_initial_state(wa_id, push_name)
                return

            estado = user_state.get("estado", "inicio")

            # Roteamento principal por estado (Switch2)
            if estado == "inicio" or estado == "inicio0":
                await self.handle_menu_principal(wa_id, text_content)
            elif estado == "doacao":
                await self.handle_doacao_tipo(wa_id, text_content)
            elif estado.startswith("doacao_item_"):
                await self.handle_doacao_item(wa_id, text_content, estado, message)
            elif estado == "acolhimento":
                await self.handle_acolhimento(wa_id, text_content)
            elif estado == "lojas":
                await self.handle_lojas(wa_id, text_content)
            elif estado == "servico":
                await self.handle_servicos(wa_id, text_content)
            elif estado == "fretes":
                await self.handle_fretes(wa_id, text_content)
            else:
                # Estado desconhecido, voltar ao início
                await self.handle_initial_state(wa_id, push_name)

        except Exception as e:
            logger.error(f"Erro no processamento: {e}", exc_info=True)

    async def handle_admin_command(self, wa_id: str, command: str, push_name: str):
        """Trata comandos de administrador."""
        if "/chat" in command.lower():
            # Permitir chat manual (implementar se necessário)
            await self.mega_api.send_text(wa_id, "Modo chat manual ativado.")
        elif "/nochat" in command.lower():
            # Resetar para modo automático
            self.supabase.update_state(wa_id, "inicio")
            await self.mega_api.send_text(wa_id, "Modo automático ativado.")

    async def handle_initial_state(self, wa_id: str, push_name: str):
        """Handle estado inicial - seleção de estado geográfico (Switch3)."""
        logger.info(f"📝 Salvando dados iniciais - wa_id: {wa_id}, nome: {push_name}")
        
        # Salvar nome do WhatsApp (pushName) na tabela conversas, como no n8n
        try:
            self.supabase.create_or_update_user(wa_id, {
                "estado": "inicio",
                "nome": push_name or ""
            })
            logger.info(f"✅ Dados salvos no banco: wa_id=+{wa_id}, nome={push_name}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar dados iniciais: {e}", exc_info=True)
        
        # Enviar mensagem inicial (menu principal) - como no fluxo original n8n
        try:
            logger.info(f"📤 Enviando mensagem de boas-vindas (menu principal) para {wa_id}")
            result = await self.mega_api.send_text(wa_id, WELCOME_MESSAGE)
            if result:
                logger.info("✅ Mensagem enviada com sucesso")
            else:
                logger.error("❌ Falha ao enviar mensagem (retorno None)")
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}", exc_info=True)

    async def handle_menu_principal(self, wa_id: str, text_content: str):
        """Handle menu principal (Switch4)."""
        logger.info(f"📋 Processando menu principal - texto: '{text_content}'")
        
        # Menu principal (Switch4)
        if text_content == "1":
            logger.info("📦 Opção 1 selecionada: Doação")
            self.supabase.update_state(wa_id, "doacao")
            await self.mega_api.send_text(wa_id, DONATION_TYPE_MENU)
        elif text_content == "2":
            logger.info("🏠 Opção 2 selecionada: Acolhimento")
            self.supabase.update_state(wa_id, "acolhimento")
            await self.mega_api.send_text(wa_id, ACOLHIMENTO_WELCOME)
        elif text_content == "3":
            logger.info("🛒 Opção 3 selecionada: Lojas")
            self.supabase.update_state(wa_id, "lojas")
            await self.mega_api.send_text(wa_id, LOJAS_MENU)
        elif text_content == "4":
            logger.info("🔧 Opção 4 selecionada: Serviços")
            self.supabase.update_state(wa_id, "servico")
            await self.mega_api.send_text(wa_id, SERVICES_MENU)
        elif text_content == "5":
            logger.info("🚚 Opção 5 selecionada: Fretes")
            self.supabase.update_state(wa_id, "fretes")
            await self.mega_api.send_text(wa_id, FRETES_MENU)
        elif text_content == "0":
            logger.info("🔄 Opção 0 selecionada: Voltar ao início")
            await self.handle_initial_state(wa_id, "")
        else:
            # Texto não é uma opção válida - mostrar mensagem de erro e depois o menu
            logger.info(f"⚠️ Opção inválida: '{text_content}'. Mostrando mensagem de erro e menu")
            await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
            await self.mega_api.send_text(wa_id, WELCOME_MESSAGE)

    async def handle_doacao_tipo(self, wa_id: str, text_content: str):
        """Handle tipo de doação (Switch5)."""
        if text_content == "1":
            # Doação em valor
            await self.mega_api.send_text(wa_id, DONATION_VALUE_MESSAGE)
            self.supabase.update_state(wa_id, "inicio")
        elif text_content == "2":
            # Doação de item - mostrar categorias
            await self.mega_api.send_text(wa_id, DONATION_CATEGORY_MENU)
            self.supabase.update_state(wa_id, "doacao_item_1")
        elif text_content == "0":
            # Voltar ao menu anterior
            await self.mega_api.send_text(wa_id, WELCOME_MESSAGE)
            self.supabase.update_state(wa_id, "inicio")
        else:
            # Opção inválida - mostrar erro e reenviar menu de tipo de doação
            await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
            await self.mega_api.send_text(wa_id, DONATION_TYPE_MENU)

    async def handle_doacao_item(self, wa_id: str, text_content: str, estado: str, message: Dict[str, Any]):
        """Handle fluxo completo de doação de itens."""
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
                await self.mega_api.send_text(wa_id, DONATION_ITEM_CONDITION)
                self.supabase.update_state(wa_id, "doacao_item_2")
            elif text_content == "0":
                await self.mega_api.send_text(wa_id, DONATION_TYPE_MENU)
                self.supabase.update_state(wa_id, "doacao")
            else:
                # Opção inválida - mostrar erro e reenviar menu de categorias
                await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
                await self.mega_api.send_text(wa_id, DONATION_CATEGORY_MENU)

        # doacao_item_2: Estado dos itens
        elif estado_num == 2:
            if text_content in ["1", "2", "3", "4", "5"]:
                self.supabase.update_doacao(wa_id, {"estado_doacao": text_content})
                await self.mega_api.send_text(wa_id, DONATION_ASK_NAME)
                self.supabase.update_state(wa_id, "doacao_item_3")
            elif text_content == "0":
                await self.mega_api.send_text(wa_id, DONATION_CATEGORY_MENU)
                self.supabase.update_state(wa_id, "doacao_item_1")
            else:
                # Opção inválida - mostrar erro e reenviar menu de estado dos itens
                await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
                await self.mega_api.send_text(wa_id, DONATION_ITEM_CONDITION)

        # doacao_item_3: Solicitação de nome
        elif estado_num == 3:
            if text_content and len(text_content) > 2:
                # Salvar nome temporariamente na tabela conversas e pedir confirmação
                self.supabase.create_or_update_user(wa_id, {"mensagem_temp": text_content})
                await self.mega_api.send_text(wa_id, DONATION_CONFIRM_NAME.format(nome=text_content))
                self.supabase.update_state(wa_id, "doacao_item_4")
            else:
                await self.mega_api.send_text(wa_id, DONATION_ASK_NAME)

        # doacao_item_4: Confirmação de nome
        elif estado_num == 4:
            if text_content == "1":
                # Confirmar nome - buscar da tabela conversas
                user_state = self.supabase.get_user_state(wa_id)
                nome = user_state.get("mensagem_temp", "") if user_state else ""
                if not nome:
                    await self.mega_api.send_text(wa_id, DONATION_ASK_NAME)
                    self.supabase.update_state(wa_id, "doacao_item_3")
                    return
                self.supabase.update_doacao(wa_id, {"nome": nome})
                await self.mega_api.send_text(wa_id, DONATION_ASK_ADDRESS)
                self.supabase.update_state(wa_id, "doacao_item_5")
            elif text_content == "0":
                await self.mega_api.send_text(wa_id, WELCOME_MESSAGE)
                self.supabase.update_state(wa_id, "inicio")
            else:
                # Opção inválida - mostrar erro e reenviar confirmação de nome
                user_state = self.supabase.get_user_state(wa_id)
                nome = user_state.get("mensagem_temp", "") if user_state else ""
                if nome:
                    await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
                    await self.mega_api.send_text(wa_id, DONATION_CONFIRM_NAME.format(nome=nome))
                else:
                    # Se não tem nome salvo, pedir novamente
                    await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
                    await self.mega_api.send_text(wa_id, DONATION_ASK_NAME)
                    self.supabase.update_state(wa_id, "doacao_item_3")

        # doacao_item_5: Solicitação de endereço
        elif estado_num == 5:
            if text_content and len(text_content) > 10:
                self.supabase.create_or_update_user(wa_id, {"mensagem_temp": text_content})
                await self.mega_api.send_text(wa_id, DONATION_CONFIRM_ADDRESS.format(endereco=text_content))
                self.supabase.update_state(wa_id, "doacao_item_6")
            else:
                await self.mega_api.send_text(wa_id, DONATION_ASK_ADDRESS)

        # doacao_item_6: Confirmação de endereço
        elif estado_num == 6:
            if text_content == "1":
                user_state = self.supabase.get_user_state(wa_id)
                endereco = user_state.get("mensagem_temp", "") if user_state else ""
                if endereco:
                    self.supabase.update_doacao(wa_id, {"endereco": endereco})
                    await self.mega_api.send_text(wa_id, DONATION_ASK_PHONE)
                    self.supabase.update_state(wa_id, "doacao_item_7")
                else:
                    await self.mega_api.send_text(wa_id, DONATION_ASK_ADDRESS)
                    self.supabase.update_state(wa_id, "doacao_item_5")
            elif text_content == "0":
                await self.mega_api.send_text(wa_id, WELCOME_MESSAGE)
                self.supabase.update_state(wa_id, "inicio")
            else:
                # Opção inválida - mostrar erro e reenviar confirmação de endereço
                user_state = self.supabase.get_user_state(wa_id)
                endereco = user_state.get("mensagem_temp", "") if user_state else ""
                if endereco:
                    await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
                    await self.mega_api.send_text(wa_id, DONATION_CONFIRM_ADDRESS.format(endereco=endereco))
                else:
                    # Se não tem endereço salvo, pedir novamente
                    await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
                    await self.mega_api.send_text(wa_id, DONATION_ASK_ADDRESS)
                    self.supabase.update_state(wa_id, "doacao_item_5")

        # doacao_item_7: Solicitação de WhatsApp
        elif estado_num == 7:
            if text_content and len(text_content) >= 10:
                self.supabase.create_or_update_user(wa_id, {"mensagem_temp": text_content})
                await self.mega_api.send_text(wa_id, DONATION_CONFIRM_PHONE.format(telefone=text_content))
                self.supabase.update_state(wa_id, "doacao_item_8")
            else:
                await self.mega_api.send_text(wa_id, DONATION_ASK_PHONE)

        # doacao_item_8: Confirmação de WhatsApp
        elif estado_num == 8:
            if text_content == "1":
                user_state = self.supabase.get_user_state(wa_id)
                telefone = user_state.get("mensagem_temp", "") if user_state else ""
                if telefone:
                    self.supabase.update_doacao(wa_id, {"telefone": telefone})
                    await self.mega_api.send_text(wa_id, DONATION_ASK_EMAIL)
                    self.supabase.update_state(wa_id, "doacao_item_9")
                else:
                    await self.mega_api.send_text(wa_id, DONATION_ASK_PHONE)
                    self.supabase.update_state(wa_id, "doacao_item_7")
            elif text_content == "0":
                await self.mega_api.send_text(wa_id, WELCOME_MESSAGE)
                self.supabase.update_state(wa_id, "inicio")
            else:
                # Opção inválida - mostrar erro e reenviar confirmação de telefone
                user_state = self.supabase.get_user_state(wa_id)
                telefone = user_state.get("mensagem_temp", "") if user_state else ""
                if telefone:
                    await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
                    await self.mega_api.send_text(wa_id, DONATION_CONFIRM_PHONE.format(telefone=telefone))
                else:
                    # Se não tem telefone salvo, pedir novamente
                    await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
                    await self.mega_api.send_text(wa_id, DONATION_ASK_PHONE)
                    self.supabase.update_state(wa_id, "doacao_item_7")

        # doacao_item_9: Confirmação de email, depois horário, depois foto
        elif estado_num == 9:
            doacao = self.supabase.get_latest_doacao(wa_id)
            
            if not doacao:
                await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
                self.supabase.update_state(wa_id, "inicio")
                return
            
            user_state = self.supabase.get_user_state(wa_id)
            
            # Verificar se email foi confirmado
            if not doacao.get("email"):
                # Email ainda não confirmado
                if text_content == "1":
                    # Confirmar email da tabela conversas
                    email = user_state.get("mensagem_temp", "") if user_state else ""
                    if email and "@" in email:
                        self.supabase.update_doacao(wa_id, {"email": email})
                        await self.mega_api.send_text(wa_id, DONATION_ASK_TIME)
                    else:
                        await self.mega_api.send_text(wa_id, DONATION_ASK_EMAIL)
                elif "@" in text_content:
                    # Email fornecido, salvar temporariamente e pedir confirmação
                    self.supabase.create_or_update_user(wa_id, {"mensagem_temp": text_content})
                    await self.mega_api.send_text(wa_id, DONATION_CONFIRM_EMAIL.format(email=text_content))
                elif text_content == "0":
                    await self.mega_api.send_text(wa_id, WELCOME_MESSAGE)
                    self.supabase.update_state(wa_id, "inicio")
                else:
                    # Email corrigido ou inválido
                    if "@" not in text_content:
                        await self.mega_api.send_text(wa_id, DONATION_ASK_EMAIL)
                    else:
                        self.supabase.create_or_update_user(wa_id, {"mensagem_temp": text_content})
                        await self.mega_api.send_text(wa_id, DONATION_CONFIRM_EMAIL.format(email=text_content))
            # Horário preferencial
            elif not doacao.get("horario_preferencial"):
                if text_content in ["1", "2"]:
                    horario = "Manhã" if text_content == "1" else "Tarde"
                    self.supabase.update_doacao(wa_id, {"horario_preferencial": horario})
                    await self.mega_api.send_text(wa_id, DONATION_ASK_PHOTO)
                elif text_content == "0":
                    await self.mega_api.send_text(wa_id, WELCOME_MESSAGE)
                    self.supabase.update_state(wa_id, "inicio")
                else:
                    # Opção inválida - mostrar erro e reenviar confirmação de email
                    email = user_state.get("mensagem_temp", "") if user_state else ""
                    if email and "@" in email:
                        await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
                        await self.mega_api.send_text(wa_id, DONATION_CONFIRM_EMAIL.format(email=email))
                    else:
                        await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
                        await self.mega_api.send_text(wa_id, DONATION_ASK_EMAIL)
            # Foto
            elif is_image:
                # Foto recebida - fazer download e upload para Supabase Storage
                media_data = self.mega_api.extract_media_data(message)
                if media_data:
                    try:
                        # Fazer download da mídia
                        import tempfile
                        import os
                        import uuid
                        
                        # Criar arquivo temporário
                        file_ext = media_data.get("mimetype", "image/jpeg").split("/")[-1]
                        if file_ext == "jpeg":
                            file_ext = "jpg"
                        temp_file = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.{file_ext}")
                        
                        # Download
                        success = await self.mega_api.download_and_save_media(media_data, temp_file)
                        if success:
                                # Upload para Supabase Storage
                            file_name = f"{wa_id}/{uuid.uuid4()}.{file_ext}"
                            media_url = self.supabase.upload_media(temp_file, bucket="whatsapp_media", file_name=file_name)
                            
                            if media_url:
                                # Salvar URL na doação
                                doacao_atual = self.supabase.get_latest_doacao(wa_id)
                                fotos = doacao_atual.get("fotos", []) if doacao_atual else []
                                if not isinstance(fotos, list):
                                    fotos = []
                                fotos.append(media_url)
                                self.supabase.update_doacao(wa_id, {"fotos": fotos})
                                logger.info(f"Foto salva para {wa_id}: {media_url}")
                            
                            # Limpar arquivo temporário
                            try:
                                os.remove(temp_file)
                            except:
                                pass
                    except Exception as e:
                        logger.error(f"Erro ao processar foto de {wa_id}: {e}")
                
                await self.mega_api.send_text(wa_id, DONATION_ASK_MORE_PHOTOS)
            elif text_content == "1":
                # Adicionar mais foto
                await self.mega_api.send_text(wa_id, DONATION_ASK_PHOTO)
            elif text_content == "2":
                # Finalizar
                await self.mega_api.send_text(wa_id, DONATION_CONFIRMATION)
                self.supabase.update_state(wa_id, "inicio")
            elif text_content == "0":
                await self.mega_api.send_text(wa_id, WELCOME_MESSAGE)
                self.supabase.update_state(wa_id, "inicio")
            else:
                # Opção inválida - mostrar erro e reenviar pergunta sobre mais fotos
                await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
                await self.mega_api.send_text(wa_id, DONATION_ASK_MORE_PHOTOS)

    async def handle_acolhimento(self, wa_id: str, text_content: str):
        """Handle fluxo de acolhimento."""
        if text_content == "1":
            # Solicitar mais informações
            await self.mega_api.send_text(wa_id, ACOLHIMENTO_CONTACT)
            self.supabase.update_state(wa_id, "inicio")
        elif text_content == "2":
            # Voltar ao menu principal
            await self.mega_api.send_text(wa_id, WELCOME_MESSAGE)
            self.supabase.update_state(wa_id, "inicio")
        else:
            # Opção inválida - mostrar erro e reenviar mensagem de acolhimento
            await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
            await self.mega_api.send_text(wa_id, ACOLHIMENTO_WELCOME)

    async def handle_lojas(self, wa_id: str, text_content: str):
        """Handle fluxo de lojas."""
        if text_content == "1":
            # Falar com atendente
            await self.mega_api.send_text(wa_id, LOJAS_CONTACT)
            self.supabase.update_state(wa_id, "inicio")
        elif text_content == "2":
            # Voltar ao menu principal
            await self.mega_api.send_text(wa_id, WELCOME_MESSAGE)
            self.supabase.update_state(wa_id, "inicio")
        else:
            # Opção inválida - mostrar erro e reenviar menu de lojas
            await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
            await self.mega_api.send_text(wa_id, LOJAS_MENU)

    async def handle_servicos(self, wa_id: str, text_content: str):
        """Handle fluxo de serviços."""
        if text_content == "1":
            # Solicitar orçamento
            await self.mega_api.send_text(wa_id, SERVICES_CONTACT)
            self.supabase.update_state(wa_id, "inicio")
        elif text_content == "2":
            # Voltar ao menu principal
            await self.mega_api.send_text(wa_id, WELCOME_MESSAGE)
            self.supabase.update_state(wa_id, "inicio")
        else:
            # Opção inválida - mostrar erro e reenviar menu de serviços
            await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
            await self.mega_api.send_text(wa_id, SERVICES_MENU)

    async def handle_fretes(self, wa_id: str, text_content: str):
        """Handle fluxo de fretes."""
        if text_content == "1":
            # Solicitar orçamento
            await self.mega_api.send_text(wa_id, FRETES_CONTACT)
            self.supabase.update_state(wa_id, "inicio")
        elif text_content == "2":
            # Voltar ao menu principal
            await self.mega_api.send_text(wa_id, WELCOME_MESSAGE)
            self.supabase.update_state(wa_id, "inicio")
        else:
            # Opção inválida - mostrar erro e reenviar menu de fretes
            await self.mega_api.send_text(wa_id, ERROR_INVALID_OPTION)
            await self.mega_api.send_text(wa_id, FRETES_MENU)
