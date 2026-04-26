"""
Pruebas funcionales — Solicitud de Vacaciones con Balance y Días a Disfrutar
Sistema: GestiónRH — Administración de Empleados

TC-SOL-VAC-01  Modal usuario (Operario): al seleccionar Vacaciones aparece el widget de saldo
TC-SOL-VAC-02  Modal usuario: el campo "Días a disfrutar" es visible cuando tipo=Vacaciones
TC-SOL-VAC-03  Modal usuario: el campo "Días a disfrutar" se oculta al cambiar a otro tipo
TC-SOL-VAC-04  Modal usuario: validación — días a disfrutar requerido al enviar
TC-SOL-VAC-05  Modal usuario: validación — días no pueden superar el saldo disponible
TC-SOL-VAC-06  Modal usuario: envío exitoso de solicitud de vacaciones con días válidos
TC-SOL-VAC-07  Modal jefe (EventoLaboral): al seleccionar Vacaciones aparece campo días disfrutar
TC-SOL-VAC-08  Modal jefe: al seleccionar Vacaciones aparece sección Motivo y Observaciones
TC-SOL-VAC-09  Modal jefe: campo días se oculta al cambiar tipo de Vacaciones a Permiso
TC-SOL-VAC-10  Modal jefe: validación — días a disfrutar requerido al guardar vacaciones
TC-SOL-VAC-11  Modal jefe: validación — motivo obligatorio al guardar vacaciones
"""

import pytest
from datetime import date, timedelta
from helpers import BASE_URL, hacer_login, hacer_logout

CORREO_OPERARIO = "diana.vargas@yopmail.com"    # Rol=Operario, EmpleadoId=5
CORREO_JEFE     = "carlos.rodriguez@yopmail.com"  # Rol=Jefe
PASSWORD        = "Usuario1"

FECHA_INICIO = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
FECHA_FIN    = (date.today() + timedelta(days=10)).strftime("%Y-%m-%d")

BTN_ABRIR_MODAL_JEFE = "button[data-modal-open='modal-nuevo-evento']"


# ─── Helpers ────────────────────────────────────────────────────────────────

def _ir_a_solicitud(page):
    """Sesión limpia como Operario y navega a /Solicitud."""
    hacer_login(page, CORREO_OPERARIO, PASSWORD)
    if "/Cuenta/CambiarPassword" in page.url:
        pytest.skip("Diana redirigida a CambiarPassword — estado de BD inesperado.")
    page.goto(f"{BASE_URL}/Solicitud")
    page.wait_for_load_state("networkidle")


def _ir_a_eventos(page):
    """Sesión limpia como Jefe y navega a /EventoLaboral."""
    hacer_login(page, CORREO_JEFE, PASSWORD)
    if "/Cuenta/CambiarPassword" in page.url:
        pytest.skip("Carlos redirigido a CambiarPassword — estado de BD inesperado.")
    page.goto(f"{BASE_URL}/EventoLaboral")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector(BTN_ABRIR_MODAL_JEFE, state="visible", timeout=30000)


def _abrir_modal_solicitud(page):
    """Abre el modal de nueva solicitud en /Solicitud."""
    btn = page.locator("button[data-modal-open='modal-nueva-solicitud'], button:has-text('Nueva solicitud')")
    btn.first.click()
    page.wait_for_selector(
        "#modal-nueva-solicitud:not([hidden]), [id*='solicitud']:not([hidden])",
        timeout=5000
    )


def _abrir_modal_evento(page):
    """Abre el modal de nuevo evento en /EventoLaboral."""
    page.click(BTN_ABRIR_MODAL_JEFE)
    page.wait_for_selector("#modal-nuevo-evento:not([hidden])", timeout=5000)


def _seleccionar_primer_empleado(page):
    """Escribe en el combobox del modal jefe, espera y selecciona el primero."""
    page.fill("#ev-empleado-search", "ar")
    page.wait_for_timeout(600)
    page.wait_for_selector("#ev-empleado-list [role='option']", timeout=8000)
    page.click("#ev-empleado-list [role='option']:first-child")
    empleado_id = page.input_value("#ev-empleado")
    if not empleado_id:
        pytest.skip("No hay empleados disponibles en el combobox.")
    return empleado_id


# ─── Tests — Modal Operario (/Solicitud) ─────────────────────────────────────

def test_sol_vac01_widget_balance_visible_operario(page):
    """
    TC-SOL-VAC-01: Al seleccionar tipo=Vacaciones en el modal de Solicitud,
    debe aparecer el widget azul con los días acumulados, tomados y disponibles.
    """
    _ir_a_solicitud(page)
    _abrir_modal_solicitud(page)

    page.select_option("#sol-tipo", "Vacaciones")
    page.wait_for_timeout(800)  # AJAX + render

    widget = page.locator("#sol-vac-balance-widget, #vac-balance-widget")
    page.wait_for_selector(
        "#sol-vac-balance-widget:not([hidden]), #vac-balance-widget:not([hidden])",
        timeout=8000
    )
    assert widget.first.is_visible(), (
        "TC-SOL-VAC-01 FALLO: El widget de saldo de vacaciones no apareció en el modal de solicitud."
    )
    print("\n  ✅ TC-SOL-VAC-01 PASÓ — Widget de saldo visible en modal Operario.")


def test_sol_vac02_campo_dias_disfrutar_visible_operario(page):
    """
    TC-SOL-VAC-02: Al seleccionar tipo=Vacaciones, el campo "Días a disfrutar"
    debe hacerse visible en el modal de Solicitud.
    """
    _ir_a_solicitud(page)
    _abrir_modal_solicitud(page)

    page.select_option("#sol-tipo", "Vacaciones")
    page.wait_for_timeout(800)

    campo = page.locator("#sol-campo-dias-disfrutar, #campo-dias-disfrutar")
    assert campo.count() > 0, (
        "TC-SOL-VAC-02 FALLO: No se encontró el contenedor #sol-campo-dias-disfrutar."
    )
    assert campo.first.is_visible(), (
        "TC-SOL-VAC-02 FALLO: El campo 'Días a disfrutar' no es visible con tipo=Vacaciones."
    )
    input_dias = page.locator("#sol-dias-disfrutar, input[name='diasDisfrutar']")
    assert input_dias.count() > 0, (
        "TC-SOL-VAC-02 FALLO: No se encontró el input de días a disfrutar."
    )
    print("\n  ✅ TC-SOL-VAC-02 PASÓ — Campo días a disfrutar visible.")


def test_sol_vac03_campo_dias_oculto_otro_tipo(page):
    """
    TC-SOL-VAC-03: Al cambiar de tipo=Vacaciones a tipo=Permiso, el campo
    "Días a disfrutar" y el widget de balance deben ocultarse.
    """
    _ir_a_solicitud(page)
    _abrir_modal_solicitud(page)

    page.select_option("#sol-tipo", "Vacaciones")
    page.wait_for_timeout(800)

    # Cambiar a Permiso
    page.select_option("#sol-tipo", "Permiso")
    page.wait_for_timeout(500)

    campo = page.locator("#sol-campo-dias-disfrutar, #campo-dias-disfrutar")
    if campo.count() > 0:
        assert not campo.first.is_visible(), (
            "TC-SOL-VAC-03 FALLO: El campo días a disfrutar sigue visible con tipo=Permiso."
        )

    widget = page.locator("#sol-vac-balance-widget, #vac-balance-widget")
    if widget.count() > 0:
        assert not widget.first.is_visible(), (
            "TC-SOL-VAC-03 FALLO: El widget de saldo sigue visible con tipo=Permiso."
        )
    print("\n  ✅ TC-SOL-VAC-03 PASÓ — Campos de vacaciones ocultos al cambiar a Permiso.")


def test_sol_vac04_validacion_dias_requerido(page):
    """
    TC-SOL-VAC-04: Al enviar el modal con tipo=Vacaciones sin ingresar días,
    debe mostrarse un toast/mensaje de error y el modal debe permanecer abierto.
    """
    _ir_a_solicitud(page)
    _abrir_modal_solicitud(page)

    page.select_option("#sol-tipo", "Vacaciones")
    page.wait_for_timeout(800)

    page.fill("#sol-inicio, input[name='inicio']", FECHA_INICIO)
    page.fill("#sol-fin, input[name='fin']", FECHA_FIN)
    # No ingresa días a disfrutar

    page.click("#sol-submit")
    page.wait_for_timeout(600)

    # El modal debe seguir visible (e.preventDefault() se ejecutó)
    modal = page.locator("#modal-nueva-solicitud")
    assert modal.is_visible(), (
        "TC-SOL-VAC-04 FALLO: El modal se cerró a pesar de campos faltantes."
    )

    error_box = page.locator("#sol-error")
    assert error_box.is_visible(), (
        "TC-SOL-VAC-04 FALLO: No apareció mensaje de error al omitir días a disfrutar."
    )
    print("\n  ✅ TC-SOL-VAC-04 PASÓ — Validación de días requerido funciona.")


def test_sol_vac05_validacion_dias_no_exceden_saldo(page):
    """
    TC-SOL-VAC-05: Si se ingresan más días a disfrutar que el saldo disponible,
    debe aparecer un toast de error al intentar enviar.
    """
    _ir_a_solicitud(page)
    _abrir_modal_solicitud(page)

    page.select_option("#sol-tipo", "Vacaciones")
    page.wait_for_timeout(800)

    # Esperar que el widget esté visible (puede ser que saldo=0)
    try:
        page.wait_for_selector(
            "#sol-vac-balance-widget:not([hidden]), #vac-balance-widget:not([hidden])",
            timeout=6000
        )
    except Exception:
        pytest.skip("Widget de saldo no apareció — el empleado puede no tener saldo registrado.")

    page.fill("#sol-inicio, input[name='inicio']", FECHA_INICIO)
    page.fill("#sol-fin, input[name='fin']", FECHA_FIN)

    # Ingresar un número de días absurdamente alto
    input_dias = page.locator("#sol-dias-disfrutar, input[name='diasDisfrutar']")
    if input_dias.count() == 0 or not input_dias.first.is_visible():
        pytest.skip("Campo de días a disfrutar no visible — puede que saldo sea 0.")

    input_dias.first.fill("9999")

    page.click("#sol-submit")
    page.wait_for_timeout(600)

    error_box = page.locator("#sol-error")
    assert error_box.is_visible(), (
        "TC-SOL-VAC-05 FALLO: No apareció mensaje de error al superar el saldo."
    )
    msg = error_box.inner_text().lower()
    assert any(w in msg for w in ["saldo", "dias", "días", "disponible", "supera"]), (
        f"TC-SOL-VAC-05 FALLO: El mensaje no menciona el problema de saldo: '{msg}'"
    )
    print(f"\n  ✅ TC-SOL-VAC-05 PASÓ — Validación saldo excedido: '{msg}'")


def test_sol_vac06_envio_exitoso_vacaciones(page):
    """
    TC-SOL-VAC-06: Completar el formulario de vacaciones con datos válidos
    (dentro del saldo disponible) debe crear la solicitud y mostrar toast de éxito.
    """
    _ir_a_solicitud(page)
    _abrir_modal_solicitud(page)

    page.select_option("#sol-tipo", "Vacaciones")
    page.wait_for_timeout(800)

    try:
        page.wait_for_selector(
            "#sol-vac-balance-widget:not([hidden]), #vac-balance-widget:not([hidden])",
            timeout=6000
        )
    except Exception:
        pytest.skip("Widget de saldo no apareció — el empleado puede no tener saldo.")

    # Verificar saldo > 0
    saldo_el = page.locator("#sol-vac-disponibles")
    if saldo_el.count() > 0:
        saldo_txt = saldo_el.first.inner_text().strip()
        if saldo_txt.startswith("0"):
            pytest.skip("El empleado no tiene saldo disponible para solicitar vacaciones.")

    input_dias = page.locator("#sol-dias-disfrutar, input[name='diasDisfrutar']")
    if input_dias.count() == 0 or not input_dias.first.is_visible():
        pytest.skip("Campo días a disfrutar no visible — saldo podría ser 0.")

    page.fill("#sol-inicio, input[name='inicio']", FECHA_INICIO)
    page.fill("#sol-fin, input[name='fin']", FECHA_FIN)
    input_dias.first.fill("1")

    motivo_field = page.locator("#sol-descripcion")
    motivo_field.fill("Vacaciones de verano.")

    page.click("#sol-submit")
    page.wait_for_load_state("networkidle", timeout=10000)

    alert = page.locator(".alert--success")
    assert alert.first.is_visible(), (
        "TC-SOL-VAC-06 FALLO: No apareció mensaje de éxito tras enviar solicitud válida."
    )
    print("\n  ✅ TC-SOL-VAC-06 PASÓ — Solicitud de vacaciones enviada exitosamente.")


# ─── Tests — Modal Jefe (/EventoLaboral) ─────────────────────────────────────

def test_sol_vac07_campo_dias_disfrutar_visible_jefe(page):
    """
    TC-SOL-VAC-07: En el modal de EventoLaboral, al seleccionar tipo=Vacaciones
    y un empleado, debe aparecer el campo "Días a disfrutar".
    """
    _ir_a_eventos(page)
    _abrir_modal_evento(page)

    _seleccionar_primer_empleado(page)
    page.select_option("#ev-tipo", "Vacaciones")
    page.wait_for_timeout(800)

    page.wait_for_selector("#vac-balance-widget:not([hidden])", timeout=8000)

    campo = page.locator("#ev-campo-dias-disfrutar")
    assert campo.count() > 0, (
        "TC-SOL-VAC-07 FALLO: No existe el elemento #ev-campo-dias-disfrutar."
    )
    assert campo.first.is_visible(), (
        "TC-SOL-VAC-07 FALLO: El campo días a disfrutar no es visible con tipo=Vacaciones."
    )
    input_dias = page.locator("#ev-dias-disfrutar")
    assert input_dias.count() > 0 and input_dias.first.is_visible(), (
        "TC-SOL-VAC-07 FALLO: Input #ev-dias-disfrutar no visible."
    )
    print("\n  ✅ TC-SOL-VAC-07 PASÓ — Campo días a disfrutar visible en modal Jefe.")


def test_sol_vac08_campos_motivo_observaciones_visible_jefe(page):
    """
    TC-SOL-VAC-08: En el modal de EventoLaboral con tipo=Vacaciones,
    deben ser visibles los campos Motivo y Observaciones.
    """
    _ir_a_eventos(page)
    _abrir_modal_evento(page)

    _seleccionar_primer_empleado(page)
    page.select_option("#ev-tipo", "Vacaciones")
    page.wait_for_timeout(800)

    page.wait_for_selector("#vac-balance-widget:not([hidden])", timeout=8000)

    seccion = page.locator("#campos-vacaciones-descripcion")
    assert seccion.count() > 0, (
        "TC-SOL-VAC-08 FALLO: No existe #campos-vacaciones-descripcion."
    )
    assert seccion.first.is_visible(), (
        "TC-SOL-VAC-08 FALLO: La sección de Motivo/Observaciones no es visible."
    )
    motivo = page.locator("#ev-vac-motivo")
    assert motivo.count() > 0 and motivo.first.is_visible(), (
        "TC-SOL-VAC-08 FALLO: El textarea de Motivo (#ev-vac-motivo) no es visible."
    )
    obs = page.locator("#ev-vac-observaciones")
    assert obs.count() > 0 and obs.first.is_visible(), (
        "TC-SOL-VAC-08 FALLO: El textarea de Observaciones (#ev-vac-observaciones) no es visible."
    )
    print("\n  ✅ TC-SOL-VAC-08 PASÓ — Motivo y Observaciones visibles en modal Jefe.")


def test_sol_vac09_campos_vacaciones_ocultos_al_cambiar_tipo_jefe(page):
    """
    TC-SOL-VAC-09: Al cambiar el tipo de Vacaciones a Permiso en el modal Jefe,
    el campo días disfrutar y la sección Motivo/Observaciones deben ocultarse.
    """
    _ir_a_eventos(page)
    _abrir_modal_evento(page)

    _seleccionar_primer_empleado(page)
    page.select_option("#ev-tipo", "Vacaciones")
    page.wait_for_timeout(800)
    page.wait_for_selector("#vac-balance-widget:not([hidden])", timeout=8000)

    # Cambiar a Permiso
    page.select_option("#ev-tipo", "Permiso")
    page.wait_for_timeout(500)

    campo_dias = page.locator("#ev-campo-dias-disfrutar")
    if campo_dias.count() > 0:
        assert not campo_dias.first.is_visible(), (
            "TC-SOL-VAC-09 FALLO: #ev-campo-dias-disfrutar sigue visible con tipo=Permiso."
        )
    seccion = page.locator("#campos-vacaciones-descripcion")
    if seccion.count() > 0:
        assert not seccion.first.is_visible(), (
            "TC-SOL-VAC-09 FALLO: #campos-vacaciones-descripcion sigue visible con tipo=Permiso."
        )
    assert page.is_visible("#campos-permiso"), (
        "TC-SOL-VAC-09 FALLO: Los campos de Permiso no aparecieron."
    )
    print("\n  ✅ TC-SOL-VAC-09 PASÓ — Sección vacaciones oculta al cambiar a Permiso.")


def test_sol_vac10_validacion_dias_disfrutar_requerido_jefe(page):
    """
    TC-SOL-VAC-10: Al guardar vacaciones en el modal Jefe sin ingresar días a disfrutar,
    debe aparecer un toast de error.
    """
    _ir_a_eventos(page)
    _abrir_modal_evento(page)

    _seleccionar_primer_empleado(page)
    page.select_option("#ev-tipo", "Vacaciones")
    page.wait_for_timeout(800)
    page.wait_for_selector("#vac-balance-widget:not([hidden])", timeout=8000)

    page.fill("#ev-inicio", FECHA_INICIO)
    page.fill("#ev-fin", FECHA_FIN)
    page.fill("#ev-autorizante", "Supervisor Test")
    # NO ingresar días a disfrutar

    page.click("#btn-guardar-evento")
    page.wait_for_timeout(600)

    assert page.is_visible("#modal-nuevo-evento"), (
        "TC-SOL-VAC-10 FALLO: El modal se cerró con días vacíos."
    )
    toast = page.locator(".toast--error, .toast")
    assert toast.first.is_visible(), (
        "TC-SOL-VAC-10 FALLO: No apareció toast de error al omitir días a disfrutar."
    )
    msg = toast.first.inner_text().lower()
    assert any(w in msg for w in ["dias", "días", "disfrutar"]), (
        f"TC-SOL-VAC-10 FALLO: El toast no menciona días a disfrutar: '{msg}'"
    )
    print(f"\n  ✅ TC-SOL-VAC-10 PASÓ — Validación días requerido: '{msg}'")


def test_sol_vac11_validacion_motivo_requerido_jefe(page):
    """
    TC-SOL-VAC-11: Al guardar vacaciones en el modal Jefe sin ingresar motivo,
    debe aparecer un toast de error mencionando el motivo.
    """
    _ir_a_eventos(page)
    _abrir_modal_evento(page)

    _seleccionar_primer_empleado(page)
    page.select_option("#ev-tipo", "Vacaciones")
    page.wait_for_timeout(800)

    try:
        page.wait_for_selector("#ev-campo-dias-disfrutar:not([hidden])", timeout=6000)
    except Exception:
        pytest.skip("Campo días a disfrutar no apareció — saldo puede ser 0.")

    page.fill("#ev-inicio", FECHA_INICIO)
    page.fill("#ev-fin", FECHA_FIN)
    page.fill("#ev-autorizante", "Supervisor Test")
    page.fill("#ev-dias-disfrutar", "1")
    # NO ingresar motivo

    page.click("#btn-guardar-evento")
    page.wait_for_timeout(600)

    assert page.is_visible("#modal-nuevo-evento"), (
        "TC-SOL-VAC-11 FALLO: El modal se cerró sin ingresar motivo."
    )
    toast = page.locator(".toast--error, .toast")
    assert toast.first.is_visible(), (
        "TC-SOL-VAC-11 FALLO: No apareció toast de error al omitir el motivo."
    )
    msg = toast.first.inner_text().lower()
    assert any(w in msg for w in ["motivo", "obligatorio"]), (
        f"TC-SOL-VAC-11 FALLO: El toast no menciona el motivo: '{msg}'"
    )
    print(f"\n  ✅ TC-SOL-VAC-11 PASÓ — Validación motivo obligatorio: '{msg}'")
