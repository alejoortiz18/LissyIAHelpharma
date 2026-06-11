"""
Prueba visual: Datos maestros (solo Lissy).
Usuario: lissy.gallego@zentria.com.co / Usuario1
"""
import time

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5002"
LOGIN_EMAIL = "lissy.gallego@zentria.com.co"
LOGIN_PASSWORD = "Usuario1"


def main() -> None:
    errores: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=450)
        page = browser.new_context().new_page()

        print("1. Login Lissy")
        page.goto(f"{BASE_URL}/Cuenta/Login")
        page.wait_for_load_state("networkidle")
        page.fill("#CorreoAcceso", LOGIN_EMAIL)
        page.fill("#inputPassword", LOGIN_PASSWORD)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")

        if "/Cuenta/CambiarPassword" in page.url:
            print("   Completando cambio de contrasena obligatorio...")
            page.fill("#Dto_PasswordActual", LOGIN_PASSWORD)
            page.fill("#Dto_NuevoPassword", "Usuario1")
            page.fill("#Dto_ConfirmarPassword", "Usuario1")
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")

        print("2. Dashboard - tarjeta Ingresar datos maestros")
        if "/Dashboard" not in page.url:
            page.goto(f"{BASE_URL}/Dashboard")
            page.wait_for_load_state("networkidle")

        card_btn = page.locator("a:has-text('Ingresar datos maestros')")
        if not card_btn.is_visible():
            errores.append("No visible la tarjeta/boton en Dashboard")
        else:
            print("   OK: tarjeta visible")

        print("3. Menu lateral - Datos maestros")
        link_menu = page.locator(".sidebar-nav a:has-text('Datos maestros')")
        if not link_menu.is_visible():
            errores.append("No visible el enlace Datos maestros en el menu")
        else:
            print("   OK: enlace en menu")

        catalogos = page.locator(".sidebar-nav a:has-text('Catálogos')")
        if catalogos.count() > 0 and catalogos.first.is_visible():
            errores.append("Lissy no deberia ver el menu Catalogos")

        print("4. Abrir Datos maestros desde Dashboard")
        card_btn.click()
        page.wait_for_load_state("networkidle")

        if "/DatosMaestros" not in page.url:
            errores.append(f"No navego a DatosMaestros. URL: {page.url}")
        else:
            print(f"   OK: {page.url}")

        titulo = page.locator("h1.page-title")
        if titulo.is_visible() and "Datos maestros" in titulo.inner_text():
            print("   OK: titulo Datos maestros")
        else:
            errores.append("Titulo de pagina incorrecto")

        print("5. Pestañas Sedes / Cargos / Empresas")
        for tab in ("Sedes", "Cargos", "Empresas temporales"):
            page.locator(f".tabs a:has-text('{tab}')").click()
            page.wait_for_load_state("networkidle")
            if not page.locator(".card-title").first.is_visible():
                errores.append(f"Tab {tab} no cargo contenido")
            else:
                print(f"   OK: tab {tab}")

        print("6. Abrir modal Nueva sede (sin guardar)")
        page.goto(f"{BASE_URL}/DatosMaestros/Index?tab=sedes")
        page.wait_for_load_state("networkidle")
        page.locator("#btn-nueva-sede").click()
        page.wait_for_timeout(800)
        visible = page.evaluate(
            "() => { const m = document.getElementById('modal-sede'); return m && !m.hidden; }"
        )
        if visible:
            print("   OK: modal nueva sede")
            page.evaluate("closeModal('modal-sede')")
        else:
            errores.append("Modal nueva sede no abrio (revisar JS en vista parcial)")

        print("\n--- Resumen ---")
        if errores:
            for e in errores:
                print(f"  FALLO: {e}")
        else:
            print("  Prueba visual OK.")
        print("Pausa 12 s...")
        time.sleep(12)
        browser.close()

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
