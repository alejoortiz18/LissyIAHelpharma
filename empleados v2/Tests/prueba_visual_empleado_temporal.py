"""
Prueba visual (navegador headed): crear empleado Temporal sin fin de contrato.
Usuario de sesión: lissy.gallego@zentria.com.co / Usuario1
Correo del empleado nuevo: @yopmail.com
"""
import time
from datetime import date

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5002"
LOGIN_EMAIL = "lissy.gallego@zentria.com.co"
LOGIN_PASSWORD = "Usuario1"

FECHA_INGRESO = "2026-06-01"
CEDULA = f"99{int(time.time()) % 100000000:08d}"[:10]
CORREO_EMPLEADO = f"prueba.visual.{CEDULA}@yopmail.com"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        print(f"1. Login como {LOGIN_EMAIL}")
        page.goto(f"{BASE_URL}/Cuenta/Login")
        page.wait_for_load_state("networkidle")
        page.fill("#CorreoAcceso", LOGIN_EMAIL)
        page.fill("#inputPassword", LOGIN_PASSWORD)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")

        if "/Cuenta/CambiarPassword" in page.url:
            print("   → Cambio de contraseña obligatorio; completando...")
            page.fill("#Dto_PasswordActual", LOGIN_PASSWORD)
            page.fill("#Dto_NuevoPassword", "NuevaClave2026!")
            page.fill("#Dto_ConfirmarPassword", "NuevaClave2026!")
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")

        print(f"2. Nuevo empleado (CC {CEDULA}, correo {CORREO_EMPLEADO})")
        page.goto(f"{BASE_URL}/Empleado/Nuevo")
        page.wait_for_load_state("networkidle")

        if "/Cuenta/Login" in page.url:
            browser.close()
            raise SystemExit(
                "No se pudo acceder a Nuevo empleado (sesión no válida). "
                "Use HTTPS o revise credenciales."
            )

        page.fill("input[name='Dto.NombreCompleto']", f"Prueba Visual {CEDULA}")
        page.fill("input[name='Dto.Cedula']", CEDULA)
        page.fill("input[name='Dto.Telefono']", "3005550101")
        page.fill("input[name='Dto.CorreoElectronico']", CORREO_EMPLEADO)
        page.fill("input[name='Dto.Direccion']", "Calle Prueba 123")
        page.fill("input[name='Dto.Ciudad']", "Bogotá")
        page.fill("input[name='Dto.Departamento']", "Cundinamarca")
        page.select_option("select[name='Dto.SedeId']", index=1)
        page.select_option("select[name='Dto.CargoId']", index=1)
        page.select_option("select[name='Dto.Rol']", index=1)
        page.select_option("#TipoVinculacion", "Temporal")
        page.fill("input[name='Dto.FechaIngreso']", FECHA_INGRESO)
        page.select_option("select[name='Dto.EmpresaTemporalId']", index=1)
        # Sin FechaFinContrato — debe aplicar +6 meses (2026-12-01)

        print("3. Guardar (sin fin de contrato)")
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        if "/Empleado" in page.url and "Nuevo" not in page.url:
            print("   OK: redirigió a listado de empleados.")
        elif page.locator(".form-error").count() > 0:
            errores = [
                e.inner_text().strip()
                for e in page.locator(".form-error").all()
                if e.is_visible() and e.inner_text().strip()
            ]
            print(f"   Errores en formulario: {errores}")
        else:
            print(f"   URL final: {page.url}")

        print("4. Pausa 15 s para revisar en el navegador...")
        time.sleep(15)
        browser.close()


if __name__ == "__main__":
    main()
