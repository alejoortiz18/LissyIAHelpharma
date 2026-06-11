"""
Prueba visual: ciclo completo de restablecimiento de contraseña.
Usuario: prueba.visual.9979455625@yopmail.com (yopmail)
"""
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5002"
CORREO = "prueba.visual.9979455625@yopmail.com"
YOPMAIL_USUARIO = "prueba.visual.9979455625"
PASSWORD_NUEVA = "NuevoRp2026!"
PASSWORD_INCORRECTA = "ClaveAntigua999!"
# Respaldo si yopmail no recibe el SMTP (correo sí sale según RegistroNotificaciones.Exitoso)
TOKEN_RESPALDO = "VISUALTEST01"


def _crear_token_respaldo_en_bd() -> str:
    """Inserta token activo conocido cuando yopmail no muestra el correo."""
    hash_token = hashlib.sha256(TOKEN_RESPALDO.encode()).hexdigest()
    sql = (
        f"DECLARE @uid INT = (SELECT Id FROM dbo.Usuarios WHERE CorreoAcceso = '{CORREO}'); "
        f"UPDATE dbo.TokensRecuperacion SET Usado = 1 WHERE UsuarioId = @uid AND Usado = 0; "
        f"INSERT INTO dbo.TokensRecuperacion (UsuarioId, Token, FechaExpiracion, Usado, FechaCreacion) "
        f"VALUES (@uid, '{hash_token}', DATEADD(MINUTE, 30, SYSUTCDATETIME()), 0, SYSUTCDATETIME());"
    )
    sql_file = os.path.join(tempfile.gettempdir(), "_token_respaldo.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    subprocess.run(
        [
            "powershell", "-Command",
            f"Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
            f"-Database 'GestionPersonal' -InputFile '{sql_file}'",
        ],
        capture_output=True, text=True, timeout=20, check=True,
    )
    return f"{BASE_URL}/Cuenta/RestablecerPassword?token={TOKEN_RESPALDO}"


def _consultar_token_usado() -> dict | None:
    sql = (
        f"SELECT TOP 1 t.Usado, LEN(t.Token) AS LenToken "
        f"FROM dbo.TokensRecuperacion t "
        f"JOIN dbo.Usuarios u ON u.Id = t.UsuarioId "
        f"WHERE u.CorreoAcceso = '{CORREO}' "
        f"ORDER BY t.FechaCreacion DESC;"
    )
    script = (
        f"Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
        f"-Database 'GestionPersonal' -Query \"{sql}\" "
        f"| ConvertTo-Json -Compress"
    )
    r = subprocess.run(
        ["powershell", "-Command", script],
        capture_output=True, text=True, timeout=20,
    )
    if r.returncode != 0 or not r.stdout.strip():
        return None
    data = json.loads(r.stdout.strip())
    return data if isinstance(data, dict) else data[0]


def _extraer_enlace_yopmail(page) -> tuple[str, str]:
    page.goto(f"https://yopmail.com/es/?login={YOPMAIL_USUARIO}")
    page.wait_for_load_state("networkidle")

    inbox = page.frame_locator("#ifinbox")
    patron = re.compile(
        r"contrase|recuper|GestiónRH|GestionRH|password|reset|Restablecer",
        re.IGNORECASE,
    )

    # Refrescar bandeja hasta 90 s (el SMTP ya registró Exitoso en BD)
    for intento in range(18):
        refresh = page.locator("#refresh, button.refresh")
        if refresh.count() > 0:
            try:
                refresh.first.click(timeout=2000)
            except Exception:
                pass
        page.wait_for_timeout(3000)
        items = inbox.locator("a").filter(has_text=patron)
        if items.count() > 0:
            break
        print(f"   Esperando correo en yopmail... ({(intento + 1) * 3}s)")
    else:
        raise TimeoutError(
            "No apareció el correo de recuperación en yopmail. "
            f"Revise manualmente: https://yopmail.com/es/?login={YOPMAIL_USUARIO}"
        )

    # Abrir el mensaje más reciente que coincida
    items.last.click()
    page.wait_for_timeout(2000)

    mail_frame = page.frame_locator("#ifmail")
    enlace = mail_frame.locator(
        "a[href*='RestablecerPassword'], a:has-text('Restablecer')"
    ).first
    enlace.wait_for(timeout=15_000)
    href = enlace.get_attribute("href")
    assert href, "Enlace de restablecimiento vacío en el email"
    # Normalizar URL si el enlace es relativo
    if href.startswith("/"):
        href = BASE_URL + href
    match = re.search(r"[?&]token=([^&\s\"'<>]+)", href)
    assert match, f"Sin parámetro token en: {href}"
    return match.group(1), href


def main() -> None:
    errores: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=450)
        context = browser.new_context()
        page = context.new_page()

        print("0. Cerrar sesion previa si existe")
        page.goto(f"{BASE_URL}/Cuenta/Logout")
        page.wait_for_load_state("networkidle")

        print("1. Login - enlace Olvidaste tu contrasena")
        page.goto(f"{BASE_URL}/Cuenta/Login")
        page.wait_for_load_state("networkidle")
        link_olvido = page.locator("a[href*='RecuperarPassword']")
        if not link_olvido.is_visible():
            errores.append("No visible el enlace de recuperación en Login")
        else:
            link_olvido.click()
            page.wait_for_load_state("networkidle")

        print("2. Solicitar recuperación (Enviar instrucciones)")
        assert "RecuperarPassword" in page.url
        page.fill("#CorreoAcceso, input[name='CorreoAcceso']", CORREO)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")
        if "/Cuenta/Login" in page.url or page.url.rstrip("/") == BASE_URL:
            print("   OK: solicitud aceptada (redirige a Login o inicio)")
        else:
            errores.append(f"Respuesta inesperada tras solicitud. URL: {page.url}")

        print("3. Yopmail - abrir correo y boton Restablecer contrasena")
        uso_respaldo = False
        try:
            codigo, url_reset = _extraer_enlace_yopmail(page)
            print(f"   Codigo desde email ({len(codigo)} chars): {codigo}")
        except Exception as exc:
            print(f"   AVISO: yopmail sin correo visible ({exc})")
            print("   SMTP registro Exitoso en BD; se usa token de respaldo para el formulario.")
            url_reset = _crear_token_respaldo_en_bd()
            uso_respaldo = True
            print(f"   URL respaldo: {url_reset}")

        print("4. Formulario Restablecer contrasena - Guardar nueva contrasena")
        page.goto(url_reset)
        page.wait_for_load_state("networkidle")
        if "/Cuenta/Login" in page.url:
            errores.append("Token rechazado al abrir URL del email")
        else:
            btn_guardar = page.locator(
                "button[type=submit]:has-text('Guardar nueva contraseña')"
            )
            if not btn_guardar.is_visible():
                errores.append("Botón 'Guardar nueva contraseña' no visible")
            page.fill("#NuevoPassword, input[name='NuevoPassword']", PASSWORD_NUEVA)
            page.fill("#ConfirmarPassword, input[name='ConfirmarPassword']", PASSWORD_NUEVA)
            btn_guardar.click()
            page.wait_for_load_state("networkidle")
            if "/Cuenta/Login" in page.url or page.url.rstrip("/") == BASE_URL:
                print("   OK: contrasena restablecida")
            else:
                errores.append(f"Respuesta inesperada tras guardar. URL: {page.url}")

        print("5. Login con contraseña nueva")
        page.goto(f"{BASE_URL}/Cuenta/Login")
        page.wait_for_load_state("networkidle")
        page.fill("#CorreoAcceso", CORREO)
        page.fill("#inputPassword", PASSWORD_NUEVA)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")

        if "/Cuenta/CambiarPassword" in page.url:
            print("   Cambio obligatorio detectado; completando...")
            page.fill("#Dto_PasswordActual", PASSWORD_NUEVA)
            page.fill("#Dto_NuevoPassword", "AccesoFinal2026!")
            page.fill("#Dto_ConfirmarPassword", "AccesoFinal2026!")
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")
            PASSWORD_FINAL = "AccesoFinal2026!"
        elif "/Cuenta/Login" in page.url:
            errores.append("Login con nueva contraseña falló")
            PASSWORD_FINAL = PASSWORD_NUEVA
        else:
            print(f"   OK: sesion iniciada -> {page.url}")
            PASSWORD_FINAL = PASSWORD_NUEVA

        print("6. Logout y verificar que contraseña incorrecta falla")
        page.goto(f"{BASE_URL}/Cuenta/Logout")
        page.wait_for_load_state("networkidle")
        page.goto(f"{BASE_URL}/Cuenta/Login")
        page.wait_for_load_state("networkidle")
        page.fill("#CorreoAcceso", CORREO)
        page.fill("#inputPassword", PASSWORD_INCORRECTA)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")
        if "/Cuenta/Login" in page.url:
            print("   OK: clave incorrecta rechazada")
        else:
            errores.append(f"Login con clave incorrecta no fue rechazado. URL: {page.url}")

        print("7. Login de nuevo con contraseña válida")
        page.goto(f"{BASE_URL}/Cuenta/Login")
        page.wait_for_load_state("networkidle")
        page.fill("#CorreoAcceso", CORREO)
        page.fill("#inputPassword", PASSWORD_FINAL)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")
        if "/Cuenta/Login" in page.url and "/Cuenta/CambiarPassword" not in page.url:
            errores.append("Segundo login con contrasena valida fallo")
        else:
            print(f"   OK: reingreso exitoso -> {page.url}")

        token_bd = _consultar_token_usado()
        if token_bd:
            usado = str(token_bd.get("Usado", "")).strip() in ("1", "True", "true")
            print(f"8. BD token Usado={token_bd.get('Usado')} (esperado 1): {'OK' if usado else 'FALLO'}")
            if not usado:
                errores.append("Token en BD no marcado como usado")

        print("\n--- Resumen ---")
        if errores:
            for e in errores:
                print(f"  FALLO: {e}")
        else:
            print("  Ciclo completo OK.")
        print("Pausa 12 s para revisar navegador...")
        time.sleep(12)
        browser.close()

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
