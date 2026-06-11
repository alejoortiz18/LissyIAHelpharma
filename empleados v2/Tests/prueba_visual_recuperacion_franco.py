from __future__ import annotations

import re
from datetime import date
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

BASE_URL = "http://localhost:5002"
ADMIN_USER = "lissy.gallego@zentria.com.co"
ADMIN_PASS = "Usuario1"
FRANCO_EMAIL = "franco@yopmail.com"
FRANCO_PASS = "FrancoClave2026!"


def get_options(page, selector: str):
    return page.eval_on_selector(
        selector,
        "(s) => Array.from(s.options).map(o => ({value:o.value, text:o.textContent.trim()}))",
    )


def select_first_value(page, selector: str):
    options = get_options(page, selector)
    for opt in options:
        if opt["value"]:
            page.select_option(selector, value=opt["value"])
            return opt
    raise AssertionError(f"No hay opciones válidas en {selector}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=220)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()

        print("[1] Login con Lissy...")
        page.goto(f"{BASE_URL}/Cuenta/Login", wait_until="networkidle")
        page.fill("input[name='CorreoAcceso']", ADMIN_USER)
        page.fill("input[name='Password']", ADMIN_PASS)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.screenshot(path="visual_franco_01_login_lissy.png", full_page=True)

        print("[2] Crear usuario franco@yopmail.com...")
        page.goto(f"{BASE_URL}/Empleado/Nuevo", wait_until="networkidle")
        stamp = str(int(date.today().strftime("%d%m%Y")))
        page.fill("input[name='Dto.NombreCompleto']", "Franco Yopmail Visual")
        page.fill("input[name='Dto.Cedula']", f"77{stamp}")
        page.fill("input[name='Dto.Telefono']", "3001234567")
        page.fill("input[name='Dto.CorreoElectronico']", FRANCO_EMAIL)
        page.fill("input[name='Dto.Direccion']", "Calle 123")
        page.fill("input[name='Dto.Ciudad']", "Medellin")
        page.fill("input[name='Dto.Departamento']", "Antioquia")

        select_first_value(page, "select[name='Dto.SedeId']")
        page.wait_for_timeout(600)
        select_first_value(page, "select[name='Dto.CargoId']")
        page.select_option("select[name='Dto.Rol']", value="Operario")
        page.select_option("select[name='Dto.TipoVinculacion']", value="Directo")
        hoy = date.today().isoformat()
        page.fill("input[name='Dto.FechaIngreso']", hoy)
        page.fill("input[name='Dto.FechaInicioContrato']", hoy)

        jefes = get_options(page, "select[name='Dto.JefeInmediatoId']")
        jefe_val = next((j["value"] for j in jefes if j["value"]), "")
        if jefe_val:
            page.select_option("select[name='Dto.JefeInmediatoId']", value=jefe_val)

        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.screenshot(path="visual_franco_02_usuario_creado.png", full_page=True)

        body_text = page.locator("body").inner_text().lower()
        if "ya existe un empleado registrado con ese correo electrónico" in body_text:
            print("[INFO] franco@yopmail.com ya existía, continúo con recuperación.")

        print("[3] Solicitar recuperación para franco@yopmail.com...")
        page.goto(f"{BASE_URL}/Cuenta/Logout", wait_until="networkidle")
        page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword", wait_until="networkidle")
        page.fill("#CorreoAcceso", FRANCO_EMAIL)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.screenshot(path="visual_franco_03_solicitud_recuperacion.png", full_page=True)

        print("[4] Abrir buzón Yopmail y usar botón de restablecer...")
        page.goto("https://yopmail.com/en/?login=franco", wait_until="networkidle")
        inbox = page.frame_locator("#ifinbox")
        page.wait_for_timeout(2000)
        # Intenta abrir el primer correo disponible (más reciente) para evitar depender del texto del asunto.
        email_item = inbox.locator("a").first
        try:
            email_item.wait_for(timeout=45000)
        except PlaywrightTimeoutError:
            raise AssertionError("No llegó correo de recuperación a franco@yopmail.com en 45s.")
        email_item.click()
        page.wait_for_timeout(1500)

        mail = page.frame_locator("#ifmail")
        enlace = mail.locator("a[href*='RestablecerPassword'], a[href*='token=']").first
        enlace.wait_for(timeout=15000)
        href = enlace.get_attribute("href")
        if not href:
            raise AssertionError("No se encontró enlace de restablecimiento en el correo.")

        print("[5] Crear nueva contraseña para Franco...")
        page.goto(href, wait_until="networkidle")
        page.fill("#NuevoPassword", FRANCO_PASS)
        page.fill("#ConfirmarPassword", FRANCO_PASS)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.screenshot(path="visual_franco_04_password_restablecida.png", full_page=True)

        print("[6] Login con Franco...")
        page.fill("#CorreoAcceso", FRANCO_EMAIL)
        page.fill("#inputPassword", FRANCO_PASS)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.screenshot(path="visual_franco_05_login_franco.png", full_page=True)

        assert "/Cuenta/Login" not in page.url, "No se pudo iniciar sesión con Franco tras restablecer contraseña."
        print("OK: flujo visual completo exitoso.")
        page.wait_for_timeout(3000)
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
