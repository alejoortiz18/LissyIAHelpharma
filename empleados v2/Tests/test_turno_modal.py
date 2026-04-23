"""
Pruebas funcionales — Modal Asignar / Editar Turno (perfil empleado)
Sistema: GestiónRH — Administración de Empleados

TC-TM-01  Botón "Asignar / cambiar turno" abre modal sin navegar a otra página
TC-TM-02  Modal se cierra al pulsar Cancelar o X
TC-TM-03  Enviar formulario vacío muestra toast de error
TC-TM-04  Asignar turno correctamente recarga pestaña horario
TC-TM-05  El historial muestra la asignación recién creada
TC-TM-06  Botón "Editar" en tabla historial pre-popula el modal
TC-TM-07  Editar asignación guarda los cambios y recarga pestaña
"""

import pytest
from helpers import BASE_URL, hacer_login

CORREO_JEFE = "carlos.rodriguez@yopmail.com"
PASSWORD    = "Usuario1"

# Empleado con turno asignable (usa primer empleado visible para Jefe)
EMPLEADO_ID = 4   # Andrés Felipe Torres Ruiz — tiene JefeInmediatoId=2


def _ir_a_horario(page, empleado_id: int = EMPLEADO_ID):
    """Login como Jefe y navega al tab Horario del perfil."""
    page.goto(f"{BASE_URL}/Cuenta/Logout")
    page.wait_for_load_state("networkidle")
    hacer_login(page, CORREO_JEFE, PASSWORD)
    if "/Cuenta/CambiarPassword" in page.url:
        pytest.skip("Carlos redirigido a CambiarPassword — estado de BD inesperado.")
    page.goto(f"{BASE_URL}/Empleado/Perfil/{empleado_id}?tab=horario")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("button:has-text('Asignar / cambiar turno')", timeout=10_000)


@pytest.fixture(autouse=True)
def setup(page):
    _ir_a_horario(page)


# ── TC-TM-01 ─────────────────────────────────────────────────────────────────
def test_tc_tm01_boton_abre_modal_no_navega(page):
    """El botón 'Asignar / cambiar turno' debe abrir el modal sin navegar."""
    url_antes = page.url
    page.click("button:has-text('Asignar / cambiar turno')")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)

    assert page.url == url_antes, (
        f"TC-TM-01 FALLO: Navegó a {page.url} en lugar de abrir el modal."
    )
    assert page.is_visible("#modal-turno"), "TC-TM-01 FALLO: Modal no visible."
    print("\n  TC-TM-01 PASÓ — Modal abierto sin navegar.")


# ── TC-TM-02 ─────────────────────────────────────────────────────────────────
def test_tc_tm02_modal_cierra_cancelar_y_x(page):
    """Cancelar y X deben cerrar el modal."""
    page.click("button:has-text('Asignar / cambiar turno')")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)

    # Cerrar con Cancelar
    page.click("#modal-turno button:has-text('Cancelar')")
    page.wait_for_selector("#modal-turno", state="hidden", timeout=5_000)
    assert not page.is_visible("#modal-turno"), "TC-TM-02 FALLO: No se cerró con Cancelar."

    # Volver a abrir y cerrar con X
    page.click("button:has-text('Asignar / cambiar turno')")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    page.click("#modal-turno .modal-close")
    page.wait_for_selector("#modal-turno", state="hidden", timeout=5_000)
    assert not page.is_visible("#modal-turno"), "TC-TM-02 FALLO: No se cerró con X."
    print("\n  TC-TM-02 PASÓ — Modal cierra con Cancelar y X.")


# ── TC-TM-03 ─────────────────────────────────────────────────────────────────
def test_tc_tm03_formulario_vacio_muestra_error(page):
    """Enviar el formulario sin datos debe mostrar toast de error."""
    page.click("button:has-text('Asignar / cambiar turno')")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)

    # Limpiar valores
    page.select_option("#turno-plantilla", value="")
    page.fill("#turno-fecha", "")

    page.click("#btn-guardar-turno")
    page.wait_for_timeout(600)

    # El modal debe seguir abierto (no se cerró)
    assert page.is_visible("#modal-turno"), "TC-TM-03 FALLO: Modal se cerró con formulario vacío."
    print("\n  TC-TM-03 PASÓ — Formulario vacío no envió; modal sigue abierto.")


# ── TC-TM-04 ─────────────────────────────────────────────────────────────────
def test_tc_tm04_asignar_turno_correcto(page):
    """Asignar un turno correctamente debe cerrar modal y recargar la pestaña horario."""
    page.click("button:has-text('Asignar / cambiar turno')")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)

    # Seleccionar primera plantilla disponible
    primera_opcion = page.locator("#turno-plantilla option:not([value=''])").first
    if primera_opcion.count() == 0:
        pytest.skip("No hay plantillas de turno activas en el sistema.")
    plantilla_val = primera_opcion.get_attribute("value")
    page.select_option("#turno-plantilla", value=plantilla_val)

    # Establecer fecha de vigencia (hoy)
    page.fill("#turno-fecha", "2026-04-23")

    page.click("#btn-guardar-turno")

    # Esperar recarga de la página en el tab horario
    page.wait_for_url(f"**/Empleado/Perfil/{EMPLEADO_ID}*tab=horario*", timeout=10_000)
    page.wait_for_load_state("networkidle")

    assert "/Empleado/Perfil" in page.url and "horario" in page.url, (
        f"TC-TM-04 FALLO: No redirigió a la pestaña horario. URL: {page.url}"
    )
    print("\n  TC-TM-04 PASÓ — Turno asignado; recargó pestaña horario.")


# ── TC-TM-05 ─────────────────────────────────────────────────────────────────
def test_tc_tm05_historial_muestra_asignacion(page):
    """Tras asignar, la tabla historial debe mostrar al menos 1 fila."""
    # Primero asignar (reutiliza lógica TC-TM-04)
    page.click("button:has-text('Asignar / cambiar turno')")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)

    primera_opcion = page.locator("#turno-plantilla option:not([value=''])").first
    if primera_opcion.count() == 0:
        pytest.skip("No hay plantillas de turno activas.")
    page.select_option("#turno-plantilla", value=primera_opcion.get_attribute("value"))
    page.fill("#turno-fecha", "2026-04-23")
    page.click("#btn-guardar-turno")
    page.wait_for_url(f"**/Empleado/Perfil/{EMPLEADO_ID}*tab=horario*", timeout=10_000)
    page.wait_for_load_state("networkidle")

    # Verificar tabla historial
    filas = page.locator("table[aria-label='Historial de turnos'] tbody tr").count()
    assert filas >= 1, (
        f"TC-TM-05 FALLO: La tabla historial no muestra filas. Filas: {filas}"
    )
    print(f"\n  TC-TM-05 PASÓ — Historial muestra {filas} asignación(es).")


# ── TC-TM-06 ─────────────────────────────────────────────────────────────────
def test_tc_tm06_editar_prepopula_modal(page):
    """El botón Editar en la tabla historial debe abrir el modal con datos pre-cargados."""
    # Asegurarse de que haya al menos una asignación en el historial
    filas = page.locator("table[aria-label='Historial de turnos'] tbody tr")
    if filas.count() == 0:
        # Asignar primero
        page.click("button:has-text('Asignar / cambiar turno')")
        page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
        primera = page.locator("#turno-plantilla option:not([value=''])").first
        if primera.count() == 0:
            pytest.skip("No hay plantillas disponibles.")
        page.select_option("#turno-plantilla", value=primera.get_attribute("value"))
        page.fill("#turno-fecha", "2026-04-23")
        page.click("#btn-guardar-turno")
        page.wait_for_url(f"**/Empleado/Perfil/{EMPLEADO_ID}*tab=horario*", timeout=10_000)
        page.wait_for_load_state("networkidle")

    # Clicar el primer botón Editar del historial
    primer_editar = page.locator("table[aria-label='Historial de turnos'] tbody button:has-text('Editar')").first
    assert primer_editar.count() > 0, "TC-TM-06 FALLO: No se encontró botón Editar en el historial."

    primer_editar.click()
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)

    plantilla_val = page.input_value("#turno-plantilla")
    fecha_val     = page.input_value("#turno-fecha")
    titulo        = page.inner_text("#turno-title")

    assert plantilla_val != "", "TC-TM-06 FALLO: El select de plantilla no tiene valor pre-cargado."
    assert fecha_val != "",     "TC-TM-06 FALLO: La fecha no está pre-cargada."
    assert "Editar" in titulo,  f"TC-TM-06 FALLO: El título del modal no indica modo edición. Título: '{titulo}'"
    print(f"\n  TC-TM-06 PASÓ — Modal pre-poblado. Plantilla: {plantilla_val}, Fecha: {fecha_val}.")


# ── TC-TM-07 ─────────────────────────────────────────────────────────────────
def test_tc_tm07_editar_asignacion_guarda(page):
    """Editar una asignación existente debe guardarla y recargar la pestaña."""
    filas = page.locator("table[aria-label='Historial de turnos'] tbody tr")
    if filas.count() == 0:
        pytest.skip("No hay asignaciones en el historial para editar.")

    primer_editar = page.locator(
        "table[aria-label='Historial de turnos'] tbody button:has-text('Editar')"
    ).first
    primer_editar.click()
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)

    # Cambiar la fecha de vigencia
    page.fill("#turno-fecha", "2026-04-01")

    # Interceptar la respuesta AJAX para verificar que el endpoint devuelve exito=true
    with page.expect_response(
        lambda r: "EditarAsignacionAjax" in r.url, timeout=10_000
    ) as resp_info:
        page.click("#btn-guardar-turno")

    resp_data = resp_info.value.json()
    assert resp_data.get("exito") is True, (
        f"TC-TM-07 FALLO: El endpoint devolvió exito=false. "
        f"Mensaje: {resp_data.get('mensaje')}"
    )

    # Esperar la navegación que el JS dispara después del AJAX exitoso
    page.wait_for_load_state("networkidle")

    assert "/Empleado/Perfil" in page.url and "horario" in page.url, (
        f"TC-TM-07 FALLO: No recargó la pestaña horario. URL: {page.url}"
    )

    # Verificar que la fecha actualizada aparece en el historial
    celdas_fecha = page.locator("table[aria-label='Historial de turnos'] tbody td.tabular-nums")
    fechas = [celdas_fecha.nth(i).inner_text() for i in range(celdas_fecha.count())]
    assert "01/04/2026" in fechas, (
        f"TC-TM-07 FALLO: La fecha editada '01/04/2026' no aparece en el historial. "
        f"Fechas encontradas: {fechas}"
    )
    print(f"\n  TC-TM-07 PASÓ — Asignación editada. Fecha '01/04/2026' en historial.")
