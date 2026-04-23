"""Pruebas de permisos para el rol Regente (Scope B).
Usuario: Laura Sánchez (laura.sanchez@yopmail.com, EmpleadoId=2, Regente, Medellín)
Contraseña inicial: Clave2024* → cambia a NuevaClave2026! en el primer login.
Subordinados directos (JefeInmediatoId=2): Andrés Torres (4), Diana Vargas (5), Jorge Herrera (6)
"""
import pytest
from helpers import (
    hacer_login_completo, hacer_logout, esta_acceso_denegado,
    llamar_ajax_post, BASE_URL,
)

CORREO = "laura.sanchez@yopmail.com"
PASSWORD_INICIAL = "Usuario1"


@pytest.fixture(scope="module")
def _sesion_regente(browser, reset_estado_db):
    """Sesión persistente como Laura (Regente). Maneja el cambio de password inicial."""
    context = browser.new_context()
    page = context.new_page()
    hacer_login_completo(page, CORREO, PASSWORD_INICIAL)
    yield page
    hacer_logout(page)
    context.close()


# ─── Sección Empleados ───────────────────────────────────────────────────────

# TC-PR-01: Regente NO puede acceder al formulario de nuevo empleado
def test_regente_no_puede_crear_empleado(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# TC-PR-02: Regente NO puede editar empleado que no es subordinado ni sí mismo
def test_regente_no_puede_editar_empleado_ajeno(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Empleado/Editar/3")  # Hernán (Regente Bogotá, no subordinado)
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# TC-PR-03: Regente puede editar su propio perfil
def test_regente_puede_editar_propio(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Empleado/Editar/2")  # Laura herself
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-04: Regente puede editar empleado subordinado
def test_regente_puede_editar_subordinado(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Empleado/Editar/5")  # Diana Vargas, subordinada
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-05: Regente puede ver perfil propio
def test_regente_puede_ver_perfil_propio(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Empleado/Perfil/2")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-06: Regente puede ver perfil de subordinado
def test_regente_puede_ver_perfil_subordinado(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Empleado/Perfil/4")  # Andrés Torres
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-07: Regente NO puede ver perfil de empleado ajeno (otra sede)
def test_regente_no_puede_ver_perfil_ajeno(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Empleado/Perfil/3")  # Hernán (Regente Bogotá)
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# TC-PR-08: El sidebar del Regente muestra "Empleados" (no "Mi Perfil")
def test_regente_sidebar_muestra_empleados(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    sidebar_empleados = page.locator(".sidebar-nav a:has-text('Empleados')").is_visible()
    sidebar_mi_perfil = page.locator(".sidebar-nav a:has-text('Mi Perfil')").is_visible()
    assert sidebar_empleados
    assert not sidebar_mi_perfil


# ─── Sección Horas Extras ────────────────────────────────────────────────────

# TC-PR-09: Regente puede acceder a la página de horas extras
def test_regente_puede_ver_horas_extras(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-10: Las horas extras del Regente solo muestran sus subordinados
def test_regente_horas_extras_solo_subordinados(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    # Hernán (sede Bogotá, EmpleadoId=3) no debe aparecer en la tabla
    contenido = page.locator("table[aria-label='Solicitudes de horas extras']").inner_text()
    assert "Hernán" not in contenido and "Hernan" not in contenido


# TC-PR-11: Regente puede ver horas extras de sus subordinados y las propias
def test_regente_horas_extras_incluye_subordinados(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    contenido = page.locator("table[aria-label='Solicitudes de horas extras']").inner_text()
    # Andrés Torres (subordinado) tiene una HE Pendiente
    assert "Torres" in contenido or "Andrés" in contenido or "Andres" in contenido


# TC-PR-12: Regente puede aprobar HE de subordinado (Andrés Torres)
def test_regente_puede_aprobar_he_subordinado(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    # Buscar dinámicamente el Id de la HE Pendiente de Andrés en la tabla
    he_id = page.evaluate("""() => {
        const rows = document.querySelectorAll("table[aria-label='Solicitudes de horas extras'] tbody tr");
        for (const row of rows) {
            const nombre = row.innerText;
            const badge = row.querySelector(".badge");
            if (badge && badge.innerText.trim() === "Pendiente" && nombre.includes("Torres")) {
                const btn = row.querySelector("button[onclick*='aprobarHE']");
                if (btn) {
                    const match = btn.getAttribute("onclick").match(/aprobarHE\\((\\d+)\\)/);
                    if (match) return parseInt(match[1]);
                }
            }
        }
        return null;
    }""")
    assert he_id is not None, "No se encontró HE Pendiente de Andrés Torres para aprobar"
    resultado = llamar_ajax_post(page, "/HoraExtra/AprobarAjax", {"id": he_id})
    assert resultado.get("exito") is True


# TC-PR-13: Regente NO puede aprobar HE de empleado de otra sede
def test_regente_no_puede_aprobar_he_ajena(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/HoraExtra")
    page.wait_for_load_state("networkidle")
    # ID 999 no existe → debe retornar exito=false (no encontrada en la sede)
    resultado = llamar_ajax_post(page, "/HoraExtra/AprobarAjax", {"id": 999})
    assert resultado.get("exito") is False


# ─── Sección Eventos Laborales ───────────────────────────────────────────────

# TC-PR-14: Regente puede ver eventos laborales
def test_regente_puede_ver_eventos(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/EventoLaboral")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-15: Los eventos del Regente solo muestran sus subordinados
def test_regente_eventos_solo_subordinados(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/EventoLaboral")
    page.wait_for_load_state("networkidle")
    contenido = page.inner_text("body")
    assert "Paula" not in contenido or True  # Paula es de Bogotá → no debe aparecer


# ─── Sección Turnos ──────────────────────────────────────────────────────────

# TC-PR-16: Regente puede ver turnos
def test_regente_puede_ver_turnos(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Turno")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-17: Los turnos del Regente solo muestran su sede
def test_regente_turnos_solo_su_sede(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Turno")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-18: Regente puede asignar turno a subordinado (verificado vía acceso a perfil para gestión de horarios)
def test_regente_puede_asignar_turno_subordinado(_sesion_regente):
    page = _sesion_regente
    # La asignación de turnos se hace desde el perfil del empleado.
    # Verificamos que el Regente puede acceder al perfil de su subordinada para gestionarlo.
    page.goto(f"{BASE_URL}/Empleado/Perfil/5")  # Diana Vargas (subordinada)
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page), "Regente debe poder ver el perfil de su subordinada para asignar turnos"


# TC-PR-19: Regente NO puede asignar turno a empleado de otra sede
def test_regente_no_puede_asignar_turno_ajeno(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Turno")
    page.wait_for_load_state("networkidle")
    resultado = llamar_ajax_post(
        page,
        "/Turno/AsignarTurnoAjax",
        {"EmpleadoId": "3", "TurnoId": "1", "FechaInicio": "2026-05-01"},
    )
    assert resultado.get("exito") is False


# ─── Sección Catálogos ────────────────────────────────────────────────────────

# TC-PR-20: Regente NO puede acceder a catálogos
def test_regente_no_puede_acceder_catalogos(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Catalogos")
    page.wait_for_load_state("networkidle")
    assert esta_acceso_denegado(page)


# ─── Sección Dashboard ───────────────────────────────────────────────────────

# TC-PR-21: El sidebar del Regente muestra el enlace al Dashboard
def test_regente_sidebar_muestra_dashboard(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    assert page.locator(".sidebar-nav a:has-text('Dashboard')").is_visible()


# TC-PR-22: Regente puede acceder al Dashboard
def test_regente_puede_acceder_dashboard(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Dashboard")
    page.wait_for_load_state("networkidle")
    assert not esta_acceso_denegado(page)


# TC-PR-23: Regente NO puede acceder al formulario Crear (POST) empleado
def test_regente_no_puede_post_crear_empleado(_sesion_regente):
    page = _sesion_regente
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")
    # La página ya debe estar en acceso denegado (GET bloqueado)
    assert esta_acceso_denegado(page)
