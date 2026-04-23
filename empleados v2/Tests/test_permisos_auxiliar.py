"""Pruebas de permisos para el rol Operario (Scope C).
Usuario: Diana Vargas (diana.vargas@yopmail.com, EmpleadoId=5, Operario, Medellín)
JefeInmediatoId=2 (Laura Sánchez)
Contraseña: Clave2024*
"""
import pytest
from helpers import (
    hacer_login_completo, hacer_logout, esta_acceso_denegado,
    llamar_ajax_post, BASE_URL,
)

CORREO = "diana.vargas@yopmail.com"
PASSWORD = "Usuario1"
EMPLEADO_ID = 5


@pytest.fixture(scope="module")
def _sesion_operario(browser, reset_estado_db):
    """Sesión persistente como Diana Vargas (Operario)."""
    context = browser.new_context()
    page = context.new_page()
    hacer_login_completo(page, CORREO, PASSWORD)
    yield page
    hacer_logout(page)
    context.close()


# TC-PR-35: Operario al navegar a /Empleado es redirigido a su propio perfil
def test_operario_redirige_a_perfil_propio(_sesion_operario):
    page = _sesion_operario
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    assert f"/Empleado/Perfil/{EMPLEADO_ID}" in page.url


# TC-PR-36: Operario NO puede ver perfil de otro empleado
def test_operario_no_puede_ver_perfil_ajeno(_sesion_operario):
    page = _sesion_operario
    page.goto(f"{BASE_URL}/Empleado/Perfil/1")  # Carlos (Jefe)
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# TC-PR-37: Operario puede ver su propio perfil
def test_operario_puede_ver_perfil_propio(_sesion_operario):
    page = _sesion_operario
    page.goto(f"{BASE_URL}/Empleado/Perfil/{EMPLEADO_ID}")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-38: Operario NO puede acceder al formulario de nuevo empleado
def test_operario_no_puede_crear_empleado(_sesion_operario):
    page = _sesion_operario
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# TC-PR-39: Operario NO puede editar ningún empleado (ni propio)
def test_operario_no_puede_editar_empleado(_sesion_operario):
    page = _sesion_operario
    page.goto(f"{BASE_URL}/Empleado/Editar/{EMPLEADO_ID}")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# TC-PR-40: Operario NO puede ver la lista de eventos laborales
def test_operario_no_puede_ver_eventos(_sesion_operario):
    page = _sesion_operario
    page.goto(f"{BASE_URL}/EventoLaboral")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# TC-PR-41: Operario puede ver horas extras PERO solo las propias (no las de otros)
def test_operario_ve_solo_propias_horas_extras(_sesion_operario):
    page = _sesion_operario
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), "Operario debe poder ver sus propias HorasExtras"
    contenido = page.inner_text("body")
    # No debe verse la columna 'Empleado' ni botones de aprobación para ajenos
    # (puedeAprobar=False para Operario — sin botones de Aprobar/Rechazar)
    assert "Aprobar" not in contenido, "Operario no debe ver botones de aprobación"


# TC-PR-42: Operario NO puede ver turnos
def test_operario_no_puede_ver_turnos(_sesion_operario):
    page = _sesion_operario
    page.goto(f"{BASE_URL}/Turno")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# TC-PR-43: Operario NO puede acceder a catálogos
def test_operario_no_puede_acceder_catalogos(_sesion_operario):
    page = _sesion_operario
    page.goto(f"{BASE_URL}/Catalogos")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# TC-PR-44: Operario NO puede aprobar horas extras vía AJAX
# (navega a /HoraExtra donde sí hay TOKEN disponible)
def test_operario_no_puede_aprobar_he_ajax(_sesion_operario):
    page = _sesion_operario
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    resultado = llamar_ajax_post(page, "/HoraExtra/AprobarAjax", {"id": "1"})
    assert resultado.get("exito") is False


# TC-PR-45: El sidebar del Operario muestra "Mi Perfil" (no "Empleados")
def test_operario_sidebar_muestra_mi_perfil(_sesion_operario):
    page = _sesion_operario
    page.goto(f"{BASE_URL}/Empleado/Perfil/{EMPLEADO_ID}")
    page.wait_for_load_state("networkidle")
    sidebar_mi_perfil = page.locator(f".sidebar-nav a:has-text('Mi Perfil')").is_visible()
    sidebar_empleados = page.locator(".sidebar-nav a:has-text('Empleados')").is_visible()
    assert sidebar_mi_perfil
    assert not sidebar_empleados


# TC-PR-46: El sidebar del Operario NO muestra Dashboard
def test_operario_sidebar_no_muestra_dashboard(_sesion_operario):
    page = _sesion_operario
    page.goto(f"{BASE_URL}/Empleado/Perfil/{EMPLEADO_ID}")
    page.wait_for_load_state("networkidle")
    # Operario no tiene acceso a Dashboard → el sidebar no debe mostrarlo
    sidebar_dashboard = page.locator(".sidebar-nav a:has-text('Dashboard')").is_visible()
    assert not sidebar_dashboard


# TC-PR-47: Operario NO puede registrar evento laboral vía AJAX
# (navega a /HoraExtra para tener TOKEN disponible)
def test_operario_no_puede_registrar_evento_ajax(_sesion_operario):
    page = _sesion_operario
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    resultado = llamar_ajax_post(
        page,
        "/EventoLaboral/RegistrarAjax",
        {
            "EmpleadoId": str(EMPLEADO_ID),
            "TipoEvento": "Incapacidad",
            "FechaInicio": "2026-05-01",
            "FechaFin": "2026-05-02",
        },
    )
    assert resultado.get("exito") is False
