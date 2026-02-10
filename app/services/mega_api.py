import httpx
from app.core.config import settings
import logging
from typing import Optional, Dict, Any
import base64

logger = logging.getLogger(__name__)

class MegaApiService:
    def __init__(self):
        base_url = (settings.MEGA_API_URL or "").strip()
        
        # Adicionar protocolo automaticamente se não tiver
        if base_url and not base_url.startswith(("http://", "https://")):
            logger.warning(f"⚠️ MEGA_API_URL sem protocolo. Adicionando https:// automaticamente")
            base_url = f"https://{base_url}"
        
        # Normaliza URL para evitar duplicar "/rest" nos endpoints.
        self.base_url = base_url.rstrip("/")
        if self.base_url.endswith("/rest"):
            self.base_url = self.base_url[:-5]
        self.instance_key = settings.MEGA_API_INSTANCE_KEY
        self.token = settings.MEGA_API_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"🔧 MegaAPI configurada - URL: {self.base_url}, Instance: {self.instance_key[:20]}...")

    async def send_text(self, to_number: str, text: str) -> Optional[Dict[str, Any]]:
        """Envia uma mensagem de texto simples."""
        # Validações
        if not self.base_url:
            logger.error("MEGA_API_URL não está configurada no .env")
            return None
        
        if not self.base_url.startswith(("http://", "https://")):
            logger.error(f"MEGA_API_URL deve começar com http:// ou https://. Valor atual: {self.base_url}")
            return None
        
        if not to_number:
            logger.error("Número de destino (to_number) está vazio")
            return None
        
        if not text:
            logger.warning("Texto da mensagem está vazio")
        
        # URL correta da MegaAPI: /rest/sendMessage/{instance_key}/text
        url = f"{self.base_url}/rest/sendMessage/{self.instance_key}/text"
        payload = {
            "messageData": {
                "to": to_number,
                "text": text
            }
        }
        logger.info(f"📤 Enviando mensagem para {to_number} via {url}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Erro ao enviar mensagem para {to_number}: {e}")
                return None

    async def download_media(self, media_data: Dict[str, Any]) -> Optional[bytes]:
        """Baixa uma mídia (imagem, áudio, documento) da MegaAPI."""
        # URL correta da MegaAPI: /rest/instance/downloadMediaMessage/{instance_key}
        url = f"{self.base_url}/rest/instance/downloadMediaMessage/{self.instance_key}"
        payload = {
            "messageKeys": media_data
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload, timeout=30.0)
                response.raise_for_status()
                content_type = (response.headers.get("content-type") or "").lower()

                # Algumas respostas da MegaAPI vêm em JSON com base64/url da mídia.
                if "application/json" in content_type or response.content.startswith(b"{"):
                    try:
                        payload_json = response.json()
                        media_bytes = await self._extract_media_bytes_from_payload(client, payload_json)
                        if media_bytes:
                            logger.info(
                                "download_media: bytes extraídos de envelope JSON (keys=%s)",
                                list(payload_json.keys()) if isinstance(payload_json, dict) else type(payload_json).__name__,
                            )
                            return media_bytes
                        logger.error("download_media: resposta JSON sem bytes de mídia utilizáveis")
                        return None
                    except Exception as e:
                        logger.error(f"download_media: erro ao parsear JSON da mídia: {e}")
                        return None

                # Quando vier binário direto.
                return response.content
            except httpx.HTTPError as e:
                logger.error(f"Erro ao baixar mídia: {e}")
                return None

    async def _extract_media_bytes_from_payload(self, client: httpx.AsyncClient, payload: Any) -> Optional[bytes]:
        """Extrai bytes de mídia de payload JSON retornado pela MegaAPI."""

        async def decode_candidate(value: Any) -> Optional[bytes]:
            if value is None:
                return None
            if isinstance(value, bytes):
                return value
            if isinstance(value, dict):
                # Tenta chaves comuns primeiro
                for k in ("data", "base64", "file", "media", "buffer", "content", "body", "url", "mediaUrl"):
                    if k in value:
                        res = await decode_candidate(value.get(k))
                        if res:
                            return res
                # Fallback recursivo
                for v in value.values():
                    res = await decode_candidate(v)
                    if res:
                        return res
                return None
            if isinstance(value, list):
                for item in value:
                    res = await decode_candidate(item)
                    if res:
                        return res
                return None
            if isinstance(value, str):
                s = value.strip()
                if not s:
                    return None

                # data URI: data:image/jpeg;base64,AAAA...
                if s.startswith("data:") and ";base64," in s:
                    try:
                        return base64.b64decode(s.split(";base64,", 1)[1], validate=False)
                    except Exception:
                        return None

                # URL da mídia (quando API retorna link em vez de bytes/base64)
                if s.startswith("http://") or s.startswith("https://"):
                    try:
                        r = await client.get(s, timeout=30.0)
                        r.raise_for_status()
                        return r.content
                    except Exception as e:
                        logger.error(f"download_media: erro ao baixar mídia por URL direta: {e}")
                        return None

                # Base64 puro
                try:
                    decoded = base64.b64decode(s, validate=False)
                    # Evita aceitar textos muito curtos que não são mídia real
                    if decoded and len(decoded) > 32:
                        return decoded
                except Exception:
                    return None
            return None

        return await decode_candidate(payload)

    def extract_media_data(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrai dados de mídia de uma mensagem."""
        # Verificar diferentes tipos de mensagem com mídia
        if "imageMessage" in message:
            img = message["imageMessage"]
            return {
                "mediaKey": img.get("mediaKey"),
                "directPath": img.get("directPath"),
                "url": img.get("url"),
                "mimetype": img.get("mimetype", "image/jpeg"),
                "messageType": "image"
            }
        elif "audioMessage" in message:
            audio = message["audioMessage"]
            return {
                "mediaKey": audio.get("mediaKey"),
                "directPath": audio.get("directPath"),
                "url": audio.get("url"),
                "mimetype": audio.get("mimetype", "audio/ogg"),
                "messageType": "audio"
            }
        elif "documentMessage" in message:
            doc = message["documentMessage"]
            return {
                "mediaKey": doc.get("mediaKey"),
                "directPath": doc.get("directPath"),
                "url": doc.get("url"),
                "mimetype": doc.get("mimetype", "application/pdf"),
                "messageType": "document"
            }
        elif "videoMessage" in message:
            video = message["videoMessage"]
            return {
                "mediaKey": video.get("mediaKey"),
                "directPath": video.get("directPath"),
                "url": video.get("url"),
                "mimetype": video.get("mimetype", "video/mp4"),
                "messageType": "video"
            }
        return None

    async def download_and_save_media(self, media_data: Dict[str, Any], save_path: str) -> bool:
        """Baixa uma mídia e salva em um arquivo."""
        try:
            media_bytes = await self.download_media(media_data)
            if media_bytes:
                import os
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(media_bytes)
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao baixar e salvar mídia: {e}")
            return False
