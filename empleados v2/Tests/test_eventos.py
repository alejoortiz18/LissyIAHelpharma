"""
Pruebas funcionales — Módulo Eventos Laborales (Modal)
Sistema: GestiónRH — Administración de Empleados

TC-EV-01  Botón "Registrar evento" abre modal (NO navega a otra página)
TC-EV-02  Modal se cierra al pulsar Cancelar o X
TC-EV-03  Toggle tipo=Incapacidad muestra campos de incapacidad y oculta permiso
TC-EV-04  Toggle tipo=Permiso muestra campo descripción y oculta incapacidad
TC-EV-05  Toggle tipo=Vacaciones muestra widget de saldo (fetch AJAX)
TC-EV-06  Campo días solicitados se calcula automáticamente para vacaciones
TC-EV-07  Validación: enviar formulario vacío muestra toast de error
TC-EV-08  Modal Anular abre al clicar Anular en una fila activa
TC-EV-09  Anular sin motivo muestra toast de error
"""

import pytest
from helpers import BASE_URL, hacer_login

CORREO_JEFE = "carlos.rodriguez@yopmail.com"
PASSWORD = "Usuario1"

# Selector único para el botón que ABRE el modal (evita ambigüedad con #btn-guardar-evento)
BTN_ABRIR_MODAL = "button[data-modal-open='modal-nuevo-evento']"


def _ir_a_eventos(page):
    """Garantiza sesión limpia y carga EventoLaboral con el botón visible."""
    # 1. Cerrar cualquier sesión previa para garantizar estado limpio
    page.goto(f"{BASE_URL}/Cuenta/Logout")
    page.wait_for_load_state("networkidle")
    # 2. Login fresco
    hacer_login(page, CORREO_JEFE, PASSWORD)
    if "/Cuenta/CambiarPassword" in page.url:
        pytest.skip("Carlos redirigido a CambiarPassword — estado de BD inesperado.")
    # 3. Navegar directamente a EventoLaboral
    page.goto(f"{BASE_URL}/EventoLaboral")
    page.wait_for_load_state("networkidle")
    # 4. Confirmar que el botón de apertura de modal está visible antes de continuar
    page.wait_for_selector(BTN_ABRIR_MODAL, state="visible", timeout=10000)


@pytest.fixture(autouse=True)
def login_as_jefe(page):
    """Inicia sesión como Jefe antes de cada test de eventos."""
    _ir_a_eventos(page)


# ── TC-EV-01 ─────────────────────────────────────────────────────────────────
def test_tc_ev01_boton_abre_modal_no_navega(page):
    """El botón 'Registrar evento' debe abrir el modal en la misma página."""
    url_antes = page.url

    page.click(BTN_ABRIR_MODAL)
    page.wait_for_selector("#modal-nuevo-evento:not([hidden])", timeout=5000)

    assert page.url == url_antes, (
        f"TC-EV-01 FALLO: Navegó a {page.url} en lugar de abrir el modal."
    )
    assert page.is_visible("#modal-nuevo-evento"), (
        "TC-EV-01 FALLO: El modal no está visible."
    )
    print("\n  TC-EV-01 PASO - Modal abierto en la misma URL.")


# ── TC-EV-02 ─────────────────────────────────────────────────────────────────
def test_tc_ev02_modal_cierra_cancelar(page):
    """El botón Cancelar y la X deben cerrar el modal."""
    page.click(BTN_ABRIR_MODAL)
    page.wait_for_selector("#modal-nuevo-evento:not([hidden])", timeout=5000)

    # Cerrar con botón Cancelar
    page.click("#modal-nuevo-evento button:has-text('Cancelar')")
    page.wait_for_selector("#modal-nuevo-evento", state="hidden", timeout=5000)
    assert not page.is_visible("#modal-nuevo-evento"), (
        "TC-EV-02 FALLO: El modal no se cerró al pulsar Cancelar."
    )

    # Volver a abrir y cerrar con X
    page.click(BTN_ABRIR_MODAL)
    page.wait_for_selector("#modal-nuevo-evento", state="visible", timeout=5000)
    page.click("#modal-nuevo-evento .modal-close")
    page.wait_for_selector("#modal-nuevo-evento", state="hidden", timeout=5000)
    assert not page.is_visible("#modal-nuevo-evento"), (
        "TC-EV-02 FALLO: El modal no se cerró al pulsar la X."
    )
    print("\n  TC-EV-02 PASO - Modal se cierra con Cancelar y X.")


# ── TC-EV-03 ─────────────────────────────────────────────────────────────────
def test_tc_ev03_toggle_incapacidad(page):
    """Seleccionar tipo=Incapacidad muestra campos de incapacidad y oculta permiso."""
    page.click(BTN_ABRIR_MODAL)
    page.wait_for_selector("#modal-nuevo-evento:not([hidden])", timeout=5000)

    page.select_option("#ev-tipo", "Incapacidad")
    page.wait_for_timeout(300)

    assert page.is_visible("#campos-incapacidad"), (
        "TC-EV-03 FALLO: Los campos de incapacidad no son visibles."
    )
    assert not page.is_visible("#campos-permiso"), (
        "TC-EV-03 FALLO: Los campos de permiso están visibles cuando no deberían."
    )
    print("\n  TC-EV-03 PASO - Campos incapacidad visibles, permiso oculto.")


# ── TC-EV-04 ─────────────────────────────────────────────────────────────────
def test_tc_ev04_toggle_permiso(page):
    """Seleccionar tipo=Permiso muestra descripción y oculta incapacidad."""
    page.click(BTN_ABRIR_MODAL)
    page.wait_for_selector("#modal-nuevo-evento:not([hidden])", timeout=5000)

    page.select_option("#ev-tipo", "Permiso")
    page.wait_for_timeout(300)

    assert page.is_visible("#campos-permiso"), (
        "TC-EV-04 FALLO: Los campos de permiso no son visibles."
    )
    assert not page.is_visible("#campos-incapacidad"), (
        "TC-EV-04 FALLO: Los campos de incapacidad están visibles cuando no deberían."
    )
    print("\n  TC-EV-04 PASO - Campo permiso visible, incapacidad oculta.")


def _seleccionar_primer_empleado(page):
    """Escribe en el combobox, espera resultados y selecciona el primero."""
    page.fill("#ev-empleado-search", "ar")
    page.wait_for_timeout(500)  # esperar debounce + respuesta AJAX
    page.wait_for_selector("#ev-empleado-list [role='option']", timeout=8000)
    page.click("#ev-empleado-list [role='option']:first-child")
    empleado_id = page.input_value("#ev-empleado")
    if not empleado_id:
        pytest.skip("No hay empleados disponibles en el combobox.")
    return empleado_id


# ── TC-EV-05 ─────────────────────────────────────────────────────────────────
def test_tc_ev05_widget_vacaciones(page):
    """Seleccionar tipo=Vacaciones + empleado muestra el widget de saldo."""
    page.click(BTN_ABRIR_MODAL)
    page.wait_for_selector("#modal-nuevo-evento:not([hidden])", timeout=5000)

    _seleccionar_primer_empleado(page)
    page.select_option("#ev-tipo", "Vacaciones")

    page.wait_for_selector("#vac-balance-widget:not([hidden])", timeout=8000)

    assert page.is_visible("#vac-balance-widget"), (
        "TC-EV-05 FALLO: El widget de saldo de vacaciones no apareció."
    )
    saldo_text = page.inner_text("#vac-disponibles")
    assert "dias" in saldo_text.lower() or saldo_text != "—", (
        f"TC-EV-05 FALLO: El saldo disponible no se actualizó: '{saldo_text}'"
    )
    print(f"\n  TC-EV-05 PASO - Widget de saldo visible. Disponibles: {saldo_text}")


# ── TC-EV-06 ─────────────────────────────────────────────────────────────────
def test_tc_ev06_calculo_dias(page):
    """Los días solicitados se calculan automáticamente al ingresar fechas para vacaciones."""
    page.click(BTN_ABRIR_MODAL)
    page.wait_for_selector("#modal-nuevo-evento:not([hidden])", timeout=5000)

    _seleccionar_primer_empleado(page)
    page.select_option("#ev-tipo", "Vacaciones")
    page.wait_for_selector("#vac-balance-widget:not([hidden])", timeout=8000)

    page.fill("#ev-inicio", "2026-05-04")  # lunes
    page.fill("#ev-fin", "2026-05-08")     # viernes — 5 dias habiles (sin domingo)
    page.dispatch_event("#ev-fin", "change")
    page.wait_for_timeout(400)

    assert not page.is_hidden("#campo-dias"), (
        "TC-EV-06 FALLO: El campo de dias calculados no aparecio."
    )
    dias_val = page.input_value("#ev-dias-calc")
    assert "5" in dias_val, (
        f"TC-EV-06 FALLO: Se esperaban 5 dias habiles, se obtuvo: '{dias_val}'"
    )
    print(f"\n  TC-EV-06 PASO - Dias calculados: '{dias_val}'")


# ── TC-EV-07 ─────────────────────────────────────────────────────────────────
def test_tc_ev07_validacion_campos_vacios(page):
    """Enviar el formulario sin datos obligatorios muestra toast de error."""
    page.click(BTN_ABRIR_MODAL)
    page.wait_for_selector("#modal-nuevo-evento:not([hidden])", timeout=5000)

    page.click("#btn-guardar-evento")
    page.wait_for_timeout(600)

    assert page.is_visible("#modal-nuevo-evento"), (
        "TC-EV-07 FALLO: El modal se cerro con campos vacios."
    )
    toast = page.locator(".toast--error, .toast")
    assert toast.first.is_visible(), (
        "TC-EV-07 FALLO: No aparecio toast de error."
    )
    print("\n  TC-EV-07 PASO - Toast de error visible con campos vacios.")


# ── TC-EV-08 ─────────────────────────────────────────────────────────────────
def test_tc_ev08_modal_anular_abre(page):
    """El botón Anular en una fila activa abre el modal de anulación."""
    anular_btns = page.locator("button:has-text('Anular')")
    if anular_btns.count() == 0:
        pytest.skip("No hay eventos activos en la tabla para anular.")

    url_antes = page.url
    anular_btns.first.click()
    page.wait_for_selector("#modal-anular:not([hidden])", timeout=5000)

    assert page.url == url_antes, (
        f"TC-EV-08 FALLO: Navego a {page.url} en lugar de abrir modal de anulacion."
    )
    assert page.is_visible("#modal-anular"), (
        "TC-EV-08 FALLO: El modal de anulacion no esta visible."
    )
    print("\n  TC-EV-08 PASO - Modal de anulacion abierto.")


# ── TC-EV-09 ─────────────────────────────────────────────────────────────────
def test_tc_ev09_anular_sin_motivo_error(page):
    """Confirmar anulación sin motivo muestra toast de error."""
    anular_btns = page.locator("button:has-text('Anular')")
    if anular_btns.count() == 0:
        pytest.skip("No hay eventos activos para anular.")

    anular_btns.first.click()
    page.wait_for_selector("#modal-anular:not([hidden])", timeout=5000)

    page.fill("#motivo-anulacion", "")
    page.click("#btn-confirmar-anulacion")
    page.wait_for_timeout(600)

    assert page.is_visible("#modal-anular"), (
        "TC-EV-09 FALLO: El modal de anulacion se cerro sin motivo."
    )
    toast = page.locator(".toast--error, .toast")
    assert toast.first.is_visible(), (
        "TC-EV-09 FALLO: No aparecio toast de error al anular sin motivo."
    )
    print("\n  TC-EV-09 PASO - Toast de error al anular sin motivo.")
