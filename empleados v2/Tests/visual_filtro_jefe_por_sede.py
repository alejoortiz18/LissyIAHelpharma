"""Prueba visual: jerarquia de Jefe inmediato por cargo y sede."""
import re
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5002"
USER = "lissy.gallego@zentria.com.co"
PASSWORD = "Usuario1"
SCREENSHOT_DIR = "c:/Users/alejandro.ortiz/Documents/helpharma/Desarrollos/lissy/IA/LissyIAHelpharma/empleados v2/Tests"


def get_options(page, selector: str):
    return page.eval_on_selector(
        selector,
        "(s) => Array.from(s.options).map(o => ({"
        "value:o.value, text:o.textContent.trim(),"
        "sedeId:o.dataset.sedeId||'', cargo:o.dataset.cargo||''}))",
    )


def es_cargo_director(cargo: str) -> bool:
    c = (cargo or "").lower()
    return bool(re.search(r"\bdirector\b", c)) and "auxiliar" not in c


def es_cargo_regente(cargo: str) -> bool:
    c = (cargo or "").lower()
    return bool(re.search(r"\bregente\b", c)) and "auxiliar" not in c


def es_cargo_analista(cargo: str) -> bool:
    c = (cargo or "").lower()
    return bool(re.search(r"\banalista\b", c)) and "farmac" in c


def validar_jefes_listados(label: str, jefes: list) -> list[str]:
    errores = []
    for j in jefes:
        if "alejandro" in j["text"].lower():
            errores.append(f"{label}: aparece Alejandro")
        cargo_txt = j["cargo"] or j["text"]
        if "direccionador" in cargo_txt.lower():
            errores.append(f"{label}: cargo Direccionador no debe listarse")
        if not (es_cargo_director(cargo_txt) or es_cargo_regente(cargo_txt) or es_cargo_analista(cargo_txt)):
            errores.append(f"{label}: '{j['text']}' sin cargo Director/Regente/Analista")
        if "(" in j["text"] or ")" in j["text"]:
            errores.append(f"{label}: el jefe se muestra con cargo y no solo nombre")
    return errores


def select_option_by_contains(page, selector: str, text: str) -> str:
    options = get_options(page, selector)
    for opt in options:
        if opt["value"] and text.lower() in opt["text"].lower():
            page.select_option(selector, value=opt["value"])
            return opt["value"]
    raise AssertionError(f"No se encontro opcion '{text}' en {selector}")


def main():
    errores = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()

        print("[1] Login...")
        page.goto(f"{BASE_URL}/Cuenta/Login", wait_until="networkidle")
        page.fill("input[name='CorreoAcceso']", USER)
        page.fill("input[name='Password']", PASSWORD)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")

        print("[2] Nuevo empleado...")
        page.goto(f"{BASE_URL}/Empleado/Nuevo", wait_until="networkidle")
        page.wait_for_selector("#jefe-inmediato-select")

        sedes = [s for s in get_options(page, "select[name='Dto.SedeId']") if s["value"]]
        sede_por_id = {s["value"]: s["text"] for s in sedes}

        page.screenshot(path=f"{SCREENSHOT_DIR}/visual_jefe_01_inicial.png", full_page=True)

        # Recorrer sedes para descubrir jefes por sede para AUXILIAR
        select_option_by_contains(page, "select[name='Dto.CargoId']", "Auxiliar")
        todos_jefes = []
        vistos = set()
        for s in sedes:
            page.select_option("select[name='Dto.SedeId']", value=s["value"])
            page.wait_for_timeout(400)
            for j in get_options(page, "select[name='Dto.JefeInmediatoId']"):
                if j["value"] and j["value"] not in vistos:
                    vistos.add(j["value"])
                    j["sedeId"] = s["value"]
                    todos_jefes.append(j)

        print(f"[3] Candidatos jefe en modo Auxiliar: {len(todos_jefes)}")
        for j in todos_jefes:
            sede_nom = sede_por_id.get(j["sedeId"], j["sedeId"])
            print(f"    {sede_nom} | {j['text']}")

        sedes_con_jefe = {j["sedeId"] for j in todos_jefes}
        probar_ids = set()
        for s in sedes:
            t = s["text"].lower()
            if "bogot" in t or "medell" in t:
                probar_ids.add(s["value"])
        probar_ids.update(list(sedes_con_jefe)[:3])

        resultados = {}
        for sede_id in probar_ids:
            label = sede_por_id.get(sede_id, sede_id)
            print(f"[4] Sede: {label} (id={sede_id})")
            page.select_option("select[name='Dto.SedeId']", value=sede_id)
            page.wait_for_timeout(900)
            jefes = [j for j in get_options(page, "select[name='Dto.JefeInmediatoId']") if j["value"]]
            resultados[label] = jefes
            print(f"    Jefes visibles: {len(jefes)}")
            for j in jefes:
                print(f"      - {j['text']}")
            errores.extend(validar_jefes_listados(label, jefes))

            esperados = [j for j in todos_jefes if j["sedeId"] == sede_id]
            dirs = [j for j in esperados if es_cargo_director(j["cargo"])]
            regs = [j for j in esperados if es_cargo_regente(j["cargo"])]
            ans = [j for j in esperados if es_cargo_analista(j["cargo"])]
            esperado_ids = {j["value"] for j in (dirs if dirs else (regs if regs else ans))}
            visible_ids = {j["value"] for j in jefes}
            if esperado_ids and visible_ids != esperado_ids:
                errores.append(
                    f"{label}: se esperaban ids {esperado_ids}, se ven {visible_ids}"
                )

            safe_name = re.sub(r"[^\w]+", "_", label)[:40]
            page.screenshot(
                path=f"{SCREENSHOT_DIR}/visual_jefe_{safe_name}.png", full_page=True
            )

        # Regla Analista: sin jefe inmediato (se valida en Editar empleado ya existente)
        print("[5] Validando Analista en Editar empleado...")
        page.goto(f"{BASE_URL}/Empleado/Editar/15", wait_until="networkidle")
        page.wait_for_selector("#jefe-inmediato-select")
        jefes_analista = get_options(page, "#jefe-inmediato-select")
        jefes_analista_con_valor = [x for x in jefes_analista if x["value"]]
        if jefes_analista_con_valor:
            errores.append("Analista: no debe mostrar opciones de jefe con valor")
        if not any(not x["value"] for x in jefes_analista):
            errores.append("Analista: debe mostrar opcion 'Sin jefe inmediato'")
        page.screenshot(path=f"{SCREENSHOT_DIR}/visual_jefe_analista_sin_jefe.png", full_page=True)

        print("[6] Revision visual 8 segundos...")
        page.wait_for_timeout(8000)
        context.close()
        browser.close()

    if errores:
        print("\nFALLOS:")
        for e in errores:
            print(f"  - {e}")
        raise SystemExit(1)

    print("\nOK: prueba visual completada sin guardar empleado.")


if __name__ == "__main__":
    main()
