"""
Importa sedes en producción (Datos maestros — Lissy).
Ciudad = columna Regional; dirección = 123 para todas.
"""
import sys
import time

from playwright.sync_api import Page, sync_playwright

BASE_URL = "https://serviciosfarma.helpharma.com.co"
LOGIN_EMAIL = "lissy.gallego@zentria.com.co"
LOGIN_PASSWORD = "Usuario1"
DIRECCION = "123"

SEDES = [
    ("Farmacia La America (Medellín)", "Antioquia"),
    ("Farma Niquia", "Antioquia"),
    ("Farma Apartado", "Antioquia"),
    ("Farma Almacentro", "Antioquia"),
    ("CEDI", "Antioquia"),
    ("Farma Tunja", "Centro"),
    ("Farma Bogota", "Centro"),
    ("Farma Pereira", "Eje Cafetero"),
    ("Farma Manizales", "Eje Cafetero"),
    ("Farma Armenia", "Eje Cafetero"),
    ("Farma Monteria", "Norte"),
    ("Farma Cartagena", "Norte"),
    ("Farma Barranquilla", "Norte"),
    ("Farma Popayan", "Occidente"),
    ("Farma Cali Sur", "Occidente"),
    ("Farma Cali", "Occidente"),
    ("Farma Buga", "Occidente"),
    ("Ips Armenia", "Eje Cafetero"),
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


def _sedes_existentes(page: Page) -> set[str]:
    page.goto(f"{BASE_URL}/DatosMaestros/Index?tab=sedes", wait_until="networkidle", timeout=60000)
    if "DatosMaestros" not in page.url and "Catalogos" not in page.url:
        raise RuntimeError(f"No se pudo abrir datos maestros. URL actual: {page.url}")
    nombres: set[str] = set()
    filas = page.locator("table[aria-label='Sedes'] tbody tr")
    for i in range(filas.count()):
        texto = filas.nth(i).locator("td").first.inner_text().strip()
        if texto:
            nombres.add(texto)
    return nombres


def _crear_sede(page: Page, nombre: str, regional: str) -> str:
    page.locator("#btn-nueva-sede").click()
    page.wait_for_timeout(500)
    page.fill("#sede-nombre", nombre)
    page.fill("#sede-ciudad", regional)
    page.fill("#sede-direccion", DIRECCION)
    page.locator("#btn-guardar-sede").click()
    page.wait_for_load_state("networkidle", timeout=30000)
    page.wait_for_timeout(1000)
    toast = page.locator(".toast, [role='alert'], .alert").last
    if toast.count() and toast.is_visible():
        return toast.inner_text().strip()
    if page.locator("table[aria-label='Sedes']").filter(has_text=nombre).count():
        return "OK"
    return "Sin confirmación visible"


def main() -> int:
    creadas = 0
    omitidas = 0
    errores: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(60000)

        print(f"Conectando a {BASE_URL} ...")
        _login(page)
        print("Login OK")

        existentes = _sedes_existentes(page)
        print(f"Sedes ya registradas: {len(existentes)}")

        page.goto(f"{BASE_URL}/DatosMaestros/Index?tab=sedes", wait_until="networkidle")

        for nombre, regional in SEDES:
            if nombre in existentes:
                print(f"  SKIP (ya existe): {nombre}")
                omitidas += 1
                continue
            print(f"  Creando: {nombre} | regional/ciudad={regional} | dir={DIRECCION}")
            try:
                msg = _crear_sede(page, nombre, regional)
                if "Ya existe" in msg or "duplicad" in msg.lower():
                    omitidas += 1
                    print(f"    -> omitida: {msg}")
                elif "creada" in msg.lower() or msg == "OK" or "correctamente" in msg.lower():
                    creadas += 1
                    existentes.add(nombre)
                    print(f"    -> OK: {msg}")
                else:
                    if page.locator("table[aria-label='Sedes']").filter(has_text=nombre).count():
                        creadas += 1
                        existentes.add(nombre)
                        print("    -> OK (visible en tabla)")
                    else:
                        errores.append(f"{nombre}: {msg}")
                        print(f"    -> REVISAR: {msg}")
            except Exception as ex:
                errores.append(f"{nombre}: {ex}")
                print(f"    -> ERROR: {ex}")

        browser.close()

    print("\n--- Resumen ---")
    print(f"Creadas: {creadas}")
    print(f"Omitidas (ya existían): {omitidas}")
    print(f"Errores: {len(errores)}")
    for e in errores:
        print(f"  - {e}")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
