"""
Pruebas E2E — Modal de Desvinculación de Empleado
Rol ejecutor : Lissy (DirectorTecnico) — único rol que puede desvincular.
Empleado obj.: Creado con cédula 99000001 antes de cada test, eliminado al finalizar.
"""

import subprocess
import tempfile
import os
import pytest
from playwright.sync_api import Page, expect

from helpers import hacer_login_completo, BASE_URL

# ── Credenciales del ejecutor ──────────────────────────────────────────────────
ADMIN_EMAIL    = "lissy.g@yopmail.com"
ADMIN_PASSWORD = "Usuario1"

# Cédula única para el empleado de prueba (no debe existir en datos reales)
CC_PRUEBA = "99000001"


# ── Helpers de BD ─────────────────────────────────────────────────────────────

def _run_sql(sql: str) -> None:
    sql_file = os.path.join(tempfile.gettempdir(), "desv_test.sql")
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
        raise RuntimeError(f"SQL falló: {result.stderr}")


def _get_empleado_id() -> int | None:
    """Devuelve el Id del empleado de prueba, o None si no existe."""
    result = subprocess.run(
        [
            "powershell", "-Command",
            (
                "Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
                f"-Database 'GestionPersonal' "
                f"-Query \"SELECT Id FROM dbo.Empleados WHERE Cedula = N'{CC_PRUEBA}'\" "
                "| Select-Object -ExpandProperty Id"
            ),
        ],
        capture_output=True, text=True, timeout=15,
    )
    txt = result.stdout.strip()
    return int(txt) if txt.isdigit() else None


_SQL_CREAR = f"""
DECLARE @SedeId  INT = (SELECT TOP 1 Id FROM dbo.Sedes  WHERE Estado = N'Activa');
DECLARE @CargoId INT = (SELECT TOP 1 Id FROM dbo.Cargos WHERE Estado = N'Activo');

IF NOT EXISTS (SELECT 1 FROM dbo.Empleados WHERE Cedula = N'{CC_PRUEBA}')
BEGIN
    INSERT INTO dbo.Empleados (NombreCompleto, Cedula, SedeId, CargoId, UsuarioId,
                                TipoVinculacion, FechaIngreso, FechaInicioContrato,
                                Estado, FechaCreacion)
    VALUES (
        N'Empleado Prueba Desvinculacion', N'{CC_PRUEBA}',
        @SedeId, @CargoId, NULL,
        N'Directo', '2024-01-01', '2024-01-01',
        N'Activo', GETDATE()
    );
END
"""

_SQL_LIMPIAR = f"""
DECLARE @EmpId INT = (SELECT Id FROM dbo.Empleados WHERE Cedula = N'{CC_PRUEBA}');

IF @EmpId IS NOT NULL
BEGIN
    DELETE FROM dbo.HistorialDesvinculaciones WHERE EmpleadoId = @EmpId;
    DELETE FROM dbo.EventosLaborales          WHERE EmpleadoId = @EmpId;
    DELETE FROM dbo.Empleados                 WHERE Id         = @EmpId;
END
"""

_SQL_RESTAURAR_ACTIVO = f"""
UPDATE dbo.Empleados SET Estado = N'Activo' WHERE Cedula = N'{CC_PRUEBA}';
"""


# ── Fixture ────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def empleado_prueba():
    """Crea el empleado antes del test y lo elimina después."""
    _run_sql(_SQL_LIMPIAR)   # limpiar si quedó de una ejecución anterior
    _run_sql(_SQL_CREAR)
    yield
    _run_sql(_SQL_LIMPIAR)


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_desv_01_boton_abre_modal(page: Page):
    """TC-DESV-01: El botón 'Desvincular' en el perfil abre el modal."""
    hacer_login_completo(page, ADMIN_EMAIL, ADMIN_PASSWORD)

    emp_id = _get_empleado_id()
    assert emp_id, "El empleado de prueba no fue creado en la BD"

    page.goto(f"{BASE_URL}/Empleado/Perfil/{emp_id}")
    page.wait_for_load_state("networkidle")

    # El overlay del modal debe estar oculto al inicio
    modal = page.locator("#modal-desvincular")
    expect(modal).to_be_hidden()

    # Click en botón Desvincular
    page.locator("button[data-modal-open='modal-desvincular']").click()

    # El modal debe ser visible
    expect(modal).to_be_visible()
    expect(page.locator("#modal-desv-title")).to_have_text("Desvincular empleado")


def test_desv_02_cancelar_cierra_modal(page: Page):
    """TC-DESV-02: El botón 'Cancelar' cierra el modal sin cambiar el estado."""
    hacer_login_completo(page, ADMIN_EMAIL, ADMIN_PASSWORD)

    emp_id = _get_empleado_id()
    assert emp_id

    page.goto(f"{BASE_URL}/Empleado/Perfil/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.locator("button[data-modal-open='modal-desvincular']").click()
    expect(page.locator("#modal-desvincular")).to_be_visible()

    # Click Cancelar
    page.locator("#modal-desvincular button[data-modal-close]").first.click()

    expect(page.locator("#modal-desvincular")).to_be_hidden()

    # El empleado sigue Activo
    result = subprocess.run(
        [
            "powershell", "-Command",
            (
                "Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
                f"-Database 'GestionPersonal' "
                f"-Query \"SELECT Estado FROM dbo.Empleados WHERE Cedula = N'{CC_PRUEBA}'\" "
                "| Select-Object -ExpandProperty Estado"
            ),
        ],
        capture_output=True, text=True, timeout=15,
    )
    assert result.stdout.strip() == "Activo", "El empleado no debería haber cambiado de estado"


def test_desv_03_confirmacion_exitosa_redirige_a_lista(page: Page):
    """TC-DESV-03: Completar el formulario y confirmar → redirige a la lista de empleados."""
    hacer_login_completo(page, ADMIN_EMAIL, ADMIN_PASSWORD)

    emp_id = _get_empleado_id()
    assert emp_id

    page.goto(f"{BASE_URL}/Empleado/Perfil/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.locator("button[data-modal-open='modal-desvincular']").click()
    expect(page.locator("#modal-desvincular")).to_be_visible()

    # Llenar fecha y motivo
    page.fill("#desv-fecha", "2026-04-28")
    page.fill("#desv-motivo", "Renuncia voluntaria — test automatizado")

    # Confirmar
    page.locator("button[form='form-desvincular']").click()
    page.wait_for_load_state("networkidle")

    # Debe redirigir a /Empleado (lista)
    assert "/Empleado" in page.url and "/Perfil" not in page.url, \
        f"Se esperaba redirección a lista de empleados, URL actual: {page.url}"

    # Debe aparecer alerta de éxito
    expect(page.locator(".alert--success")).to_be_visible()


def test_desv_04_empleado_queda_inactivo_en_bd(page: Page):
    """TC-DESV-04: Después de confirmar la desvinculación el estado en BD es Inactivo."""
    hacer_login_completo(page, ADMIN_EMAIL, ADMIN_PASSWORD)

    emp_id = _get_empleado_id()
    assert emp_id

    page.goto(f"{BASE_URL}/Empleado/Perfil/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.locator("button[data-modal-open='modal-desvincular']").click()
    page.fill("#desv-fecha", "2026-04-28")
    page.fill("#desv-motivo", "Prueba de estado en BD")
    page.locator("button[form='form-desvincular']").click()
    page.wait_for_load_state("networkidle")

    result = subprocess.run(
        [
            "powershell", "-Command",
            (
                "Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
                f"-Database 'GestionPersonal' "
                f"-Query \"SELECT Estado FROM dbo.Empleados WHERE Cedula = N'{CC_PRUEBA}'\" "
                "| Select-Object -ExpandProperty Estado"
            ),
        ],
        capture_output=True, text=True, timeout=15,
    )
    assert result.stdout.strip() == "Inactivo", \
        f"Se esperaba 'Inactivo' en BD, se obtuvo: '{result.stdout.strip()}'"


def test_desv_05_historial_registrado_en_bd(page: Page):
    """TC-DESV-05: Después de confirmar queda un registro en HistorialDesvinculaciones."""
    hacer_login_completo(page, ADMIN_EMAIL, ADMIN_PASSWORD)

    emp_id = _get_empleado_id()
    assert emp_id

    page.goto(f"{BASE_URL}/Empleado/Perfil/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.locator("button[data-modal-open='modal-desvincular']").click()
    page.fill("#desv-fecha", "2026-04-28")
    page.fill("#desv-motivo", "Verificación de historial")
    page.locator("button[form='form-desvincular']").click()
    page.wait_for_load_state("networkidle")

    result = subprocess.run(
        [
            "powershell", "-Command",
            (
                "Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
                f"-Database 'GestionPersonal' "
                f"-Query \"SELECT COUNT(*) AS N FROM dbo.HistorialDesvinculaciones WHERE EmpleadoId = {emp_id}\" "
                "| Select-Object -ExpandProperty N"
            ),
        ],
        capture_output=True, text=True, timeout=15,
    )
    count = int(result.stdout.strip() or "0")
    assert count >= 1, f"Se esperaba al menos 1 registro en historial, se encontraron {count}"


def test_desv_06_sin_motivo_no_procesa(page: Page):
    """TC-DESV-06: Enviar sin motivo → servidor valida, muestra error en perfil y empleado sigue Activo."""
    hacer_login_completo(page, ADMIN_EMAIL, ADMIN_PASSWORD)

    emp_id = _get_empleado_id()
    assert emp_id

    page.goto(f"{BASE_URL}/Empleado/Perfil/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.locator("button[data-modal-open='modal-desvincular']").click()
    expect(page.locator("#modal-desvincular")).to_be_visible()

    # Dejar el motivo vacío, sólo llenar la fecha
    page.fill("#desv-fecha", "2026-04-28")
    page.fill("#desv-motivo", "")

    # Enviar (el formulario tiene novalidate → el servidor valida)
    page.locator("button[form='form-desvincular']").click()
    page.wait_for_load_state("networkidle")

    # Debe redirigir de vuelta al Perfil con alerta de error
    assert "/Empleado/Perfil" in page.url, \
        f"Se esperaba permanecer en Perfil, URL actual: {page.url}"

    # La alerta de error debe estar visible
    expect(page.locator(".alert--error, [class*=alert--error]")).to_be_visible()

    # El empleado debe seguir Activo en BD
    result = subprocess.run(
        [
            "powershell", "-Command",
            (
                "Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
                f"-Database 'GestionPersonal' "
                f"-Query \"SELECT Estado FROM dbo.Empleados WHERE Cedula = N'{CC_PRUEBA}'\" "
                "| Select-Object -ExpandProperty Estado"
            ),
        ],
        capture_output=True, text=True, timeout=15,
    )
    assert result.stdout.strip() == "Activo", \
        f"El empleado debería seguir Activo, se obtuvo: '{result.stdout.strip()}'"


def test_desv_07_perfil_muestra_inactivo_tras_desvinculacion(page: Page):
    """TC-DESV-07: Si se accede al perfil del empleado desvinculado, muestra badge Inactivo."""
    hacer_login_completo(page, ADMIN_EMAIL, ADMIN_PASSWORD)

    emp_id = _get_empleado_id()
    assert emp_id

    # Desvincular
    page.goto(f"{BASE_URL}/Empleado/Perfil/{emp_id}")
    page.wait_for_load_state("networkidle")
    page.locator("button[data-modal-open='modal-desvincular']").click()
    page.fill("#desv-fecha", "2026-04-28")
    page.fill("#desv-motivo", "Prueba badge inactivo")
    page.locator("button[form='form-desvincular']").click()
    page.wait_for_load_state("networkidle")

    # Volver al perfil
    page.goto(f"{BASE_URL}/Empleado/Perfil/{emp_id}")
    page.wait_for_load_state("networkidle")

    # Badge Inactivo visible y botón Desvincular ausente
    expect(page.locator(".badge--inactivo")).to_be_visible()
    expect(page.locator("button[data-modal-open='modal-desvincular']")).to_have_count(0)
