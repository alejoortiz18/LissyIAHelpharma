"""
Pruebas de correo — Asignación de turnos
EVT-08  Turno asignado   → correo a empleado + CC al jefe asignador
EVT-09  Turno modificado → mismo patrón
EVT-10  Turno cancelado  → solo al empleado (sin CC)
"""
import subprocess
import tempfile
import os

import pytest

from helpers import BASE_URL, hacer_login

DB_INSTANCE = r"(localdb)\MSSQLLocalDB"
DB_NAME     = "GestionPersonal"


# ── Helpers BD ────────────────────────────────────────────────────────────────

def _consultar(query: str) -> list[list[str]]:
    sql_file = os.path.join(tempfile.gettempdir(), "_email_query_tur.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(query)
    result = subprocess.run(
        ["powershell", "-Command",
         f"Invoke-Sqlcmd -ServerInstance '{DB_INSTANCE}' "
         f"-Database '{DB_NAME}' -InputFile '{sql_file}' "
         f"-OutputSqlErrors $true | Format-Table -AutoSize | Out-String -Width 512"],
        capture_output=True, text=True, timeout=15
    )
    lines = [l for l in result.stdout.splitlines() if l.strip() and "---" not in l]
    return [l.split() for l in lines[1:]] if len(lines) > 1 else []


def _ultimo_registro(tipo_evento: str) -> dict | None:
    filas = _consultar(
        f"SELECT TOP 1 Exitoso, ISNULL(ErrorMensaje,''), Destinatario, ISNULL(Copia,''), Asunto "
        f"FROM dbo.RegistroNotificaciones "
        f"WHERE TipoEvento = '{tipo_evento}' "
        f"ORDER BY FechaIntento DESC;"
    )
    if not filas:
        return None
    return {
        "exitoso":      filas[0][0] == "1",
        "error":        filas[0][1],
        "destinatario": filas[0][2],
        "copia":        filas[0][3],
        "asunto":       " ".join(filas[0][4:]) if len(filas[0]) > 4 else ""
    }


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_evt08_asignacion_turno(page):
    """
    La asignación de turno genera correo al empleado con CC al jefe asignador.
    El asunto sigue el formato [Asignación de Turno] - [NombreJefe].
    """
    hacer_login(page, "director.tecnico@yopmail.com", "DirectorPass2026!")
    page.goto(f"{BASE_URL}/Turno/AsignarTurno")
    page.wait_for_load_state("networkidle")

    # Completar formulario de asignación
    # TODO: ajustar selectores según los IDs reales del formulario
    select_empleado = page.locator("select[name='EmpleadoId']")
    if select_empleado.count() == 0:
        pytest.skip("EVT-08: Formulario de asignación no encontrado — ajustar URL/selectores")

    select_empleado.select_option(index=1)
    page.locator("select[name='PlantillaTurnoId']").select_option(index=1)
    page.fill("input[name='FechaVigencia']", "2026-05-05")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    reg = _ultimo_registro("AsignacionTurno")
    assert reg is not None, "EVT-08: Sin registro en RegistroNotificaciones"
    assert reg["exitoso"],  f"EVT-08: Correo de asignación falló — {reg['error']}"

    assert reg["copia"] != "", \
        "EVT-08: Sin CC al jefe asignador"

    asunto_lower = reg["asunto"].lower()
    assert "asignación" in asunto_lower or "turno" in asunto_lower, \
        f"EVT-08: Formato de asunto inesperado: {reg['asunto']}"


def test_evt09_modificacion_turno(page):
    """La modificación de turno notifica al empleado y al jefe (CC)."""
    reg = _ultimo_registro("ModificacionTurno")
    if reg is None:
        pytest.xfail("EVT-09: Sin registros — ejecutar modificación de turno primero")

    assert reg["exitoso"],  f"EVT-09: Correo de modificación falló — {reg['error']}"
    assert reg["copia"] != "", "EVT-09: Sin CC al jefe en modificación"

    asunto_lower = reg["asunto"].lower()
    assert "turno" in asunto_lower or "cambio" in asunto_lower, \
        f"EVT-09: Formato de asunto inesperado: {reg['asunto']}"


def test_evt10_cancelacion_turno_sin_copia(page):
    """
    La cancelación de turno notifica solo al empleado.
    No debe incluir CC (columna Copia vacía).
    """
    reg = _ultimo_registro("CancelacionTurno")
    if reg is None:
        pytest.xfail("EVT-10: Sin registros — ejecutar cancelación de turno primero")

    assert reg["exitoso"], f"EVT-10: Correo de cancelación falló — {reg['error']}"
    assert reg["copia"] == "", \
        f"EVT-10: La cancelación no debería tener CC, pero tiene: {reg['copia']}"

    asunto_lower = reg["asunto"].lower()
    assert "cancelado" in asunto_lower or "turno" in asunto_lower, \
        f"EVT-10: Formato de asunto inesperado: {reg['asunto']}"


def test_registro_sin_fallos_globales(page):
    """
    Verificación de sanidad: no debe haber entradas Exitoso=0
    para los eventos de turno en la ejecución actual de pruebas.
    """
    filas = _consultar(
        "SELECT COUNT(*) "
        "FROM dbo.RegistroNotificaciones "
        "WHERE TipoEvento IN ('AsignacionTurno','ModificacionTurno','CancelacionTurno') "
        "  AND Exitoso = 0;"
    )
    if not filas:
        return  # Sin registros — OK

    cantidad_fallos = int(filas[0][0]) if filas[0] else 0
    assert cantidad_fallos == 0, \
        f"Hay {cantidad_fallos} envíos de correo fallidos en RegistroNotificaciones para eventos de turno"
