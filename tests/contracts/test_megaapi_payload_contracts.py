import json
import os
import unittest
from unittest.mock import patch

from app.flows.manager import FlowManager


FIXTURES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "megaapi")
)


class _SupabaseMock:
    def __init__(self):
        self.users = {}

    def get_user_state(self, wa_id):
        return self.users.get(wa_id)

    def create_or_update_user(self, wa_id, updates):
        if wa_id not in self.users:
            self.users[wa_id] = {"wa_id": f"+{wa_id}"}
        self.users[wa_id].update(updates)

    def update_state(self, wa_id, estado):
        self.create_or_update_user(wa_id, {"estado": estado})

    def create_doacao(self, wa_id, tipo_doacao):
        return {"id": 1, "wa_id": f"+{wa_id}", "tipo_doacao": tipo_doacao}

    def update_doacao(self, wa_id, updates):
        return None

    def get_latest_doacao(self, wa_id):
        return None

    def upload_media(self, file_path, bucket="whatsapp_media", file_name=None, content_type=None):
        return f"https://fake-supabase.com/storage/{bucket}/{file_name}"


class _MegaMock:
    def __init__(self):
        self.sent = []

    async def send_text(self, to_number, text):
        self.sent.append({"to": to_number, "text": text})
        return {"ok": True}

    def extract_media_data(self, message):
        if "imageMessage" in message:
            return {
                "mediaKey": message["imageMessage"].get("mediaKey"),
                "directPath": message["imageMessage"].get("directPath"),
                "url": message["imageMessage"].get("url"),
                "mimetype": message["imageMessage"].get("mimetype", "image/jpeg"),
                "messageType": "image",
            }
        return None

    async def download_media(self, media_data):
        return b""


class TestMegaApiPayloadContracts(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    def _load(name: str):
        with open(os.path.join(FIXTURES_DIR, name), "r", encoding="utf-8") as f:
            return json.load(f)

    async def test_ack_payload_is_ignored(self):
        data = self._load("ack_message.json")
        with patch("app.flows.manager.SupabaseService", side_effect=_SupabaseMock), patch(
            "app.flows.manager.MegaApiService", side_effect=_MegaMock
        ):
            manager = FlowManager()
            await manager.handle_message(data)
            self.assertEqual(manager.mega_api.sent, [])
            self.assertEqual(manager.supabase.users, {})

    async def test_senderpn_is_used_as_primary_user_key(self):
        data = self._load("conversation_senderpn.json")
        with patch("app.flows.manager.SupabaseService", side_effect=_SupabaseMock), patch(
            "app.flows.manager.MegaApiService", side_effect=_MegaMock
        ):
            manager = FlowManager()
            await manager.handle_message(data)
            self.assertIn("5511974124980", manager.supabase.users)
            self.assertEqual(manager.mega_api.sent[-1]["to"], "5511974124980")

    def test_extract_text_content_contract_variants(self):
        with patch("app.flows.manager.SupabaseService", side_effect=_SupabaseMock), patch(
            "app.flows.manager.MegaApiService", side_effect=_MegaMock
        ):
            manager = FlowManager()

            self.assertEqual(manager.extract_text_content({"conversation": "Oi"}), "Oi")
            self.assertEqual(
                manager.extract_text_content({"extendedTextMessage": {"text": "Texto estendido"}}),
                "Texto estendido",
            )
            self.assertEqual(
                manager.extract_text_content(
                    {"ephemeralMessage": {"message": {"extendedTextMessage": {"text": "Efemera"}}}}
                ),
                "Efemera",
            )
            self.assertEqual(
                manager.extract_text_content(
                    {"listResponseMessage": {"singleSelectReply": {"selectedRowId": "2"}}}
                ),
                "2",
            )

    def test_extract_media_data_contract_image_payload(self):
        data = self._load("image_message.json")
        with patch("app.flows.manager.SupabaseService", side_effect=_SupabaseMock), patch(
            "app.flows.manager.MegaApiService", side_effect=_MegaMock
        ):
            manager = FlowManager()
            media = manager.mega_api.extract_media_data(data["message"])
            self.assertEqual(media["messageType"], "image")
            self.assertEqual(media["mimetype"], "image/jpeg")
            self.assertTrue(media["directPath"])


if __name__ == "__main__":
    unittest.main()
