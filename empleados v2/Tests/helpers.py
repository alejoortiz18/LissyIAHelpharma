"""Funciones reutilizables para las pruebas de login."""
import re

BASE_URL = "http://localhost:5002"


def hacer_login(page, correo: str, password: str):
    """Navega al login, rellena el formulario y hace submit."""
    page.goto(f"{BASE_URL}/Cuenta/Login")
    page.wait_for_load_state("networkidle")
    page.fill("#CorreoAcceso", correo)
    page.fill("#inputPassword", password)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


def hacer_logout(page):
    """Navega al endpoint de logout."""
    page.goto(f"{BASE_URL}/Cuenta/Logout")
    page.wait_for_load_state("networkidle")


def obtener_url_actual(page) -> str:
    """Retorna el path de la URL actual (sin host)."""
    return page.url.replace(BASE_URL, "")


def hay_error_formulario(page) -> bool:
    """Verifica si existe algún mensaje de error visible en el formulario."""
    errores = page.locator(".form-error").all()
    return any(e.is_visible() and e.inner_text().strip() != "" for e in errores)


def obtener_texto_error(page) -> str:
    """Obtiene el texto del primer mensaje de error visible."""
    errores = page.locator(".form-error").all()
    for e in errores:
        texto = e.inner_text().strip()
        if e.is_visible() and texto:
            return texto
    return ""


def hacer_login_completo(page, correo: str, password: str):
    """Login con manejo automático del flujo CambiarPassword si DebeCambiarPassword=1."""
    hacer_logout(page)
    hacer_login(page, correo, password)
    if "/Cuenta/CambiarPassword" in page.url:
        nueva_password = "NuevaClave2026!"
        page.fill("#Dto_PasswordActual", password)
        page.fill("#Dto_NuevoPassword", nueva_password)
        page.fill("#Dto_ConfirmarPassword", nueva_password)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")


def esta_acceso_denegado(page) -> bool:
    """Verifica si la página actual es de acceso denegado."""
    return "Acceso-Denegado" in page.url


def elemento_sidebar_visible(page, texto: str) -> bool:
    """Verifica si un ítem del sidebar es visible por su texto."""
    return page.locator(f".sidebar-nav a:has-text('{texto}')").is_visible()


def obtener_token_antiforgery(page) -> str:
    """Obtiene el token antiforgery de la página actual.
    Busca en múltiples ubicaciones: const TOKEN, meta tag, hidden input, o inline JS."""
    content = page.content()
    # Patrón 1: const TOKEN = '...'
    match = re.search(r"const TOKEN\s*=\s*'([^']+)'", content)
    if match:
        return match.group(1)
    # Patrón 2: meta tag <meta name="__RequestVerificationToken" content="...">
    meta_val = page.evaluate(
        "() => { var m = document.querySelector('meta[name=\"__RequestVerificationToken\"]'); return m ? m.getAttribute('content') : ''; }"
    )
    if meta_val:
        return meta_val
    # Patrón 3: hidden input
    input_val = page.evaluate(
        "() => { var el = document.querySelector('input[name=\"__RequestVerificationToken\"]'); return el ? el.value : ''; }"
    )
    if input_val:
        return input_val
    # Patrón 4: Razor inline JS: return input ? input.value : 'TOKEN';
    match2 = re.search(r"return input \? input\.value : '([^']+)'", content)
    if match2:
        return match2.group(1)
    return ""


def llamar_ajax_post(page, ruta: str, datos: dict) -> dict:
    """Hace un POST al endpoint AJAX usando el token antiforgery de la página cargada.
    Requiere que la página actual ya tenga definida la constante TOKEN."""
    token = obtener_token_antiforgery(page)
    form_data = {k: str(v) for k, v in datos.items()}
    form_data["__RequestVerificationToken"] = token
    response = page.request.post(f"{BASE_URL}{ruta}", form=form_data)
    return response.json()
