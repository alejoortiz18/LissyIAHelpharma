"""
Pruebas funcionales — Página de Plantillas de Turno (/Turno)
Sistema: GestiónRH — Administración de Empleados

Cubre el bug de regresión: las tarjetas de plantilla mostraban "undefined 0 días laborales"
debido a que el JSON embebido en la página usaba PascalCase pero el JS esperaba camelCase.

TC-PT-01  Las tarjetas de plantilla no muestran "undefined" en el nombre
TC-PT-02  Las tarjetas de plantilla muestran al menos 1 día laboral (no "0 días laborales")
TC-PT-03  Crear una plantilla genera exactamente una tarjeta nueva con el nombre correcto
TC-PT-04  La tarjeta nueva no muestra "undefined" ni "0 días laborales"
TC-PT-05  El modal de detalle ("Ver plantilla") muestra el nombre correcto al hacer clic en la tarjeta
"""

import subprocess
import tempfile
import os
import time

import pytest
from helpers import BASE_URL, hacer_login

CORREO_JEFE = "carlos.rodriguez@yopmail.com"
PASSWORD    = "Usuario1"

# Nombre único para la plantilla de prueba (incluye timestamp para evitar colisiones)
_TS = str(int(time.time()))
NOMBRE_PLANTILLA_TEST = f"Turno Test Automatizado {_TS}"


# ── Fixture: limpieza de plantilla creada en tests ──────────────────────────

@pytest.fixture(scope="module", autouse=True)
def limpiar_plantilla_test():
    """Elimina la plantilla de prueba de la BD al terminar el módulo."""
    yield
    sql = (
        f"DELETE FROM dbo.PlantillasTurnoDetalle "
        f"WHERE PlantillaTurnoId = ("
        f"  SELECT Id FROM dbo.PlantillasTurno WHERE Nombre = '{NOMBRE_PLANTILLA_TEST}'"
        f"); "
        f"DELETE FROM dbo.PlantillasTurno WHERE Nombre = '{NOMBRE_PLANTILLA_TEST}';"
    )
    sql_file = os.path.join(tempfile.gettempdir(), "cleanup_plantilla_test.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    subprocess.run(
        [
            "powershell", "-Command",
            (
                f"Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
                f"-Database 'GestionPersonal' -InputFile '{sql_file}'"
            ),
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )


# ── Helper ───────────────────────────────────────────────────────────────────

def _ir_a_turnos(page):
    """Login como Jefe y navega a la página de Turnos."""
    page.goto(f"{BASE_URL}/Cuenta/Logout")
    page.wait_for_load_state("networkidle")
    hacer_login(page, CORREO_JEFE, PASSWORD)
    if "/Cuenta/CambiarPassword" in page.url:
        pytest.skip("Carlos redirigido a CambiarPassword — estado de BD inesperado.")
    page.goto(f"{BASE_URL}/Turno")
    page.wait_for_load_state("networkidle")
    # Espera a que el JS renderice las tarjetas
    page.wait_for_selector("#plantillas-grid", timeout=8_000)


# ── TC-PT-01 ─────────────────────────────────────────────────────────────────
def test_tc_pt01_tarjetas_no_muestran_undefined(page):
    """Ninguna tarjeta debe mostrar 'undefined' como nombre de plantilla."""
    _ir_a_turnos(page)

    titulos = page.locator("#plantillas-grid .card-title").all()
    if not titulos:
        pytest.skip("No hay plantillas en la BD — omitiendo TC-PT-01.")

    for titulo in titulos:
        texto = titulo.inner_text().strip()
        assert texto != "undefined", (
            f"TC-PT-01 FALLO: Una tarjeta muestra 'undefined' como nombre. "
            f"Texto encontrado: '{texto}'"
        )
        assert texto != "", (
            "TC-PT-01 FALLO: Una tarjeta muestra un nombre vacío."
        )


# ── TC-PT-02 ─────────────────────────────────────────────────────────────────
def test_tc_pt02_tarjetas_muestran_dias_laborales(page):
    """Ninguna tarjeta debe mostrar '0 días laborales' ni 'undefined días laborales'."""
    _ir_a_turnos(page)

    cuerpos = page.locator("#plantillas-grid .card-body p").all()
    if not cuerpos:
        pytest.skip("No hay plantillas en la BD — omitiendo TC-PT-02.")

    for cuerpo in cuerpos:
        texto = cuerpo.inner_text().strip().lower()
        assert "undefined" not in texto, (
            f"TC-PT-02 FALLO: Encontrado 'undefined' en descripción de tarjeta: '{texto}'"
        )
        assert not texto.startswith("0 días"), (
            f"TC-PT-02 FALLO: Tarjeta muestra '0 días laborales': '{texto}'"
        )


# ── TC-PT-03 ─────────────────────────────────────────────────────────────────
def test_tc_pt03_crear_plantilla_agrega_una_tarjeta(page):
    """Crear una plantilla genera exactamente una tarjeta nueva."""
    _ir_a_turnos(page)

    tarjetas_antes = page.locator("#plantillas-grid .card").count()

    # Abre modal
    page.click("#btn-nueva-plantilla")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)

    # Rellena nombre
    page.fill("#t-nombre", NOMBRE_PLANTILLA_TEST)

    # Activa Lunes y Viernes con horario
    page.check("#s-check-0")   # Lunes
    page.wait_for_selector("#s-times-0:not([hidden])", timeout=3_000)
    page.fill("#s-in-0", "08:00")
    page.fill("#s-out-0", "17:00")

    page.check("#s-check-4")   # Viernes
    page.wait_for_selector("#s-times-4:not([hidden])", timeout=3_000)
    page.fill("#s-in-4", "08:00")
    page.fill("#s-out-4", "17:00")

    # Guarda — espera la navegación que dispara window.location.reload()
    with page.expect_navigation(wait_until="networkidle", timeout=15_000):
        page.click("#btn-guardar-turno")

    # Espera a que el JS renderice las tarjetas tras el reload
    page.wait_for_selector("#plantillas-grid", timeout=8_000)

    # Espera a que la cantidad de tarjetas sea la esperada
    page.wait_for_function(
        f"document.querySelectorAll('#plantillas-grid .card').length >= {tarjetas_antes + 1}",
        timeout=8_000,
    )

    tarjetas_despues = page.locator("#plantillas-grid .card").count()
    assert tarjetas_despues == tarjetas_antes + 1, (
        f"TC-PT-03 FALLO: Se esperaba {tarjetas_antes + 1} tarjetas, "
        f"encontradas {tarjetas_despues}."
    )


# ── TC-PT-04 ─────────────────────────────────────────────────────────────────
def test_tc_pt04_nueva_tarjeta_sin_undefined(page):
    """La tarjeta de la plantilla recién creada no debe mostrar 'undefined' ni '0 días laborales'."""
    _ir_a_turnos(page)

    # Busca la tarjeta por nombre exacto
    tarjeta_titulo = page.locator(
        f"#plantillas-grid .card-title >> text={NOMBRE_PLANTILLA_TEST}"
    )

    if tarjeta_titulo.count() == 0:
        pytest.skip(
            f"TC-PT-04: La plantilla '{NOMBRE_PLANTILLA_TEST}' no existe aún — "
            "este test debe ejecutarse después de TC-PT-03."
        )

    # Verifica el nombre
    assert tarjeta_titulo.first.inner_text().strip() == NOMBRE_PLANTILLA_TEST, (
        "TC-PT-04 FALLO: El nombre de la tarjeta nueva no coincide."
    )

    # Verifica la descripción (días laborales)
    tarjeta = tarjeta_titulo.first.locator("xpath=ancestor::div[contains(@class,'card')]")
    desc = tarjeta.locator(".card-body p").first.inner_text().strip().lower()

    assert "undefined" not in desc, (
        f"TC-PT-04 FALLO: 'undefined' encontrado en descripción: '{desc}'"
    )
    assert not desc.startswith("0 días"), (
        f"TC-PT-04 FALLO: La tarjeta nueva muestra '0 días laborales': '{desc}'"
    )
    # Debe indicar los 2 días que se configuraron (Lunes + Viernes)
    assert desc.startswith("2 días"), (
        f"TC-PT-04 FALLO: Se esperaban 2 días laborales pero se obtuvo: '{desc}'"
    )


# ── TC-PT-05 ─────────────────────────────────────────────────────────────────
def test_tc_pt05_modal_ver_plantilla_muestra_nombre_correcto(page):
    """Al hacer clic en una tarjeta existente, el modal de detalle muestra el nombre correcto."""
    _ir_a_turnos(page)

    titulos = page.locator("#plantillas-grid .card-title").all()
    if not titulos:
        pytest.skip("No hay plantillas — omitiendo TC-PT-05.")

    # Toma el primer nombre visible (no "undefined")
    nombre_esperado = titulos[0].inner_text().strip()
    assert nombre_esperado != "undefined", (
        "TC-PT-05 PRECONDICIÓN: El nombre de la primera tarjeta es 'undefined' — "
        "fix no aplicado."
    )

    # Clic en la tarjeta (no en el botón Editar)
    titulos[0].click()
    page.wait_for_selector("#modal-ver-turno:not([hidden])", timeout=5_000)

    nombre_modal = page.locator("#ver-turno-title").inner_text().strip()
    assert nombre_modal == nombre_esperado, (
        f"TC-PT-05 FALLO: Modal muestra '{nombre_modal}', esperado '{nombre_esperado}'."
    )
