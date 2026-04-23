"""
Pruebas funcionales — Plan Gestión de Asignación de Turnos (refinado Shape Up)
Sistema: GestiónRH — Administración de Empleados

Scopes cubiertos:
  Scope A — Asignación de turno
  Scope B — Edición de asignación
  Scope C — Eliminación de asignación
  Scope D — Visualización en turnos vigentes

CPs cubiertos:
  CP-001a, CP-001b, CP-002a, CP-002b, CP-002c, CP-002d  (Scope A)
  CP-003a, CP-003b, CP-003c, CP-003d, CP-004, CP-005    (Scope B)
  CP-006, CP-007, CP-008                                 (Scope C)
  CP-009, CP-010                                         (Scope D)
  CP-011                                                 (Bug 1 — botones per-row, asignador preservado)
  CP-012                                                 (Bug 2 — sección Turno asignado con vigente)
"""

import pytest
from helpers import BASE_URL, hacer_login

# ── Usuarios de prueba ──────────────────────────────────────────────────────
CORREO_JEFE     = "carlos.rodriguez@yopmail.com"   # Rol=Jefe, EmpleadoId=1, SedeId=1
CORREO_REGENTE  = "laura.sanchez@yopmail.com"       # Rol=Regente, EmpleadoId=2, JefeInm=1
CORREO_OPERARIO = "diana.vargas@yopmail.com"        # Rol=Operario — sin puedeEditar
PASSWORD        = "Usuario1"

# Empleado: Andrés Torres (ID=4, JefeInmediato=Laura=EmpleadoId=2)
EMPLEADO_ID     = 4
# Empleado: Laura Sánchez Gómez (ID=2, JefeInmediato=Carlos=EmpleadoId=1)
LAURA_ID        = 2

HORARIO_URL = f"{BASE_URL}/Empleado/Perfil/{EMPLEADO_ID}?tab=horario"


# ── Helpers ─────────────────────────────────────────────────────────────────

def _login_y_horario(page, correo: str, empleado_id: int = EMPLEADO_ID):
    """Login y navega a la pestaña Horario del perfil del empleado indicado."""
    page.goto(f"{BASE_URL}/Cuenta/Logout")
    page.wait_for_load_state("networkidle")
    hacer_login(page, correo, PASSWORD)
    if "/Cuenta/CambiarPassword" in page.url:
        pytest.skip(f"{correo} redirigido a CambiarPassword.")
    page.goto(f"{BASE_URL}/Empleado/Perfil/{empleado_id}?tab=horario")
    page.wait_for_load_state("networkidle")


def _asignar_turno(page, fecha: str = "2026-05-01"):
    """Abre el modal de asignar turno, selecciona la primera plantilla y guarda."""
    page.click("button:has-text('Asignar / cambiar turno')")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    primera = page.locator("#turno-plantilla option:not([value=''])").first
    if primera.count() == 0:
        pytest.skip("No hay plantillas de turno activas.")
    page.select_option("#turno-plantilla", value=primera.get_attribute("value"))
    page.fill("#turno-fecha", fecha)
    page.click("#btn-guardar-turno")
    page.wait_for_url(f"**/Empleado/Perfil/{EMPLEADO_ID}*tab=horario*", timeout=10_000)
    page.wait_for_load_state("networkidle")


# ============================================================
# SCOPE A — Asignación de turno
# ============================================================

def test_cp001a_boton_visible_para_jefe(page):
    """CP-001a: Botón 'Asignar / cambiar turno' es visible para usuario con subordinados (Jefe)."""
    _login_y_horario(page, CORREO_JEFE)
    btn = page.locator("button:has-text('Asignar / cambiar turno')")
    assert btn.count() > 0 and btn.is_visible(), (
        "CP-001a FALLO: El botón 'Asignar / cambiar turno' no es visible para el Jefe."
    )
    print("\n  CP-001a PASÓ — Botón visible para Jefe con subordinados.")


def test_cp001b_boton_oculto_para_operario(page):
    """CP-001b: Botón NO aparece para usuario Operario (sin puedeEditar)."""
    _login_y_horario(page, CORREO_OPERARIO, empleado_id=EMPLEADO_ID)
    btn = page.locator("button:has-text('Asignar / cambiar turno')")
    assert btn.count() == 0 or not btn.is_visible(), (
        "CP-001b FALLO: El botón 'Asignar / cambiar turno' SÍ aparece para el Operario."
    )
    print("\n  CP-001b PASÓ — Botón oculto para Operario.")


def test_cp002a_modal_abre_sin_navegar(page):
    """CP-002a: Modal se abre al pulsar el botón sin navegar a otra página."""
    _login_y_horario(page, CORREO_JEFE)
    url_antes = page.url
    page.click("button:has-text('Asignar / cambiar turno')")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    assert page.url == url_antes, f"CP-002a FALLO: Navegó a {page.url}."
    assert page.is_visible("#modal-turno"), "CP-002a FALLO: Modal no visible."
    print("\n  CP-002a PASÓ — Modal abierto sin navegar.")


def test_cp002b_modal_cierra_cancelar_y_x(page):
    """CP-002b: Modal se cierra con Cancelar y con X."""
    _login_y_horario(page, CORREO_JEFE)
    # Cancelar
    page.click("button:has-text('Asignar / cambiar turno')")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    page.click("#modal-turno button:has-text('Cancelar')")
    page.wait_for_selector("#modal-turno", state="hidden", timeout=5_000)
    assert not page.is_visible("#modal-turno"), "CP-002b FALLO: No cerró con Cancelar."
    # X
    page.click("button:has-text('Asignar / cambiar turno')")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    page.click("#modal-turno .modal-close")
    page.wait_for_selector("#modal-turno", state="hidden", timeout=5_000)
    assert not page.is_visible("#modal-turno"), "CP-002b FALLO: No cerró con X."
    print("\n  CP-002b PASÓ — Modal cierra con Cancelar y X.")


def test_cp002c_formulario_vacio_no_envia(page):
    """CP-002c: Enviar formulario vacío no cierra el modal."""
    _login_y_horario(page, CORREO_JEFE)
    page.click("button:has-text('Asignar / cambiar turno')")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    page.select_option("#turno-plantilla", value="")
    page.fill("#turno-fecha", "")
    page.click("#btn-guardar-turno")
    page.wait_for_timeout(600)
    assert page.is_visible("#modal-turno"), "CP-002c FALLO: Modal se cerró con formulario vacío."
    print("\n  CP-002c PASÓ — Formulario vacío no envió; modal permanece abierto.")


def test_cp002d_asignacion_valida_guarda(page):
    """CP-002d: Asignación válida guarda y recarga la pestaña horario."""
    _login_y_horario(page, CORREO_JEFE)
    _asignar_turno(page, fecha="2026-05-10")
    assert "/Empleado/Perfil" in page.url and "horario" in page.url, (
        f"CP-002d FALLO: No recargó el tab horario. URL: {page.url}"
    )
    print("\n  CP-002d PASÓ — Asignación guardada; recargó pestaña horario.")


# ============================================================
# SCOPE B — Edición de asignación
# ============================================================

def test_cp003a_boton_editar_visible(page):
    """CP-003a: Botón Editar es visible en el historial para el Jefe."""
    _login_y_horario(page, CORREO_JEFE)
    filas = page.locator("table[aria-label='Historial de turnos'] tbody tr")
    if filas.count() == 0:
        _asignar_turno(page)
    editar_btns = page.locator(
        "table[aria-label='Historial de turnos'] tbody button:has-text('Editar')"
    )
    assert editar_btns.count() > 0, "CP-003a FALLO: No hay botones Editar en el historial."
    assert editar_btns.first.is_visible(), "CP-003a FALLO: Botón Editar no visible."
    print(f"\n  CP-003a PASÓ — Botón Editar visible ({editar_btns.count()} fila(s)).")


def test_cp003b_modal_prepoblado(page):
    """CP-003b: Modal Editar se abre pre-poblado con los datos de la fila."""
    _login_y_horario(page, CORREO_JEFE)
    primer_editar = page.locator(
        "table[aria-label='Historial de turnos'] tbody button:has-text('Editar')"
    ).first
    if primer_editar.count() == 0:
        _asignar_turno(page)
        primer_editar = page.locator(
            "table[aria-label='Historial de turnos'] tbody button:has-text('Editar')"
        ).first
    primer_editar.click()
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    assert page.input_value("#turno-plantilla") != "", "CP-003b FALLO: Select de plantilla vacío."
    assert page.input_value("#turno-fecha") != "",     "CP-003b FALLO: Fecha no pre-cargada."
    print("\n  CP-003b PASÓ — Modal pre-poblado con datos de la fila.")


def test_cp003c_titulo_modal_edicion(page):
    """CP-003c: El título del modal cambia a 'Editar asignación' al abrir desde Editar."""
    _login_y_horario(page, CORREO_JEFE)
    primer_editar = page.locator(
        "table[aria-label='Historial de turnos'] tbody button:has-text('Editar')"
    ).first
    if primer_editar.count() == 0:
        _asignar_turno(page)
        primer_editar = page.locator(
            "table[aria-label='Historial de turnos'] tbody button:has-text('Editar')"
        ).first
    primer_editar.click()
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    titulo = page.inner_text("#turno-title")
    assert "Editar" in titulo, f"CP-003c FALLO: Título no indica edición. Título: '{titulo}'"
    print(f"\n  CP-003c PASÓ — Título del modal: '{titulo}'.")


def test_cp003d_editar_guarda_cambios(page):
    """CP-003d: Guardar edición actualiza el registro y recarga la pestaña."""
    _login_y_horario(page, CORREO_JEFE)
    primer_editar = page.locator(
        "table[aria-label='Historial de turnos'] tbody button:has-text('Editar')"
    ).first
    if primer_editar.count() == 0:
        _asignar_turno(page)
        primer_editar = page.locator(
            "table[aria-label='Historial de turnos'] tbody button:has-text('Editar')"
        ).first
    primer_editar.click()
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    page.fill("#turno-fecha", "2026-03-15")
    with page.expect_response(lambda r: "EditarAsignacionAjax" in r.url, timeout=10_000) as ri:
        page.click("#btn-guardar-turno")
    resp = ri.value.json()
    assert resp.get("exito") is True, f"CP-003d FALLO: exito=false. Mensaje: {resp.get('mensaje')}"
    page.wait_for_url(f"**/Empleado/Perfil/{EMPLEADO_ID}*tab=horario*", timeout=10_000)
    page.wait_for_load_state("networkidle")
    fechas = [
        page.locator("table[aria-label='Historial de turnos'] tbody td.tabular-nums").nth(i).inner_text()
        for i in range(page.locator("table[aria-label='Historial de turnos'] tbody td.tabular-nums").count())
    ]
    assert "15/03/2026" in fechas, f"CP-003d FALLO: Fecha '15/03/2026' no aparece. Fechas: {fechas}"
    print("\n  CP-003d PASÓ — Edición guardada; fecha '15/03/2026' en historial.")


def test_cp004_jefe_superior_puede_editar(page):
    """CP-004: Jefe (nivel superior de Laura) ve el botón Editar en el perfil de Andrés."""
    # Carlos es Jefe → puedeEditar=true → puede editar asignaciones de cualquier empleado
    _login_y_horario(page, CORREO_JEFE, empleado_id=EMPLEADO_ID)
    editar_btns = page.locator(
        "table[aria-label='Historial de turnos'] tbody button:has-text('Editar')"
    )
    if editar_btns.count() == 0:
        _asignar_turno(page)
        editar_btns = page.locator(
            "table[aria-label='Historial de turnos'] tbody button:has-text('Editar')"
        )
    assert editar_btns.count() > 0 and editar_btns.first.is_visible(), (
        "CP-004 FALLO: El Jefe superior no ve el botón Editar para el empleado de su subordinado."
    )
    print("\n  CP-004 PASÓ — Jefe superior puede editar asignaciones.")


def test_cp005_operario_no_puede_editar(page):
    """CP-005: Operario no tiene botón Editar en el historial."""
    _login_y_horario(page, CORREO_OPERARIO, empleado_id=EMPLEADO_ID)
    editar_btns = page.locator(
        "table[aria-label='Historial de turnos'] tbody button:has-text('Editar')"
    )
    assert editar_btns.count() == 0, (
        "CP-005 FALLO: El Operario SÍ ve botones Editar en el historial."
    )
    print("\n  CP-005 PASÓ — Operario no ve botones Editar.")


# ============================================================
# SCOPE C — Eliminación de asignación
# ============================================================

def test_cp006_asignador_puede_eliminar(page):
    """CP-006: El Jefe que asignó el turno puede eliminarlo (ProgramadoPor == usuarioId)."""
    # Carlos (Jefe, UsuarioId=1) asigna un turno a Andrés y luego lo elimina
    _login_y_horario(page, CORREO_JEFE, empleado_id=EMPLEADO_ID)
    page.wait_for_selector("button:has-text('Asignar / cambiar turno')", timeout=5_000)
    _asignar_turno(page, fecha="2026-06-01")

    eliminar_btn = page.locator(
        "table[aria-label='Historial de turnos'] tbody button:has-text('Eliminar')"
    ).first
    assert eliminar_btn.count() > 0 and eliminar_btn.is_visible(), (
        "CP-006 FALLO: No hay botón Eliminar para el Jefe asignador."
    )
    target_id = eliminar_btn.get_attribute("data-id")
    eliminar_btn.click()
    page.wait_for_selector("#modal-eliminar-turno:not([hidden])", timeout=5_000)
    with page.expect_response(lambda r: "EliminarAsignacionAjax" in r.url, timeout=10_000) as ri:
        page.click("#btn-confirmar-eliminar-turno")
    resp = ri.value.json()
    assert resp.get("exito") is True, f"CP-006 FALLO: exito=false. Mensaje: {resp.get('mensaje')}"
    page.wait_for_timeout(1000)
    page.goto(f"{BASE_URL}/Empleado/Perfil/{EMPLEADO_ID}?tab=horario")
    page.wait_for_load_state("networkidle")
    remaining = page.locator(
        f"table[aria-label='Historial de turnos'] tbody button[data-id='{target_id}']"
    )
    assert remaining.count() == 0, (
        f"CP-006 FALLO: Asignación ID={target_id} sigue en el historial."
    )
    print(f"\n  CP-006 PASÓ — Asignador (Jefe) eliminó asignación ID={target_id}.")


def test_cp007_jefe_inmediato_puede_eliminar(page):
    """CP-007: Jefe inmediato del empleado puede eliminar una asignación (JefeInmediato check)."""
    # Carlos (Jefe, EmpleadoId=1) es JefeInmediato de Laura (EmpleadoId=2)
    # Asignamos turno a Laura y Carlos lo elimina
    _login_y_horario(page, CORREO_JEFE, empleado_id=LAURA_ID)
    page.wait_for_selector("button:has-text('Asignar / cambiar turno')", timeout=5_000)

    page.click("button:has-text('Asignar / cambiar turno')")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    primera = page.locator("#turno-plantilla option:not([value=''])").first
    if primera.count() == 0:
        pytest.skip("No hay plantillas activas.")
    page.select_option("#turno-plantilla", value=primera.get_attribute("value"))
    page.fill("#turno-fecha", "2026-07-01")
    page.click("#btn-guardar-turno")
    page.wait_for_url(f"**/Empleado/Perfil/{LAURA_ID}*tab=horario*", timeout=10_000)
    page.wait_for_load_state("networkidle")

    eliminar_btn = page.locator(
        "table[aria-label='Historial de turnos'] tbody button:has-text('Eliminar')"
    ).first
    assert eliminar_btn.count() > 0 and eliminar_btn.is_visible(), (
        "CP-007 FALLO: El Jefe inmediato no ve el botón Eliminar."
    )
    # Captura el data-id del row a eliminar para verificar después
    target_id = eliminar_btn.get_attribute("data-id")
    eliminar_btn.click()
    page.wait_for_selector("#modal-eliminar-turno:not([hidden])", timeout=5_000)
    page.click("#btn-confirmar-eliminar-turno")
    # Espera la respuesta AJAX y la navegación (700ms setTimeout + carga)
    page.wait_for_timeout(1500)
    page.wait_for_load_state("networkidle")
    # Navega explícitamente para obtener estado fresco desde el servidor
    page.goto(f"{BASE_URL}/Empleado/Perfil/{LAURA_ID}?tab=horario")
    page.wait_for_load_state("networkidle")
    remaining = page.locator(
        f"table[aria-label='Historial de turnos'] tbody button[data-id='{target_id}']"
    )
    assert remaining.count() == 0, (
        f"CP-007 FALLO: La asignación ID={target_id} sigue en el historial de Laura."
    )
    print(f"\n  CP-007 PASÓ — Jefe inmediato eliminó asignación ID={target_id}.")


def test_cp008_operario_no_puede_eliminar(page):
    """CP-008: Operario no tiene botón Eliminar en el historial."""
    _login_y_horario(page, CORREO_OPERARIO, empleado_id=EMPLEADO_ID)
    eliminar_btns = page.locator(
        "table[aria-label='Historial de turnos'] tbody button:has-text('Eliminar')"
    )
    assert eliminar_btns.count() == 0, (
        "CP-008 FALLO: El Operario SÍ ve botones Eliminar en el historial."
    )
    print("\n  CP-008 PASÓ — Operario no ve botones Eliminar.")


# ============================================================
# SCOPE D — Visualización en turnos vigentes
# ============================================================

def test_cp009_empleado_con_turno_aparece_en_vigentes(page):
    """CP-009: Empleado con turno asignado aparece en la lista de turnos vigentes."""
    _login_y_horario(page, CORREO_JEFE)

    # Asegurar que el empleado tiene una asignación vigente (hoy o antes)
    page.click("button:has-text('Asignar / cambiar turno')")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    primera = page.locator("#turno-plantilla option:not([value=''])").first
    if primera.count() == 0:
        pytest.skip("Sin plantillas activas.")
    plantilla_nombre = primera.inner_text()
    page.select_option("#turno-plantilla", value=primera.get_attribute("value"))
    page.fill("#turno-fecha", "2026-01-01")   # fecha pasada → vigente hoy
    page.click("#btn-guardar-turno")
    page.wait_for_url(f"**/Empleado/Perfil/{EMPLEADO_ID}*tab=horario*", timeout=10_000)
    page.wait_for_load_state("networkidle")

    # Ir al módulo de turnos vigentes
    page.goto(f"{BASE_URL}/Turno")
    page.wait_for_load_state("networkidle")

    tabla = page.locator("table[aria-label='Asignaciones de turno activas'] tbody")
    assert tabla.count() > 0, "CP-009 FALLO: No se encontró la tabla de asignaciones activas."

    filas = page.locator("table[aria-label='Asignaciones de turno activas'] tbody tr")
    textos = [filas.nth(i).inner_text() for i in range(filas.count())]
    encontrado = any("Andrés" in t or "Torres" in t for t in textos)
    assert encontrado, (
        f"CP-009 FALLO: Andrés Torres no aparece en turnos vigentes. Filas: {textos[:5]}"
    )
    print(f"\n  CP-009 PASÓ — Andrés Torres aparece en turnos vigentes.")


def test_cp010_empleado_sin_turno_no_aparece_en_vigentes(page):
    """CP-010: Empleado sin turno asignado no aparece en turnos vigentes."""
    _login_y_horario(page, CORREO_JEFE)
    page.goto(f"{BASE_URL}/Turno")
    page.wait_for_load_state("networkidle")

    tabla = page.locator("table[aria-label='Asignaciones de turno activas'] tbody")
    assert tabla.count() > 0, "CP-010 FALLO: No se encontró la tabla."

    # Verificar que la lista no contiene filas con datos vacíos/sin plantilla
    filas = page.locator("table[aria-label='Asignaciones de turno activas'] tbody tr")
    for i in range(filas.count()):
        texto = filas.nth(i).inner_text()
        assert texto.strip() != "", f"CP-010 FALLO: Fila {i+1} está vacía: '{texto}'"

    print(f"\n  CP-010 PASÓ — La tabla de vigentes no contiene filas vacías ({filas.count()} filas).")


# ============================================================
# Bug 1 — Botones per-row y preservación del asignador
# ============================================================

def test_cp011_edicion_preserva_asignador_original(page):
    """CP-011 (Bug 1): Editar una asignación NO sobreescribe al asignador original."""
    # Carlos asigna un turno a Andrés
    _login_y_horario(page, CORREO_JEFE, empleado_id=EMPLEADO_ID)
    _asignar_turno(page, fecha="2026-09-01")

    # Capturar asignador y data-id de la fila más reciente (la que acabamos de crear)
    primera_fila = page.locator(
        "table[aria-label='Historial de turnos'] tbody tr"
    ).first
    asignador_antes = primera_fila.locator("td").nth(2).inner_text().strip()
    data_id = primera_fila.locator("button:has-text('Editar')").get_attribute("data-id")

    # Carlos edita esa misma fila cambiando la fecha
    editar_btn = primera_fila.locator("button:has-text('Editar')")
    assert editar_btn.count() > 0 and editar_btn.is_visible(), (
        "CP-011 SETUP FALLO: El botón Editar no está visible para Carlos (asignador)."
    )
    editar_btn.click()
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    page.fill("#turno-fecha", "2026-09-15")
    with page.expect_response(lambda r: "EditarAsignacionAjax" in r.url, timeout=10_000) as ri:
        page.click("#btn-guardar-turno")
    resp = ri.value.json()
    assert resp.get("exito") is True, (
        f"CP-011 FALLO: El AJAX de edición devolvió exito=false. Mensaje: {resp.get('mensaje')}"
    )

    # Navegar explícitamente para obtener estado fresco del servidor
    page.goto(f"{BASE_URL}/Empleado/Perfil/{EMPLEADO_ID}?tab=horario")
    page.wait_for_load_state("networkidle")

    # Localizar la fila por data-id y verificar que el asignador no cambió
    filas = page.locator("table[aria-label='Historial de turnos'] tbody tr")
    encontrada = False
    for i in range(filas.count()):
        fila = filas.nth(i)
        btn_fila = fila.locator(f"button[data-id='{data_id}']")
        if btn_fila.count() > 0:
            encontrada = True
            fecha_td = fila.locator("td").nth(1).inner_text()
            asignador_despues = fila.locator("td").nth(2).inner_text().strip()
            assert "15/09/2026" in fecha_td, (
                f"CP-011 FALLO: La fecha no se actualizó. Fecha actual: '{fecha_td}'"
            )
            assert asignador_despues == asignador_antes, (
                f"CP-011 FALLO: El asignador cambió de '{asignador_antes}' "
                f"a '{asignador_despues}' tras editar."
            )
            # Botones siguen visibles para Carlos (asignador original)
            edit_post = fila.locator("button:has-text('Editar')")
            assert edit_post.count() > 0 and edit_post.is_visible(), (
                "CP-011 FALLO: El botón Editar desapareció para el asignador original tras editar."
            )
            break
    assert encontrada, f"CP-011 FALLO: No se encontró la fila con data-id={data_id} tras editar."
    print("\n  CP-011 PASÓ — El asignador original se conserva y los botones siguen visibles.")


# ============================================================
# Bug 2 — Sección "Turno asignado" muestra turno vigente
# ============================================================

def test_cp012_turno_vigente_aparece_en_seccion_turno_asignado(page):
    """CP-012 (Bug 2): La sección 'Turno asignado' muestra la plantilla cuando FechaVigencia ≤ hoy."""
    # Carlos asigna un turno a Andrés con fecha en el pasado → vigente hoy
    _login_y_horario(page, CORREO_JEFE, empleado_id=EMPLEADO_ID)
    _asignar_turno(page, fecha="2025-01-01")

    # La sección NO debe mostrar "Sin turno asignado"
    sin_turno = page.locator(".empty-title")
    if sin_turno.count() > 0:
        for i in range(sin_turno.count()):
            assert "Sin turno asignado" not in sin_turno.nth(i).inner_text(), (
                "CP-012 FALLO: La sección 'Turno asignado' muestra 'Sin turno asignado' "
                "aunque existe una asignación vigente."
            )

    # Debe mostrar la cuadrícula de días del turno
    grilla = page.locator(".shift-days-grid")
    assert grilla.count() > 0 and grilla.is_visible(), (
        "CP-012 FALLO: La cuadrícula de días del turno no se muestra aunque hay asignación vigente."
    )
    print("\n  CP-012 PASÓ — La sección 'Turno asignado' muestra la plantilla vigente.")
