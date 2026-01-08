from app.services.mega_api import MegaApiService
from app.services.supabase_service import SupabaseService
from app.templates.menus import Menus
from app.templates.messages import Messages

class FlowManager:
    def __init__(self):
        self.mega_api = MegaApiService()
        self.supabase = SupabaseService()

    async def handle_message(self, data: dict):
        """
        Recebe o payload do webhook e decide o que fazer.
        """
        try:
            # Extrair informações básicas (simplificado)
            body = data.get("body", {})
            message = body.get("message", {})
            key = body.get("key", {})
            remote_jid = key.get("remoteJid", "")
            from_me = key.get("fromMe", False)
            is_group = body.get("isGroup", False)

            if from_me or is_group:
                return # Ignorar minhas mensagens ou grupos

            wa_id = remote_jid.split("@")[0]
            
            # Aqui entraria a lógica de extrair texto, imagem, etc.
            text_content = ""
            if "conversation" in message:
                text_content = message["conversation"]
            elif "extendedTextMessage" in message:
                text_content = message["extendedTextMessage"]["text"]
            
            # Lógica simples de resposta para teste
            user_state = self.supabase.get_user_state(wa_id)
            
            # Se não tem estado ou reset, manda menu inicial
            if not user_state or text_content.lower() in ["oi", "ola", "começar"]:
                await self.mega_api.send_text(wa_id, Menus.STATES_MENU)
                self.supabase.create_or_update_user(wa_id, {"estado": "inicio"})
            else:
                # Aqui você expandiria para switch cases ou if/else com base no estado
                await self.mega_api.send_text(wa_id, f"Você disse: {text_content}. (Fluxo ainda não implementado)")

        except Exception as e:
            print(f"Erro no processamento: {e}")
