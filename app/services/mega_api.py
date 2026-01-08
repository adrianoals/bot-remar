import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MegaApiService:
    def __init__(self):
        self.base_url = settings.MEGA_API_URL
        self.instance_key = settings.MEGA_API_INSTANCE_KEY
        self.token = settings.MEGA_API_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def send_text(self, to_number: str, text: str):
        """Envie uma mensagem de texto simples."""
        url = f"{self.base_url}/sendMessage/{self.instance_key}/text"
        payload = {
            "messageData": {
                "to": to_number,
                "text": text
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Erro ao enviar mensagem para {to_number}: {e}")
                return None

    # Implementar outros métodos como send_image, download_media, etc.
