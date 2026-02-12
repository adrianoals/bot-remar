from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.core.config import settings
from app.services.supabase_service import SupabaseService
import re

router = APIRouter()
supabase = SupabaseService()

ADMIN_COOKIE = "admin_auth"


def _is_logged(request: Request) -> bool:
    return request.cookies.get(ADMIN_COOKIE) == "1"


def _base_layout(content: str) -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Painel Admin</title>
  <style>
    body {{ font-family: -apple-system, system-ui, Segoe UI, Roboto, Arial, sans-serif; max-width: 680px; margin: 32px auto; padding: 0 16px; }}
    h1 {{ margin: 0 0 16px; font-size: 24px; }}
    .card {{ border: 1px solid #ddd; border-radius: 10px; padding: 16px; margin-bottom: 16px; }}
    .row {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    input {{ padding: 10px; border: 1px solid #ccc; border-radius: 8px; width: 100%; box-sizing: border-box; }}
    button {{ padding: 10px 14px; border: 0; border-radius: 8px; cursor: pointer; }}
    .primary {{ background: #111; color: #fff; }}
    .warn {{ background: #b3261e; color: #fff; }}
    .ok {{ background: #1b5e20; color: #fff; }}
    .muted {{ color: #666; font-size: 14px; }}
  </style>
</head>
<body>{content}</body>
</html>"""


def _login_page(error: str = "") -> HTMLResponse:
    err = f'<p style="color:#b3261e">{error}</p>' if error else ""
    html = _base_layout(
        f"""
        <h1>Painel Admin</h1>
        <div class="card">
          <p class="muted">Digite usuário e senha para acessar.</p>
          {err}
          <form method="post" action="/admin/login">
            <div style="margin-bottom:8px"><input name="username" placeholder="Usuário" required /></div>
            <div style="margin-bottom:12px"><input type="password" name="password" placeholder="Senha" required /></div>
            <button class="primary" type="submit">Entrar</button>
          </form>
        </div>
        """
    )
    return HTMLResponse(html)


def _panel_page(msg: str = "") -> HTMLResponse:
    enabled = supabase.get_global_automation_enabled()
    status = "ATIVA" if enabled else "DESATIVADA"
    msg_html = f'<p style="color:#1b5e20">{msg}</p>' if msg else ""
    html = _base_layout(
        f"""
        <h1>Painel Admin</h1>
        <p><strong>Status global:</strong> {status}</p>
        {msg_html}
        <div class="card">
          <h3>Automação global</h3>
          <div class="row">
            <form method="post" action="/admin/action"><input type="hidden" name="action" value="activate_all" /><button class="ok" type="submit">Ativar todos</button></form>
            <form method="post" action="/admin/action"><input type="hidden" name="action" value="deactivate_all" /><button class="warn" type="submit">Desativar todos</button></form>
          </div>
        </div>
        <div class="card">
          <h3>Automação por número</h3>
          <p class="muted">Formato obrigatório: +5511999999999</p>
          <form method="post" action="/admin/action">
            <input type="hidden" name="action" value="activate_one" />
            <div style="margin-bottom:8px"><input name="wa_id" placeholder="+5511999999999" required /></div>
            <button class="ok" type="submit">Ativar número</button>
          </form>
          <div style="height:8px"></div>
          <form method="post" action="/admin/action">
            <input type="hidden" name="action" value="deactivate_one" />
            <div style="margin-bottom:8px"><input name="wa_id" placeholder="+5511999999999" required /></div>
            <button class="warn" type="submit">Desativar número</button>
          </form>
        </div>
        <form method="post" action="/admin/logout">
          <button type="submit">Sair</button>
        </form>
        """
    )
    return HTMLResponse(html)


@router.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    if not _is_logged(request):
        return _login_page()
    return _panel_page()


@router.post("/admin/login")
def admin_login(username: str = Form(...), password: str = Form(...)):
    if username == (settings.ADMIN_USER or "") and password == (settings.ADMIN_PASSWORD or ""):
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(ADMIN_COOKIE, "1", httponly=True, samesite="lax")
        return response
    return _login_page("Credenciais inválidas.")


@router.post("/admin/logout")
def admin_logout():
    response = RedirectResponse(url="/admin", status_code=303)
    response.delete_cookie(ADMIN_COOKIE)
    return response


@router.post("/admin/action")
def admin_action(request: Request, action: str = Form(...), wa_id: str = Form(default="")):
    if not _is_logged(request):
        return _login_page("Sessão expirada.")

    msg = "Ação executada."
    if action == "activate_all":
        ok1 = supabase.set_global_automation(True)
        ok2 = supabase.set_all_users_to_initial()
        msg = "Automação ativada para todos." if (ok1 and ok2) else "Falha ao ativar global."
    elif action == "deactivate_all":
        ok = supabase.set_global_automation(False)
        msg = "Automação desativada para todos." if ok else "Falha ao desativar global."
    elif action in ("activate_one", "deactivate_one"):
        raw = (wa_id or "").strip()
        if not re.match(r"^\+\d{10,15}$", raw):
            return _panel_page("Número inválido. Use o formato +5511999999999.")
        digits = re.sub(r"\D", "", raw)
        ok = supabase.set_user_automation(digits, action == "activate_one")
        if ok:
            msg = f"Número {raw} atualizado com sucesso."
        else:
            msg = f"Falha ao atualizar {raw}."
    else:
        msg = "Ação inválida."

    return _panel_page(msg)
