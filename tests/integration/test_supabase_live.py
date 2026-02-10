import os
import unittest


@unittest.skipUnless(
    os.getenv("RUN_LIVE_TESTS") == "1",
    "Defina RUN_LIVE_TESTS=1 para executar testes de integracao reais",
)
class TestSupabaseLive(unittest.TestCase):
    def setUp(self):
        from app.core.config import settings
        from supabase import create_client

        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def test_tables_are_accessible(self):
        self.client.table("conversas").select("wa_id").limit(1).execute()
        self.client.table("doacoes").select("id").limit(1).execute()

    def test_storage_bucket_exists(self):
        buckets = self.client.storage.list_buckets()
        names = [b.name for b in buckets]
        self.assertIn("whatsapp_media", names)

    def test_rpc_get_ultima_doacao_is_callable(self):
        # apenas contrato de chamada; pode retornar vazio
        self.client.rpc("get_ultima_doacao", {"wa_id_param": "+5511999999999"}).execute()


if __name__ == "__main__":
    unittest.main()
