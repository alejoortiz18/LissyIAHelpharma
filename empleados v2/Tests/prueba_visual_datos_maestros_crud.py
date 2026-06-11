"""
Prueba visual CRUD datos maestros (Lissy): crear y actualizar sede, cargo, empresa temporal.
"""
import time

from playwright.sync_api import Page, expect, sync_playwright

BASE_URL = "http://localhost:5002"
LOGIN_EMAIL = "lissy.gallego@zentria.com.co"
LOGIN_PASSWORD = "Usuario1"

SUFIJO = str(int(time.time()))[-6:]


def _login(page: Page) -> None:
    page.goto(f"{BASE_URL}/Cuenta/Login")
    page.wait_for_load_state("networkidle")
    page.fill("#CorreoAcceso", LOGIN_EMAIL)
    page.fill("#inputPassword", LOGIN_PASSWORD)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")
    if "/Cuenta/CambiarPassword" in page.url:
        page.fill("#Dto_PasswordActual", LOGIN_PASSWORD)
        page.fill("#Dto_NuevoPassword", "Usuario1")
        page.fill("#Dto_ConfirmarPassword", "Usuario1")
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")


def _ir_tab(page: Page, tab: str) -> None:
    page.goto(f"{BASE_URL}/DatosMaestros/Index?tab={tab}")
    page.wait_for_load_state("networkidle")


def _crear_sede(page: Page, nombre: str, ciudad: str, direccion: str) -> None:
    page.locator("#btn-nueva-sede").click()
    page.wait_for_timeout(400)
    page.fill("#sede-nombre", nombre)
    page.fill("#sede-ciudad", ciudad)
    page.fill("#sede-direccion", direccion)
    page.locator("#btn-guardar-sede").click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)


def _editar_sede(page: Page, nombre_orig: str, nombre_nuevo: str, ciudad: str, direccion: str) -> None:
    fila = page.locator("table[aria-label='Sedes'] tbody tr").filter(has_text=nombre_orig).first
    fila.locator("button:has-text('Editar')").click()
    page.wait_for_timeout(400)
    page.fill("#sede-nombre", nombre_nuevo)
    page.fill("#sede-ciudad", ciudad)
    page.fill("#sede-direccion", direccion)
    page.locator("#btn-guardar-sede").click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)


def _crear_cargo(page: Page, nombre: str) -> None:
    page.locator("#btn-nuevo-cargo").click()
    page.wait_for_timeout(400)
    page.fill("#cargo-nombre", nombre)
    page.locator("#btn-guardar-cargo").click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)


def _editar_cargo(page: Page, nombre_orig: str, nombre_nuevo: str) -> None:
    fila = page.locator("table[aria-label='Cargos'] tbody tr").filter(has_text=nombre_orig).first
    fila.locator("button:has-text('Editar')").click()
    page.wait_for_timeout(400)
    page.fill("#cargo-nombre", nombre_nuevo)
    page.locator("#btn-guardar-cargo").click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)


def _crear_empresa(page: Page, nombre: str) -> None:
    page.locator("#btn-nueva-empresa").click()
    page.wait_for_timeout(400)
    page.fill("#empresa-nombre", nombre)
    page.locator("#btn-guardar-empresa").click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)


def _editar_empresa(page: Page, nombre_orig: str, nombre_nuevo: str) -> None:
    fila = page.locator("table[aria-label='Empresas temporales'] tbody tr").filter(
        has_text=nombre_orig
    ).first
    fila.locator("button:has-text('Editar')").click()
    page.wait_for_timeout(400)
    page.fill("#empresa-nombre", nombre_nuevo)
    page.locator("#btn-guardar-empresa").click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)


def main() -> None:
    sede_crear = f"Sede Prueba {SUFIJO}"
    sede_edit = f"Sede Actualizada {SUFIJO}"
    cargo_crear = f"Cargo Prueba {SUFIJO}"
    cargo_edit = f"Cargo Actualizado {SUFIJO}"
    emp_crear = f"Empresa Prueba {SUFIJO}"
    emp_edit = f"Empresa Actualizada {SUFIJO}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        page = browser.new_context().new_page()

        print("1. Login Lissy")
        _login(page)
        page.goto(f"{BASE_URL}/DatosMaestros/Index?tab=sedes")
        page.wait_for_load_state("networkidle")

        print(f"2. Crear sede: {sede_crear}")
        _crear_sede(page, sede_crear, "Bogota", "Calle Prueba 100")
        expect(page.locator("table[aria-label='Sedes']")).to_contain_text(sede_crear)
        print("   OK: sede creada visible en tabla")

        print(f"3. Actualizar sede -> {sede_edit}")
        _editar_sede(page, sede_crear, sede_edit, "Medellin", "Carrera 50 # 10")
        expect(page.locator("table[aria-label='Sedes']")).to_contain_text(sede_edit)
        expect(page.locator("table[aria-label='Sedes']")).not_to_contain_text(sede_crear)
        print("   OK: sede actualizada")

        print(f"4. Crear cargo: {cargo_crear}")
        _ir_tab(page, "cargos")
        _crear_cargo(page, cargo_crear)
        expect(page.locator("table[aria-label='Cargos']")).to_contain_text(cargo_crear)
        print("   OK: cargo creado")

        print(f"5. Actualizar cargo -> {cargo_edit}")
        _editar_cargo(page, cargo_crear, cargo_edit)
        expect(page.locator("table[aria-label='Cargos']")).to_contain_text(cargo_edit)
        print("   OK: cargo actualizado")

        print(f"6. Crear empresa temporal: {emp_crear}")
        _ir_tab(page, "empresas")
        _crear_empresa(page, emp_crear)
        expect(page.locator("table[aria-label='Empresas temporales']")).to_contain_text(emp_crear)
        print("   OK: empresa creada")

        print(f"7. Actualizar empresa -> {emp_edit}")
        _editar_empresa(page, emp_crear, emp_edit)
        expect(page.locator("table[aria-label='Empresas temporales']")).to_contain_text(emp_edit)
        print("   OK: empresa actualizada")

        print("\n--- Resumen: CRUD datos maestros OK ---")
        print(f"   Sede: {sede_edit}")
        print(f"   Cargo: {cargo_edit}")
        print(f"   Empresa: {emp_edit}")
        print("Pausa 10 s para revisar...")
        time.sleep(10)
        browser.close()


if __name__ == "__main__":
    main()
