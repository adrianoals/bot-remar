import unittest
from unittest.mock import MagicMock, patch
import logging
import sys
import os

# Adiciona o diretório raiz ao path para importar os módulos da app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.flows.manager import FlowManager

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
    
    def upload_media(self, file_path, bucket="whatsapp_media", file_name=None):
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

if __name__ == '__main__':
    unittest.main()
