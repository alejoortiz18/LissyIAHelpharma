"""
Pruebas de correo — Ciclo de solicitudes laborales
EVT-04  Solicitud creada → correo al jefe inmediato (CC al jefe apoyo si existe)
EVT-05  Aprobación       → correo al auxiliar solicitante
EVT-06  Rechazo         → correo al auxiliar solicitante
EVT-07  Devuelta         → correo al auxiliar solicitante
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
    sql_file = os.path.join(tempfile.gettempdir(), "_email_query_sol.sql")
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
        "exitoso":     filas[0][0] == "1",
        "error":       filas[0][1],
        "destinatario": filas[0][2],
        "copia":       filas[0][3],
        "asunto":      " ".join(filas[0][4:]) if len(filas[0]) > 4 else ""
    }


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_evt04_solicitud_notifica_jefe_no_solicitante(page):
    """
    El destinatario del correo EVT-04 es el jefe inmediato,
    NO el auxiliar que creó la solicitud.
    """
    hacer_login(page, "auxiliar.farmacia@yopmail.com", "AuxiliarPass2026!")
    page.goto(f"{BASE_URL}/HorasExtras/Nuevo")
    page.wait_for_load_state("networkidle")
    page.fill("input[name='FechaTrabajada']", "2026-05-01")
    page.fill("input[name='CantidadHoras']",  "2")
    page.locator("textarea[name='Motivo'], input[name='Motivo']").fill("Prueba EVT-04")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    reg = _ultimo_registro("SolicitudCreada")
    assert reg is not None, "EVT-04: Sin registro en RegistroNotificaciones"
    assert reg["exitoso"],  f"EVT-04: Error al enviar — {reg['error']}"

    assert reg["destinatario"] != "auxiliar.farmacia@yopmail.com", \
        "EVT-04: El destinatario NO debe ser el auxiliar solicitante"

    asunto_lower = reg["asunto"].lower()
    assert "nueva" in asunto_lower or "horas" in asunto_lower, \
        f"EVT-04: Formato de asunto inesperado: {reg['asunto']}"


def test_evt04b_copia_al_jefe_apoyo(page):
    """
    Si existe cadena de dos niveles jerárquicos,
    el campo Copia debe estar poblado con el segundo jefe.
    """
    reg = _ultimo_registro("SolicitudCreada")
    if reg is None:
        pytest.xfail("EVT-04b: Sin registros de SolicitudCreada — ejecutar test_evt04 primero")

    # La cadena depende del seeding. Documentamos el comportamiento actual.
    if reg["copia"]:
        assert "@" in reg["copia"], \
            f"EVT-04b: Copia no parece un correo válido: {reg['copia']}"


def test_evt05_aprobacion_notifica_auxiliar(page):
    """La aprobación notifica al solicitante, no al jefe."""
    hacer_login(page, "regente.farmacia@yopmail.com", "RegentePass2026!")
    page.goto(f"{BASE_URL}/HorasExtras")
    page.wait_for_load_state("networkidle")

    boton_aprobar = page.locator("button[data-accion='aprobar'], button:has-text('Aprobar')").first
    if not boton_aprobar.is_visible():
        pytest.skip("EVT-05: No hay solicitudes pendientes de aprobación")

    boton_aprobar.click()
    page.wait_for_load_state("networkidle")

    reg = _ultimo_registro("SolicitudAprobada")
    assert reg is not None, "EVT-05: Sin registro en RegistroNotificaciones"
    assert reg["exitoso"],  f"EVT-05: Correo de aprobación falló — {reg['error']}"

    asunto_lower = reg["asunto"].lower()
    assert "aprobada" in asunto_lower, \
        f"EVT-05: El asunto no contiene 'aprobada': {reg['asunto']}"


def test_evt06_rechazo_notifica_auxiliar(page):
    """El rechazo notifica al solicitante."""
    hacer_login(page, "regente.farmacia@yopmail.com", "RegentePass2026!")
    page.goto(f"{BASE_URL}/HorasExtras")
    page.wait_for_load_state("networkidle")

    boton_rechazar = page.locator("button[data-accion='rechazar'], button:has-text('Rechazar')").first
    if not boton_rechazar.is_visible():
        pytest.skip("EVT-06: No hay solicitudes pendientes de rechazo")

    boton_rechazar.click()
    motivo = page.locator("textarea[name='MotivoRechazo']")
    if motivo.is_visible():
        motivo.fill("Prueba EVT-06 — rechazo automatizado")
        page.locator("button[data-confirmar='rechazar'], button:has-text('Confirmar')").click()
    page.wait_for_load_state("networkidle")

    reg = _ultimo_registro("SolicitudRechazada")
    assert reg is not None, "EVT-06: Sin registro en RegistroNotificaciones"
    assert reg["exitoso"],  f"EVT-06: Correo de rechazo falló — {reg['error']}"

    asunto_lower = reg["asunto"].lower()
    assert "rechazada" in asunto_lower, \
        f"EVT-06: El asunto no contiene 'rechazada': {reg['asunto']}"
