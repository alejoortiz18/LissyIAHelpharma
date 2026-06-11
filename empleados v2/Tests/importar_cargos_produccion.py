"""
Importa cargos en producción (Datos maestros — Lissy).
"""
import re
import sys

from playwright.sync_api import Page, sync_playwright

BASE_URL = "https://serviciosfarma.helpharma.com.co"
LOGIN_EMAIL = "lissy.gallego@zentria.com.co"
LOGIN_PASSWORD = "Usuario1"

CARGOS = [
    "Auxiliar de Farmacia",
    "Regente de Farmacia",
    "Auxiliar de farmacia",
    "Director Técnico",
    "Analista de servicios farmaceuticos",
    "Auxiliar Administrativo",
    "Lider de Procesos",
    "Direccionador",
    "Director Tecnico",
]


def _login(page: Page) -> None:
    page.goto(f"{BASE_URL}/Cuenta/Login", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#CorreoAcceso", timeout=30000)
    page.fill("#CorreoAcceso", LOGIN_EMAIL)
    page.fill("#inputPassword", LOGIN_PASSWORD)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle", timeout=60000)
    if "/Cuenta/CambiarPassword" in page.url:
        page.fill("#Dto_PasswordActual", LOGIN_PASSWORD)
        page.fill("#Dto_NuevoPassword", LOGIN_PASSWORD)
        page.fill("#Dto_ConfirmarPassword", LOGIN_PASSWORD)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle", timeout=60000)


def _cargos_existentes(page: Page) -> set[str]:
    page.goto(f"{BASE_URL}/DatosMaestros/Index?tab=cargos", wait_until="networkidle", timeout=60000)
    nombres: set[str] = set()
    filas = page.locator("table[aria-label='Cargos'] tbody tr")
    for i in range(filas.count()):
        texto = filas.nth(i).locator("td").first.inner_text().strip()
        if texto:
            nombres.add(texto)
    return nombres


def _token_antiforgery(page: Page) -> str:
    html = page.content()
    m = re.search(r"const TOKEN = '([^']+)'", html)
    if not m:
        raise RuntimeError("No se encontró TOKEN antiforgery en la página.")
    return m.group(1)


def _crear_cargo_ajax(page: Page, nombre: str) -> tuple[bool, str]:
    page.goto(f"{BASE_URL}/DatosMaestros/Index?tab=cargos", wait_until="networkidle", timeout=60000)
    token = _token_antiforgery(page)
    resp = page.request.post(
        f"{BASE_URL}/DatosMaestros/CrearCargoAjax",
        form={
            "__RequestVerificationToken": token,
            "Nombre": nombre,
        },
    )
    data = resp.json()
    return bool(data.get("exito")), str(data.get("mensaje", ""))


def _crear_cargo(page: Page, nombre: str) -> bool:
    ok, msg = _crear_cargo_ajax(page, nombre)
    if ok or "Ya existe" in msg:
        return True
    return False


def main() -> int:
    creados = 0
    omitidos = 0
    errores: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(60000)

        print(f"Conectando a {BASE_URL} ...")
        _login(page)
        print("Login OK")

        existentes = _cargos_existentes(page)
        print(f"Cargos ya registrados: {len(existentes)}")

        page.goto(f"{BASE_URL}/DatosMaestros/Index?tab=cargos", wait_until="networkidle")

        for nombre in CARGOS:
            if nombre in existentes:
                print(f"  SKIP (ya existe): {nombre}")
                omitidos += 1
                continue
            print(f"  Creando: {nombre}")
            try:
                if _crear_cargo(page, nombre):
                    creados += 1
                    existentes.add(nombre)
                    print("    -> OK")
                else:
                    errores.append(nombre)
                    print("    -> REVISAR (no visible en tabla)")
            except Exception as ex:
                errores.append(f"{nombre}: {ex}")
                print(f"    -> ERROR: {ex}")

        browser.close()

    print("\n--- Resumen ---")
    print(f"Creados: {creados}")
    print(f"Omitidos: {omitidos}")
    print(f"Errores: {len(errores)}")
    for e in errores:
        print(f"  - {e}")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
