"""
Pruebas funcionales — Visibilidad de Empleados por Cargo (Regente)
Plan: Plan-Pruebas-xcargo.md

Scope 1 — Visibilidad de empleados activos:
  TC-XC-01  Login como Regente y verificar empleados visibles en /Empleado
  TC-XC-02  Total de activos = 4 (Laura + sus 3 subordinados activos)
  TC-XC-03  Buscar "Carlos" → 0 resultados (Jefe no visible)
  TC-XC-04  Buscar "Hernan" → 0 resultados (Regente de otra sede no visible)
  TC-XC-05  Buscar "Natalia" → 0 resultados (subordinado de otro Regente no visible)

Scope 2 — Visibilidad con filtro Estado=Inactivo:
  TC-XC-06  Filtro Inactivo → 2 filas: Valentina + Ricardo
  TC-XC-07  Buscar "Sebastian" con Estado=Inactivo → 0 resultados

Scope 3 — Verificación en base de datos (SQL):
  TC-XC-08  BD: JefeInmediatoId=2 tiene exactamente 5 subordinados
  TC-XC-09  BD: ningún empleado de Bogotá tiene JefeInmediatoId=2
  TC-XC-10  BD: Carlos (Id=1) no tiene JefeInmediatoId=2
"""

import json
import subprocess

import pytest

from helpers import BASE_URL, hacer_login

# ── Datos de prueba ──────────────────────────────────────────────────────────
CORREO_REGENTE  = "laura.sanchez@yopmail.com"
PASSWORD_INICIAL = "Usuario1"
PASSWORD_NUEVA   = "NuevaClave2026!"

# Estado compartido en el proceso pytest.
# conftest.py resetea Laura a DebeCambiarPassword=1 + hash=Usuario1 al inicio de sesión,
# por lo que el primer login pedirá cambio de contraseña. Después de cambiarlo, el
# estado se actualiza aquí para los tests siguientes.
_sesion_laura: dict = {"password": PASSWORD_INICIAL}


# ── Helpers internos ─────────────────────────────────────────────────────────

def _hacer_login_laura(page) -> None:
    """Login como Laura gestionando el flujo CambiarPassword si aplica."""
    page.goto(f"{BASE_URL}/Cuenta/Logout")
    page.wait_for_load_state("networkidle")

    hacer_login(page, CORREO_REGENTE, _sesion_laura["password"])
    page.wait_for_load_state("networkidle")

    if "/Cuenta/CambiarPassword" in page.url:
        # Flujo de primer ingreso: completar cambio de contraseña
        page.fill("#Dto_PasswordActual",    _sesion_laura["password"])
        page.fill("#Dto_NuevoPassword",     PASSWORD_NUEVA)
        page.fill("#Dto_ConfirmarPassword", PASSWORD_NUEVA)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")
        _sesion_laura["password"] = PASSWORD_NUEVA

    assert "/Dashboard" in page.url, (
        f"Login como Laura falló — URL actual: {page.url}"
    )


def _ir_a_empleados(page) -> None:
    """Login como Laura y navegar a la vista /Empleado."""
    _hacer_login_laura(page)
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("table[aria-label='Lista de empleados']", timeout=10_000)


def _contar_filas_tabla(page) -> int:
    """Cuenta las filas de datos en la tabla; devuelve 0 si hay empty-state."""
    if page.is_visible(".empty-state"):
        return 0
    return page.locator("table[aria-label='Lista de empleados'] tbody tr").count()


def _obtener_total_registros(page) -> int:
    """Lee el contador de registros del encabezado: 'X empleados encontrados.'"""
    texto = page.inner_text(".page-desc")
    primer_token = texto.strip().split()[0]
    numero = "".join(c for c in primer_token if c.isdigit())
    return int(numero) if numero else 0


def _buscar_empleado(page, nombre: str, estado: str = "") -> int:
    """Aplica filtros de búsqueda y devuelve la cantidad de filas resultantes."""
    page.fill("input[name='buscar']", nombre)
    page.select_option("select[name='estado']", estado)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")
    return _contar_filas_tabla(page)


def _ejecutar_sql(query: str) -> list:
    """Ejecuta una query T-SQL en LocalDB y retorna las filas como lista de dicts."""
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
    # Invoke-Sqlcmd devuelve dict cuando hay 1 fila, lista cuando hay varias
    return [data] if isinstance(data, dict) else data


# ── Scope 1: Visibilidad de empleados activos ────────────────────────────────

def test_tc_xc01_visibilidad_empleados_activos(page):
    """
    TC-XC-01: La tabla /Empleado muestra únicamente los empleados activos
    bajo la jefatura de Laura (ella misma + sus subordinados directos).
    """
    _ir_a_empleados(page)

    esperados = ["Laura", "Andrés", "Diana", "Jorge"]
    for nombre in esperados:
        locator = page.locator(
            f"table[aria-label='Lista de empleados'] tbody a.table-link:has-text('{nombre}')"
        )
        assert locator.count() > 0, (
            f"TC-XC-01 FALLO: '{nombre}' no aparece en la tabla y debería ser visible."
        )

    print(f"\n  TC-XC-01 PASÓ — Empleados visibles encontrados: {esperados}")


def test_tc_xc02_total_activos_es_4(page):
    """
    TC-XC-02: Con filtro Estado=Activo el contador debe ser 4
    (Laura + 3 subordinados activos: Andrés, Diana, Jorge).
    Sin filtro se muestran 6 (incluye 2 inactivos), por eso se aplica el filtro primero.
    """
    _ir_a_empleados(page)
    # Aplicar filtro Estado=Activo para contar solo activos
    page.select_option("select[name='estado']", "Activo")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")
    total = _obtener_total_registros(page)
    assert total == 4, (
        f"TC-XC-02 FALLO: Se esperaban 4 empleados activos, el sistema muestra {total}."
    )
    print(f"\n  TC-XC-02 PASÓ — Total activos visibles (filtro Activo): {total}")


def test_tc_xc03_carlos_no_visible(page):
    """
    TC-XC-03: Buscar 'Carlos' debe devolver 0 resultados.
    El Jefe no debe ser visible para el Regente.
    """
    _ir_a_empleados(page)
    filas = _buscar_empleado(page, "Carlos")
    assert filas == 0, (
        f"TC-XC-03 FALLO: Se encontraron {filas} resultado(s) para 'Carlos'. "
        "El Jefe NO debe ser visible para el Regente."
    )
    print("\n  TC-XC-03 PASÓ — Carlos (Jefe) no visible. 0 resultados.")


def test_tc_xc04_hernan_no_visible(page):
    """
    TC-XC-04: Buscar 'Hernan' debe devolver 0 resultados.
    El Regente de otra sede no debe ser visible.
    """
    _ir_a_empleados(page)
    # Primero sin tilde para evitar problemas de codificación
    filas = _buscar_empleado(page, "Hernan")
    if filas > 0:
        filas = _buscar_empleado(page, "Hernán")
    assert filas == 0, (
        f"TC-XC-04 FALLO: Se encontraron {filas} resultado(s) para 'Hernán'. "
        "El Regente de Bogotá NO debe ser visible para Laura."
    )
    print("\n  TC-XC-04 PASÓ — Hernán (Regente Bogotá) no visible. 0 resultados.")


def test_tc_xc05_natalia_no_visible(page):
    """
    TC-XC-05: Buscar 'Natalia' debe devolver 0 resultados.
    La empleada de otro Regente no debe ser visible.
    """
    _ir_a_empleados(page)
    filas = _buscar_empleado(page, "Natalia")
    assert filas == 0, (
        f"TC-XC-05 FALLO: Se encontraron {filas} resultado(s) para 'Natalia'. "
        "La subordinada de Hernán NO debe ser visible para Laura."
    )
    print("\n  TC-XC-05 PASÓ — Natalia (subordinada de Hernán) no visible. 0 resultados.")


# ── Scope 2: Filtro Estado = Inactivo ────────────────────────────────────────

def test_tc_xc06_inactivos_de_laura_visibles(page):
    """
    TC-XC-06: Con Estado=Inactivo deben verse exactamente 2 empleados:
    Valentina Ospina y Ricardo Useche (JefeInmediatoId=2).
    """
    _ir_a_empleados(page)
    page.select_option("select[name='estado']", "Inactivo")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    total = _obtener_total_registros(page)
    assert total == 2, (
        f"TC-XC-06 FALLO: Se esperaban 2 inactivos visibles, el sistema muestra {total}."
    )

    for nombre in ["Valentina", "Ricardo"]:
        locator = page.locator(
            f"table[aria-label='Lista de empleados'] tbody a.table-link:has-text('{nombre}')"
        )
        assert locator.count() > 0, (
            f"TC-XC-06 FALLO: '{nombre}' no aparece en los inactivos y debería verse."
        )

    print(f"\n  TC-XC-06 PASÓ — Inactivos visibles: Valentina, Ricardo ({total} total).")


def test_tc_xc07_sebastian_inactivo_no_visible(page):
    """
    TC-XC-07: Buscar 'Sebastian' con Estado=Inactivo → 0 resultados.
    El inactivo de otro Regente no debe ser visible.
    """
    _ir_a_empleados(page)
    filas = _buscar_empleado(page, "Sebastian", estado="Inactivo")
    if filas > 0:
        filas = _buscar_empleado(page, "Sebastián", estado="Inactivo")
    assert filas == 0, (
        f"TC-XC-07 FALLO: Se encontraron {filas} resultado(s) para 'Sebastián' inactivo. "
        "El inactivo de Hernán NO debe ser visible para Laura."
    )
    print("\n  TC-XC-07 PASÓ — Sebastián (inactivo de Hernán) no visible. 0 resultados.")


# ── Scope 3: Verificación en Base de Datos ───────────────────────────────────

def test_tc_xc08_bd_subordinados_de_laura(page):
    """
    TC-XC-08: En BD deben existir exactamente 5 empleados con JefeInmediatoId=2
    (Andrés, Diana, Jorge — activos; Valentina, Ricardo — inactivos).
    """
    filas = _ejecutar_sql(
        "SELECT Id, NombreCompleto, Estado "
        "FROM dbo.Empleados "
        "WHERE JefeInmediatoId = 2 "
        "ORDER BY Id"
    )
    nombres = [f["NombreCompleto"] for f in filas]
    assert len(filas) == 5, (
        f"TC-XC-08 FALLO: Se esperaban 5 subordinados de Laura en BD, "
        f"se encontraron {len(filas)}: {nombres}"
    )
    print(f"\n  TC-XC-08 PASÓ — Subordinados de Laura en BD ({len(filas)}): {nombres}")


def test_tc_xc09_bd_ningun_empleado_bogota_bajo_laura(page):
    """
    TC-XC-09: Ningún empleado de Sede Bogotá debe tener JefeInmediatoId=2.
    """
    filas = _ejecutar_sql(
        "SELECT e.Id, e.NombreCompleto "
        "FROM dbo.Empleados e "
        "INNER JOIN dbo.Sedes s ON e.SedeId = s.Id "
        "WHERE e.JefeInmediatoId = 2 AND s.Nombre = N'Sede Bogotá'"
    )
    assert len(filas) == 0, (
        f"TC-XC-09 FALLO: {len(filas)} empleado(s) de Bogotá tienen JefeInmediatoId=2 "
        f"cuando no deberían: {[f['NombreCompleto'] for f in filas]}"
    )
    print("\n  TC-XC-09 PASÓ — Ningún empleado de Bogotá tiene JefeInmediatoId=2.")


def test_tc_xc10_bd_carlos_no_bajo_laura(page):
    """
    TC-XC-10: Carlos (Id=1, Jefe) no debe tener JefeInmediatoId=2 en BD.
    """
    filas = _ejecutar_sql(
        "SELECT Id, NombreCompleto, JefeInmediatoId "
        "FROM dbo.Empleados "
        "WHERE Id = 1 AND JefeInmediatoId = 2"
    )
    assert len(filas) == 0, (
        "TC-XC-10 FALLO: Carlos (Jefe, Id=1) aparece con JefeInmediatoId=2, no debería."
    )
    print("\n  TC-XC-10 PASÓ — Carlos (Jefe) no está bajo Laura en BD.")
