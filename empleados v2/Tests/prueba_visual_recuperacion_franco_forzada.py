from __future__ import annotations

from datetime import date
from playwright.sync_api import sync_playwright
import subprocess

BASE_URL = "http://localhost:5002"
ADMIN_USER = "lissy.gallego@zentria.com.co"
ADMIN_PASS = "Usuario1"
FRANCO_EMAIL = "franco@yopmail.com"
FRANCO_PASS = "FrancoClave2026!"
TOKEN_FORZADO = "FRANCO12345AB"


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


def forzar_token_bd():
    sql = f"""
;WITH ult AS (
    SELECT TOP 1 t.Id
    FROM TokensRecuperacion t
    JOIN Usuarios u ON u.Id = t.UsuarioId
    WHERE u.CorreoAcceso = '{FRANCO_EMAIL}'
    ORDER BY t.Id DESC
)
UPDATE t
SET t.Token = LOWER(CONVERT(varchar(64), HASHBYTES('SHA2_256', '{TOKEN_FORZADO}'), 2)),
    t.Usado = 0,
    t.FechaExpiracion = DATEADD(MINUTE, 30, GETUTCDATE())
FROM TokensRecuperacion t
JOIN ult ON ult.Id = t.Id;
"""
    subprocess.run(
        [
            "sqlcmd",
            "-S",
            r"(localdb)\MSSQLLocalDB",
            "-d",
            "GestionPersonal",
            "-Q",
            sql,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


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
        page.screenshot(path="visual_forzada_01_login_lissy.png", full_page=True)

        print("[2] Crear/validar usuario franco@yopmail.com...")
        page.goto(f"{BASE_URL}/Empleado/Nuevo", wait_until="networkidle")
        stamp = str(int(date.today().strftime("%d%m%Y")))
        page.fill("input[name='Dto.NombreCompleto']", "Franco Yopmail Visual")
        page.fill("input[name='Dto.Cedula']", f"88{stamp}")
        page.fill("input[name='Dto.Telefono']", "3001234567")
        page.fill("input[name='Dto.CorreoElectronico']", FRANCO_EMAIL)
        page.fill("input[name='Dto.Direccion']", "Calle 123")
        page.fill("input[name='Dto.Ciudad']", "Medellin")
        page.fill("input[name='Dto.Departamento']", "Antioquia")
        select_first_value(page, "select[name='Dto.SedeId']")
        page.wait_for_timeout(500)
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
        page.screenshot(path="visual_forzada_02_crear_franco.png", full_page=True)

        print("[3] Solicitar recuperación para Franco...")
        page.goto(f"{BASE_URL}/Cuenta/Logout", wait_until="networkidle")
        page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword", wait_until="networkidle")
        page.fill("#CorreoAcceso", FRANCO_EMAIL)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.screenshot(path="visual_forzada_03_recuperacion_solicitada.png", full_page=True)

        print("[4] Forzar token de recuperación en BD para continuar la prueba visual...")
        forzar_token_bd()

        print("[5] Restablecer contraseña con token válido...")
        page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token={TOKEN_FORZADO}", wait_until="networkidle")
        page.fill("#inputNuevoPassword", FRANCO_PASS)
        page.fill("#inputConfirmarPassword", FRANCO_PASS)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.screenshot(path="visual_forzada_04_password_restablecida.png", full_page=True)

        print("[6] Login con Franco...")
        page.fill("#CorreoAcceso", FRANCO_EMAIL)
        page.fill("#inputPassword", FRANCO_PASS)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.screenshot(path="visual_forzada_05_login_franco.png", full_page=True)

        assert "/Cuenta/Login" not in page.url, "No se pudo iniciar sesión con Franco."
        print("OK: Flujo visual completo (con token controlado en BD) finalizado.")
        page.wait_for_timeout(3000)
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
