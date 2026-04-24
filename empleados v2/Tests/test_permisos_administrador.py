"""Pruebas de permisos para el rol Administrador — Scope G (TC-PR-84 a TC-PR-96).
Usuario: admin@yopmail.com — rol técnico de plataforma (sin EmpleadoId)
Contraseña: Usuario1  (DebeCambiarPassword=0 — no requiere cambio en primer login)
Superusuario sin restricciones: accede a todo, incluido Catálogos.
"""
import pytest
from helpers import (
    hacer_login_completo, hacer_logout, esta_acceso_denegado,
    llamar_ajax_post, BASE_URL,
)

CORREO   = "admin@yopmail.com"
PASSWORD = "Usuario1"
# EmpleadoId de un empleado activo para las pruebas de escritura
EMP_ID_TEST = 1   # Carlos Alberto Rodríguez Mora — DirectorTecnico Medellín


@pytest.fixture(scope="module")
def _sesion_admin(browser, reset_estado_db):
    """Sesión persistente como Administrador de plataforma."""
    context = browser.new_context()
    page = context.new_page()
    hacer_login_completo(page, CORREO, PASSWORD)
    yield page
    hacer_logout(page)
    context.close()


# TC-PR-84: Dashboard visible en el menú del Administrador
def test_tc_pr_84_dashboard_visible_sidebar(_sesion_admin):
    page = _sesion_admin
    page.goto(f"{BASE_URL}/Dashboard")
    page.wait_for_load_state("networkidle")
    assert page.locator(".sidebar-nav a:has-text('Dashboard')").is_visible(), \
        "TC-PR-84: El ítem Dashboard no está visible en el sidebar del Administrador"


# TC-PR-85: Administrador puede acceder al Dashboard
def test_tc_pr_85_dashboard_accesible(_sesion_admin):
    page = _sesion_admin
    page.goto(f"{BASE_URL}/Dashboard")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-85: Administrador debería poder acceder al Dashboard"


# TC-PR-86: Administrador ve todo el personal (multi-sede, sin filtro)
def test_tc_pr_86_ve_todo_personal_multi_sede(_sesion_admin):
    page = _sesion_admin
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-86: Administrador debería poder acceder a la lista de empleados"
    contenido = page.content()
    tiene_medellin = "Medellín" in contenido or "Medellin" in contenido
    tiene_bogota   = "Bogotá" in contenido or "Bogota" in contenido
    assert tiene_medellin and tiene_bogota, \
        "TC-PR-86: Administrador debe ver empleados de ambas sedes"


# TC-PR-87: Administrador puede acceder al formulario de nuevo empleado
def test_tc_pr_87_puede_crear_empleados(_sesion_admin):
    page = _sesion_admin
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-87: Administrador debería poder acceder al formulario de nuevo empleado"
    assert "/Empleado/Nuevo" in page.url


# TC-PR-88: Administrador puede editar cualquier empleado
def test_tc_pr_88_puede_editar_empleados(_sesion_admin):
    page = _sesion_admin
    page.goto(f"{BASE_URL}/Empleado/Editar/{EMP_ID_TEST}")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-88: Administrador debería poder editar cualquier empleado"


# TC-PR-89: Administrador puede ver la lista de eventos laborales (todas las sedes)
def test_tc_pr_89_ve_eventos_laborales(_sesion_admin):
    page = _sesion_admin
    page.goto(f"{BASE_URL}/EventoLaboral")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-89: Administrador debería poder acceder a eventos laborales"


# TC-PR-90: Administrador puede registrar un evento laboral
def test_tc_pr_90_puede_registrar_evento(_sesion_admin):
    page = _sesion_admin
    page.goto(f"{BASE_URL}/EventoLaboral")
    page.wait_for_load_state("networkidle")
    resp = llamar_ajax_post(page, "/EventoLaboral/RegistrarAjax", {
        "EmpleadoId":      EMP_ID_TEST,
        "TipoEvento":      "Permiso",
        "FechaInicio":     "2026-08-01",
        "FechaFin":        "2026-08-01",
        "AutorizadoPor":   "Administrador",
        "Descripcion":     "Test permiso Admin",
        "DiasSolicitados": 1,
    })
    assert resp.get("exito") is True, \
        f"TC-PR-90: Administrador debería poder registrar eventos — respuesta: {resp}"


# TC-PR-91: Administrador puede ver la página de turnos (todas las sedes)
def test_tc_pr_91_ve_turnos(_sesion_admin):
    page = _sesion_admin
    page.goto(f"{BASE_URL}/Turno")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-91: Administrador debería poder acceder a turnos"


# TC-PR-93: Administrador puede ver horas extras (todas las sedes)
def test_tc_pr_93_ve_horas_extras(_sesion_admin):
    page = _sesion_admin
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-93: Administrador debería poder acceder a horas extras"


# TC-PR-95: El sidebar del Administrador muestra el ítem "Catálogos"
def test_tc_pr_95_catalogos_visibles_sidebar(_sesion_admin):
    page = _sesion_admin
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    catalogo_visible = page.locator(".sidebar-nav a:has-text('Catálogos')").is_visible()
    assert catalogo_visible, \
        "TC-PR-95: El Administrador debe ver el ítem 'Catálogos' en el sidebar"


# TC-PR-96: Administrador puede acceder a catálogos por URL directa
def test_tc_pr_96_puede_acceder_catalogos(_sesion_admin):
    page = _sesion_admin
    page.goto(f"{BASE_URL}/Catalogos")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-96: Administrador debería poder acceder a /Catalogos"
