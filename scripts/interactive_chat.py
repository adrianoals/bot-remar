import asyncio
import logging
import sys
import os
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.flows.manager import FlowManager

# Configurar logs para serem limpos, mostrando apenas o essencial
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("ChatSimulator")

# Cores para o terminal ficarem bonitas
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# === MOCKS ===
# (Versão simplificada dos mocks para interação em tempo real)

class InteractiveSupabaseMock:
    def __init__(self):
        self.user_data = {}
        self.doacoes = []
        print(f"{Colors.WARNING}⚠️  Usando Supabase Simulado (Memória){Colors.ENDC}")

    def get_user_state(self, wa_id):
        return self.user_data.get(wa_id)

    def create_or_update_user(self, wa_id, updates):
        if wa_id not in self.user_data:
            self.user_data[wa_id] = {"wa_id": f"+{wa_id}", "estado": "inicio"}
        
        # Atualiza o estado
        self.user_data[wa_id].update(updates)
        
        # Feedback visual de mudança de estado, se houver
        if 'estado' in updates:
            print(f"{Colors.WARNING}   [Estado alterado para: {updates['estado']}]{Colors.ENDC}")

    def update_state(self, wa_id, estado):
        self.create_or_update_user(wa_id, {"estado": estado})
    
    def create_doacao(self, wa_id, tipo_doacao):
        # Cria uma nova doação
        doacao = {
            "id": len(self.doacoes) + 1,
            "wa_id": f"+{wa_id}",
            "tipo_doacao": tipo_doacao,
            "criado_em": datetime.now().isoformat(),
            "fotos": []
        }
        self.doacoes.append(doacao)
        print(f"{Colors.WARNING}   [Nova doação criada: {tipo_doacao}]{Colors.ENDC}")
        return doacao

    def update_doacao(self, wa_id, updates):
        # Atualiza a última doação do usuário
        user_doacoes = [d for d in self.doacoes if d['wa_id'] == f"+{wa_id}"]
        if user_doacoes:
            user_doacoes[-1].update(updates)
            # Mostra o que foi atualizado
            items = ", ".join([f"{k}={v}" for k, v in updates.items()])
            print(f"{Colors.WARNING}   [Doação atualizada: {items}]{Colors.ENDC}")

    def get_latest_doacao(self, wa_id):
        user_doacoes = [d for d in self.doacoes if d['wa_id'] == f"+{wa_id}"]
        return user_doacoes[-1] if user_doacoes else None
    
    def upload_media(self, file_path, bucket, file_name=None):
        return "https://url-simulada.com/imagem.jpg"

class InteractiveMegaApiMock:
    def __init__(self):
        print(f"{Colors.WARNING}⚠️  Usando MegaAPI Simulada (Terminal){Colors.ENDC}")

    async def send_text(self, to_number, text):
        # Simula o "Typing..." para dar um efeito realista
        await asyncio.sleep(0.5)
        print(f"\n{Colors.GREEN}🤖 BOT:{Colors.ENDC}")
        print(f"{Colors.GREEN}{text}{Colors.ENDC}")
        print("-" * 30)
        return {"success": True}

    def extract_media_data(self, message):
        # Simula extração se o usuário digitar [FOTO]
        if "conversation" in message and message["conversation"].strip().upper() == "[FOTO]":
             print(f"{Colors.WARNING}   [Simulando envio de imagem...]{Colors.ENDC}")
             return {"mimetype": "image/jpeg", "messageType": "image"}
        return None

    async def download_and_save_media(self, media_data, path):
        return True

# === SISTEMA DE CHAT ===

async def run_chat():
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== SIMULADOR DE CHATBOT REMAR ==={Colors.ENDC}")
    print("Digite suas mensagens e pressione ENTER.")
    print("Para simular envio de foto, digite: [FOTO]")
    print(f"Para sair, digite: {Colors.FAIL}sair{Colors.ENDC} ou {Colors.FAIL}exit{Colors.ENDC}")
    print("-" * 50)

    # Patch nas classes originais para usar os Mocks
    import app.flows.manager
    app.flows.manager.SupabaseService = InteractiveSupabaseMock
    app.flows.manager.MegaApiService = InteractiveMegaApiMock

    manager = FlowManager()
    wa_id = "5511999999999" # ID Fictício

    while True:
        try:
            # Input do usuário
            user_input = input(f"\n{Colors.CYAN}👤 VOCÊ: {Colors.ENDC}")
            
            if user_input.lower() in ["sair", "exit", "quit"]:
                print(f"\n{Colors.HEADER}Encerrando simulação. Até logo! 👋{Colors.ENDC}")
                break

            if not user_input.strip():
                continue

            # Montar payload igual ao da MegaAPI
            # Se for [FOTO], o mock da MegaApi vai interpretar como imagem
            data = {
                "key": {
                    "remoteJid": f"{wa_id}@s.whatsapp.net",
                    "fromMe": False,
                    "id": "MSG-SIMULADA-123"
                },
                "pushName": "Usuário Teste",
                "message": {
                    "conversation": user_input
                },
                "messageType": "conversation",
                "isGroup": False
            }

            # Se o usuário digitou [FOTO], vamos enganar o fluxo para achar que é imagem
            if user_input.strip().upper() == "[FOTO]":
                 data["message"] = {
                     "imageMessage": {
                         "url": "https://...",
                         "mimetype": "image/jpeg",
                         "caption": "Segue a foto"
                     }
                 }

            # Processar mensagem
            await manager.handle_message(data)

        except KeyboardInterrupt:
            print(f"\n{Colors.HEADER}Encerrando simulação...{Colors.ENDC}")
            break
        except Exception as e:
            print(f"{Colors.FAIL}Erro na simulação: {e}{Colors.ENDC}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(run_chat())
    except KeyboardInterrupt:
        pass
