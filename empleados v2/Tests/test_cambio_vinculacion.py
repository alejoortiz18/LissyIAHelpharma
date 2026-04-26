"""
Pruebas E2E — Cambio de Tipo de Vinculación: Temporal → Directo
Plan: Documentos/Pruebas/Playwright/Plan-CambioTipoVinculacionRefinado.md

Empleado de prueba: Camila Andrea Ríos Vargas — CC 99887766
La fixture reset_empleado_temporal la pone en estado Temporal antes de cada test
y la restaura a Temporal al finalizar.

Rol ejecutor: Sofía Gómez (Analista) — sofia.gomez@yopmail.com
"""
import pytest
from playwright.sync_api import Page, expect
from helpers import hacer_login_completo, hacer_logout, BASE_URL

ANALISTA_EMAIL    = "sofia.gomez@yopmail.com"
ANALISTA_PASSWORD = "Usuario1"

EMPLEADO_CC       = "99887766"
EMPLEADO_EMAIL    = "camila.rios@yopmail.com"
EMPLEADO_PASSWORD = "Usuario1"

FECHA_INICIO_DIRECTO = "2026-04-25"


# ── helpers ──────────────────────────────────────────────────────────────────

def buscar_empleado_por_cc(page: Page, cc: str) -> int:
    """Busca un empleado por CC en /Empleado y retorna su id."""
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    page.fill("input[name=buscar]", cc)
    page.keyboard.press("Enter")
    page.wait_for_load_state("networkidle")
    fila = page.locator("table tbody tr").first
    enlace = fila.locator("a[href*='/Empleado/Perfil/']").first
    href = enlace.get_attribute("href")
    return int(href.split("/")[-1])


# ── TC-VIN-01 — Formulario muestra el selector TipoVinculacion preseleccionado ─
def test_tc_vin_01_formulario_muestra_selector_tipo_vinculacion(
    page: Page, reset_empleado_temporal
):
    """TC-VIN-01: /Empleado/Editar/{id} muestra <select id=TipoVinculacion> con 'Temporal'."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = buscar_empleado_por_cc(page, EMPLEADO_CC)

    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    selector = page.locator("#TipoVinculacion")
    expect(selector).to_be_visible()
    expect(selector).to_have_value("Temporal")


# ── TC-VIN-02 — Seleccionar Directo oculta la sección temporal ───────────────
def test_tc_vin_02_seleccionar_directo_oculta_seccion_temporal(
    page: Page, reset_empleado_temporal
):
    """TC-VIN-02: Al cambiar a Directo, #seccion-temporal se oculta (JS)."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = buscar_empleado_por_cc(page, EMPLEADO_CC)

    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    seccion = page.locator("#seccion-temporal")
    expect(seccion).to_be_visible()

    page.select_option("#TipoVinculacion", "Directo")
    expect(seccion).to_be_hidden()


# ── TC-VIN-03 — Seleccionar Temporal vuelve a mostrar la sección ─────────────
def test_tc_vin_03_seleccionar_temporal_muestra_seccion_temporal(
    page: Page, reset_empleado_temporal
):
    """TC-VIN-03: Después de Directo, volver a Temporal re-muestra #seccion-temporal."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = buscar_empleado_por_cc(page, EMPLEADO_CC)

    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Directo")
    seccion = page.locator("#seccion-temporal")
    expect(seccion).to_be_hidden()

    page.select_option("#TipoVinculacion", "Temporal")
    expect(seccion).to_be_visible()


# ── TC-VIN-04 — Flujo principal: cambio guardado correctamente ────────────────
def test_tc_vin_04_cambio_exitoso_temporal_a_directo(
    page: Page, reset_empleado_temporal
):
    """TC-VIN-04: Guardar Temporal→Directo redirige al perfil y muestra mensaje de éxito."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = buscar_empleado_por_cc(page, EMPLEADO_CC)

    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name$='FechaInicioContrato']", FECHA_INICIO_DIRECTO)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Empleado/Perfil/" in page.url

    # TempData["Exito"] renderizado como mensaje de éxito
    exito = page.locator(".alert--success, .alert-success, [class*='success']")
    expect(exito.first).to_be_visible()


# ── TC-VIN-05 — El perfil refleja Directo y oculta sección temporal ───────────
def test_tc_vin_05_perfil_muestra_tipo_directo(
    page: Page, reset_empleado_temporal
):
    """TC-VIN-05: Tras guardar, el perfil muestra 'Directo' y oculta sección 'Contrato temporal'."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = buscar_empleado_por_cc(page, EMPLEADO_CC)

    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")
    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name$='FechaInicioContrato']", FECHA_INICIO_DIRECTO)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Verificar que el perfil muestra "Directo"
    perfil_tipo = page.locator(".dl-value", has_text="Directo")
    expect(perfil_tipo.first).to_be_visible()

    # La sección "Contrato temporal" NO debe aparecer en el perfil
    badge_temporal = page.locator(".badge--temporal")
    expect(badge_temporal).to_be_hidden()


# ── TC-VIN-06 — FechaIngreso permanece sin cambios ───────────────────────────
def test_tc_vin_06_fecha_ingreso_no_cambia(
    page: Page, reset_empleado_temporal
):
    """TC-VIN-06: FechaIngreso (2025-07-01) no se modifica tras el cambio de vinculación."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = buscar_empleado_por_cc(page, EMPLEADO_CC)

    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")
    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name$='FechaInicioContrato']", FECHA_INICIO_DIRECTO)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Verificar FechaIngreso en el perfil (debe conservar 2025)
    perfil = page.locator(".dl-item", has_text="Fecha de ingreso")
    expect(perfil).to_contain_text("2025")


# ── TC-VIN-07 — Saldo de vacaciones = 0 inmediatamente después del cambio ────
def test_tc_vin_07_saldo_vacaciones_cero_post_cambio(
    page: Page, reset_empleado_temporal
):
    """TC-VIN-07: Con FechaInicioContrato = hoy, saldo de vacaciones muestra 0."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = buscar_empleado_por_cc(page, EMPLEADO_CC)

    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")
    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name$='FechaInicioContrato']", FECHA_INICIO_DIRECTO)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    page.goto(f"{BASE_URL}/Empleado/Perfil/{emp_id}?tab=datos")
    page.wait_for_load_state("networkidle")

    saldo = page.locator(".dl-item", has_text="Vacaciones disponibles")
    expect(saldo).to_contain_text("0")


# ── TC-VIN-08 — Solo Analista puede acceder a Editar ─────────────────────────
def test_tc_vin_08_operario_no_puede_editar(page: Page):
    """TC-VIN-08: Un usuario Operario intenta acceder a /Empleado/Editar y es denegado."""
    hacer_login_completo(page, EMPLEADO_EMAIL, EMPLEADO_PASSWORD)

    # Usamos id=1 (Carlos, Jefe) para confirmar que el acceso es denegado.
    # El servidor puede devolver 403 directamente; capturamos la excepción y
    # verificamos que la URL final refleja denegación o que la página no es el formulario.
    try:
        page.goto(f"{BASE_URL}/Empleado/Editar/1")
        page.wait_for_load_state("networkidle")
    except Exception:
        pass  # 403/ERR_HTTP_RESPONSE_CODE_FAILURE es también un resultado válido

    final_url = page.url
    assert "Acceso-Denegado" in final_url or "/Cuenta/IniciarSesion" in final_url or \
           "/Empleado/Editar/" not in final_url


# ── TC-VIN-09 — EmpresaTemporalId y FechaFinContrato quedan null ─────────────
def test_tc_vin_09_campos_temporales_quedan_nulos(
    page: Page, reset_empleado_temporal
):
    """TC-VIN-09: Tras guardar Directo, EmpresaTemporalId y FechaFinContrato = vacíos en el formulario."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = buscar_empleado_por_cc(page, EMPLEADO_CC)

    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")
    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name$='FechaInicioContrato']", FECHA_INICIO_DIRECTO)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Volver a abrir el formulario para verificar que los campos quedaron nulos
    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    expect(page.locator("#TipoVinculacion")).to_have_value("Directo")

    empresa_select = page.locator("select[name$='EmpresaTemporalId']")
    expect(empresa_select).to_have_value("")

    fecha_fin = page.locator("input[name$='FechaFinContrato']")
    expect(fecha_fin).to_have_value("")
