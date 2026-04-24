"""Pruebas de permisos para el rol Direccionador — Scope F (TC-PR-71 a TC-PR-83).
Usuario: Pedro Ramírez (pedro.ramirez@yopmail.com, EmpleadoId=14, Direccionador, Bogotá)
Contraseña: Usuario1
Acceso idéntico al Auxiliar de Farmacia (Operario): solo información propia.
"""
import pytest
from helpers import (
    hacer_login_completo, hacer_logout, esta_acceso_denegado,
    llamar_ajax_post, BASE_URL,
)

CORREO     = "pedro.ramirez@yopmail.com"
PASSWORD   = "Usuario1"
EMPLEADO_ID = 14   # Pedro Ramírez — Direccionador Bogotá


@pytest.fixture(scope="module")
def _sesion_direccionador(browser, reset_estado_db):
    """Sesión persistente como Pedro Ramírez (Direccionador)."""
    context = browser.new_context()
    page = context.new_page()
    hacer_login_completo(page, CORREO, PASSWORD)
    yield page
    hacer_logout(page)
    context.close()


# TC-PR-71: Dashboard NO visible en menú del Direccionador
def test_tc_pr_71_dashboard_no_visible_sidebar(_sesion_direccionador):
    page = _sesion_direccionador
    page.goto(f"{BASE_URL}/Empleado/Perfil/{EMPLEADO_ID}")
    page.wait_for_load_state("networkidle")
    dashboard_visible = page.locator(".sidebar-nav a:has-text('Dashboard')").is_visible()
    assert not dashboard_visible, \
        "TC-PR-71: El Direccionador NO debe ver el ítem 'Dashboard' en el sidebar"


# TC-PR-72: Menú "Empleados" del Direccionador muestra "Mi Perfil"
def test_tc_pr_72_sidebar_muestra_mi_perfil(_sesion_direccionador):
    page = _sesion_direccionador
    page.goto(f"{BASE_URL}/Empleado/Perfil/{EMPLEADO_ID}")
    page.wait_for_load_state("networkidle")
    sidebar_mi_perfil  = page.locator(".sidebar-nav a:has-text('Mi Perfil')").is_visible()
    sidebar_empleados  = page.locator(".sidebar-nav a:has-text('Empleados')").is_visible()
    assert sidebar_mi_perfil, \
        "TC-PR-72: El Direccionador debe ver 'Mi Perfil' en el sidebar"
    assert not sidebar_empleados, \
        "TC-PR-72: El Direccionador NO debe ver 'Empleados' en el sidebar"


# TC-PR-73: Direccionador al navegar a /Empleado es redirigido a su propio perfil
def test_tc_pr_73_redirigido_a_perfil_propio(_sesion_direccionador):
    page = _sesion_direccionador
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    assert f"/Empleado/Perfil/{EMPLEADO_ID}" in page.url, \
        f"TC-PR-73: Debería redirigir a /Empleado/Perfil/{EMPLEADO_ID}, llegó a {page.url}"


# TC-PR-74: Direccionador NO puede ver el perfil de otro empleado
def test_tc_pr_74_no_puede_ver_perfil_ajeno(_sesion_direccionador):
    page = _sesion_direccionador
    page.goto(f"{BASE_URL}/Empleado/Perfil/1")   # Carlos (DirectorTecnico)
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page), \
        "TC-PR-74: Direccionador no debería poder ver el perfil de otro empleado"


# TC-PR-75: Direccionador NO puede acceder al formulario de nuevo empleado
def test_tc_pr_75_no_puede_crear_empleado(_sesion_direccionador):
    page = _sesion_direccionador
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page), \
        "TC-PR-75: Direccionador no debería poder crear empleados"


# TC-PR-76: Eventos Laborales ocultos en el menú del Direccionador
def test_tc_pr_76_eventos_ocultos_sidebar(_sesion_direccionador):
    page = _sesion_direccionador
    page.goto(f"{BASE_URL}/Empleado/Perfil/{EMPLEADO_ID}")
    page.wait_for_load_state("networkidle")
    eventos_visible = page.locator(".sidebar-nav a:has-text('Eventos Laborales')").is_visible()
    assert not eventos_visible, \
        "TC-PR-76: El Direccionador NO debe ver 'Eventos Laborales' en el sidebar"


# TC-PR-77: Direccionador NO puede acceder a Eventos Laborales por URL
def test_tc_pr_77_no_puede_acceder_eventos(_sesion_direccionador):
    page = _sesion_direccionador
    page.goto(f"{BASE_URL}/EventoLaboral")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page), \
        "TC-PR-77: Direccionador no debería poder acceder a /EventoLaboral"


# TC-PR-78: Turnos ocultos en el menú del Direccionador
def test_tc_pr_78_turnos_ocultos_sidebar(_sesion_direccionador):
    page = _sesion_direccionador
    page.goto(f"{BASE_URL}/Empleado/Perfil/{EMPLEADO_ID}")
    page.wait_for_load_state("networkidle")
    turnos_visible = page.locator(".sidebar-nav a:has-text('Horarios')").is_visible()
    assert not turnos_visible, \
        "TC-PR-78: El Direccionador NO debe ver 'Horarios y Turnos' en el sidebar"


# TC-PR-79: Direccionador NO puede acceder a Turnos por URL
def test_tc_pr_79_no_puede_acceder_turnos(_sesion_direccionador):
    page = _sesion_direccionador
    page.goto(f"{BASE_URL}/Turno")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page), \
        "TC-PR-79: Direccionador no debería poder acceder a /Turno"


# TC-PR-80: Direccionador puede acceder a Horas Extras (solo propias)
def test_tc_pr_80_puede_ver_propias_horas_extras(_sesion_direccionador):
    page = _sesion_direccionador
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-80: Direccionador debería poder acceder a /HoraExtra (para ver las propias)"


# TC-PR-81: Direccionador NO puede aprobar una hora extra
def test_tc_pr_81_no_puede_aprobar_he(_sesion_direccionador):
    page = _sesion_direccionador
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    # Intenta aprobar una HE con id=1 (cualquiera) — debe ser rechazado
    resp = llamar_ajax_post(page, "/HoraExtra/AprobarAjax", {"id": 1})
    assert resp.get("exito") is False, \
        f"TC-PR-81: Direccionador no debería poder aprobar HE — respuesta: {resp}"


# TC-PR-82: Catálogos ocultos en el menú del Direccionador
def test_tc_pr_82_catalogos_ocultos_sidebar(_sesion_direccionador):
    page = _sesion_direccionador
    page.goto(f"{BASE_URL}/Empleado/Perfil/{EMPLEADO_ID}")
    page.wait_for_load_state("networkidle")
    catalogo_visible = page.locator(".sidebar-nav a:has-text('Catálogos')").is_visible()
    assert not catalogo_visible, \
        "TC-PR-82: El Direccionador NO debe ver el ítem 'Catálogos' en el sidebar"


# TC-PR-83: Direccionador NO puede acceder a catálogos por URL directa
def test_tc_pr_83_no_puede_acceder_catalogos(_sesion_direccionador):
    page = _sesion_direccionador
    page.goto(f"{BASE_URL}/Catalogos")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page), \
        "TC-PR-83: Direccionador no debería poder acceder a /Catalogos"
