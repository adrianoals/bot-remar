from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.client: Client = create_client(self.url, self.key)

    def get_user_state(self, wa_id: str):
        """Busca o estado atual da conversa do usuário."""
        try:
            response = self.client.table("conversas").select("*").eq("wa_id", wa_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar estado do usuário {wa_id}: {e}")
            return None

    def create_or_update_user(self, wa_id: str, updates: dict):
        """Cria ou atualiza o registro do usuário na tabela conversas."""
        try:
            existing = self.get_user_state(wa_id)
            if existing:
                self.client.table("conversas").update(updates).eq("wa_id", wa_id).execute()
            else:
                data = {"wa_id": wa_id, **updates}
                self.client.table("conversas").insert(data).execute()
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário {wa_id}: {e}")

    # Outros métodos para salvar doações, registrar logs, etc.
