"""
Pruebas funcionales — Recuperación de Contraseña (Scope 4)
Sistema: GestiónRH — Administración de Empleados

TC-12   Solicitar reseteo → mensaje de instrucciones en Login
TC-13   Verificar recepción del email en yopmail.com
TC-14   Token válido → nueva contraseña → login exitoso con nueva clave
TC-15a  Token expirado → sistema rechaza
TC-15b  Token ya usado → sistema rechaza

Tokens de referencia (Documentos/BD/Seeding_Completo.sql — fuente de verdad):
  TK1H6K9M2N  → Natalia Bermúdez, vigente hasta 2026-04-24, Usado=0  (TC-14)
  TK7E4D8F5G  → Andrés Torres,   expirado 2026-04-10,      Usado=0  (TC-15a)
  TK3F9A2B1C  → Laura Sánchez,   expirado,                 Usado=1  (TC-15b)
"""

import re

import pytest

from helpers import BASE_URL, hacer_login, hay_error_formulario

# ── Datos de prueba ───────────────────────────────────────────────────────────
# Dominio obligatorio: @yopmail.com (regla de negocio)
CORREO_RECUPERACION         = "carlos.rodriguez@yopmail.com"
YOPMAIL_USUARIO             = "carlos.rodriguez"

# Tokens del Seeding_Completo.sql
TOKEN_VIGENTE   = "TK1H6K9M2N"   # Natalia Bermúdez — expira 2026-04-24, Usado=0
TOKEN_EXPIRADO  = "TK7E4D8F5G"   # Andrés Torres    — expirado 2026-04-10, Usado=0
TOKEN_USADO     = "TK3F9A2B1C"   # Laura Sánchez    — Usado=1

CORREO_NATALIA              = "natalia.bermudez@yopmail.com"
PASSWORD_NUEVA_RECUPERACION = "RecuperadaClave2026!"


# ── TC-12: Solicitar reseteo ──────────────────────────────────────────────────
def test_tc12_solicitar_reseteo(page):
    """
    Ingresar correo en /Cuenta/RecuperarPassword y enviar.
    El sistema debe redirigir a Login con mensaje informativo,
    sin revelar si el correo existe o no (no enumeración de usuarios).
    """
    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.wait_for_load_state("networkidle")

    page.fill("#CorreoAcceso", CORREO_RECUPERACION)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    url_actual = page.url
    assert "/Cuenta/Login" in url_actual, (
        f"TC-12 FALLO: Debía redirigir a Login, URL actual: {url_actual}"
    )

    # Mensaje genérico (no revela si el correo existe)
    mensaje = page.locator(".alert--info").inner_text()
    assert mensaje.strip() != "", (
        "TC-12 FALLO: No se mostró mensaje informativo tras solicitar recuperación."
    )
    print(f"\n  [OK] TC-12 PASO - Redirigió a Login. Mensaje: '{mensaje.strip()}'")


# ── TC-13: Verificar email en yopmail.com ─────────────────────────────────────
def test_tc13_verificar_email_yopmail(page):
    """
    Navega a yopmail.com y verifica que el email de recuperación
    llegó a la bandeja de carlos.rodriguez@yopmail.com.
    Requiere que TC-12 haya enviado el email previamente.
    Timeout de 30s para contemplar demoras de entrega.

    Cómo verificar manualmente:
      1. Abrir https://yopmail.com
      2. Ingresar 'carlos.rodriguez' en el campo de búsqueda
      3. La bandeja se muestra automáticamente
    """
    page.goto(f"https://yopmail.com/en/?login={YOPMAIL_USUARIO}")
    page.wait_for_load_state("networkidle")

    # El inbox se carga en un iframe con id="ifinbox"
    inbox = page.frame_locator("#ifinbox")

    # Esperar hasta 30s a que aparezca un email sobre recuperación de contraseña
    email_item = inbox.locator("a").filter(
        has_text=re.compile(r"contrase|recuper|GestiónRH|password|reset", re.IGNORECASE)
    ).first
    email_item.wait_for(timeout=30000)
    email_item.click()
    page.wait_for_timeout(1500)

    # El contenido del email se muestra en iframe con id="ifmail"
    mail_frame = page.frame_locator("#ifmail")
    enlace_reset = mail_frame.locator(
        "a[href*='RestablecerPassword'], a[href*='token']"
    ).first
    enlace_reset.wait_for(timeout=10000)

    href = enlace_reset.get_attribute("href")
    assert href is not None and (
        "RestablecerPassword" in href or "token=" in href
    ), (
        f"TC-13 FALLO: No se encontró enlace de restablecimiento en el email. href={href}"
    )
    print(f"\n  [OK] TC-13 PASO - Email de recuperacion recibido. Enlace: {href}")


# ── TC-14: Token válido → nueva contraseña → login exitoso ───────────────────
def test_tc14_restablecer_con_token_valido(page):
    """
    Usa el token vigente del seeding (TK1H6K9M2N — Natalia Bermúdez, expira 2026-04-24).
    Navega a /Cuenta/RestablecerPassword?token=TOKEN, establece nueva contraseña
    y verifica que el login funciona con la nueva clave.

    Estado esperado tras la prueba:
      - dbo.TokensRecuperacion WHERE Token='TK1H6K9M2N' → Usado=1
      - Natalia Bermúdez puede iniciar sesión con RecuperadaClave2026!

    Nota: conftest.py resetea este token a Usado=0 antes de cada sesión de tests.
    """
    url_reset = f"{BASE_URL}/Cuenta/RestablecerPassword?token={TOKEN_VIGENTE}"
    page.goto(url_reset)
    page.wait_for_load_state("networkidle")

    # Si el token ya fue usado en una ejecución anterior y el conftest no lo reseteó
    if "/Cuenta/Login" in page.url:
        pytest.skip(
            "TC-14 OMITIDO: El token vigente ya fue consumido. "
            "Reaplicar Seeding_Completo.sql o ejecutar con la suite completa."
        )

    assert "RestablecerPassword" in page.url, (
        f"TC-14 FALLO: No se cargó el formulario de restablecimiento. URL: {page.url}"
    )

    page.fill("#NuevoPassword", PASSWORD_NUEVA_RECUPERACION)
    page.fill("#ConfirmarPassword", PASSWORD_NUEVA_RECUPERACION)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    url_actual = page.url
    assert "/Cuenta/Login" in url_actual, (
        f"TC-14 FALLO: Debía redirigir a Login tras cambio exitoso. URL: {url_actual}"
    )

    # Mensaje de éxito
    mensaje = page.locator(".alert--success").inner_text()
    assert mensaje.strip() != "", (
        f"TC-14 FALLO: No se mostró mensaje de éxito. URL: {url_actual}"
    )

    # Verificar que el login funciona con la nueva contraseña
    page.fill("#CorreoAcceso", CORREO_NATALIA)
    page.fill("#Password", PASSWORD_NUEVA_RECUPERACION)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    url_post_login = page.url
    assert "/Cuenta/Login" not in url_post_login, (
        f"TC-14 FALLO: Login con nueva contraseña falló. URL: {url_post_login}"
    )
    print(
        f"\n  [OK] TC-14 PASO - Token vigente usado, nueva contrasena operativa. "
        f"URL: {url_post_login}"
    )


# ── TC-15a: Token expirado → sistema rechaza ─────────────────────────────────
def test_tc15a_token_expirado(page):
    """
    Intenta restablecer con token expirado (TK7E4D8F5G — Andrés Torres, expiró 2026-04-10).
    El sistema debe rechazarlo mostrando error o redirigir a Login.
    """
    url_reset = f"{BASE_URL}/Cuenta/RestablecerPassword?token={TOKEN_EXPIRADO}"
    page.goto(url_reset)
    page.wait_for_load_state("networkidle")

    # El sistema puede rechazar el token directamente en GET (redirect a Login)
    if "/Cuenta/Login" in page.url:
        print(f"\n  [OK] TC-15a PASO - Token expirado rechazado en GET, redirigió a Login.")
        return

    # Si muestra el formulario, intentar el submit y verificar que falla
    page.fill("#NuevoPassword", "Intento2026!")
    page.fill("#ConfirmarPassword", "Intento2026!")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert hay_error_formulario(page) or "/Cuenta/Login" in page.url, (
        f"TC-15a FALLO: Token expirado fue aceptado incorrectamente. URL: {page.url}"
    )
    print(f"\n  [OK] TC-15a PASO - Token expirado rechazado correctamente.")


# ── TC-15b: Token ya usado → sistema rechaza ─────────────────────────────────
def test_tc15b_token_ya_usado(page):
    """
    Intenta restablecer con token ya utilizado (TK3F9A2B1C — Laura Sánchez, Usado=1).
    El sistema debe rechazarlo mostrando error o redirigir a Login.
    """
    url_reset = f"{BASE_URL}/Cuenta/RestablecerPassword?token={TOKEN_USADO}"
    page.goto(url_reset)
    page.wait_for_load_state("networkidle")

    # El sistema puede rechazar el token directamente en GET
    if "/Cuenta/Login" in page.url:
        print(f"\n  [OK] TC-15b PASO - Token usado rechazado en GET, redirigió a Login.")
        return

    # Si muestra el formulario, intentar el submit y verificar que falla
    page.fill("#NuevoPassword", "Intento2026!")
    page.fill("#ConfirmarPassword", "Intento2026!")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert hay_error_formulario(page) or "/Cuenta/Login" in page.url, (
        f"TC-15b FALLO: Token ya usado fue aceptado incorrectamente. URL: {page.url}"
    )
    print(f"\n  [OK] TC-15b PASO - Token ya usado rechazado correctamente.")
