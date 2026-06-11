from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import time

from playwright.sync_api import Page, sync_playwright

BASE_URL = "http://localhost:5002"
USER = "lissy.gallego@zentria.com.co"
PASSWORD = "Usuario1"


@dataclass
class Creado:
    nombre: str
    sede_label: str
    rol: str


def fill(page: Page, selector: str, value: str) -> None:
    page.fill(selector, value)


def select_by_label_contains(page: Page, selector: str, text: str) -> str:
    options = page.eval_on_selector(
        selector,
        "(s) => Array.from(s.options).map(o => ({value:o.value, text:o.textContent.trim()}))",
    )
    for opt in options:
        if opt["value"] and text.lower() in opt["text"].lower():
            page.select_option(selector, value=opt["value"])
            return opt["text"]
    raise AssertionError(f"No se encontró opción con '{text}' en {selector}")


def get_options(page: Page, selector: str):
    return page.eval_on_selector(
        selector,
        "(s) => Array.from(s.options).map(o => ({value:o.value, text:o.textContent.trim()}))",
    )


def login(page: Page) -> None:
    page.goto(f"{BASE_URL}/Cuenta/Login", wait_until="networkidle")
    fill(page, "input[name='CorreoAcceso']", USER)
    fill(page, "input[name='Password']", PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")


def create_employee(
    page: Page,
    nombre: str,
    rol: str,
    sede_contains: str,
    jefe_nombre_contains: str | None = None,
) -> Creado:
    page.goto(f"{BASE_URL}/Empleado/Nuevo", wait_until="networkidle")

    # Datos base únicos
    stamp = str(int(time.time() * 1000))[-8:]
    cedula = f"9{stamp}"
    correo = f"qa.{stamp}@yopmail.com"
    hoy = date.today().isoformat()

    fill(page, "input[name='Dto.NombreCompleto']", nombre)
    fill(page, "input[name='Dto.Cedula']", cedula)
    fill(page, "input[name='Dto.Telefono']", "3001234567")
    fill(page, "input[name='Dto.CorreoElectronico']", correo)
    fill(page, "input[name='Dto.Direccion']", "Calle QA 123")
    fill(page, "input[name='Dto.Ciudad']", "Bogota")
    fill(page, "input[name='Dto.Departamento']", "Cundinamarca")

    sede_label = select_by_label_contains(page, "select[name='Dto.SedeId']", sede_contains)
    page.wait_for_timeout(500)

    # Cargo: primero válido
    cargos = get_options(page, "select[name='Dto.CargoId']")
    cargo = next((c for c in cargos if c["value"]), None)
    assert cargo is not None, "No hay cargos disponibles"
    page.select_option("select[name='Dto.CargoId']", value=cargo["value"])

    page.select_option("select[name='Dto.Rol']", value=rol)
    page.select_option("select[name='Dto.TipoVinculacion']", value="Directo")
    fill(page, "input[name='Dto.FechaIngreso']", hoy)
    fill(page, "input[name='Dto.FechaInicioContrato']", hoy)

    if jefe_nombre_contains:
        jefes = get_options(page, "select[name='Dto.JefeInmediatoId']")
        jefe = next(
            (j for j in jefes if j["value"] and jefe_nombre_contains.lower() in j["text"].lower()),
            None,
        )
        assert jefe is not None, f"No aparece jefe esperado: {jefe_nombre_contains}"
        page.select_option("select[name='Dto.JefeInmediatoId']", value=jefe["value"])
    else:
        page.select_option("select[name='Dto.JefeInmediatoId']", value="")

    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    assert "/Empleado" in page.url, "No regresó a módulo Empleados tras guardar"
    assert page.locator(".alert--error, .validation-summary-errors").count() == 0, "Formulario devolvió errores"
    print(f"[OK] Empleado creado: {nombre} ({rol}) en {sede_label}")
    return Creado(nombre=nombre, sede_label=sede_label, rol=rol)


def validate_jefe_options(page: Page, sede_contains: str):
    page.goto(f"{BASE_URL}/Empleado/Nuevo", wait_until="networkidle")
    sede_label = select_by_label_contains(page, "select[name='Dto.SedeId']", sede_contains)
    page.wait_for_timeout(800)
    opts = get_options(page, "select[name='Dto.JefeInmediatoId']")
    print(f"[CHECK] Jefes para '{sede_label}': {[o['text'] for o in opts]}")
    return sede_label, opts


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=180)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        login(page)

        # Caso 1: sede sin Director (solo Regente) -> Bogotá (estado actual)
        _, jefes_bog_inicial = validate_jefe_options(page, "Bogotá")
        assert len([o for o in jefes_bog_inicial if o["value"]]) == 0, (
            "La sede Bogotá debe iniciar sin jefe administrativo para validar caso Regente-only."
        )

        reg_qa = create_employee(
            page=page,
            nombre=f"Regente Bogota QA {int(time.time())}",
            rol="Regente",
            sede_contains="Bogotá",
            jefe_nombre_contains=None,
        )

        _, jefes_qa = validate_jefe_options(page, "Bogotá")
        assert any(reg_qa.nombre.lower() in o["text"].lower() for o in jefes_qa if o["value"]), (
            "En sede sin Director debe aparecer Regente como jefe inmediato"
        )

        # Caso 2: sede con Director + Regente (prioridad Director)
        dir_bog = create_employee(
            page=page,
            nombre=f"Director Bogota QA {int(time.time())}",
            rol="DirectorTecnico",
            sede_contains="Bogotá",
            jefe_nombre_contains=None,
        )

        reg_bog = create_employee(
            page=page,
            nombre=f"Regente Bogota QA {int(time.time())}",
            rol="Regente",
            sede_contains="Bogotá",
            jefe_nombre_contains=dir_bog.nombre,
        )

        _, jefes_bog = validate_jefe_options(page, "Bogotá")
        assert any(dir_bog.nombre.lower() in o["text"].lower() for o in jefes_bog), (
            "Con Director+Regente debe aparecer Director"
        )
        assert not any(reg_bog.nombre.lower() in o["text"].lower() for o in jefes_bog), (
            "Con Director+Regente no debe mostrarse Regente en jefe inmediato"
        )

        # Caso 3: filtro por sede (no mezclar jefes entre sedes)
        _, jefes_med = validate_jefe_options(page, "Medellín")
        assert not any(dir_bog.nombre.lower() in o["text"].lower() for o in jefes_med), (
            "Jefes de Bogotá no deben aparecer en Medellín"
        )

        page.screenshot(path="resultado_validacion_jerarquia_sede.png", full_page=True)
        print("\nValidacion completada: comportamiento conforme a reglas de negocio.")
        print("   - Sede sin Director: usa Regente.")
        print("   - Sede con Director+Regente: usa Director.")
        print("   - Filtro por sede aplicado correctamente.")
        print("   - No se mezclan jefes entre sedes.")
        page.wait_for_timeout(3000)
        context.close()
        browser.close()


if __name__ == "__main__":
    main()

