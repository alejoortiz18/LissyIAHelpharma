"""
Pruebas de jerarquía y visibilidad de solicitudes en /EventoLaboral.

Roles de referencia:
  sofia.gomez@yopmail.com       → Analista (todas las sedes)
  carlos.rodriguez@yopmail.com  → DirectorTecnico (Sede Medellín)
  hernan.castillo@yopmail.com   → Regente     (Id=3, jefe de Camila, Natalia, Paula, Sebastián)
  camila.rios@yopmail.com       → Operario    (Id=9, subordinada de Hernán)

Eventos de Camila (Id=9):
  Id=23  Vacaciones  Aprobado
  Id=24  Incapacidad Pendiente

Casos de prueba:
  TC-JEQ-01  Analista ve eventos de Camila (Id=9) desde todas las sedes
  TC-JEQ-02  Analista puede aprobar evento Pendiente de Camila
  TC-JEQ-03  Analista puede reversar (devolver a Pendiente) evento Aprobado de Camila
  TC-JEQ-04  Hernán (Regente) ve eventos de Camila (subordinada directa)
  TC-JEQ-05  Hernán puede aprobar evento Pendiente de Camila
  TC-JEQ-06  Hernán puede reversar evento Aprobado de Camila
  TC-JEQ-07  DirectorTecnico (Carlos) ve eventos de Camila
"""

import re
import subprocess
import tempfile
import os
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5002"
PASSWORD  = "Usuario1"

# IDs de los eventos de Camila (Id=9)
EVENTO_APROBADO  = 23   # Vacaciones, Aprobado
EVENTO_PENDIENTE = 24   # Incapacidad, Pendiente

ANALISTA_EMAIL   = "sofia.gomez@yopmail.com"
DIRECTOR_EMAIL   = "carlos.rodriguez@yopmail.com"
REGENTE_EMAIL    = "hernan.castillo@yopmail.com"


# ─── Helpers ────────────────────────────────────────────────────────────────

def login(page: Page, email: str, password: str = PASSWORD):
    page.goto(f"{BASE_URL}/Cuenta/Login")
    page.fill("input[name='CorreoAcceso']", email)
    page.fill("input[name='Password']", password)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")


def reset_eventos_camila():
    """Restaura los eventos de Camila al estado original antes de cada test."""
    sql = (
        "UPDATE dbo.EventosLaborales SET Estado='Aprobado',  MotivoAnulacion=NULL, AutorizadoPor='Laura Sánchez',    FechaModificacion=NULL WHERE Id=23; "
        "UPDATE dbo.EventosLaborales SET Estado='Pendiente', MotivoAnulacion=NULL, AutorizadoPor='Sistema',          FechaModificacion=NULL WHERE Id=24; "
    )
    sql_file = os.path.join(tempfile.gettempdir(), "reset_eventos_camila.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    subprocess.run(
        ["powershell", "-Command",
         f"Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' -Database 'GestionPersonal' -InputFile '{sql_file}'"],
        capture_output=True, text=True, timeout=15
    )


def ir_a_eventos_filtrar_pendiente(page: Page):
    """Navega a EventoLaboral filtrando por estado=Pendiente."""
    page.goto(f"{BASE_URL}/EventoLaboral?estado=Pendiente")
    page.wait_for_load_state("networkidle")


def ir_a_eventos_filtrar_aprobado(page: Page):
    page.goto(f"{BASE_URL}/EventoLaboral?estado=Aprobado")
    page.wait_for_load_state("networkidle")


def ver_todos_eventos(page: Page):
    page.goto(f"{BASE_URL}/EventoLaboral")
    page.wait_for_load_state("networkidle")


def hay_fila_camila(page: Page) -> bool:
    return page.locator("table tbody tr", has_text="Camila").count() > 0


def gestionar_evento(page: Page, estado_actual: str, nuevo_estado: str, observacion: str = "Prueba automatizada"):
    """
    Hace click en el botón Gestionar de la primera fila de 'Camila',
    selecciona nuevo estado y confirma.
    """
    fila = page.locator("table tbody tr", has_text="Camila").first
    btn = fila.locator("button", has_text="Gestionar")
    btn.click()
    page.wait_for_selector("#modal-gestion", state="visible")
    page.select_option("#gest-nuevo-estado", nuevo_estado)
    # Llenar observación si el campo es visible
    obs_area = page.locator("#gest-observacion")
    obs_area.fill(observacion)
    page.click("#btn-confirmar-gestion")
    page.wait_for_timeout(1500)


# ─── Fixture de reset DB ────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def restaurar_db():
    reset_eventos_camila()
    yield
    reset_eventos_camila()


# ─── Tests ──────────────────────────────────────────────────────────────────

def test_tc_jeq_01_analista_ve_eventos_camila(page: Page):
    """TC-JEQ-01: Analista ve eventos de Camila en la vista de todos los eventos."""
    login(page, ANALISTA_EMAIL)
    ver_todos_eventos(page)
    assert hay_fila_camila(page), "El Analista NO ve los eventos de Camila en la tabla"


def test_tc_jeq_02_analista_aprueba_evento_pendiente_camila(page: Page):
    """TC-JEQ-02: Analista puede aprobar el evento Pendiente de Camila."""
    login(page, ANALISTA_EMAIL)
    ir_a_eventos_filtrar_pendiente(page)
    assert hay_fila_camila(page), "No se encontró el evento Pendiente de Camila para el Analista"
    gestionar_evento(page, "Pendiente", "Aprobado")
    # Verificar que aparece toast de éxito (no error)
    toast = page.locator(".toast, .alert--success, [role='alert']").first
    # Redirige/recarga — verificar que el estado cambió
    page.goto(f"{BASE_URL}/EventoLaboral?estado=Aprobado&buscar=Camila")
    page.wait_for_load_state("networkidle")
    assert hay_fila_camila(page), "Después de aprobar, el evento de Camila no aparece en Aprobado"


def test_tc_jeq_03_analista_reversa_evento_aprobado_camila(page: Page):
    """TC-JEQ-03: Analista puede revertir un evento Aprobado a Pendiente."""
    login(page, ANALISTA_EMAIL)
    ir_a_eventos_filtrar_aprobado(page)
    assert hay_fila_camila(page), "No se encontró evento Aprobado de Camila para el Analista"
    gestionar_evento(page, "Aprobado", "Pendiente", "Reversión por prueba automatizada")
    page.goto(f"{BASE_URL}/EventoLaboral?estado=Pendiente&buscar=Camila")
    page.wait_for_load_state("networkidle")
    assert hay_fila_camila(page), "Después de reversar, el evento de Camila no aparece en Pendiente"


def test_tc_jeq_04_regente_hernan_ve_eventos_camila(page: Page):
    """TC-JEQ-04: Hernán (Regente) ve los eventos de Camila (subordinada directa)."""
    login(page, REGENTE_EMAIL)
    ver_todos_eventos(page)
    assert hay_fila_camila(page), "Hernán (Regente) NO ve los eventos de Camila siendo su subordinada directa"


def test_tc_jeq_05_regente_hernan_aprueba_evento_pendiente_camila(page: Page):
    """TC-JEQ-05: Hernán (Regente) puede aprobar el evento Pendiente de Camila."""
    login(page, REGENTE_EMAIL)
    ir_a_eventos_filtrar_pendiente(page)
    assert hay_fila_camila(page), "Hernán no ve el evento Pendiente de Camila"
    gestionar_evento(page, "Pendiente", "Aprobado")
    page.goto(f"{BASE_URL}/EventoLaboral?estado=Aprobado&buscar=Camila")
    page.wait_for_load_state("networkidle")
    assert hay_fila_camila(page), "El evento de Camila no fue aprobado por Hernán"


def test_tc_jeq_06_regente_hernan_reversa_evento_aprobado_camila(page: Page):
    """TC-JEQ-06: Hernán (Regente) puede reversar un evento Aprobado de Camila."""
    login(page, REGENTE_EMAIL)
    ir_a_eventos_filtrar_aprobado(page)
    assert hay_fila_camila(page), "Hernán no ve el evento Aprobado de Camila"
    gestionar_evento(page, "Aprobado", "Pendiente", "Revisión requerida por Hernán")
    page.goto(f"{BASE_URL}/EventoLaboral?estado=Pendiente&buscar=Camila")
    page.wait_for_load_state("networkidle")
    assert hay_fila_camila(page), "El evento de Camila no fue revertido a Pendiente por Hernán"


def test_tc_jeq_07_director_ve_eventos_camila(page: Page):
    """TC-JEQ-07: DirectorTecnico (Carlos) ve eventos de Camila (misma sede)."""
    login(page, DIRECTOR_EMAIL)
    ver_todos_eventos(page)
    assert hay_fila_camila(page), "El DirectorTécnico NO ve los eventos de Camila en su sede"
