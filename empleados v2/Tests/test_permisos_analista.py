"""Pruebas de permisos para el rol Analista — Scope E (TC-PR-57 a TC-PR-70).
Usuario: Sofía Gómez (sofia.gomez@yopmail.com, EmpleadoId=17, Analista, Medellín)
Contraseña: Usuario1
Acceso total multi-sede. NO puede acceder a catálogos.
"""
import pytest
from helpers import (
    hacer_login_completo, hacer_logout, esta_acceso_denegado,
    llamar_ajax_post, BASE_URL,
)

CORREO  = "sofia.gomez@yopmail.com"
PASSWORD = "Usuario1"
# EmpId de un empleado activo de OTRA sede (Bogotá) para verificar acceso multi-sede
EMP_ID_BOGOTA  = 3   # Hernán David Castillo Mejía — Regente Bogotá
# EmpId de un empleado activo de la propia sede (Medellín)
EMP_ID_MED = 1   # Carlos Rodríguez — DirectorTecnico Medellín


@pytest.fixture(scope="module")
def _sesion_analista(browser, reset_estado_db):
    """Sesión persistente como Sofía Gómez (Analista)."""
    context = browser.new_context()
    page = context.new_page()
    hacer_login_completo(page, CORREO, PASSWORD)
    yield page
    hacer_logout(page)
    context.close()


# TC-PR-57: Analista ve el ítem "Dashboard" en el sidebar
def test_tc_pr_57_dashboard_visible_sidebar(_sesion_analista):
    page = _sesion_analista
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    assert page.locator(".sidebar-nav a:has-text('Dashboard')").is_visible(), \
        "TC-PR-57: El ítem Dashboard no está visible en el sidebar del Analista"


# TC-PR-58: Analista puede acceder al Dashboard
def test_tc_pr_58_dashboard_accesible(_sesion_analista):
    page = _sesion_analista
    page.goto(f"{BASE_URL}/Dashboard")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), "TC-PR-58: Analista debería poder acceder al Dashboard"


# TC-PR-59: Analista ve empleados de TODAS las sedes (multi-sede)
def test_tc_pr_59_ve_empleados_multi_sede(_sesion_analista):
    page = _sesion_analista
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), "TC-PR-59: Analista debería acceder a la lista de empleados"
    # Verifica que hay empleados de Medellín Y de Bogotá
    contenido = page.content()
    tiene_medellin = "Medellín" in contenido or "Medellin" in contenido
    tiene_bogota   = "Bogotá" in contenido or "Bogota" in contenido
    assert tiene_medellin and tiene_bogota, \
        "TC-PR-59: Analista debe ver empleados de ambas sedes (Medellín y Bogotá)"


# TC-PR-60: Analista puede ver el perfil de cualquier empleado
def test_tc_pr_60_puede_ver_perfil_cualquier(_sesion_analista):
    page = _sesion_analista
    page.goto(f"{BASE_URL}/Empleado/Perfil/{EMP_ID_BOGOTA}")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-60: Analista debería poder ver el perfil de un empleado de otra sede"


# TC-PR-61: Analista puede acceder al formulario de nuevo empleado
def test_tc_pr_61_puede_acceder_nuevo_empleado(_sesion_analista):
    page = _sesion_analista
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-61: Analista debería poder acceder al formulario de nuevo empleado"
    assert "/Empleado/Nuevo" in page.url


# TC-PR-62: Analista puede acceder al formulario de edición de cualquier empleado
def test_tc_pr_62_puede_editar_empleados(_sesion_analista):
    page = _sesion_analista
    page.goto(f"{BASE_URL}/Empleado/Editar/{EMP_ID_MED}")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-62: Analista debería poder editar cualquier empleado"


# TC-PR-63: Analista puede ver la lista de eventos laborales
def test_tc_pr_63_ve_eventos_laborales(_sesion_analista):
    page = _sesion_analista
    page.goto(f"{BASE_URL}/EventoLaboral")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-63: Analista debería poder acceder a eventos laborales"


# TC-PR-64: Analista puede registrar un evento laboral
def test_tc_pr_64_puede_registrar_evento(_sesion_analista):
    page = _sesion_analista
    page.goto(f"{BASE_URL}/EventoLaboral")
    page.wait_for_load_state("networkidle")
    resp = llamar_ajax_post(page, "/EventoLaboral/RegistrarAjax", {
        "EmpleadoId":      EMP_ID_MED,
        "TipoEvento":      "Permiso",
        "FechaInicio":     "2026-07-01",
        "FechaFin":        "2026-07-01",
        "AutorizadoPor":   "Sofia Gomez",
        "Descripcion":     "Test permiso Analista",
        "DiasSolicitados": 1,
    })
    assert resp.get("exito") is True, \
        f"TC-PR-64: Analista debería poder registrar eventos — respuesta: {resp}"


# TC-PR-65: Analista puede ver la página de turnos
def test_tc_pr_65_ve_turnos(_sesion_analista):
    page = _sesion_analista
    page.goto(f"{BASE_URL}/Turno")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-65: Analista debería poder acceder a turnos"


# TC-PR-66: Analista puede ver la página de horas extras
def test_tc_pr_67_ve_horas_extras(_sesion_analista):
    page = _sesion_analista
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), \
        "TC-PR-67: Analista debería poder acceder a horas extras"


# TC-PR-69: El sidebar del Analista NO muestra el ítem "Catálogos"
def test_tc_pr_69_catalogos_ocultos_sidebar(_sesion_analista):
    page = _sesion_analista
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    catalogo_visible = page.locator(".sidebar-nav a:has-text('Catálogos')").is_visible()
    assert not catalogo_visible, \
        "TC-PR-69: El Analista NO debe ver el ítem 'Catálogos' en el sidebar"


# TC-PR-70: Analista NO puede acceder a catálogos por URL directa
def test_tc_pr_70_no_puede_acceder_catalogos(_sesion_analista):
    page = _sesion_analista
    page.goto(f"{BASE_URL}/Catalogos")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page), \
        "TC-PR-70: Analista no debería poder acceder a /Catalogos"


# TC-PR-66 (original): El sidebar muestra "Empleados" (no "Mi Perfil")
def test_tc_pr_66_sidebar_muestra_empleados(_sesion_analista):
    page = _sesion_analista
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    sidebar_empleados = page.locator(".sidebar-nav a:has-text('Empleados')").is_visible()
    sidebar_mi_perfil = page.locator(".sidebar-nav a:has-text('Mi Perfil')").is_visible()
    assert sidebar_empleados, "TC-PR-66: El Analista debe ver 'Empleados' en el sidebar"
    assert not sidebar_mi_perfil, "TC-PR-66: El Analista no debe ver 'Mi Perfil' en el sidebar"
