"""
Pruebas E2E — Reglas de negocio de fechas por tipo de vinculación

Cobertura:
  TC-FEC-01: Crear empleado Temporal → actualizar a Directo, verificar BD
  TC-FEC-02: Crear empleado Directo con FechaInicioContrato, verificar BD
  TC-FEC-03: Validación integral en BD — regla de negocio para todos los empleados activos

Rol ejecutor: Sofía Gómez (Analista) — sofia.gomez@yopmail.com

Regla de negocio de fechas:
  - Directo  : FechaIngreso obligatoria, FechaInicioContrato obligatoria y >= FechaIngreso
  - Temporal : FechaIngreso obligatoria, FechaInicioContrato = NULL, EmpresaTemporalId obligatoria
"""

import json
import os
import subprocess
import tempfile

import pytest
from playwright.sync_api import Page, expect

from helpers import hacer_login_completo, BASE_URL

ANALISTA_EMAIL    = "sofia.gomez@yopmail.com"
ANALISTA_PASSWORD = "Usuario1"

# Cédulas únicas para los empleados creados en estas pruebas (no colisionan con el seeding)
CC_TEMPORAL_LUEGO_DIRECTO = "55512301"   # TC-FEC-01
CC_DIRECTO_NUEVO          = "55512302"   # TC-FEC-02

FECHA_INGRESO         = "2026-06-01"
FECHA_INICIO_CONTRATO = "2026-06-15"   # diferente de FechaIngreso a propósito
FECHA_FIN_CONTRATO    = "2027-06-01"

# Correos generados por los helpers de formulario
_CORREO_01 = f"fec.{CC_TEMPORAL_LUEGO_DIRECTO}@yopmail.com"
_CORREO_02 = f"fec.{CC_DIRECTO_NUEVO}@yopmail.com"


# ── utilidades SQL ─────────────────────────────────────────────────────────────

def _ejecutar_sql(query: str) -> list:
    """Ejecuta una SELECT T-SQL en LocalDB y retorna las filas como lista de dicts."""
    script = (
        f"Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
        f"-Database 'GestionPersonal' "
        f"-Query \"{query}\" "
        f"| ConvertTo-Json -Compress"
    )
    result = subprocess.run(
        ["powershell", "-Command", script],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        pytest.fail(f"Error al ejecutar SQL: {result.stderr}")
    output = result.stdout.strip()
    if not output or output.lower() == "null":
        return []
    data = json.loads(output)
    return [data] if isinstance(data, dict) else data


def _run_sql(sql: str) -> None:
    """Ejecuta un bloque SQL (sin resultado) contra LocalDB."""
    sql_file = os.path.join(tempfile.gettempdir(), "fec_cleanup.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    result = subprocess.run(
        [
            "powershell", "-Command",
            (
                f"Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
                f"-Database 'GestionPersonal' -InputFile '{sql_file}'"
            ),
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        pytest.fail(f"SQL falló: {result.stderr}")


def _datos_contrato(cedula: str) -> dict | None:
    """Retorna los campos de contrato de un empleado por cédula (o None si no existe)."""
    filas = _ejecutar_sql(
        f"SELECT TipoVinculacion, FechaIngreso, FechaInicioContrato, "
        f"EmpresaTemporalId, FechaFinContrato "
        f"FROM dbo.Empleados WHERE Cedula = '{cedula}'"
    )
    return filas[0] if filas else None


def _buscar_id_empleado(page: Page, cedula: str) -> int:
    """Busca un empleado por CC en /Empleado y retorna su Id."""
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    page.fill("input[name=buscar]", cedula)
    page.keyboard.press("Enter")
    page.wait_for_load_state("networkidle")
    enlace = (
        page.locator("table tbody tr")
        .first.locator("a[href*='/Empleado/Perfil/']")
        .first
    )
    href = enlace.get_attribute("href")
    return int(href.split("/")[-1])


# ── fixture de limpieza ────────────────────────────────────────────────────────

def _borrar_empleados_prueba() -> None:
    cedulas = f"'{CC_TEMPORAL_LUEGO_DIRECTO}', '{CC_DIRECTO_NUEVO}'"
    correos = f"'{_CORREO_01}', '{_CORREO_02}'"
    sql = (
        # 1. Contactos de emergencia (FK → Empleados)
        f"DELETE ce FROM dbo.ContactosEmergencia ce "
        f"INNER JOIN dbo.Empleados e ON ce.EmpleadoId = e.Id "
        f"WHERE e.Cedula IN ({cedulas}); "
        # 2. Romper FK Empleados.UsuarioId antes de borrar Usuarios
        f"UPDATE dbo.Empleados SET UsuarioId = NULL WHERE Cedula IN ({cedulas}); "
        # 3. Borrar Empleados
        f"DELETE FROM dbo.Empleados WHERE Cedula IN ({cedulas}); "
        # 4. Borrar Usuarios (pueden quedar huérfanos si el paso anterior falló)
        f"DELETE FROM dbo.Usuarios WHERE CorreoAcceso IN ({correos});"
    )
    _run_sql(sql)


@pytest.fixture(autouse=True)
def limpiar_empleados_fec():
    """Elimina los empleados de prueba ANTES y DESPUÉS de cada test del módulo."""
    _borrar_empleados_prueba()
    yield
    _borrar_empleados_prueba()


# ── helpers de formulario ──────────────────────────────────────────────────────

def _crear_empleado_temporal(page: Page, cedula: str) -> None:
    """Rellena y envía el formulario Nuevo con tipo Temporal."""
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")
    page.fill("input[name='Dto.NombreCompleto']", f"Prueba Fec {cedula}")
    page.fill("input[name='Dto.Cedula']",          cedula)
    page.fill("input[name='Dto.Telefono']",         "3001239901")
    page.fill("input[name='Dto.CorreoElectronico']", f"fec.{cedula}@yopmail.com")
    page.fill("input[name='Dto.Direccion']",         "Cra 5 #5-5")
    page.fill("input[name='Dto.Ciudad']",            "Bogotá")
    page.fill("input[name='Dto.Departamento']",      "Cundinamarca")
    page.select_option("select[name='Dto.SedeId']",  index=1)
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']",     "Operario")
    page.select_option("#TipoVinculacion",           "Temporal")
    page.fill("input[name='Dto.FechaIngreso']",      FECHA_INGRESO)
    page.select_option("select[name='Dto.EmpresaTemporalId']", index=1)
    page.fill("input[name='Dto.FechaFinContrato']",  FECHA_FIN_CONTRATO)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


def _crear_empleado_directo(page: Page, cedula: str) -> None:
    """Rellena y envía el formulario Nuevo con tipo Directo."""
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")
    page.fill("input[name='Dto.NombreCompleto']", f"Prueba Fec {cedula}")
    page.fill("input[name='Dto.Cedula']",          cedula)
    page.fill("input[name='Dto.Telefono']",         "3001239902")
    page.fill("input[name='Dto.CorreoElectronico']", f"fec.{cedula}@yopmail.com")
    page.fill("input[name='Dto.Direccion']",         "Cra 6 #6-6")
    page.fill("input[name='Dto.Ciudad']",            "Medellín")
    page.fill("input[name='Dto.Departamento']",      "Antioquia")
    page.select_option("select[name='Dto.SedeId']",  index=1)
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']",     "Operario")
    page.select_option("#TipoVinculacion",           "Directo")
    page.fill("input[name='Dto.FechaIngreso']",      FECHA_INGRESO)
    page.fill("input[name='Dto.FechaInicioContrato']", FECHA_INICIO_CONTRATO)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


# ── TC-FEC-01: Crear Temporal → actualizar a Directo ──────────────────────────

def test_tc_fec_01_crear_temporal_actualizar_a_directo(page: Page):
    """
    TC-FEC-01: Crea un empleado Temporal (sin FechaInicioContrato),
    verifica en BD que FechaInicioContrato es NULL y EmpresaTemporalId está asignada,
    luego actualiza el empleado a Directo asignando FechaInicioContrato,
    y vuelve a verificar en BD que FechaInicioContrato quedó guardada y
    EmpresaTemporalId quedó en NULL.
    """
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)

    # ── Paso 1: Crear como Temporal ───────────────────────────────────────────
    _crear_empleado_temporal(page, CC_TEMPORAL_LUEGO_DIRECTO)
    assert "/Empleado" in page.url, (
        f"La creación Temporal no redirigió a /Empleado. URL actual: {page.url}"
    )

    # ── Paso 2: Verificar en BD — estado Temporal ─────────────────────────────
    datos_temporal = _datos_contrato(CC_TEMPORAL_LUEGO_DIRECTO)
    assert datos_temporal is not None, (
        f"El empleado CC={CC_TEMPORAL_LUEGO_DIRECTO} no fue encontrado en la BD tras la creación."
    )
    assert datos_temporal["TipoVinculacion"] == "Temporal", (
        f"TipoVinculacion esperado 'Temporal', obtenido: {datos_temporal['TipoVinculacion']}"
    )
    assert datos_temporal["FechaInicioContrato"] is None, (
        f"FechaInicioContrato debe ser NULL para Temporal, "
        f"pero fue: {datos_temporal['FechaInicioContrato']}"
    )
    assert datos_temporal["EmpresaTemporalId"] is not None, (
        "EmpresaTemporalId debe estar asignada para un empleado Temporal."
    )

    # ── Paso 3: Actualizar a Directo ──────────────────────────────────────────
    emp_id = _buscar_id_empleado(page, CC_TEMPORAL_LUEGO_DIRECTO)
    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Directo")
    # grupo-inicio-contrato debe aparecer al seleccionar Directo
    grupo_inicio = page.locator("#grupo-inicio-contrato")
    expect(grupo_inicio).to_be_visible()
    page.fill("input[name$='FechaInicioContrato']", FECHA_INICIO_CONTRATO)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Empleado/Perfil/" in page.url, (
        f"La actualización a Directo no redirigió al perfil. URL actual: {page.url}"
    )

    # ── Paso 4: Verificar en BD — estado Directo ──────────────────────────────
    datos_directo = _datos_contrato(CC_TEMPORAL_LUEGO_DIRECTO)
    assert datos_directo["TipoVinculacion"] == "Directo", (
        f"TipoVinculacion esperado 'Directo', obtenido: {datos_directo['TipoVinculacion']}"
    )
    assert datos_directo["FechaInicioContrato"] is not None, (
        "FechaInicioContrato debe ser NOT NULL para un empleado Directo."
    )
    assert datos_directo["EmpresaTemporalId"] is None, (
        f"EmpresaTemporalId debe ser NULL tras cambio a Directo, "
        f"pero fue: {datos_directo['EmpresaTemporalId']}"
    )
    assert datos_directo["FechaFinContrato"] is None, (
        "FechaFinContrato debe ser NULL para un empleado Directo."
    )


# ── TC-FEC-02: Crear empleado Directo ─────────────────────────────────────────

def test_tc_fec_02_crear_directo_con_fecha_inicio_contrato(page: Page):
    """
    TC-FEC-02: Crea un empleado con contrato Directo ingresando FechaIngreso
    y FechaInicioContrato por separado desde el formulario.
    Verifica en BD que ambas fechas quedaron guardadas y que
    EmpresaTemporalId y FechaFinContrato son NULL.
    """
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)

    # ── Paso 1: Verificar toggle JS de #grupo-inicio-contrato ─────────────────
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    grupo_inicio = page.locator("#grupo-inicio-contrato")

    # El formulario carga con TipoVinculacion = Directo (valor por defecto del enum)
    # por lo tanto el grupo-inicio-contrato debe estar VISIBLE al cargar
    expect(grupo_inicio).to_be_visible()

    # Al seleccionar Temporal, el grupo debe OCULTARSE
    page.select_option("#TipoVinculacion", "Temporal")
    expect(grupo_inicio).to_be_hidden()

    # Al volver a seleccionar Directo, el grupo debe MOSTRARSE
    page.select_option("#TipoVinculacion", "Directo")
    expect(grupo_inicio).to_be_visible()

    # ── Paso 2: Crear el empleado Directo ─────────────────────────────────────
    _crear_empleado_directo(page, CC_DIRECTO_NUEVO)
    assert "/Empleado" in page.url, (
        f"La creación Directo no redirigió a /Empleado. URL actual: {page.url}"
    )

    # ── Paso 3: Verificar en BD ───────────────────────────────────────────────
    datos = _datos_contrato(CC_DIRECTO_NUEVO)
    assert datos is not None, (
        f"El empleado CC={CC_DIRECTO_NUEVO} no fue encontrado en la BD tras la creación."
    )
    assert datos["TipoVinculacion"] == "Directo", (
        f"TipoVinculacion esperado 'Directo', obtenido: {datos['TipoVinculacion']}"
    )
    assert datos["FechaIngreso"] is not None, (
        "FechaIngreso debe ser NOT NULL para un empleado Directo."
    )
    assert datos["FechaInicioContrato"] is not None, (
        "FechaInicioContrato debe ser NOT NULL para un empleado Directo creado con ese campo."
    )
    assert datos["EmpresaTemporalId"] is None, (
        "EmpresaTemporalId debe ser NULL para un empleado Directo."
    )
    assert datos["FechaFinContrato"] is None, (
        "FechaFinContrato debe ser NULL para un empleado Directo."
    )


# ── TC-FEC-03: Validación integral en base de datos ───────────────────────────

def test_tc_fec_03_validacion_bd_regla_negocio_fechas():
    """
    TC-FEC-03: Consulta directamente la BD para verificar que todos los empleados
    activos cumplen la regla de negocio de fechas:
      - Directo  : FechaInicioContrato IS NOT NULL, EmpresaTemporalId IS NULL
      - Temporal : FechaInicioContrato IS NULL,     EmpresaTemporalId IS NOT NULL
    """
    # Excluir cédulas de prueba de otros archivos para evitar interferencias
    cedulas_excluidas = (
        "'12345001', '12345002', "
        f"'{CC_TEMPORAL_LUEGO_DIRECTO}', '{CC_DIRECTO_NUEVO}'"
    )

    # ── Caso A: Directo sin FechaInicioContrato (viola la regla) ──────────────
    violadores_directo = _ejecutar_sql(
        f"SELECT Cedula, TipoVinculacion, FechaInicioContrato "
        f"FROM dbo.Empleados "
        f"WHERE TipoVinculacion = 'Directo' "
        f"  AND FechaInicioContrato IS NULL "
        f"  AND Estado = 'Activo' "
        f"  AND Cedula NOT IN ({cedulas_excluidas})"
    )
    assert violadores_directo == [], (
        f"TC-FEC-03 FALLO: Empleados Directo sin FechaInicioContrato: {violadores_directo}"
    )

    # ── Caso B: Temporal con FechaInicioContrato (viola la regla) ─────────────
    violadores_temporal_inicio = _ejecutar_sql(
        f"SELECT Cedula, TipoVinculacion, FechaInicioContrato "
        f"FROM dbo.Empleados "
        f"WHERE TipoVinculacion = 'Temporal' "
        f"  AND FechaInicioContrato IS NOT NULL "
        f"  AND Estado = 'Activo' "
        f"  AND Cedula NOT IN ({cedulas_excluidas})"
    )
    assert violadores_temporal_inicio == [], (
        f"TC-FEC-03 FALLO: Empleados Temporal con FechaInicioContrato: "
        f"{violadores_temporal_inicio}"
    )

    # ── Caso C: Temporal sin EmpresaTemporalId (viola la regla) ───────────────
    violadores_temporal_empresa = _ejecutar_sql(
        f"SELECT Cedula, TipoVinculacion, EmpresaTemporalId "
        f"FROM dbo.Empleados "
        f"WHERE TipoVinculacion = 'Temporal' "
        f"  AND EmpresaTemporalId IS NULL "
        f"  AND Estado = 'Activo' "
        f"  AND Cedula NOT IN ({cedulas_excluidas})"
    )
    assert violadores_temporal_empresa == [], (
        f"TC-FEC-03 FALLO: Empleados Temporal sin EmpresaTemporalId: "
        f"{violadores_temporal_empresa}"
    )
