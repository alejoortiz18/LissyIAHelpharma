"""
Revisa sedes en producción vs lista objetivo; inserta solo las faltantes no ambiguas.
"""
import re
import sys

from playwright.sync_api import Page, sync_playwright

BASE_URL = "https://serviciosfarma.helpharma.com.co"
LOGIN_EMAIL = "lissy.gallego@zentria.com.co"
LOGIN_PASSWORD = "Usuario1"
DIRECCION = "123"

# Lista exacta del usuario (imagen)
SEDES_OBJETIVO = [
    "IPS Almacentro Piso 11 (Medellín)",
    "Farmacia La America (Medellín)",
    "Farmacia Almacentro (Local 285)",
    "Farma Sur",
    "Farma Norte",
    "Farma Niquia",
    "Farma Apartado",
    "Farma Almacentro",
    "CEDI",
    "Domicilios Medellin",
    "IPS Panorama (Bogotá)",
    "Farma Tunja",
    "Farma Bogota",
    "IPS Centro de Especialistas DASHA (Manizales)",
    "Farma Pereira",
    "Farma Manizales",
    "Farma Armenia",
    "IPS Mall San Vicente (Barranquilla)",
    "Farma Monteria",
    "Farma Cartagena",
    "Farma Barranquilla",
    "IPS Tequendama (Cali)",
    "Farma Popayan",
    "Farma Cali Sur",
    "Farma Cali",
    "Farma Buga",
    "IPS City Médica (Rionegro)",
    "Administrativo",
    "Ips Pereira",
    "Ips Armenia",
    "Equipo Estrategico",
    "Supernumerario",
    "Fmanizales2",
]

# No insertar (ya existe o pendiente confirmación)
SEDES_NO_INSERTAR = {
    "Ips Armenia",  # ya existe en BD
    "Equipo Estrategico",  # sin confirmación del usuario
    "Farma Sur",  # ciudad sin confirmar
    "Farma Norte",  # ciudad sin confirmar
}

# Ciudad inferida solo para sedes físicas claras (nombre contiene ciudad o patrón conocido)
CIUDAD_POR_SEDE = {
    "IPS Almacentro Piso 11 (Medellín)": "Medellín",
    "Farmacia La America (Medellín)": "Medellín",
    "Farmacia Almacentro (Local 285)": "Medellín",
    "Domicilios Medellin": "Medellín",
    "IPS Panorama (Bogotá)": "Bogotá",
    "IPS Centro de Especialistas DASHA (Manizales)": "Manizales",
    "IPS Mall San Vicente (Barranquilla)": "Barranquilla",
    "IPS Tequendama (Cali)": "Cali",
    "IPS City Médica (Rionegro)": "Rionegro",
    "Farma Tunja": "Tunja",
    "Farma Bogota": "Bogotá",
    "Farma Pereira": "Pereira",
    "Farma Manizales": "Manizales",
    "Farma Armenia": "Armenia",
    "Farma Monteria": "Montería",
    "Farma Cartagena": "Cartagena",
    "Farma Barranquilla": "Barranquilla",
    "Farma Popayan": "Popayán",
    "Farma Cali Sur": "Cali",
    "Farma Cali": "Cali",
    "Farma Buga": "Buga",
    "Farma Niquia": "Medellín",
    "Farma Apartado": "Apartadó",
    "Farma Almacentro": "Medellín",
    "CEDI": "Medellín",
    "Administrativo": "General",
    "Supernumerario": "General",
    "Fmanizales2": "Manizales",
    "Ips Pereira": "Pereira",
}


def _login(page: Page) -> None:
    page.goto(f"{BASE_URL}/Cuenta/Login", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#CorreoAcceso", timeout=30000)
    page.fill("#CorreoAcceso", LOGIN_EMAIL)
    page.fill("#inputPassword", LOGIN_PASSWORD)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle", timeout=60000)


def _token(page: Page) -> str:
    html = page.content()
    m = re.search(r"const TOKEN = '([^']+)'", html)
    if not m:
        raise RuntimeError("TOKEN antiforgery no encontrado")
    return m.group(1)


def _sedes_en_produccion(page: Page) -> list[str]:
    page.goto(f"{BASE_URL}/DatosMaestros/Index?tab=sedes", wait_until="networkidle", timeout=60000)
    nombres: list[str] = []
    filas = page.locator("table[aria-label='Sedes'] tbody tr")
    for i in range(filas.count()):
        t = filas.nth(i).locator("td").first.inner_text().strip()
        if t:
            nombres.append(t)
    return nombres


def _crear_sede_ajax(page: Page, nombre: str, ciudad: str) -> tuple[bool, str]:
    page.goto(f"{BASE_URL}/DatosMaestros/Index?tab=sedes", wait_until="networkidle", timeout=60000)
    token = _token(page)
    resp = page.request.post(
        f"{BASE_URL}/DatosMaestros/CrearSedeAjax",
        form={
            "__RequestVerificationToken": token,
            "Nombre": nombre,
            "Ciudad": ciudad,
            "Direccion": DIRECCION,
        },
    )
    data = resp.json()
    return bool(data.get("exito")), str(data.get("mensaje", ""))


def main() -> int:
    insertar = "--insertar" in sys.argv

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(60000)
        _login(page)
        existentes = set(_sedes_en_produccion(page))
        browser.close()

    ya_existen = []
    faltan_claras = []
    dudosas = []

    for nombre in SEDES_OBJETIVO:
        if nombre in SEDES_NO_INSERTAR:
            dudosas.append(nombre)
            continue
        if nombre in existentes:
            ya_existen.append(nombre)
        else:
            faltan_claras.append(nombre)

    print("=== SEDES EN PRODUCCION (", len(existentes), ") ===")
    for n in sorted(existentes):
        print(" ", n)

    print("\n=== YA EXISTEN (no insertar) ===", len(ya_existen))
    for n in ya_existen:
        print(" ", n)

    print("\n=== FALTAN - CLARAS (candidatas a insertar) ===", len(faltan_claras))
    for n in faltan_claras:
        print(" ", n, "| ciudad propuesta:", CIUDAD_POR_SEDE.get(n, "?"))

    print("\n=== OMITIDAS (no insertar por ahora) ===", len(dudosas))
    for n in dudosas:
        existe = "SI" if n in existentes else "NO"
        print(" ", n, "| en BD:", existe)

    if not insertar:
        print("\n(Modo solo revision. Ejecutar con --insertar para crear faltantes claras.)")
        return 0

    if not faltan_claras:
        print("\nNada que insertar (claras).")
        return 0

    creadas = 0
    errores = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        _login(page)
        for nombre in faltan_claras:
            ciudad = CIUDAD_POR_SEDE.get(nombre)
            if not ciudad:
                errores.append(f"{nombre}: sin ciudad definida")
                continue
            ok, msg = _crear_sede_ajax(page, nombre, ciudad)
            if ok or "Ya existe" in msg:
                creadas += 1
                print(f"OK: {nombre}")
            else:
                errores.append(f"{nombre}: {msg}")
        browser.close()

    print(f"\nInsertadas: {creadas}, errores: {len(errores)}")
    for e in errores:
        print(" ", e)
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
