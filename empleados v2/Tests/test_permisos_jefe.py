"""Pruebas de permisos para el rol Jefe (Scope A).
Usuario: Carlos Rodríguez (carlos.rodriguez@yopmail.com, EmpleadoId=1, Jefe, Medellín)
Contraseña: Clave2024*
"""
import pytest
from helpers import hacer_login_completo, hacer_logout, esta_acceso_denegado, BASE_URL

CORREO = "carlos.rodriguez@yopmail.com"
PASSWORD = "Usuario1"


@pytest.fixture(scope="module")
def _sesion_jefe(browser):
    """Sesión persistente como Carlos (Jefe)."""
    context = browser.new_context()
    page = context.new_page()
    hacer_login_completo(page, CORREO, PASSWORD)
    yield page
    hacer_logout(page)
    context.close()


# TC-PJ-01: Jefe puede ver lista completa de empleados
def test_jefe_ve_lista_empleados(_sesion_jefe):
    page = _sesion_jefe
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)
    assert "/Empleado" in page.url


# TC-PJ-02: Jefe puede crear nuevo empleado (accede al formulario)
def test_jefe_puede_acceder_nuevo_empleado(_sesion_jefe):
    page = _sesion_jefe
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)
    assert "/Empleado/Nuevo" in page.url


# TC-PJ-03: Jefe puede editar cualquier empleado
def test_jefe_puede_editar_empleado_ajeno(_sesion_jefe):
    page = _sesion_jefe
    page.goto(f"{BASE_URL}/Empleado/Editar/2")  # Laura (Regente)
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PJ-04: Jefe puede ver perfil de cualquier empleado
def test_jefe_puede_ver_perfil_cualquier(_sesion_jefe):
    page = _sesion_jefe
    page.goto(f"{BASE_URL}/Empleado/Perfil/5")  # Diana (Operario)
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PJ-05: Jefe ve todas las horas extras (sin filtro de jerarquía)
def test_jefe_ve_todas_horas_extras(_sesion_jefe):
    page = _sesion_jefe
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)
    # Debe haber más de una fila en la tabla
    filas = page.locator("table[aria-label='Solicitudes de horas extras'] tbody tr").all()
    assert len(filas) > 1


# TC-PJ-06: Jefe ve todos los eventos laborales
def test_jefe_ve_todos_eventos(_sesion_jefe):
    page = _sesion_jefe
    page.goto(f"{BASE_URL}/EventoLaboral")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PJ-07: Jefe puede acceder a turnos
def test_jefe_ve_turnos(_sesion_jefe):
    page = _sesion_jefe
    page.goto(f"{BASE_URL}/Turno")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PJ-08: Jefe puede acceder a catálogos
def test_jefe_puede_acceder_catalogos(_sesion_jefe):
    page = _sesion_jefe
    page.goto(f"{BASE_URL}/Catalogos")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PJ-09: El sidebar del Jefe muestra el link "Empleados" (no "Mi Perfil")
def test_jefe_sidebar_muestra_empleados(_sesion_jefe):
    page = _sesion_jefe
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    sidebar_empleados = page.locator(".sidebar-nav a:has-text('Empleados')").is_visible()
    sidebar_mi_perfil = page.locator(".sidebar-nav a:has-text('Mi Perfil')").is_visible()
    assert sidebar_empleados
    assert not sidebar_mi_perfil
