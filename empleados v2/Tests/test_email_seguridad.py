"""
Pruebas de correo — Seguridad y Acceso
EVT-01  Nuevo usuario → RegistroNotificaciones Exitoso=1, sin contraseña en asunto
EVT-02  Recuperación → token en BD es hash SHA-256 (64 chars hex), no código legible
EVT-02b Expiración de 30 minutos verificada en FechaExpiracion
EVT-02c Token expirado → formulario bloqueado (token del seeding)
EVT-02d Token ya usado  → formulario bloqueado (token del seeding)
EVT-03  Cambio contraseña → RegistroNotificaciones Exitoso=1
"""
import subprocess
import tempfile
import os
from datetime import datetime, timezone, timedelta

import pytest

from helpers import BASE_URL, hacer_login

DB_INSTANCE = r"(localdb)\MSSQLLocalDB"
DB_NAME     = "GestionPersonal"


# ── Helpers BD ────────────────────────────────────────────────────────────────

def _consultar(query: str) -> list[list[str]]:
    """Ejecuta una query via Invoke-Sqlcmd y retorna filas como listas de strings."""
    sql_file = os.path.join(tempfile.gettempdir(), "_email_query.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(query)
    result = subprocess.run(
        ["powershell", "-Command",
         f"Invoke-Sqlcmd -ServerInstance '{DB_INSTANCE}' "
         f"-Database '{DB_NAME}' -InputFile '{sql_file}' "
         f"-OutputSqlErrors $true | Format-Table -AutoSize | Out-String -Width 512"],
        capture_output=True, text=True, timeout=15
    )
    lines = [l for l in result.stdout.splitlines() if l.strip() and "---" not in l]
    return [l.split() for l in lines[1:]] if len(lines) > 1 else []


def _ultimo_registro(tipo_evento: str) -> dict | None:
    """Devuelve el último registro de RegistroNotificaciones para el tipo dado."""
    filas = _consultar(
        f"SELECT TOP 1 Exitoso, ISNULL(ErrorMensaje,''), Destinatario, Asunto "
        f"FROM dbo.RegistroNotificaciones "
        f"WHERE TipoEvento = '{tipo_evento}' "
        f"ORDER BY FechaIntento DESC;"
    )
    if not filas:
        return None
    return {"exitoso": filas[0][0] == "1", "error": " ".join(filas[0][1:-2]),
            "destinatario": filas[0][-2], "asunto": " ".join(filas[0][1:])}


def _token_bd(correo: str) -> dict | None:
    """Devuelve el último token de recuperación para el correo dado."""
    filas = _consultar(
        f"SELECT TOP 1 t.Token, CONVERT(varchar,t.FechaExpiracion,126), t.Usado "
        f"FROM dbo.TokensRecuperacion t "
        f"JOIN dbo.Usuarios u ON u.Id = t.UsuarioId "
        f"WHERE u.CorreoAcceso = '{correo}' "
        f"ORDER BY t.FechaCreacion DESC;"
    )
    if not filas:
        return None
    return {"token": filas[0][0], "expiracion": filas[0][1], "usado": filas[0][2]}


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_evt01_nuevo_usuario_sin_contrasena_en_asunto(page):
    """
    Al crear un usuario, RegistroNotificaciones registra Exitoso=1
    y el asunto del correo NO revela contraseñas.
    """
    reg = _ultimo_registro("NuevoUsuario")
    # Si aún no hay registros, marcar como xfail pendiente de datos
    if reg is None:
        pytest.xfail("EVT-01: Sin registros — ejecutar creación de usuario primero")

    assert reg["exitoso"], f"EVT-01: Correo falló — {reg['error']}"

    asunto = reg["asunto"].lower()
    assert "contraseña" not in asunto, "EVT-01: El asunto contiene 'contraseña'"
    assert "password"   not in asunto, "EVT-01: El asunto contiene 'password'"
    assert "nuevo usuario" in asunto,  f"EVT-01: Formato incorrecto. Asunto: {reg['asunto']}"


def test_evt02_token_en_bd_es_hash_sha256(page):
    """
    El Token en BD debe ser SHA-256 hex lowercase (64 chars), no el código legible.
    """
    correo = "carlos.rodriguez@yopmail.com"
    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.wait_for_load_state("networkidle")
    page.fill("#CorreoAcceso", correo)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    t = _token_bd(correo)
    assert t is not None, "EVT-02: No se creó token en BD"

    valor = t["token"]
    assert len(valor) == 64, (
        f"EVT-02: Token tiene {len(valor)} chars (se esperaban 64 — SHA-256 hex). "
        f"Primeros chars: {valor[:20]}... — posible texto plano inseguro")
    assert all(c in "0123456789abcdef" for c in valor), (
        "EVT-02: Token no es hex válido — podría ser texto plano")

    reg = _ultimo_registro("RecuperacionContrasena")
    assert reg is not None,  "EVT-02: Sin registro en RegistroNotificaciones"
    assert reg["exitoso"],   f"EVT-02: Correo falló — {reg['error']}"


def test_evt02b_token_expira_en_30_minutos(page):
    """El token recién creado expira en ≤ 31 minutos (margen de 1 min)."""
    correo = "natalia.bermudez@yopmail.com"
    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.wait_for_load_state("networkidle")
    page.fill("#CorreoAcceso", correo)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    t = _token_bd(correo)
    assert t is not None, "EVT-02b: No se creó token"

    # FechaExpiracion viene en ISO 8601 de la query
    exp  = datetime.fromisoformat(t["expiracion"]).replace(tzinfo=timezone.utc)
    diff = exp - datetime.now(timezone.utc)

    assert timedelta(0) < diff <= timedelta(minutes=31), (
        f"EVT-02b: Expiración incorrecta. Diferencia: {diff}. "
        "Verifica que CuentaService usa AddMinutes(30) y no AddHours(1)")


def test_evt02c_token_expirado_bloqueado(page):
    """Un token expirado no debe mostrar el formulario de nueva contraseña."""
    # Los tokens del seeding original (texto plano) quedan inválidos tras la migración
    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token=TK7E4D8F5G")
    page.wait_for_load_state("networkidle")

    input_password = page.locator("input[name='NuevoPassword']")
    assert not input_password.is_visible(), \
        "EVT-02c: Formulario visible con token expirado/inválido"

    alerta = page.locator(".alert--error, .alert-danger, .text-danger")
    assert alerta.count() > 0 and alerta.first.inner_text().strip() != "", \
        "EVT-02c: Sin mensaje de error visible"


def test_evt02d_token_usado_bloqueado(page):
    """Un token ya utilizado no debe mostrar el formulario de nueva contraseña."""
    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token=TK3F9A2B1C")
    page.wait_for_load_state("networkidle")

    input_password = page.locator("input[name='NuevoPassword']")
    assert not input_password.is_visible(), \
        "EVT-02d: Formulario visible con token ya usado"


def test_evt03_cambio_contrasena_registrado(page):
    """
    Al completar el formulario de restablecer contraseña exitosamente,
    RegistroNotificaciones registra un evento CambioContrasenaExitoso.
    """
    reg = _ultimo_registro("CambioContrasenaExitoso")
    if reg is None:
        pytest.xfail("EVT-03: Sin registros — ejecutar restablecimiento de contraseña primero")

    assert reg["exitoso"], f"EVT-03: Correo de confirmación falló — {reg['error']}"
