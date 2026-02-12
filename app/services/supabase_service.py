from supabase import create_client, Client
from app.core.config import settings
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.client: Client = create_client(self.url, self.key)

    def get_user_state(self, wa_id: str) -> Optional[Dict[str, Any]]:
        """Busca o estado atual da conversa do usuário."""
        try:
            response = self.client.table("conversas").select("*").eq("wa_id", f"+{wa_id}").execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar estado do usuário {wa_id}: {e}")
            return None

    def get_global_automation_enabled(self) -> bool:
        """Retorna se a automação global está ativa (default=True)."""
        try:
            response = (
                self.client.table("automacao_controle")
                .select("ativo_global")
                .eq("id", 1)
                .limit(1)
                .execute()
            )
            if response.data:
                return bool(response.data[0].get("ativo_global", True))
            return True
        except Exception as e:
            logger.warning(f"Falha ao consultar automação global (assumindo ativa): {e}")
            return True

    def set_global_automation(self, enabled: bool) -> bool:
        """Ativa/desativa automação global."""
        try:
            payload = {"id": 1, "ativo_global": bool(enabled), "atualizado_em": datetime.now().isoformat()}
            self.client.table("automacao_controle").upsert(payload).execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar automação global: {e}")
            return False

    def set_all_users_to_initial(self) -> bool:
        """Reseta todos os usuários para estado inicial."""
        try:
            payload = {
                "estado": "inicio",
                "mensagem_temp": None,
                "data": datetime.now().strftime("%Y-%m-%d"),
                "horario": datetime.now().strftime("%H:%M:%S"),
            }
            self.client.table("conversas").update(payload).neq("wa_id", "").execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao resetar estados de todos usuários: {e}")
            return False

    def set_user_automation(self, wa_id: str, enabled: bool) -> bool:
        """Ativa/desativa automação para um usuário (via estado em conversas)."""
        try:
            target_state = "inicio" if enabled else "manual"
            self.create_or_update_user(wa_id, {"estado": target_state, "mensagem_temp": None})
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar automação do usuário {wa_id}: {e}")
            return False

    def create_or_update_user(self, wa_id: str, updates: dict):
        """Cria ou atualiza o registro do usuário na tabela conversas."""
        try:
            from datetime import datetime
            timezone = 'America/Sao_Paulo'
            
            logger.info(f"💾 create_or_update_user chamado - wa_id: {wa_id}, updates: {updates}")
            
            # Adicionar data e horário se não existirem
            if 'data' not in updates:
                updates['data'] = datetime.now().strftime('%Y-%m-%d')
            if 'horario' not in updates:
                updates['horario'] = datetime.now().strftime('%H:%M:%S')
            
            existing = self.get_user_state(wa_id)
            logger.info(f"🔍 Usuário existente? {existing is not None}")
            
            if existing:
                logger.info(f"🔄 Atualizando usuário existente: +{wa_id}")
                logger.info(f"📝 Campos a atualizar: {updates}")
                result = self.client.table("conversas").update(updates).eq("wa_id", f"+{wa_id}").execute()
                logger.info(f"✅ Usuário atualizado: {result.data if hasattr(result, 'data') else 'OK'}")
            else:
                logger.info(f"➕ Criando novo usuário: +{wa_id}")
                data = {"wa_id": f"+{wa_id}", **updates}
                logger.info(f"📝 Dados a inserir: {data}")
                result = self.client.table("conversas").insert(data).execute()
                logger.info(f"✅ Usuário criado: {result.data if hasattr(result, 'data') else 'OK'}")
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar usuário {wa_id}: {e}", exc_info=True)

    def update_state(self, wa_id: str, estado: str):
        """Atualiza apenas o estado do usuário."""
        self.create_or_update_user(wa_id, {"estado": estado})

    def create_doacao(self, wa_id: str, tipo_doacao: str) -> Optional[Dict[str, Any]]:
        """Cria um novo registro de doação na tabela doacoes."""
        try:
            from datetime import datetime
            timezone = 'America/Sao_Paulo'
            now = datetime.now()
            
            data = {
                "wa_id": f"+{wa_id}",
                "tipo_doacao": tipo_doacao,
                "criado_em": now.isoformat(),
                "atualizado_em": now.isoformat()
            }
            
            response = self.client.table("doacoes").insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Erro ao criar doação para {wa_id}: {e}")
            return None

    def update_doacao(self, wa_id: str, updates: dict):
        """Atualiza um registro de doação existente."""
        try:
            from datetime import datetime
            updates['atualizado_em'] = datetime.now().isoformat()
            
            # Buscar doação mais recente do usuário
            response = self.client.table("doacoes").select("*").eq("wa_id", f"+{wa_id}").order("criado_em", desc=True).limit(1).execute()
            
            if response.data:
                doacao_id = response.data[0]['id']
                self.client.table("doacoes").update(updates).eq("id", doacao_id).execute()
            else:
                logger.warning(f"Nenhuma doação encontrada para atualizar: {wa_id}")
        except Exception as e:
            logger.error(f"Erro ao atualizar doação para {wa_id}: {e}")

    def get_latest_doacao(self, wa_id: str) -> Optional[Dict[str, Any]]:
        """Busca a doação mais recente do usuário."""
        try:
            response = self.client.table("doacoes").select("*").eq("wa_id", f"+{wa_id}").order("criado_em", desc=True).limit(1).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar doação para {wa_id}: {e}")
            return None

    def upload_media(
        self,
        file_path: str,
        bucket: str = "whatsapp_media",
        file_name: str = None,
        content_type: Optional[str] = None,
    ) -> Optional[str]:
        """Faz upload de uma mídia para o Supabase Storage."""
        try:
            import os
            import mimetypes
            if not file_name:
                file_name = os.path.basename(file_path)
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Preserva o mimetype real quando fornecido; fallback por extensão.
            if not content_type:
                guessed, _ = mimetypes.guess_type(file_name or file_path)
                content_type = guessed or "application/octet-stream"
            
            # Upload para Supabase Storage
            response = self.client.storage.from_(bucket).upload(
                file_name,
                file_data,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            
            # Obter URL pública
            public_url_response = self.client.storage.from_(bucket).get_public_url(file_name)
            return public_url_response
        except Exception as e:
            logger.error(f"Erro ao fazer upload de mídia: {e}")
            return None
