"""
Pruebas de validación post-despliegue — GestiónRH
==================================================
Verifica que la aplicación desplegada responde correctamente
y que las funciones principales están operativas.

URL base  : http://localhost:5000
Usuario   : lissy.gallego@zentria.com.co  (rol Analista)
Contraseña: Usuario1

TC-D01  Página de login es accesible y carga sin errores
TC-D02  Login con credenciales correctas → redirige a Dashboard
TC-D03  Login con credenciales incorrectas → permanece en Login con error
TC-D04  Dashboard carga indicadores (empleados activos, etc.)
TC-D05  Módulo Empleados: lista carga sin errores
TC-D06  Perfil de empleado: carga datos completos
TC-D07  Módulo Eventos Laborales: carga sin errores
TC-D08  Módulo Horarios y Turnos: carga sin errores
TC-D09  Módulo Horas Extras: carga sin errores
TC-D10  Página Acceso-Denegado: devuelve 200 (no 404)
TC-D11  Ruta protegida sin sesión → redirige a Login
TC-D12  Logout limpia sesión y redirige a Login
"""

import pytest
from playwright.sync_api import Page, expect

# ── Configuración ─────────────────────────────────────────────────────────────
import os
BASE_URL     = os.environ.get("APP_BASE_URL", "http://localhost:5000").rstrip("/")
CORREO       = "lissy.gallego@zentria.com.co"
PASSWORD     = "Usuario1"
PWD_INVALIDA = "Clave_Incorrecta_999"

# Timeouts ampliados para servidor de producción (ms)
NAV_TIMEOUT  = 120_000   # 2 min para navegaciones
ACT_TIMEOUT  =  90_000   # 90 s para acciones (click, fill…)


# ── Fixture: timeouts extendidos ──────────────────────────────────────────────
@pytest.fixture(autouse=True)
def configurar_timeouts(page: Page):
    """Aplica timeouts amplios para que el servidor de producción tenga tiempo de responder."""
    page.set_default_navigation_timeout(NAV_TIMEOUT)
    page.set_default_timeout(ACT_TIMEOUT)


# ── Helpers locales ───────────────────────────────────────────────────────────
def login(page: Page) -> None:
    """Inicia sesión con el usuario principal de prueba."""
    page.goto(f"{BASE_URL}/Cuenta/Login", timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)
    page.locator("#CorreoAcceso").fill(CORREO)
    page.locator("#inputPassword").fill(PASSWORD)
    with page.expect_navigation(timeout=NAV_TIMEOUT):
        page.locator("button[type=submit]").click()
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)


def logout(page: Page) -> None:
    """Cierra la sesión actual."""
    page.goto(f"{BASE_URL}/Cuenta/Logout", timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)


def hay_error_pagina(page: Page) -> bool:
    """Devuelve True si la página muestra la vista de error genérico."""
    return (
        "An error occurred" in page.content()
        or "/Home/Error" in page.url
    )


# ── TC-D01: Página de login accesible ─────────────────────────────────────────
def test_d01_login_accesible(page: Page):
    page.goto(f"{BASE_URL}/Cuenta/Login", timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)

    assert "/Cuenta/Login" in page.url or page.url == f"{BASE_URL}/"
    assert not hay_error_pagina(page), "TC-D01 FALLO: La página de login muestra un error."
    expect(page.locator("#CorreoAcceso")).to_be_visible()
    expect(page.locator("#inputPassword")).to_be_visible()
    print(f"\n  ✅ TC-D01 PASÓ — Login accesible en {page.url}")


# ── TC-D02: Login correcto → Dashboard ────────────────────────────────────────
def test_d02_login_correcto(page: Page):
    login(page)

    login_url = f"{BASE_URL}/Cuenta/Login"
    assert page.url.rstrip("/") != login_url.rstrip("/"), (
        f"TC-D02 FALLO: Sigue en Login, credenciales rechazadas."
    )
    assert not hay_error_pagina(page), "TC-D02 FALLO: La página muestra un error."
    print(f"\n  ✅ TC-D02 PASÓ — Redirigido a: {page.url}")


# ── TC-D03: Login incorrecto → permanece en Login ────────────────────────────
def test_d03_login_incorrecto(page: Page):
    page.goto(f"{BASE_URL}/Cuenta/Login", timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)
    page.locator("#CorreoAcceso").fill(CORREO)
    page.locator("#inputPassword").fill(PWD_INVALIDA)
    page.locator("button[type=submit]").click()
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)

    es_url_login = "/Cuenta/Login" in page.url or page.url.rstrip("/") == BASE_URL
    assert es_url_login, (
        f"TC-D03 FALLO: Debía permanecer en Login, redirigió a: {page.url}"
    )
    errores = page.locator(".form-error").all()
    hay_error = any(
        e.is_visible() and e.inner_text().strip()
        for e in errores
    )
    assert hay_error, "TC-D03 FALLO: No se mostró mensaje de error."
    print(f"\n  ✅ TC-D03 PASÓ — Error de credenciales mostrado correctamente.")


# ── TC-D04: Dashboard con indicadores ────────────────────────────────────────
def test_d04_dashboard_indicadores(page: Page):
    login(page)

    page.goto(f"{BASE_URL}/Dashboard/Index", timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)

    assert not hay_error_pagina(page), "TC-D04 FALLO: Dashboard muestra error."
    expect(page.locator("h1")).to_contain_text("Dashboard")
    # Al menos el indicador de empleados activos debe estar presente
    contenido = page.content()
    assert "Empleados activos" in contenido, (
        "TC-D04 FALLO: No se encontró el indicador 'Empleados activos'."
    )
    print(f"\n  ✅ TC-D04 PASÓ — Dashboard carga con indicadores.")


# ── TC-D05: Módulo Empleados ─────────────────────────────────────────────────
def test_d05_empleados_lista(page: Page):
    login(page)

    page.goto(f"{BASE_URL}/Empleado/Index", timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)

    assert not hay_error_pagina(page), "TC-D05 FALLO: Módulo Empleados muestra error."
    expect(page.locator("h1")).to_contain_text("Empleados")
    expect(page.locator("table")).to_be_visible()
    print(f"\n  ✅ TC-D05 PASÓ — Lista de empleados carga correctamente.")


# ── TC-D06: Perfil de empleado ───────────────────────────────────────────────
def test_d06_perfil_empleado(page: Page):
    login(page)

    page.goto(f"{BASE_URL}/Empleado/Perfil/1", timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)

    assert not hay_error_pagina(page), "TC-D06 FALLO: Perfil de empleado muestra error."
    expect(page.locator("h1")).to_be_visible()
    # Verifica que se muestren las pestañas del perfil
    expect(page.locator("[role=tablist]")).to_be_visible()
    print(f"\n  ✅ TC-D06 PASÓ — Perfil de empleado carga datos.")


# ── TC-D07: Módulo Eventos Laborales ─────────────────────────────────────────
def test_d07_eventos_laborales(page: Page):
    login(page)

    page.goto(f"{BASE_URL}/EventoLaboral/Index", timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)

    assert not hay_error_pagina(page), "TC-D07 FALLO: Módulo Eventos Laborales muestra error."
    expect(page.locator("h1")).to_contain_text("Eventos")
    print(f"\n  ✅ TC-D07 PASÓ — Módulo Eventos Laborales carga correctamente.")


# ── TC-D08: Módulo Horarios y Turnos ─────────────────────────────────────────
def test_d08_horarios_turnos(page: Page):
    login(page)

    page.goto(f"{BASE_URL}/Turno/Index", timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)

    assert not hay_error_pagina(page), "TC-D08 FALLO: Módulo Horarios y Turnos muestra error."
    expect(page.locator("h1")).to_be_visible()
    print(f"\n  ✅ TC-D08 PASÓ — Módulo Horarios y Turnos carga correctamente.")


# ── TC-D09: Módulo Horas Extras ──────────────────────────────────────────────
def test_d09_horas_extras(page: Page):
    login(page)

    page.goto(f"{BASE_URL}/HoraExtra/Index", timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)

    assert not hay_error_pagina(page), "TC-D09 FALLO: Módulo Horas Extras muestra error."
    expect(page.locator("h1")).to_be_visible()
    print(f"\n  ✅ TC-D09 PASÓ — Módulo Horas Extras carga correctamente.")


# ── TC-D10: Página Acceso-Denegado devuelve 200 ──────────────────────────────
def test_d10_acceso_denegado_existe(page: Page):
    login(page)

    response = page.goto(f"{BASE_URL}/Cuenta/Acceso-Denegado", timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)

    assert response is not None and response.status == 200, (
        f"TC-D10 FALLO: /Cuenta/Acceso-Denegado devolvió {response and response.status} en lugar de 200."
    )
    assert not hay_error_pagina(page), "TC-D10 FALLO: La página de acceso denegado muestra error genérico."
    print(f"\n  ✅ TC-D10 PASÓ — Página Acceso-Denegado responde 200.")


# ── TC-D11: Ruta protegida sin sesión → Login ────────────────────────────────
def test_d11_ruta_protegida_sin_sesion(page: Page):
    # Asegurar que no hay sesión activa
    logout(page)

    page.goto(f"{BASE_URL}/Dashboard/Index", timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)

    es_url_login = "/Cuenta/Login" in page.url or page.url.rstrip("/") == BASE_URL
    assert es_url_login, (
        f"TC-D11 FALLO: Ruta protegida no redirigió a Login. URL: {page.url}"
    )
    print(f"\n  ✅ TC-D11 PASÓ — Ruta protegida redirige a Login sin sesión.")


# ── TC-D12: Logout limpia sesión ─────────────────────────────────────────────
def test_d12_logout(page: Page):
    login(page)
    assert "/Dashboard" in page.url or "/Cuenta/CambiarPassword" in page.url

    logout(page)

    es_url_login_1 = "/Cuenta/Login" in page.url or page.url.rstrip("/") == BASE_URL
    assert es_url_login_1, (
        f"TC-D12 FALLO: Logout no redirigió a Login. URL: {page.url}"
    )
    # Verificar que la sesión realmente se cerró: acceder a ruta protegida
    page.goto(f"{BASE_URL}/Dashboard/Index", timeout=NAV_TIMEOUT)
    page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT)
    es_url_login_2 = "/Cuenta/Login" in page.url or page.url.rstrip("/") == BASE_URL
    assert es_url_login_2, (
        "TC-D12 FALLO: Después del logout aún se puede acceder al Dashboard."
    )
    print(f"\n  ✅ TC-D12 PASÓ — Logout limpia la sesión correctamente.")
