"""Pruebas de permisos para el rol AuxiliarRegente (Scope D).
Usuario: Andrés Torres (andres.torres@yopmail.com, EmpleadoId=4, AuxiliarRegente, Medellín)
JefeInmediatoId=2 (Laura Sánchez)
Andrés NO tiene subordinados (nadie tiene JefeInmediatoId=4).
Contraseña: Clave2024*
"""
import pytest
from helpers import (
    hacer_login_completo, hacer_logout, esta_acceso_denegado,
    llamar_ajax_post, BASE_URL,
)

CORREO = "andres.torres@yopmail.com"
PASSWORD = "Usuario1"
EMPLEADO_ID = 4


@pytest.fixture(scope="module")
def _sesion_aux_regente(browser, reset_estado_db):
    """Sesión persistente como Andrés Torres (AuxiliarRegente)."""
    context = browser.new_context()
    page = context.new_page()
    hacer_login_completo(page, CORREO, PASSWORD)
    yield page
    hacer_logout(page)
    context.close()


# ─── Sección Empleados ───────────────────────────────────────────────────────

# TC-PR-48: AuxiliarRegente sin subordinados: la lista solo muestra él mismo
def test_aux_regente_lista_empleados_solo_propio(_sesion_aux_regente):
    page = _sesion_aux_regente
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)
    filas = page.locator("table tbody tr").all()
    assert len(filas) == 1


# TC-PR-49: AuxiliarRegente NO puede crear nuevo empleado
def test_aux_regente_no_puede_crear_empleado(_sesion_aux_regente):
    page = _sesion_aux_regente
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# TC-PR-50: AuxiliarRegente puede editar su propio perfil
def test_aux_regente_puede_editar_propio(_sesion_aux_regente):
    page = _sesion_aux_regente
    page.goto(f"{BASE_URL}/Empleado/Editar/{EMPLEADO_ID}")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-51: AuxiliarRegente NO puede editar empleado ajeno
def test_aux_regente_no_puede_editar_ajeno(_sesion_aux_regente):
    page = _sesion_aux_regente
    page.goto(f"{BASE_URL}/Empleado/Editar/5")  # Diana Vargas (sub. de Laura, no de Andrés)
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# TC-PR-52: AuxiliarRegente puede ver su propio perfil
def test_aux_regente_puede_ver_perfil_propio(_sesion_aux_regente):
    page = _sesion_aux_regente
    page.goto(f"{BASE_URL}/Empleado/Perfil/{EMPLEADO_ID}")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-53: AuxiliarRegente NO puede ver perfil de empleado ajeno
def test_aux_regente_no_puede_ver_perfil_ajeno(_sesion_aux_regente):
    page = _sesion_aux_regente
    page.goto(f"{BASE_URL}/Empleado/Perfil/2")  # Laura (su jefa)
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# ─── Sección Horas Extras ────────────────────────────────────────────────────

# TC-PR-54: AuxiliarRegente puede ver las horas extras (solo las suyas, sin subordinados)
def test_aux_regente_puede_ver_horas_extras(_sesion_aux_regente):
    page = _sesion_aux_regente
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-55: Las horas extras del AuxiliarRegente solo muestran las propias
# (no tiene subordinados → no aparecen Diana ni Jorge)
def test_aux_regente_horas_extras_solo_propias(_sesion_aux_regente):
    page = _sesion_aux_regente
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    contenido = page.locator("table[aria-label='Solicitudes de horas extras']").inner_text()
    assert "Diana" not in contenido
    assert "Jorge" not in contenido


# TC-PR-56: AuxiliarRegente NO puede aprobar su propia HE
# (su JefeInmediatoId=2 ≠ su empId=4 → AprobarAjax retorna exito=false)
def test_aux_regente_no_puede_aprobar_propia_he(_sesion_aux_regente):
    page = _sesion_aux_regente
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    # Buscar la HE de Andrés en la tabla
    he_id = page.evaluate("""() => {
        const rows = document.querySelectorAll("table[aria-label='Solicitudes de horas extras'] tbody tr");
        for (const row of rows) {
            const badge = row.querySelector(".badge");
            if (badge && badge.innerText.trim() === "Pendiente") {
                // Buscar el botón aprobar o el mensaje "Requiere otro supervisor"
                const btn = row.querySelector("button[onclick*='aprobarHE']");
                if (btn) {
                    const match = btn.getAttribute("onclick").match(/aprobarHE\\((\\d+)\\)/);
                    if (match) return parseInt(match[1]);
                }
            }
        }
        return null;
    }""")
    if he_id is None:
        pytest.skip("No se encontró botón aprobar (puede estar mostrando 'Requiere otro supervisor')")
    resultado = llamar_ajax_post(page, "/HoraExtra/AprobarAjax", {"id": he_id})
    assert resultado.get("exito") is False


# ─── Sección Catálogos ────────────────────────────────────────────────────────

# TC-PR-57: AuxiliarRegente NO puede acceder a catálogos
def test_aux_regente_no_puede_acceder_catalogos(_sesion_aux_regente):
    page = _sesion_aux_regente
    page.goto(f"{BASE_URL}/Catalogos")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# ─── Sección Dashboard ───────────────────────────────────────────────────────

# TC-PR-58: AuxiliarRegente puede acceder al Dashboard
def test_aux_regente_puede_acceder_dashboard(_sesion_aux_regente):
    page = _sesion_aux_regente
    page.goto(f"{BASE_URL}/Dashboard")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-59: El sidebar del AuxiliarRegente muestra Dashboard y Empleados
def test_aux_regente_sidebar_completo(_sesion_aux_regente):
    page = _sesion_aux_regente
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    assert page.locator(".sidebar-nav a:has-text('Dashboard')").is_visible()
    assert page.locator(".sidebar-nav a:has-text('Empleados')").is_visible()
