import unittest
from unittest.mock import patch
import logging
import sys
import os

# Adiciona o diretório raiz ao path para importar os módulos da app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.flows.manager import FlowManager
from app.services.google_sheets_service import GoogleSheetsService

# Configuração básica de logging para ver o fluxo no terminal
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("Simulation")

class MockSupabaseService:
    def __init__(self):
        self.users = {}
        self.doacoes = {}
        self._doacao_counter = 0

    def get_user_state(self, wa_id):
        # Retorna o estado do usuário (removendo o + do wa_id para a chave interna se necessário)
        return self.users.get(wa_id)

    def create_or_update_user(self, wa_id, updates):
        if wa_id not in self.users:
            self.users[wa_id] = {"wa_id": f"+{wa_id}"}
        self.users[wa_id].update(updates)
        logger.info(f"💾 [SUPABASE MOCK] Usuário {wa_id} atualizado: {updates}")

    def update_state(self, wa_id, estado):
        self.create_or_update_user(wa_id, {"estado": estado})

    def create_doacao(self, wa_id, tipo_doacao):
        self._doacao_counter += 1
        doacao_id = self._doacao_counter
        entry = {
            "id": doacao_id,
            "wa_id": f"+{wa_id}",
            "tipo_doacao": tipo_doacao,
            "fotos": []
        }
        if wa_id not in self.doacoes:
            self.doacoes[wa_id] = []
        self.doacoes[wa_id].append(entry)
        logger.info(f"🎁 [SUPABASE MOCK] Doação criada: {tipo_doacao}")
        return entry

    def update_doacao(self, wa_id, updates):
        if wa_id in self.doacoes and self.doacoes[wa_id]:
            # Atualiza a última
            self.doacoes[wa_id][-1].update(updates)
            logger.info(f"🎁 [SUPABASE MOCK] Doação atualizada: {updates}")

    def get_latest_doacao(self, wa_id):
        if wa_id in self.doacoes and self.doacoes[wa_id]:
            return self.doacoes[wa_id][-1]
        return None
    
    def upload_media(self, file_path, bucket="whatsapp_media", file_name=None, content_type=None):
        return f"https://fake-supabase.com/storage/{bucket}/{file_name}"

class MockMegaApiService:
    def __init__(self):
        self.sent_messages = []

    async def send_text(self, to_number, text):
        logger.info(f"📱 [WHATSAPP MOCK] Bot para {to_number}: {text[:50]}..." if len(text) > 50 else f"📱 [WHATSAPP MOCK] Bot para {to_number}: {text}")
        self.sent_messages.append({"to": to_number, "text": text})
        return {"id": "fake_msg_id"}
    
    def extract_media_data(self, message):
        # Mock de extração de mídia se necessário
        if "imageMessage" in message:
            return {"mimetype": "image/jpeg", "messageType": "image"}
        return None

    async def download_media(self, media_data):
        # Retorna bytes válidos de PNG para testes de detecção por assinatura.
        return b"\x89PNG\r\n\x1a\n" + b"test-image-bytes"

    async def download_and_save_media(self, media_data, path):
        # Cria um arquivo fake
        with open(path, 'w') as f:
            f.write("fake image data")
        return True

class TestFlowSimulation(unittest.IsolatedAsyncioTestCase):
    
    async def test_fluxo_doacao_completo(self):
        """
        Simula um usuário fazendo uma doação completa de item.
        """
        print("\n\n=== INICIANDO SIMULAÇÃO DE FLUXO DE DOAÇÃO ===")
        
        # Mocks
        with patch('app.flows.manager.SupabaseService', side_effect=MockSupabaseService) as MockSupabase, \
             patch('app.flows.manager.MegaApiService', side_effect=MockMegaApiService) as MockMega:
            
            # Instancia o gerenciador (que vai usar os mocks)
            manager = FlowManager()
            
            # Acessar as instâncias reais dos mocks para asserções
            mock_supabase = manager.supabase
            mock_mega = manager.mega_api
            
            wa_id = "5511999999999"
            
            # Helper para enviar mensagem do usuário
            async def user_sends(text):
                print(f"\n👤 [USUÁRIO] Envia: {text}")
                data = {
                    "key": {"remoteJid": f"{wa_id}@s.whatsapp.net", "fromMe": False},
                    "message": {"conversation": text},
                    "pushName": "Adriano Tester"
                }
                await manager.handle_message(data)

            # 1. Usuário envia "Oi"
            await user_sends("Oi")
            
            # Verifica se o estado foi salvo e mensagem de boas vindas enviada
            state = mock_supabase.get_user_state(wa_id)
            self.assertEqual(state['estado'], 'inicio')
            # A última mensagem enviada pelo bot deve ser o menu principal (WELCOME_MESSAGE está no manager, difícil checar o valor exato sem importar, mas checamos se enviou)
            self.assertTrue(len(mock_mega.sent_messages) > 0)
            
            # 2. Usuário escolhe "1" (Doação)
            await user_sends("1")
            state = mock_supabase.get_user_state(wa_id)
            self.assertEqual(state['estado'], 'doacao')
            
            # 3. Usuário escolhe "2" (Doação de Item)
            await user_sends("2")
            state = mock_supabase.get_user_state(wa_id)
            self.assertEqual(state['estado'], 'doacao_item_1')
            
            # 4. Usuário escolhe Categoria "1" (Móveis)
            await user_sends("1")
            state = mock_supabase.get_user_state(wa_id)
            self.assertEqual(state['estado'], 'doacao_item_2')
            latest_doacao = mock_supabase.get_latest_doacao(wa_id)
            self.assertEqual(latest_doacao['tipo_doacao'], 'Móveis')
            
            # 5. Condição do item "1" (Bom)
            await user_sends("1")
            state = mock_supabase.get_user_state(wa_id)
            self.assertEqual(state['estado'], 'doacao_item_3') # Pede nome
            
            # 6. Informa Nome "Adriano"
            await user_sends("Adriano")
            state = mock_supabase.get_user_state(wa_id)
            self.assertEqual(state['estado'], 'doacao_item_4') # Confirma nome
            
            # 7. Confirma Nome "1"
            await user_sends("1")
            state = mock_supabase.get_user_state(wa_id)
            self.assertEqual(state['estado'], 'doacao_item_5') # Pede endereço
            self.assertEqual(mock_supabase.get_latest_doacao(wa_id)['nome_responsavel'], 'Adriano')

            print("\n=== SIMULAÇÃO CONCLUÍDA COM SUCESSO ===")

    async def test_estado_doacao_salva_texto_template(self):
        """
        Garante que estado_doacao salva o texto (não o número da opção).
        """
        with patch('app.flows.manager.SupabaseService', side_effect=MockSupabaseService), \
             patch('app.flows.manager.MegaApiService', side_effect=MockMegaApiService):
            manager = FlowManager()
            wa_id = "5511999999999"

            async def user_sends(text):
                data = {
                    "key": {"remoteJid": f"{wa_id}@s.whatsapp.net", "fromMe": False},
                    "message": {"conversation": text},
                    "pushName": "Adriano Tester"
                }
                await manager.handle_message(data)

            await user_sends("Oi")
            await user_sends("1")  # menu principal -> doacao
            await user_sends("2")  # tipo doacao -> item
            await user_sends("1")  # categoria
            await user_sends("2")  # estado item

            doacao = manager.supabase.get_latest_doacao(wa_id)
            self.assertEqual(doacao["estado_doacao"], "Usado em bom estado")

    async def test_senderpn_define_chave_conversa_e_destino(self):
        """
        Garante que senderPn é usado (normalizado) para chave do Supabase e destino da resposta.
        """
        with patch('app.flows.manager.SupabaseService', side_effect=MockSupabaseService), \
             patch('app.flows.manager.MegaApiService', side_effect=MockMegaApiService):
            manager = FlowManager()
            data = {
                "key": {
                    "remoteJid": "5511000000000@s.whatsapp.net",
                    "senderPn": "+55 (11) 98888-7777@s.whatsapp.net",
                    "fromMe": False
                },
                "message": {"conversation": "Oi"},
                "pushName": "Teste SenderPn"
            }
            await manager.handle_message(data)

            normalized = "5511988887777"
            self.assertIsNotNone(manager.supabase.get_user_state(normalized))
            self.assertEqual(manager.mega_api.sent_messages[-1]["to"], normalized)

    async def test_multiplas_fotos_acumulam_no_campo_fotos(self):
        with patch('app.flows.manager.SupabaseService', side_effect=MockSupabaseService), \
             patch('app.flows.manager.MegaApiService', side_effect=MockMegaApiService):
            manager = FlowManager()
            wa_id = "5511999999999"

            # Estado pronto para etapa de fotos
            manager.supabase.create_or_update_user(wa_id, {"estado": "doacao_item_9"})
            manager.supabase.create_doacao(wa_id, "Móveis")
            manager.supabase.update_doacao(
                wa_id,
                {
                    "email": "teste@email.com",
                    "horario_preferencial": "Tarde",
                    "fotos": '["https://existente"]',
                },
            )

            async def send_image():
                data = {
                    "key": {"remoteJid": f"{wa_id}@s.whatsapp.net", "fromMe": False},
                    "message": {"imageMessage": {"mimetype": "image/heic"}},
                    "pushName": "Adriano Tester",
                }
                await manager.handle_message(data)

            await send_image()
            await send_image()

            doacao = manager.supabase.get_latest_doacao(wa_id)
            fotos = FlowManager._parse_fotos(doacao.get("fotos"))
            self.assertGreaterEqual(len(fotos), 3)


class CapturingSheetsService(GoogleSheetsService):
    def __init__(self):
        self.rows = []

    def _append(self, sheet_name, values):
        self.rows.append((sheet_name, values))


class TestDataFormatting(unittest.TestCase):
    def test_parse_fotos_from_json_string_dict(self):
        fotos = FlowManager._parse_fotos('{"imagem1":"https://a","imagem2":"https://b"}')
        self.assertEqual(fotos, ["https://a", "https://b"])

    def test_append_doacao_item_column_order_matches_n8n(self):
        sheets = CapturingSheetsService()
        doacao = {
            "nome_responsavel": "Joao",
            "email": "joao@email.com",
            "telefone_whatsapp": "11999999999",
            "endereco_retirada": "Rua A, 123",
            "tipo_doacao": "Móveis",
            "estado_doacao": "Novo",
            "horario_preferencial": "Manhã",
            "fotos": '["https://img1","https://img2"]',
        }

        sheets.append_doacao_item(doacao, telefone="5511999999999")
        self.assertEqual(len(sheets.rows), 1)
        _, row = sheets.rows[0]

        # Ordem esperada conforme mapeamento do n8n (Doação Item):
        # Data Criação, Horário, Nome, Email, Telefone, Endereço,
        # Tipo De Doação, Estado Doação, Horário Preferencial, Fotos, Verificar Foto
        self.assertEqual(row[2], "Joao")
        self.assertEqual(row[3], "joao@email.com")
        self.assertEqual(row[4], "11999999999")
        self.assertEqual(row[5], "Rua A, 123")
        self.assertEqual(row[6], "Móveis")
        self.assertEqual(row[7], "Novo")
        self.assertEqual(row[8], "Manhã")
        self.assertIn("https://img1", row[9])
        self.assertIn("https://img2", row[9])
        self.assertEqual(row[10], "Copie a URL")

if __name__ == '__main__':
    unittest.main()
