"""
Serviço de integração com Google Sheets (append de linhas).
Usado para registrar no REMAR CHAT: doação valor, acolhimento, lojas, serviço, fretes e doação item.
Requer Service Account configurada (ver docs/GOOGLE_SHEETS_SETUP.md).
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# Escopo necessário para editar planilhas
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Nomes exatos das abas na planilha REMAR CHAT
SHEET_DOACAO_VALOR = "Doação Valor"
SHEET_ACOLHIMENTO = "Acolhimento"
SHEET_LOJAS = "Lojas Solidárias"
SHEET_SERVICO = "Contratar Um Serviço"
SHEET_FRETES = "Fretes e Mudanças"
SHEET_DOACAO_ITEM = "Doação Item"


def _fmt_data(s: Optional[str]) -> str:
    """Converte data YYYY-MM-DD para DD/MM/YYYY. Se vazio, usa hoje (America/Sao_Paulo)."""
    if s:
        try:
            d = datetime.strptime(str(s)[:10], "%Y-%m-%d")
            return d.strftime("%d/%m/%Y")
        except Exception:
            pass
    return datetime.now().strftime("%d/%m/%Y")


def _fmt_horario(s: Optional[str]) -> str:
    """Retorna horário no formato HH:MM ou HH:MM:SS. Se vazio, usa agora."""
    if s:
        v = str(s).strip()
        if v:
            return v
    return datetime.now().strftime("%H:%M:%S")


def _fmt_fotos(fotos: Any) -> str:
    """Converte fotos (lista de URLs ou string) em uma única string."""
    if fotos is None:
        return ""
    if isinstance(fotos, list):
        return "\n".join(str(u) for u in fotos)
    if isinstance(fotos, dict):
        return "\n".join(str(u) for u in fotos.values())
    if isinstance(fotos, str):
        raw = fotos.strip()
        if not raw:
            return ""
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return "\n".join(str(u) for u in parsed)
            if isinstance(parsed, dict):
                return "\n".join(str(u) for u in parsed.values())
        except Exception:
            pass
        return raw
    return str(fotos)


class GoogleSheetsService:
    """
    Append de linhas no Google Sheets (planilha REMAR CHAT).
    Se GOOGLE_SHEETS_SPREADSHEET_ID ou credenciais não estiverem configurados, todas as chamadas são no-op.
    """

    def __init__(self) -> None:
        self._enabled = False
        self._sheet_id: Optional[str] = settings.GOOGLE_SHEETS_SPREADSHEET_ID or None
        self._service: Any = None

        if not self._sheet_id or not self._sheet_id.strip():
            logger.info("Google Sheets: GOOGLE_SHEETS_SPREADSHEET_ID não configurado; integração desativada.")
            return

        try:
            import os
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            creds = None
            if settings.GOOGLE_APPLICATION_CREDENTIALS and settings.GOOGLE_APPLICATION_CREDENTIALS.strip():
                path = settings.GOOGLE_APPLICATION_CREDENTIALS.strip()
                if not os.path.isabs(path):
                    # Resolver em relação ao diretório de trabalho atual (raiz do projeto)
                    path = os.path.join(os.getcwd(), path)
                if not os.path.isfile(path):
                    raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {path}")
                creds = service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
            elif settings.GOOGLE_SHEETS_CREDENTIALS_JSON and settings.GOOGLE_SHEETS_CREDENTIALS_JSON.strip():
                info = json.loads(settings.GOOGLE_SHEETS_CREDENTIALS_JSON.strip())
                creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

            if creds is None:
                logger.warning(
                    "Google Sheets: Defina GOOGLE_APPLICATION_CREDENTIALS ou GOOGLE_SHEETS_CREDENTIALS_JSON; "
                    "integração desativada."
                )
                return

            self._service = build("sheets", "v4", credentials=creds)
            self._enabled = True
            logger.info("Google Sheets: integração ativada.")
        except Exception as e:
            logger.warning(f"Google Sheets: falha ao inicializar ({e}); integração desativada.")

    def _append(self, sheet_name: str, values: List[Any]) -> None:
        if not self._enabled or not self._service:
            return
        try:
            body = {"values": [values]}
            range_name = f"'{sheet_name}'!A:Z"
            (
                self._service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self._sheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body=body,
                )
                .execute()
            )
            logger.info(f"Google Sheets: linha adicionada na aba '{sheet_name}'.")
        except Exception as e:
            logger.error(f"Google Sheets: erro ao adicionar linha na aba '{sheet_name}': {e}", exc_info=True)

    def append_doacao_valor(self, conv: Dict[str, Any], telefone: Optional[str] = None) -> None:
        """Append na aba Doação Valor: Data, Horário, Telefone, Nome, Doação Valor = '-'."""
        # telefone: número real (reply_to/senderPn) quando disponível; senão wa_id da conversa
        row = [
            _fmt_data(conv.get("data")),
            _fmt_horario(conv.get("horario")),
            (telefone or conv.get("wa_id") or "").strip(),
            conv.get("nome") or "",
            "-",
        ]
        self._append(SHEET_DOACAO_VALOR, row)

    def append_acolhimento(self, conv: Dict[str, Any], telefone: Optional[str] = None) -> None:
        """Append na aba Acolhimento: Data, Horário, Telefone, Nome, Acolhimento = 'Aguardando Acolhimento'."""
        row = [
            _fmt_data(conv.get("data")),
            _fmt_horario(conv.get("horario")),
            (telefone or conv.get("wa_id") or "").strip(),
            conv.get("nome") or "",
            "Aguardando Acolhimento",
        ]
        self._append(SHEET_ACOLHIMENTO, row)

    def append_lojas(self, conv: Dict[str, Any], telefone: Optional[str] = None) -> None:
        """Append na aba Lojas Solidárias: Data, Horário, Telefone, Nome, Lojas = 'Contato para Lojas Soidárias'."""
        row = [
            _fmt_data(conv.get("data")),
            _fmt_horario(conv.get("horario")),
            (telefone or conv.get("wa_id") or "").strip(),
            conv.get("nome") or "",
            "Contato para Lojas Soidárias",
        ]
        self._append(SHEET_LOJAS, row)

    def append_servico(self, conv: Dict[str, Any], telefone: Optional[str] = None) -> None:
        """Append na aba Contratar Um Serviço: Data, Horário, Telefone, Nome, 'Contratar um Serviço' = 'Contato Para Serviço'."""
        row = [
            _fmt_data(conv.get("data")),
            _fmt_horario(conv.get("horario")),
            (telefone or conv.get("wa_id") or "").strip(),
            conv.get("nome") or "",
            "Contato Para Serviço",
        ]
        self._append(SHEET_SERVICO, row)

    def append_fretes(self, conv: Dict[str, Any], telefone: Optional[str] = None) -> None:
        """Append na aba Fretes e Mudanças: Data, Horário, Telefone, Nome, 'Frees e Mudanças' = 'Contato Para Fretes e Mudanças'."""
        row = [
            _fmt_data(conv.get("data")),
            _fmt_horario(conv.get("horario")),
            (telefone or conv.get("wa_id") or "").strip(),
            conv.get("nome") or "",
            "Contato Para Fretes e Mudanças",
        ]
        self._append(SHEET_FRETES, row)

    def append_doacao_item(self, doacao: Dict[str, Any], telefone: Optional[str] = None) -> None:
        """
        Append na aba Doação Item.
        telefone: número real (reply_to/senderPn) quando disponível; senão vazio.
        doacao: nome_responsavel, endereco_retirada, telefone_whatsapp, email, tipo_doacao, estado_doacao,
                horario_preferencial, fotos (ou nome, endereco, telefone conforme tabela)
        """
        nome = doacao.get("nome_responsavel") or doacao.get("nome") or ""
        endereco = doacao.get("endereco_retirada") or doacao.get("endereco") or ""
        # Prioriza telefone informado pelo usuário no fluxo de doação.
        # Se ausente, usa telefone do remetente.
        tel_info = doacao.get("telefone_whatsapp") or doacao.get("telefone") or (telefone or "").strip()
        row = [
            datetime.now().strftime("%d-%m-%Y"),
            datetime.now().strftime("%H:%M:%S"),
            nome,
            doacao.get("email") or "",
            tel_info,
            endereco,
            doacao.get("tipo_doacao") or "",
            doacao.get("estado_doacao") or "",
            doacao.get("horario_preferencial") or "",
            _fmt_fotos(doacao.get("fotos")),
            "Copie a URL",
        ]
        self._append(SHEET_DOACAO_ITEM, row)
