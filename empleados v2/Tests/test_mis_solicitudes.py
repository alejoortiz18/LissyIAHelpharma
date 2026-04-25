"""
Pruebas funcionales — Módulo "Mis Solicitudes"
Sistema: GestiónRH — Administración de Empleados

TC-SOL-01  Operario ve ítem "Mis Solicitudes" en el menú lateral
TC-SOL-02  Navegar a /Solicitud muestra la lista vacía o con registros propios
TC-SOL-03  Modal "Nueva solicitud" se abre y tiene los campos requeridos
TC-SOL-04  Validación cliente: enviar formulario vacío muestra error
TC-SOL-05  Crear solicitud tipo Permiso con todos los campos → estado Pendiente
TC-SOL-06  Rutas de EventoLaboral siguen bloqueadas para Operario
TC-SOL-07  Usuarios de otros roles (Jefe) NO ven "Mis Solicitudes" en el menú
"""

import pytest
from datetime import date, timedelta
from helpers import BASE_URL, hacer_login, hacer_logout

CORREO_OPERARIO = "diana.vargas@yopmail.com"
CORREO_JEFE     = "carlos.rodriguez@yopmail.com"
PASSWORD        = "Usuario1"

FECHA_INICIO = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")
FECHA_FIN    = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")


# ── TC-SOL-01: Ítem de menú visible para Operario ───────────────────────────
def test_sol01_menu_mis_solicitudes_visible_operario(page):
    """
    Al iniciar sesión como Operario, el nav lateral debe mostrar "Mis Solicitudes".
    """
    hacer_login(page, CORREO_OPERARIO, PASSWORD)
    page.wait_for_url(f"**/Dashboard", timeout=8000)

    nav_link = page.locator("a[href*='/Solicitud']")
    assert nav_link.count() > 0, "TC-SOL-01 FALLO: No se encontró enlace a /Solicitud en el nav."

    texto = nav_link.first.inner_text().strip()
    assert "Solicitudes" in texto, (
        f"TC-SOL-01 FALLO: El texto del enlace era '{texto}', se esperaba 'Mis Solicitudes'."
    )
    print(f"\n  ✅ TC-SOL-01 PASÓ — Menú 'Mis Solicitudes' visible: '{texto}'")


# ── TC-SOL-02: Página /Solicitud carga correctamente ────────────────────────
def test_sol02_pagina_mis_solicitudes_carga(page):
    """
    GET /Solicitud debe retornar 200 y mostrar el encabezado correcto.
    """
    hacer_login(page, CORREO_OPERARIO, PASSWORD)
    page.wait_for_url(f"**/Dashboard", timeout=8000)

    page.goto(f"{BASE_URL}/Solicitud")
    page.wait_for_load_state("networkidle")

    url_actual = page.url
    assert "/Solicitud" in url_actual, (
        f"TC-SOL-02 FALLO: No redirigió a /Solicitud. URL actual: {url_actual}"
    )

    # El título de página debe estar presente
    titulo = page.locator("h1.page-title")
    assert titulo.count() > 0 and titulo.first.is_visible(), (
        "TC-SOL-02 FALLO: No se encontró el h1.page-title."
    )
    texto_titulo = titulo.first.inner_text().strip()
    assert "Solicitudes" in texto_titulo, (
        f"TC-SOL-02 FALLO: Título inesperado: '{texto_titulo}'"
    )
    print(f"\n  ✅ TC-SOL-02 PASÓ — Página cargada, título: '{texto_titulo}'")


# ── TC-SOL-03: Modal de nueva solicitud tiene campos requeridos ──────────────
def test_sol03_modal_nueva_solicitud_campos(page):
    """
    El modal debe contener select de tipo, fecha inicio, fecha fin y textarea de motivo.
    """
    hacer_login(page, CORREO_OPERARIO, PASSWORD)
    page.goto(f"{BASE_URL}/Solicitud")
    page.wait_for_load_state("networkidle")

    # Abrir modal
    btn_nueva = page.locator("button[data-modal-open='modal-nueva-solicitud']")
    assert btn_nueva.count() > 0, "TC-SOL-03 FALLO: Botón 'Nueva solicitud' no encontrado."
    btn_nueva.first.click()
    page.wait_for_timeout(500)

    modal = page.locator("#modal-nueva-solicitud")
    assert modal.is_visible(), "TC-SOL-03 FALLO: El modal no se abrió."

    # Verificar campos
    assert page.locator("#sol-tipo").is_visible(),        "TC-SOL-03 FALLO: Select tipo no visible."
    assert page.locator("#sol-inicio").is_visible(),      "TC-SOL-03 FALLO: Input fecha inicio no visible."
    assert page.locator("#sol-fin").is_visible(),         "TC-SOL-03 FALLO: Input fecha fin no visible."
    assert page.locator("#sol-descripcion").is_visible(), "TC-SOL-03 FALLO: Textarea motivo no visible."

    print("\n  ✅ TC-SOL-03 PASÓ — Modal contiene todos los campos requeridos.")


# ── TC-SOL-04: Validación cliente — formulario vacío muestra error ───────────
def test_sol04_validacion_formulario_vacio(page):
    """
    Enviar el formulario sin completar campos debe mostrar el bloque de error del cliente.
    """
    hacer_login(page, CORREO_OPERARIO, PASSWORD)
    page.goto(f"{BASE_URL}/Solicitud")
    page.wait_for_load_state("networkidle")

    page.locator("button[data-modal-open='modal-nueva-solicitud']").first.click()
    page.wait_for_timeout(500)

    # Enviar formulario vacío
    page.locator("#sol-submit").click()
    page.wait_for_timeout(400)

    error_box = page.locator("#sol-error")
    assert error_box.is_visible(), (
        "TC-SOL-04 FALLO: El bloque de error #sol-error no se mostró al enviar vacío."
    )
    texto_error = error_box.inner_text().strip()
    assert len(texto_error) > 0, "TC-SOL-04 FALLO: El bloque de error está vacío."
    print(f"\n  ✅ TC-SOL-04 PASÓ — Error de validación mostrado: '{texto_error}'")


# ── TC-SOL-05: Crear solicitud tipo Permiso ──────────────────────────────────
def test_sol05_crear_solicitud_permiso(page):
    """
    Completar y enviar una solicitud de Permiso debe:
    - Redirigir a /Solicitud
    - Mostrar mensaje de éxito
    - Registrar la solicitud con estado 'Pendiente'
    """
    hacer_login(page, CORREO_OPERARIO, PASSWORD)
    page.goto(f"{BASE_URL}/Solicitud")
    page.wait_for_load_state("networkidle")

    page.locator("button[data-modal-open='modal-nueva-solicitud']").first.click()
    page.wait_for_timeout(500)

    # Rellenar formulario
    page.select_option("#sol-tipo", "Permiso")
    page.fill("#sol-inicio", FECHA_INICIO)
    page.fill("#sol-fin", FECHA_FIN)
    page.fill("#sol-descripcion", "Permiso para trámite médico personal - prueba automatizada")

    # Enviar
    page.locator("#sol-submit").click()
    page.wait_for_load_state("networkidle")

    url_actual = page.url
    assert "/Solicitud" in url_actual, (
        f"TC-SOL-05 FALLO: No redirigió a /Solicitud. URL: {url_actual}"
    )

    # Verificar mensaje de éxito
    alert_exito = page.locator(".alert--success")
    assert alert_exito.count() > 0 and alert_exito.first.is_visible(), (
        "TC-SOL-05 FALLO: No se mostró alerta de éxito."
    )
    texto_exito = alert_exito.first.inner_text().strip()
    assert "pendiente" in texto_exito.lower() or "solicitud" in texto_exito.lower(), (
        f"TC-SOL-05 FALLO: Texto de éxito inesperado: '{texto_exito}'"
    )
    print(f"\n  ✅ TC-SOL-05 PASÓ — Solicitud creada. Mensaje: '{texto_exito}'")

    # Verificar badge 'Pendiente' en la tabla
    badge_pendiente = page.locator(".badge--pendiente")
    assert badge_pendiente.count() > 0, (
        "TC-SOL-05 FALLO: No se encontró badge 'Pendiente' en la lista."
    )
    print(f"  ✅ TC-SOL-05 Badge 'Pendiente' visible en la lista.")


# ── TC-SOL-06: /EventoLaboral sigue bloqueado para Operario ─────────────────
def test_sol06_evento_laboral_bloqueado_operario(page):
    """
    Un Operario que navega directamente a /EventoLaboral debe recibir Forbid (403/redirect).
    """
    hacer_login(page, CORREO_OPERARIO, PASSWORD)

    bloqueado = False
    try:
        page.goto(f"{BASE_URL}/EventoLaboral")
        page.wait_for_load_state("networkidle")
        url_actual = page.url
        # Fue redirigido fuera de EventoLaboral (p.ej. AccessDenied o Dashboard)
        if "/EventoLaboral" not in url_actual:
            bloqueado = True
        # O está en EventoLaboral pero sin el contenido esperado
        elif page.locator(".page-title").count() == 0:
            bloqueado = True
    except Exception as e:
        # Playwright lanza excepción cuando el servidor devuelve 4xx/5xx sin body
        if "ERR_HTTP_RESPONSE_CODE_FAILURE" in str(e) or "net::" in str(e):
            bloqueado = True
        else:
            raise

    assert bloqueado, "TC-SOL-06 FALLO: El Operario pudo acceder a /EventoLaboral sin restricción."
    print(f"\n  ✅ TC-SOL-06 PASÓ — /EventoLaboral bloqueado para Operario.")


# ── TC-SOL-07: Jefe NO ve "Mis Solicitudes" en el menú ──────────────────────
def test_sol07_jefe_no_ve_mis_solicitudes(page):
    """
    Un usuario con rol Jefe no debe ver el ítem "Mis Solicitudes" en el nav.
    """
    hacer_login(page, CORREO_JEFE, PASSWORD)
    url_post_login = page.url
    # El jefe puede tener DebeCambiarPassword=0 — avanzar si quedó en Dashboard
    if "/Cuenta/CambiarPassword" in url_post_login:
        pytest.skip("Jefe requiere cambio de contraseña — saltando TC-SOL-07.")

    page.wait_for_url(f"**/Dashboard", timeout=8000)

    nav_solicitud = page.locator("a[href*='/Solicitud']")
    assert nav_solicitud.count() == 0, (
        f"TC-SOL-07 FALLO: El Jefe ve el enlace 'Mis Solicitudes' en el menú — no debería."
    )
    print("\n  ✅ TC-SOL-07 PASÓ — Jefe no ve 'Mis Solicitudes' en el menú.")
