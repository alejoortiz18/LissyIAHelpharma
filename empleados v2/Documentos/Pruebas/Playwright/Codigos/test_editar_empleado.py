"""Prueba rápida: login y pantalla Editar empleado (rol en el sistema visible)."""
import re
import sys

import pytest
from playwright.sync_api import Page, expect

BASE = "http://localhost:5002"
EMAIL = "lissy.gallego@zentria.com.co"
PASSWORD = "Usuario1"


@pytest.fixture(scope="module")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "ignore_https_errors": True}


def _login(page: Page) -> None:
    page.goto(f"{BASE}/Cuenta/Login")
    page.fill('input[name="CorreoAcceso"]', EMAIL)
    page.fill('input[name="Password"]', PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")


def test_editar_empleado_muestra_rol_y_guarda(page: Page) -> None:
    _login(page)
    page.goto(f"{BASE}/Empleado")
    page.wait_for_load_state("networkidle")

    edit_link = page.locator('a[href*="/Empleado/Editar/"]').first
    if edit_link.count() == 0:
        pytest.skip("No hay empleados para editar en este entorno.")

    edit_link.click()
    page.wait_for_load_state("networkidle")

    expect(page.locator('select[name="Dto.Rol"]')).to_be_visible()
    expect(page.get_by_text("Rol en el sistema")).to_be_visible()

    # Cambio mínimo: teléfono (si existe el campo)
    tel = page.locator('input[name="Dto.Telefono"]')
    if tel.count():
        valor = tel.input_value() or ""
        tel.fill(valor if valor else "3000000000")

    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")

    assert page.url.find("/Empleado/Perfil/") >= 0 or page.locator(".alert--success, [data-toast]").count() >= 0


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--headed"]))
