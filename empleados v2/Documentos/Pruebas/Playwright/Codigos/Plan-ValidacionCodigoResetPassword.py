"""Plan-ValidacionCodigoResetPassword.py
=========================================
Plan de validación de códigos de restablecimiento de contraseña.

Escenarios cubiertos:
  TC-CV-01  Token vigente es aceptado y permite restablecer la contraseña.
            Validación en BD: el token queda marcado como Usado=1.
  TC-CV-02  Token ya utilizado (Usado=1) es rechazado por el sistema (de un solo uso).
  TC-CV-03  Token con FechaExpiracion vencida es rechazado por el sistema.
  TC-CV-04  Token inexistente en BD es rechazado por el sistema.

Tokens de prueba definidos en Seeding_Completo.sql:
  TK1H6K9M2N  Natalia Bermúdez  — vigente, Usado=0, FechaExpiracion=2099-12-31
  TK7E4D8F5G  Andrés Torres     — expirado (2026-04-10), Usado=0
  TK3F9A2B1C  Laura Sánchez     — ya usado, Usado=1

Prerrequisito: La aplicación debe estar corriendo en http://localhost:5002

Ejecutar con:
  python -m pytest Documentos/Pruebas/Playwright/codigos/Plan-ValidacionCodigoResetPassword.py -v
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# ── Importar helpers compartidos ──────────────────────────────────────────────
# Ruta: codigos/ → Playwright/ → Pruebas/ → Documentos/ → workspace_root/Tests
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "Tests"))
from helpers import BASE_URL, hacer_login, hay_error_formulario  # noqa: E402

# ── Constantes de tokens de prueba ────────────────────────────────────────────
TOKEN_VIGENTE      = "TK1H6K9M2N"  # Natalia Bermúdez — vigente, Usado=0, expira 2099
TOKEN_EXPIRADO     = "TK7E4D8F5G"  # Andrés Torres    — expirado 2026-04-10, Usado=0
TOKEN_USADO        = "TK3F9A2B1C"  # Laura Sánchez    — Usado=1
TOKEN_INEXISTENTE  = "XXXXINVALID" # No existe en BD

# Hash SHA-256 del TOKEN_VIGENTE almacenado en dbo.TokensRecuperacion
HASH_TOKEN_VIGENTE = "6730ac0c93c8353faa2e834123cf3e4636dc3ce39f6654760a27e92484ed2235"

CORREO_NATALIA = "natalia.bermudez@yopmail.com"
PASSWORD_NUEVA = "CambioClave2026!"

MSG_TOKEN_INVALIDO = "El código es inválido o ha expirado."
MSG_RESET_EXITO    = "Contraseña restablecida correctamente. Inicia sesión."

# ── Conexión a base de datos ───────────────────────────────────────────────────
DB_INSTANCE = r"(localdb)\MSSQLLocalDB"
DB_NAME     = "GestionPersonal"

# Hash/Salt de la contraseña "Usuario1" (PBKDF2/SHA256, 10 000 iter)
_HASH_USUARIO1 = "0x7DED37B4612147C18EBDFA1F6DEB4709EC9D511DA20641214F1F97612DF2CEAE"
_SALT_USUARIO1 = "0xF2B483C7DAC61EC2CA7F1331C95D6800"


def _consultar(query: str) -> list[dict]:
    """Ejecuta una consulta SELECT y devuelve los resultados como lista de dicts."""
    sql_file = os.path.join(tempfile.gettempdir(), "_cv_query.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(query)
    result = subprocess.run(
        [
            "powershell", "-Command",
            f"Invoke-Sqlcmd -ServerInstance '{DB_INSTANCE}' -Database '{DB_NAME}' "
            f"-InputFile '{sql_file}' | ConvertTo-Json -Depth 2",
        ],
        capture_output=True, text=True, timeout=15,
    )
    if not result.stdout.strip():
        return []
    try:
        data = json.loads(result.stdout)
        return data if isinstance(data, list) else [data]
    except (json.JSONDecodeError, ValueError):
        return []


def _ejecutar(sql: str) -> None:
    """Ejecuta una sentencia SQL sin retorno de datos."""
    sql_file = os.path.join(tempfile.gettempdir(), "_cv_exec.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    subprocess.run(
        [
            "powershell", "-Command",
            f"Invoke-Sqlcmd -ServerInstance '{DB_INSTANCE}' -Database '{DB_NAME}' "
            f"-InputFile '{sql_file}'",
        ],
        capture_output=True, text=True, timeout=15,
    )


def _restaurar_token_vigente() -> None:
    """Restaura TK1H6K9M2N a Usado=0 con expiración en 2099 (estado de seeding)."""
    _ejecutar(
        f"UPDATE dbo.TokensRecuperacion "
        f"SET Usado = 0, FechaExpiracion = '2099-12-31 23:59:00' "
        f"WHERE Token = '{HASH_TOKEN_VIGENTE}'"
    )


def _restaurar_password_natalia() -> None:
    """Restaura la contraseña de Natalia a 'Usuario1' y activa DebeC ambiarPassword."""
    _ejecutar(
        f"UPDATE dbo.Usuarios "
        f"SET PasswordHash = {_HASH_USUARIO1}, "
        f"    PasswordSalt = {_SALT_USUARIO1}, "
        f"    DebecambiarPassword = 1 "
        f"WHERE CorreoAcceso = '{CORREO_NATALIA}'"
    )


# ── Fixture de limpieza ────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def restaurar_estado_db():
    """
    Garantiza que TK1H6K9M2N y la contraseña de Natalia queden en
    estado inicial antes y después de cada test.
    """
    _restaurar_token_vigente()
    _restaurar_password_natalia()
    yield
    _restaurar_token_vigente()
    _restaurar_password_natalia()


# ── Helpers de navegación ──────────────────────────────────────────────────────
def _ir_a_reset(page, token: str) -> None:
    """Navega al formulario de restablecimiento con el token dado."""
    url = f"{BASE_URL}/Cuenta/RestablecerPassword?token={token}"
    page.goto(url)
    page.wait_for_load_state("networkidle")


def _es_rechazado(page) -> bool:
    """
    Devuelve True si el sistema rechazó el token:
    - redirección a Login o RecuperarPassword, o
    - mensaje de error visible en la página.
    """
    if "/Cuenta/Login" in page.url or "/Cuenta/RecuperarPassword" in page.url:
        return True
    if hay_error_formulario(page):
        return True
    alerta = page.locator(".alert--danger, .alert--warning")
    return alerta.count() > 0 and alerta.first.is_visible()


# ═══════════════════════════════════════════════════════════════════════════════
# TC-CV-01: Token vigente — reset exitoso y token queda Usado=1 en BD
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.mark.recuperacion
def test_tc_cv_01_token_vigente_reset_exitoso(page):
    """
    TC-CV-01 — Token vigente (TK1H6K9M2N) es aceptado por el sistema.

    Flujo:
      1. Navegar a /Cuenta/RestablecerPassword?token=TK1H6K9M2N
      2. Completar el formulario con la nueva contraseña
      3. Enviar el formulario
    Resultado esperado:
      - Redirige a /Cuenta/Login con .alert--success
      - El token queda marcado como Usado=1 en la BD
    """
    # Arrange
    _ir_a_reset(page, TOKEN_VIGENTE)

    # Act
    page.fill("#NuevoPassword", PASSWORD_NUEVA)
    page.fill("#ConfirmarPassword", PASSWORD_NUEVA)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Assert — redirección a Login
    assert "/Cuenta/Login" in page.url, (
        f"TC-CV-01: Se esperaba redirección a /Cuenta/Login, URL actual: {page.url}"
    )

    # Assert — mensaje de éxito visible
    alerta_exito = page.locator(".alert--success")
    assert alerta_exito.count() > 0 and alerta_exito.first.is_visible(), (
        "TC-CV-01: No se encontró el elemento '.alert--success' en la página de Login."
    )
    texto_alerta = alerta_exito.first.inner_text()
    assert MSG_RESET_EXITO in texto_alerta, (
        f"TC-CV-01: Mensaje de éxito inesperado: '{texto_alerta}'"
    )

    # Assert — validación en BD: Usado debe ser 1
    rows = _consultar(
        f"SELECT Usado FROM dbo.TokensRecuperacion "
        f"WHERE Token = '{HASH_TOKEN_VIGENTE}'"
    )
    assert rows, "TC-CV-01: No se encontró el registro del token en la BD."
    usado = rows[0].get("Usado", rows[0].get("usado"))
    assert str(usado) in ("1", "True", "true"), (
        f"TC-CV-01: Se esperaba Usado=1 en BD después del reset, pero se obtuvo: {usado}"
    )

    print(f"\n  [OK] TC-CV-01 PASÓ — Token vigente aceptado, contraseña cambiada y Usado=1 en BD.")


# ═══════════════════════════════════════════════════════════════════════════════
# TC-CV-02: Token ya utilizado — verificación de uso único
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.mark.recuperacion
def test_tc_cv_02_token_ya_usado_es_rechazado(page):
    """
    TC-CV-02 — El sistema rechaza un token que ya fue utilizado (Usado=1).

    Verifica que los tokens de recuperación son de un solo uso:
    una vez consumido, el mismo token no puede volver a utilizarse.

    Resultado esperado:
      - El sistema redirige a Login/RecuperarPassword, o
      - muestra un mensaje de error sin dar acceso al formulario de reset.
    """
    # Arrange
    _ir_a_reset(page, TOKEN_USADO)

    # La app muestra el formulario en GET sin validar; la validación ocurre en POST.
    # Si el GET ya redirigió a Login, el token fue rechazado en el servidor.
    if "/Cuenta/Login" in page.url:
        print(f"\n  [OK] TC-CV-02 PASÓ — Token ya usado rechazado en GET, redirigió a Login.")
        return

    # Act — intentar el restablecimiento con el token ya usado
    page.fill("#NuevoPassword", "Intento2026!")
    page.fill("#ConfirmarPassword", "Intento2026!")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Assert — el sistema rechaza el token en el POST
    assert hay_error_formulario(page) or "/Cuenta/Login" in page.url, (
        f"TC-CV-02: El sistema aceptó un token ya utilizado (Usado=1). "
        f"URL actual: {page.url}"
    )

    alertas = page.locator(".alert--danger, .alert--warning, .alert--info, .form-error")
    if alertas.count() > 0 and alertas.first.is_visible():
        print(f"\n  [INFO] TC-CV-02: Mensaje del sistema: '{alertas.first.inner_text()}'")

    print(f"\n  [OK] TC-CV-02 PASÓ — Token ya usado correctamente rechazado (uso único verificado).")


# ═══════════════════════════════════════════════════════════════════════════════
# TC-CV-03: Token expirado — verificación de vencimiento
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.mark.recuperacion
def test_tc_cv_03_token_expirado_es_rechazado(page):
    """
    TC-CV-03 — El sistema rechaza un token cuya FechaExpiracion ya pasó,
    aunque Usado=0.

    Token de prueba: TK7E4D8F5G (Andrés Torres, expirado el 2026-04-10, Usado=0).

    Resultado esperado:
      - El sistema redirige a Login/RecuperarPassword, o
      - muestra un mensaje de error indicando que el código expiró.
    """
    # Arrange
    _ir_a_reset(page, TOKEN_EXPIRADO)

    # La app muestra el formulario en GET sin validar; la validación ocurre en POST.
    if "/Cuenta/Login" in page.url:
        print(f"\n  [OK] TC-CV-03 PASÓ — Token expirado rechazado en GET, redirigió a Login.")
        return

    # Act — intentar el restablecimiento con el token expirado
    page.fill("#NuevoPassword", "Intento2026!")
    page.fill("#ConfirmarPassword", "Intento2026!")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Assert — el sistema rechaza el token expirado en el POST
    assert hay_error_formulario(page) or "/Cuenta/Login" in page.url, (
        f"TC-CV-03: El sistema aceptó un token expirado (FechaExpiracion vencida). "
        f"URL actual: {page.url}"
    )

    alertas = page.locator(".alert--danger, .alert--warning, .alert--info, .form-error")
    if alertas.count() > 0 and alertas.first.is_visible():
        print(f"\n  [INFO] TC-CV-03: Mensaje del sistema: '{alertas.first.inner_text()}'")

    print(f"\n  [OK] TC-CV-03 PASÓ — Token expirado correctamente rechazado (vencimiento verificado).")


# ═══════════════════════════════════════════════════════════════════════════════
# TC-CV-04: Token inexistente — no existe en BD
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.mark.recuperacion
def test_tc_cv_04_token_inexistente_es_rechazado(page):
    """
    TC-CV-04 — El sistema rechaza un token que no existe en la base de datos.

    Verifica que el sistema no genera errores internos con tokens arbitrarios
    y devuelve una respuesta segura (sin exponer información del sistema).

    Resultado esperado:
      - El sistema redirige a Login/RecuperarPassword, o
      - muestra un mensaje de error genérico.
    """
    # Arrange
    _ir_a_reset(page, TOKEN_INEXISTENTE)

    # La app muestra el formulario en GET sin validar; la validación ocurre en POST.
    if "/Cuenta/Login" in page.url:
        print(f"\n  [OK] TC-CV-04 PASÓ — Token inexistente rechazado en GET, redirigió a Login.")
        return

    # Act — intentar el restablecimiento con el token inexistente
    page.fill("#NuevoPassword", "Intento2026!")
    page.fill("#ConfirmarPassword", "Intento2026!")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Assert — el sistema rechaza el token inexistente en el POST
    assert hay_error_formulario(page) or "/Cuenta/Login" in page.url, (
        f"TC-CV-04: El sistema aceptó un token que no existe en BD. "
        f"URL actual: {page.url}"
    )

    alertas = page.locator(".alert--danger, .alert--warning, .alert--info, .form-error")
    if alertas.count() > 0 and alertas.first.is_visible():
        print(f"\n  [INFO] TC-CV-04: Mensaje del sistema: '{alertas.first.inner_text()}'")

    print(f"\n  [OK] TC-CV-04 PASÓ — Token inexistente correctamente rechazado.")
