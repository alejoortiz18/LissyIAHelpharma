"""Script de diagnóstico — ejecutar directamente (no con pytest)."""
from playwright.sync_api import sync_playwright

BTN = "button[data-modal-open='modal-nuevo-evento']"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("--- LOGOUT ---")
    page.goto("http://localhost:5002/Cuenta/Logout")
    page.wait_for_load_state("networkidle")
    print("URL after logout:", page.url)

    print("--- LOGIN ---")
    page.goto("http://localhost:5002/Cuenta/Login")
    page.wait_for_load_state("networkidle")
    page.fill("#CorreoAcceso", "carlos.rodriguez@yopmail.com")
    page.fill("#Password", "Usuario1")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")
    print("URL after login:", page.url)

    print("--- NAVIGATE TO EventoLaboral ---")
    page.goto("http://localhost:5002/EventoLaboral")
    page.wait_for_load_state("networkidle")
    print("URL after navigate:", page.url)

    btns = page.locator(BTN)
    count = btns.count()
    print("Button count:", count)
    if count > 0:
        print("Button visible:", btns.first.is_visible())
    print("Page title:", page.title())

    # Check body snippet
    body = page.inner_text("body")[:500]
    print("Body snippet:", body)

    browser.close()
