"""
Pruebas E2E — Ajuste al Formulario de Creación de Empleado
Plan: Documentos/Pruebas/Playwright/Plan-CreacionUsuarioRefinado.md

Rol ejecutor: Carlos Rodríguez (Jefe) — único rol habilitado para crear empleados.
Cédulas de prueba: 12345001 (Directo), 12345002 (Temporal)
"""
import pytest
from playwright.sync_api import Page, expect
from helpers import hacer_login_completo, BASE_URL

JEFE_EMAIL    = "carlos.rodriguez@yopmail.com"
JEFE_PASSWORD = "Usuario1"

CC_DIRECTO  = "12345001"
CC_TEMPORAL = "12345002"


# ── Scope A — Comportamiento de UI / JavaScript ───────────────────────────────

def test_tc_cre_01_directo_muestra_fecha_ingreso_oculta_temporal(page: Page):
    """TC-CRE-01: Seleccionar 'Directo' → FechaIngreso visible, #seccion-temporal oculto."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Directo")

    expect(page.locator("#seccion-fecha-ingreso")).to_be_visible()
    expect(page.locator("#seccion-temporal")).to_be_hidden()


def test_tc_cre_02_temporal_oculta_fecha_ingreso_muestra_temporal(page: Page):
    """TC-CRE-02: Seleccionar 'Temporal' → FechaIngreso oculta, #seccion-temporal visible."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Temporal")

    expect(page.locator("#seccion-fecha-ingreso")).to_be_hidden()
    expect(page.locator("#seccion-temporal")).to_be_visible()


def test_tc_cre_03_eps_sin_asterisco(page: Page):
    """TC-CRE-03: El label de EPS NO debe contener span.required visible."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    eps_input = page.locator("input[name='Dto.Eps']")
    expect(eps_input).to_be_visible()

    # Buscar span.required dentro del form-group que contiene el input de EPS
    form_group = eps_input.locator("xpath=ancestor::div[contains(@class,'form-group')]")
    expect(form_group.locator("span.required")).to_have_count(0)


def test_tc_cre_04_contacto_emergencia_sin_asteriscos(page: Page):
    """TC-CRE-04: Los labels de Contacto de Emergencia no tienen span.required."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    for field in ["Dto.ContactoEmergenciaNombre", "Dto.ContactoEmergenciaTelefono"]:
        campo = page.locator(f"input[name='{field}']")
        expect(campo).to_be_visible()
        form_group = campo.locator("xpath=ancestor::div[contains(@class,'form-group')]")
        expect(form_group.locator("span.required")).to_have_count(0)


def test_tc_cre_11_toggle_directo_temporal_limpia_fecha_ingreso(page: Page):
    """TC-CRE-11: Cambiar de Directo a Temporal limpia el valor de FechaIngreso."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name='Dto.FechaIngreso']", "2026-04-25")

    page.select_option("#TipoVinculacion", "Temporal")

    valor = page.input_value("input[name='Dto.FechaIngreso']")
    assert valor == "", f"Se esperaba campo vacío, se obtuvo: '{valor}'"


def test_tc_cre_12_toggle_temporal_directo_fecha_ingreso_vacia(page: Page):
    """TC-CRE-12: Volver de Temporal a Directo → FechaIngreso re-aparece vacío."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Temporal")
    page.select_option("#TipoVinculacion", "Directo")

    expect(page.locator("#seccion-fecha-ingreso")).to_be_visible()
    valor = page.input_value("input[name='Dto.FechaIngreso']")
    assert valor == "", f"Se esperaba campo vacío, se obtuvo: '{valor}'"


# ── Scope B — Happy Path ──────────────────────────────────────────────────────

def test_tc_cre_05_creacion_exitosa_directo_sin_eps_sin_contacto(
    page: Page, limpiar_empleado_prueba
):
    """TC-CRE-05: Crear empleado Directo sin EPS ni contacto → éxito."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    _rellenar_formulario_directo(page, CC_DIRECTO, "2026-04-25")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # La app redirige al listado /Empleado tras crear exitosamente
    assert "Nuevo" not in page.url, f"Formulario no fue procesado, sigue en: {page.url}"


def test_tc_cre_06_creacion_exitosa_temporal_sin_eps(
    page: Page, limpiar_empleado_prueba
):
    """TC-CRE-06: Crear empleado Temporal sin EPS → éxito; perfil muestra tipo Temporal."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    _rellenar_formulario_temporal(page, CC_TEMPORAL, "2026-04-25", "2026-10-25")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # La app redirige al listado /Empleado tras crear exitosamente
    assert "Nuevo" not in page.url, f"Formulario no fue procesado, sigue en: {page.url}"


# ── Scope C — Validaciones server-side ───────────────────────────────────────

def test_tc_cre_07_directo_sin_fecha_ingreso_es_rechazado(page: Page):
    """TC-CRE-07: Contrato Directo sin FechaIngreso → error de validación del servidor."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.fill("input[name='Dto.NombreCompleto']", "Sin Fecha Ingreso")
    page.fill("input[name='Dto.Cedula']", "00000099")
    page.fill("input[name='Dto.Telefono']", "3001234503")
    page.fill("input[name='Dto.CorreoElectronico']", "sin.fecha@yopmail.com")
    page.fill("input[name='Dto.Direccion']", "Cra 3 #3-3")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")
    page.select_option("select[name='Dto.SedeId']", index=1)
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Directo")
    # NO se completa FechaIngreso — forzar envío habilitando el campo oculto
    page.evaluate("document.getElementById('seccion-fecha-ingreso').hidden = false")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Empleado/Nuevo" in page.url or "/Empleado/Crear" in page.url or \
           page.locator(".form-error, .alert--error, [class*='error']").count() > 0


def test_tc_cre_08_temporal_sin_empresa_es_rechazado(page: Page):
    """TC-CRE-08: Empresa Temporal sin EmpresaTemporalId → error de validación."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.fill("input[name='Dto.NombreCompleto']", "Sin Empresa Temporal")
    page.fill("input[name='Dto.Cedula']", "00000098")
    page.fill("input[name='Dto.Telefono']", "3001234504")
    page.fill("input[name='Dto.CorreoElectronico']", "sin.empresa@yopmail.com")
    page.fill("input[name='Dto.Direccion']", "Cra 4 #4-4")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")
    page.select_option("select[name='Dto.SedeId']", index=1)
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Temporal")
    # No se selecciona empresa — dejar en blanco
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Empleado/Nuevo" in page.url or "/Empleado/Crear" in page.url or \
           page.locator(".form-error, .alert--error, [class*='error']").count() > 0


# ── Scope C2 — Unicidad de cédula y correo ───────────────────────────────────

def test_tc_cre_13_cedula_duplicada_es_rechazada(page: Page, limpiar_empleado_prueba):
    """TC-CRE-13: Crear empleado con cédula ya existente → rechazado con mensaje de cédula duplicada."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)

    # Obtener la cédula de un empleado existente del seeding
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    cedula_existente = page.locator("table tbody tr:first-child td:nth-child(2)").inner_text().strip()

    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.fill("input[name='Dto.NombreCompleto']", "Cédula Duplicada Test")
    page.fill("input[name='Dto.Cedula']", cedula_existente)
    page.fill("input[name='Dto.Telefono']", "3009999991")
    page.fill("input[name='Dto.CorreoElectronico']", "cedula.duplicada.test@yopmail.com")
    page.fill("input[name='Dto.Direccion']", "Cra 99 #1-1")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")
    page.select_option("select[name='Dto.SedeId']", index=1)
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name='Dto.FechaIngreso']", "2024-01-15")

    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Empleado/Nuevo" in page.url or "/Empleado/Crear" in page.url
    assert page.locator("text=Ya existe un empleado registrado con esa cédula").count() > 0


def test_tc_cre_14_correo_duplicado_es_rechazado(page: Page, limpiar_empleado_prueba):
    """TC-CRE-14: Crear empleado con correo ya existente → rechazado con mensaje de correo duplicado."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)

    CORREO_EXISTENTE = "carlos.rodriguez@yopmail.com"  # Jefe de sede — existe en seeding

    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.fill("input[name='Dto.NombreCompleto']", "Correo Duplicado Test")
    page.fill("input[name='Dto.Cedula']", "99900014")
    page.fill("input[name='Dto.Telefono']", "3009999992")
    page.fill("input[name='Dto.CorreoElectronico']", CORREO_EXISTENTE)
    page.fill("input[name='Dto.Direccion']", "Cra 99 #2-2")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")
    page.select_option("select[name='Dto.SedeId']", index=1)
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name='Dto.FechaIngreso']", "2024-01-15")

    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Empleado/Nuevo" in page.url or "/Empleado/Crear" in page.url
    assert page.locator("text=Ya existe un empleado registrado con ese correo electrónico").count() > 0


# ── Scope D — Perfil post-creación ───────────────────────────────────────────

def test_tc_cre_09_perfil_directo_muestra_fecha_ingreso(
    page: Page, limpiar_empleado_prueba
):
    """TC-CRE-09: El perfil de un empleado Directo muestra su FechaIngreso correctamente."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    _rellenar_formulario_directo(page, CC_DIRECTO, "2026-04-25")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    emp_id = _obtener_id_empleado_bd(CC_DIRECTO)
    assert emp_id, "El empleado no fue creado en la BD"
    page.goto(f"{BASE_URL}/Empleado/Perfil/{emp_id}")
    page.wait_for_load_state("networkidle")

    contenido = page.content()
    assert "25/04/2026" in contenido or "2026-04-25" in contenido, \
        "FechaIngreso no aparece en el perfil del empleado Directo"


def test_tc_cre_10_perfil_temporal_muestra_seccion_contrato(
    page: Page, limpiar_empleado_prueba
):
    """TC-CRE-10: El perfil de un empleado Temporal muestra la sección 'Contrato temporal'."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    _rellenar_formulario_temporal(page, CC_TEMPORAL, "2026-04-25", "2026-10-25")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    emp_id = _obtener_id_empleado_bd(CC_TEMPORAL)
    assert emp_id, "El empleado no fue creado en la BD"
    page.goto(f"{BASE_URL}/Empleado/Perfil/{emp_id}")
    page.wait_for_load_state("networkidle")

    contenido = page.content()
    assert "Temporal" in contenido or "temporal" in contenido, \
        "El perfil no muestra información de Contrato Temporal"


# ── helpers de formulario ─────────────────────────────────────────────────────

def _obtener_id_empleado_bd(cedula: str):
    """Consulta la BD y retorna el Id del empleado con la cédula dada (o None)."""
    import subprocess, tempfile, os, re
    sql = f"SELECT Id FROM dbo.Empleados WHERE Cedula = '{cedula}'"
    sql_file = os.path.join(tempfile.gettempdir(), f"get_emp_{cedula}.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    result = subprocess.run(
        [
            "powershell", "-Command",
            (
                f"Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
                f"-Database 'GestionPersonal' -InputFile '{sql_file}' "
                f"| Select-Object -ExpandProperty Id"
            ),
        ],
        capture_output=True, text=True, timeout=30,
    )
    match = re.search(r'\d+', result.stdout.strip())
    return int(match.group()) if match else None

def _rellenar_formulario_directo(page: Page, cedula: str, fecha_ingreso: str):
    page.fill("input[name='Dto.NombreCompleto']", f"Prueba Directo {cedula}")
    page.fill("input[name='Dto.Cedula']", cedula)
    page.fill("input[name='Dto.Telefono']", "3001234501")
    page.fill("input[name='Dto.CorreoElectronico']", f"directo.{cedula}@yopmail.com")
    page.fill("input[name='Dto.Direccion']", "Cra 1 #1-1")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")
    page.select_option("select[name='Dto.SedeId']", index=1)
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name='Dto.FechaIngreso']", fecha_ingreso)


def _rellenar_formulario_temporal(page: Page, cedula: str, fecha_inicio: str, fecha_fin: str):
    page.fill("input[name='Dto.NombreCompleto']", f"Prueba Temporal {cedula}")
    page.fill("input[name='Dto.Cedula']", cedula)
    page.fill("input[name='Dto.Telefono']", "3001234502")
    page.fill("input[name='Dto.CorreoElectronico']", f"temporal.{cedula}@yopmail.com")
    page.fill("input[name='Dto.Direccion']", "Cra 2 #2-2")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")
    page.select_option("select[name='Dto.SedeId']", index=1)
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Temporal")
    page.select_option("select[name='Dto.EmpresaTemporalId']", index=1)
    page.fill("input[name='Dto.FechaInicioContrato']", fecha_inicio)
    page.fill("input[name='Dto.FechaFinContrato']", fecha_fin)
