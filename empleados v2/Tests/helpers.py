"""Funciones reutilizables para las pruebas de login."""

BASE_URL = "http://localhost:5002"


def hacer_login(page, correo: str, password: str):
    """Navega al login, rellena el formulario y hace submit."""
    page.goto(f"{BASE_URL}/Cuenta/Login")
    page.wait_for_load_state("networkidle")
    page.fill("#CorreoAcceso", correo)
    page.fill("#Password", password)
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
