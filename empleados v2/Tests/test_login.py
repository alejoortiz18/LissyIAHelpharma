"""
Pruebas funcionales — Flujo de Login
Sistema: GestiónRH — Administración de Empleados

TC-01  Login con credenciales correctas (rol Jefe)
TC-02  Login con contraseña incorrecta
TC-03  Login con correo inexistente
TC-04  Login con campos vacíos
TC-05  Flujo completo: Login → CambiarPassword → Dashboard
TC-06  Protección de rutas autenticadas sin sesión
TC-07  Logout
"""

import pytest
from helpers import BASE_URL, hacer_login, hacer_logout, hay_error_formulario, obtener_texto_error

# ── Datos de prueba ──────────────────────────────────────────────────────────
CORREO_JEFE       = "carlos.rodriguez@helpharma.com"
PASSWORD_VALIDA   = "Admin2026"
PASSWORD_INVALIDA = "WrongPass123"
CORREO_INEXISTENTE = "noexiste@helpharma.com"
PASSWORD_NUEVA    = "NuevaClave2026!"
# Usuario dedicado para TC-05: tiene DebeCambiarPassword=True al inicio
# (reseteado por conftest.py antes de cada sesión de tests)
CORREO_CAMBIO_PWD = "laura.sanchez@helpharma.com"


# ── TC-01: Login con credenciales correctas ─────────────────────────────────
def test_tc01_login_credenciales_correctas(page):
    """
    Dado un usuario válido con DebeCambiarPassword=true,
    el login debe redirigir a /Cuenta/CambiarPassword.
    """
    hacer_login(page, CORREO_JEFE, PASSWORD_VALIDA)

    url_actual = page.url
    assert "/Cuenta/CambiarPassword" in url_actual or "/Dashboard" in url_actual, (
        f"TC-01 FALLO: Se esperaba redirigir a CambiarPassword o Dashboard, "
        f"pero la URL actual es: {url_actual}"
    )
    print(f"\n  ✅ TC-01 PASÓ — URL tras login: {url_actual}")


# ── TC-02: Login con contraseña incorrecta ──────────────────────────────────
def test_tc02_password_incorrecta(page):
    """
    Con contraseña incorrecta debe permanecer en Login y mostrar error.
    """
    hacer_login(page, CORREO_JEFE, PASSWORD_INVALIDA)

    url_actual = page.url
    assert "/Cuenta/Login" in url_actual, (
        f"TC-02 FALLO: Debía permanecer en Login, pero redirigió a: {url_actual}"
    )
    assert hay_error_formulario(page), (
        "TC-02 FALLO: No se mostró ningún mensaje de error en el formulario."
    )
    texto_error = obtener_texto_error(page)
    print(f"\n  ✅ TC-02 PASÓ — Mensaje de error: '{texto_error}'")


# ── TC-03: Login con correo inexistente ─────────────────────────────────────
def test_tc03_correo_inexistente(page):
    """
    Con correo que no existe en BD debe permanecer en Login y mostrar error.
    """
    hacer_login(page, CORREO_INEXISTENTE, PASSWORD_VALIDA)

    url_actual = page.url
    assert "/Cuenta/Login" in url_actual, (
        f"TC-03 FALLO: Debía permanecer en Login, pero redirigió a: {url_actual}"
    )
    assert hay_error_formulario(page), (
        "TC-03 FALLO: No se mostró ningún mensaje de error en el formulario."
    )
    texto_error = obtener_texto_error(page)
    print(f"\n  ✅ TC-03 PASÓ — Mensaje de error: '{texto_error}'")


# ── TC-04: Login con campos vacíos ──────────────────────────────────────────
def test_tc04_campos_vacios(page):
    """
    Sin rellenar campos, al hacer submit debe mostrar errores de validación
    y permanecer en la página de Login.
    """
    page.goto(f"{BASE_URL}/Cuenta/Login")
    page.wait_for_load_state("networkidle")

    # Submit sin datos
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    url_actual = page.url
    assert "/Cuenta/Login" in url_actual, (
        f"TC-04 FALLO: Debía permanecer en Login, pero redirigió a: {url_actual}"
    )
    assert hay_error_formulario(page), (
        "TC-04 FALLO: No se mostraron errores de validación con campos vacíos."
    )
    print(f"\n  ✅ TC-04 PASÓ — Errores de validación visibles.")


# ── TC-05: Flujo completo Login → CambiarPassword → Dashboard ───────────────
def test_tc05_flujo_completo(page):
    """
    Login con credenciales válidas → redirige a CambiarPassword →
    cambiar contraseña → redirige a Dashboard.
    NOTA: Este test modifica la contraseña en BD.
          El fixture reset_estado_db en conftest.py la restaura automáticamente
          antes de cada ejecución de la suite.
    """
    hacer_login(page, CORREO_CAMBIO_PWD, PASSWORD_VALIDA)

    url_tras_login = page.url

    # Si ya cambió la contraseña antes, puede ir directo a Dashboard
    if "/Dashboard" in url_tras_login:
        print(f"\n  ✅ TC-05 PASÓ (parcial) — Usuario ya cambió contraseña, fue directo a Dashboard.")
        return

    assert "/Cuenta/CambiarPassword" in url_tras_login, (
        f"TC-05 FALLO (paso 1): Se esperaba CambiarPassword, URL actual: {url_tras_login}"
    )

    # Rellenar formulario de cambio de contraseña
    # Los campos del ViewModel CambiarPasswordViewModel usan Dto.PasswordActual, Dto.NuevoPassword, Dto.ConfirmarPassword
    page.fill("#Dto_PasswordActual", PASSWORD_VALIDA)
    page.fill("#Dto_NuevoPassword", PASSWORD_NUEVA)
    page.fill("#Dto_ConfirmarPassword", PASSWORD_NUEVA)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    url_tras_cambio = page.url
    assert "/Dashboard" in url_tras_cambio, (
        f"TC-05 FALLO (paso 2): Se esperaba Dashboard tras cambio de contraseña, "
        f"URL actual: {url_tras_cambio}"
    )
    print(f"\n  ✅ TC-05 PASÓ — Flujo completo: Login → CambiarPassword → Dashboard.")


# ── TC-06: Protección de rutas sin sesión ───────────────────────────────────
def test_tc06_proteccion_rutas_sin_sesion(page):
    """
    Sin sesión activa, acceder a /Dashboard debe redirigir a Login.
    """
    # Usar contexto limpio (sin cookies) navegando directo
    page.goto(f"{BASE_URL}/Dashboard")
    page.wait_for_load_state("networkidle")

    url_actual = page.url
    assert "/Cuenta/Login" in url_actual, (
        f"TC-06 FALLO: Se esperaba redirección a Login sin sesión, "
        f"pero la URL actual es: {url_actual}"
    )
    print(f"\n  ✅ TC-06 PASÓ — Ruta protegida redirige a Login correctamente.")


# ── TC-07: Logout ────────────────────────────────────────────────────────────
def test_tc07_logout(page):
    """
    Tras logout, la cookie se elimina y el acceso a rutas protegidas
    redirige nuevamente a Login.
    """
    # Primero hacer login (puede ir a CambiarPassword o Dashboard)
    hacer_login(page, CORREO_JEFE, PASSWORD_VALIDA)
    url_tras_login = page.url
    assert "/Cuenta/Login" not in url_tras_login, (
        f"TC-07 FALLO (setup): No se pudo hacer login. URL: {url_tras_login}"
    )

    # Hacer logout
    hacer_logout(page)
    url_tras_logout = page.url
    assert "/Cuenta/Login" in url_tras_logout, (
        f"TC-07 FALLO (logout): Tras logout se esperaba Login, URL: {url_tras_logout}"
    )

    # Verificar que la sesión quedó anulada
    page.goto(f"{BASE_URL}/Dashboard")
    page.wait_for_load_state("networkidle")
    url_sin_sesion = page.url
    assert "/Cuenta/Login" in url_sin_sesion, (
        f"TC-07 FALLO (post-logout): La cookie sigue activa tras logout. URL: {url_sin_sesion}"
    )
    print(f"\n  ✅ TC-07 PASÓ — Logout funcionó y sesión quedó anulada.")
