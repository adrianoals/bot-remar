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

    def create_or_update_user(self, wa_id: str, updates: dict):
        """Cria ou atualiza o registro do usuário na tabela conversas."""
        try:
            from datetime import datetime
            timezone = 'America/Sao_Paulo'
            
            # Adicionar data e horário se não existirem
            if 'data' not in updates:
                updates['data'] = datetime.now().strftime('%Y-%m-%d')
            if 'horario' not in updates:
                updates['horario'] = datetime.now().strftime('%H:%M:%S')
            
            existing = self.get_user_state(wa_id)
            if existing:
                self.client.table("conversas").update(updates).eq("wa_id", f"+{wa_id}").execute()
            else:
                data = {"wa_id": f"+{wa_id}", **updates}
                self.client.table("conversas").insert(data).execute()
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário {wa_id}: {e}")

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

    def upload_media(self, file_path: str, bucket: str = "whatsapp_media", file_name: str = None) -> Optional[str]:
        """Faz upload de uma mídia para o Supabase Storage."""
        try:
            import os
            if not file_name:
                file_name = os.path.basename(file_path)
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Detectar content-type
            content_type = "image/jpeg"
            if file_path.endswith('.png'):
                content_type = "image/png"
            elif file_path.endswith('.gif'):
                content_type = "image/gif"
            elif file_path.endswith('.mp4'):
                content_type = "video/mp4"
            elif file_path.endswith('.pdf'):
                content_type = "application/pdf"
            
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
