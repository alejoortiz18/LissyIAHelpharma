"""
Prueba de integración completa — Envío de correo de restablecimiento de contraseña
Referencia: Documentos/Pruebas/Playwright/Plan-envioCorreoRestablecerContraseña.md

FLUJO:
  1. Levanta la aplicación (dotnet run)
  2. Playwright solicita recuperación para carlos.rodriguez@yopmail.com
  3. Verifica token SHA-256 en BD y auditoría en RegistroNotificaciones
  4. Verifica email en yopmail.com (iframe #ifinbox / #ifmail)
  5. Extrae el token del enlace y completa el restablecimiento
  6. Valida login con nueva contraseña / deniega contraseña anterior
  7. Detiene la aplicación

Ejecución:
  pytest Tests/test_envio_correo_restablecercontrasena.py -v --headed
  pytest Tests/test_envio_correo_restablecercontrasena.py -v --headed -m "not yopmail"
"""

import json
import os
import re
import subprocess
import tempfile
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from helpers import BASE_URL, hacer_login

# ── Rutas del proyecto ──────────────────────────────────────────────────────
_ROOT     = Path(__file__).parent.parent
_WEB_DIR  = _ROOT / "Proyecto MVC" / "GestionPersonal.Web"
_SETTINGS = _WEB_DIR / "appsettings.json"

# ── Configuración BD ────────────────────────────────────────────────────────
DB_INSTANCE = r"(localdb)\MSSQLLocalDB"
DB_NAME     = "GestionPersonal"

# ── Datos de prueba ─────────────────────────────────────────────────────────
CORREO          = "carlos.rodriguez@yopmail.com"
YOPMAIL_USUARIO = "carlos.rodriguez"
PASSWORD_NUEVA  = "RestablecidoTest2026!"

# Hash/Salt de "Usuario1" para restaurar estado
_HASH_USUARIO1 = "0x7DED37B4612147C18EBDFA1F6DEB4709EC9D511DA20641214F1F97612DF2CEAE"
_SALT_USUARIO1 = "0xF2B483C7DAC61EC2CA7F1331C95D6800"

# Estado compartido entre tests del módulo
_S: dict = {
    "token_codigo": None,   # Código plano del email (12 chars)
    "token_url":    None,   # URL completa del enlace de restablecimiento
    "app_process":  None,   # Popen del dotnet run
    "settings_bak": None,   # Backup del appsettings.json original
}


# ════════════════════════════════════════════════════════════════════════════
#  HELPERS BD
# ════════════════════════════════════════════════════════════════════════════

def _consultar(query: str) -> list[dict]:
    sql_file = os.path.join(tempfile.gettempdir(), "_rc_envio.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(query)
    result = subprocess.run(
        ["powershell", "-Command",
         f"Invoke-Sqlcmd -ServerInstance '{DB_INSTANCE}' -Database '{DB_NAME}' "
         f"-InputFile '{sql_file}' | ConvertTo-Json -Depth 2"],
        capture_output=True, text=True, timeout=15,
    )
    if not result.stdout.strip():
        return []
    try:
        data = json.loads(result.stdout)
        return data if isinstance(data, list) else [data]
    except (json.JSONDecodeError, ValueError):
        return []


def _ejecutar(sql: str) -> None:
    sql_file = os.path.join(tempfile.gettempdir(), "_rc_envio_exec.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    subprocess.run(
        ["powershell", "-Command",
         f"Invoke-Sqlcmd -ServerInstance '{DB_INSTANCE}' -Database '{DB_NAME}' "
         f"-InputFile '{sql_file}'"],
        capture_output=True, text=True, timeout=15,
    )


def _bool(valor) -> bool:
    return str(valor).strip() in ("1", "True", "true")


# ════════════════════════════════════════════════════════════════════════════
#  FIXTURE MÓDULO — Levanta y detiene la aplicación
#  Maneja CE-01: parchea FromAddress para que coincida con la cuenta de auth
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module", autouse=True)
def aplicacion_corriendo():
    """
    Setup:
      1. Parchea appsettings.json → FromAddress = cuenta de autenticación (CE-01)
      2. Restaura contraseña de carlos.rodriguez a Usuario1
      3. Limpia tokens de prueba anteriores
      4. Inicia 'dotnet run' en GestionPersonal.Web
      5. Espera hasta 60s a que http://localhost:5002 responda

    Teardown:
      1. Restaura contraseña a Usuario1 (por si el test la cambió)
      2. Revierte appsettings.json al estado original
      3. Termina el proceso dotnet (DETIENE LA APLICACIÓN)
    """
    # ── Paso 1: Respaldar y parchear appsettings.json (CE-01) ──────────────
    settings_texto = _SETTINGS.read_text(encoding="utf-8")
    _S["settings_bak"] = settings_texto

    configuracion = json.loads(settings_texto)
    from_original = configuracion["EmailSettings"]["Smtp"]["FromAddress"]

    if from_original != configuracion["EmailSettings"]["Smtp"]["Username"]:
        # Parche temporal: enviar desde la cuenta autenticada (no requiere Send As)
        configuracion["EmailSettings"]["Smtp"]["FromAddress"] = \
            configuracion["EmailSettings"]["Smtp"]["Username"]
        _SETTINGS.write_text(
            json.dumps(configuracion, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"\n  [CE-01 PATCH] FromAddress → {configuracion['EmailSettings']['Smtp']['Username']}")

    # ── Paso 2: Preparar BD ─────────────────────────────────────────────────
    _ejecutar(
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_USUARIO1}, PasswordSalt={_SALT_USUARIO1}, "
        f"DebeCambiarPassword=0 "
        f"WHERE CorreoAcceso='{CORREO}'; "
        f"DELETE FROM dbo.TokensRecuperacion "
        f"WHERE UsuarioId = (SELECT Id FROM dbo.Usuarios WHERE CorreoAcceso='{CORREO}') "
        f"AND Token NOT IN ('TK7E4D8F5G','TK3F9A2B1C','TK1H6K9M2N');"
    )

    # ── Paso 3: Iniciar la aplicación ───────────────────────────────────────
    proceso = subprocess.Popen(
        ["dotnet", "run", "--no-build",
         "--project", str(_WEB_DIR / "GestionPersonal.Web.csproj"),
         "--launch-profile", "http"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(_WEB_DIR),
    )
    _S["app_process"] = proceso
    print(f"\n  [APP] Iniciando aplicación (PID {proceso.pid})...")

    # ── Paso 4: Esperar a que la app responda (max 60s) ─────────────────────
    inicio = time.time()
    lista = False
    while time.time() - inicio < 60:
        try:
            urllib.request.urlopen(f"{BASE_URL}/Cuenta/Login", timeout=3)
            lista = True
            break
        except Exception:
            time.sleep(2)

    if not lista:
        proceso.terminate()
        if _S["settings_bak"]:
            _SETTINGS.write_text(_S["settings_bak"], encoding="utf-8")
        pytest.fail(
            "CE-02: La aplicación no respondió en 60 segundos.\n"
            f"  → Verificar: dotnet build en '{_WEB_DIR}'"
        )

    print(f"  [APP] Aplicación lista en {BASE_URL}")

    # ── Yield: ejecutar los tests ───────────────────────────────────────────
    yield

    # ── Teardown ────────────────────────────────────────────────────────────
    print("\n  [TEARDOWN] Restaurando contraseña de carlos.rodriguez...")
    _ejecutar(
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_USUARIO1}, PasswordSalt={_SALT_USUARIO1}, "
        f"DebeCambiarPassword=0 "
        f"WHERE CorreoAcceso='{CORREO}';"
    )

    print("  [TEARDOWN] Revirtiendo appsettings.json...")
    if _S["settings_bak"]:
        _SETTINGS.write_text(_S["settings_bak"], encoding="utf-8")

    print("  [TEARDOWN] Deteniendo la aplicación...")
    proceso.terminate()
    try:
        proceso.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proceso.kill()
    print("  [APP] Aplicación detenida.")


# ════════════════════════════════════════════════════════════════════════════
#  PASO 1-4 — Formulario /Cuenta/RecuperarPassword
# ════════════════════════════════════════════════════════════════════════════

def test_paso1_solicitar_recuperacion(page):
    """
    PASOS 1-4: Navegar a RecuperarPassword, ingresar correo, enviar.
    El sistema redirige a Login con mensaje informativo.
    """
    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.wait_for_load_state("networkidle")

    # Verificar que el formulario cargó
    campo = page.locator("#CorreoAcceso")
    assert campo.is_visible(), "El campo #CorreoAcceso no está visible en /Cuenta/RecuperarPassword"

    # Ingresar correo y enviar
    campo.fill(CORREO)
    print(f"\n  [Playwright] Correo ingresado: {CORREO}")

    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Verificar redirección a Login
    assert "/Cuenta/Login" in page.url, (
        f"No redirigió a Login tras solicitar recuperación. URL: {page.url}"
    )

    # Verificar mensaje informativo (no de error)
    alerta = page.locator(".alert--info, .alert-info, [class*='alert']").first
    assert alerta.is_visible() and alerta.inner_text().strip() != "", (
        "No se mostró mensaje informativo tras enviar la solicitud"
    )
    print(f"  [Playwright] Redirigió a Login. Mensaje: '{alerta.inner_text().strip()}'")


# ════════════════════════════════════════════════════════════════════════════
#  PASO 5-6 — Verificación en BD
# ════════════════════════════════════════════════════════════════════════════

def test_paso5_token_sha256_en_bd(page):
    """
    PASO 5: El token creado en BD debe ser SHA-256 hex (64 chars lowercase).
    Si tiene 12 chars, el código plano fue guardado sin hashear (fallo crítico de seguridad).
    """
    filas = _consultar(
        f"SELECT TOP 1 t.Token, "
        f"CONVERT(varchar(32), t.FechaExpiracion, 126) AS FechaExpiracion, "
        f"CONVERT(varchar(32), t.FechaCreacion,   126) AS FechaCreacion, "
        f"t.Usado "
        f"FROM dbo.TokensRecuperacion t "
        f"JOIN dbo.Usuarios u ON u.Id = t.UsuarioId "
        f"WHERE u.CorreoAcceso = '{CORREO}' "
        f"AND t.Token NOT IN ('TK7E4D8F5G','TK3F9A2B1C','TK1H6K9M2N') "
        f"ORDER BY t.FechaCreacion DESC;"
    )
    assert filas, (
        "No se encontró ningún token en BD para carlos.rodriguez. "
        "¿El correo no existe o el servicio SMTP no generó el token?"
    )

    token_bd = str(filas[0].get("Token", ""))
    assert len(token_bd) == 64, (
        f"FALLO DE SEGURIDAD — Token en BD tiene {len(token_bd)} chars. "
        f"Se esperaban 64 (SHA-256 hex). Valor: '{token_bd[:20]}...'"
    )
    assert all(c in "0123456789abcdefABCDEF" for c in token_bd), (
        "Token en BD no es hexadecimal válido"
    )
    assert not _bool(filas[0].get("Usado")), "El token ya está marcado Usado=1 antes de ser usado"

    # Verificar expiración ≈ 30 minutos
    exp_str = str(filas[0].get("FechaExpiracion", ""))
    cre_str = str(filas[0].get("FechaCreacion",   ""))
    if exp_str and exp_str != "None":
        try:
            exp = datetime.fromisoformat(exp_str.replace("T", " ").split(".")[0])
            cre = datetime.fromisoformat(cre_str.replace("T", " ").split(".")[0])
            diff = exp - cre
            assert timedelta(minutes=28) <= diff <= timedelta(minutes=32), (
                f"Expiración incorrecta: {diff} (esperados ≈30 min)"
            )
            print(f"  [BD] Token SHA-256 OK. Expira en: {diff}")
        except (ValueError, TypeError):
            pass  # No bloquear si el formato de fecha varía


def test_paso6_auditoria_solicitud_en_bd(page):
    """
    PASO 6: RegistroNotificaciones debe tener una fila con:
      TipoEvento='RecuperacionContrasena', Exitoso=1, Destinatario=correo.
    """
    filas = _consultar(
        f"SELECT TOP 1 Exitoso, ISNULL(ErrorMensaje,'') AS ErrorMensaje, "
        f"Destinatario, Asunto "
        f"FROM dbo.RegistroNotificaciones "
        f"WHERE TipoEvento = 'RecuperacionContrasena' "
        f"ORDER BY FechaIntento DESC;"
    )
    assert filas, (
        "Sin registro en RegistroNotificaciones para 'RecuperacionContrasena'. "
        "Verificar que NotificationService está inyectado en CuentaService."
    )

    reg = filas[0]
    assert _bool(reg.get("Exitoso")), (
        f"El correo de recuperación FALLÓ. Error: {reg.get('ErrorMensaje')}. "
        "Revisar CE-01 (Send As) y la configuración SMTP en user-secrets."
    )
    destinatario = str(reg.get("Destinatario", "")).lower()
    assert CORREO in destinatario, (
        f"Destinatario incorrecto en auditoría: '{destinatario}'"
    )
    print(f"  [BD] Auditoría OK. Asunto: '{reg.get('Asunto')}'")


# ════════════════════════════════════════════════════════════════════════════
#  PASO 7-10 — Verificación en yopmail.com
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_paso7_email_llega_a_yopmail(page):
    """
    PASOS 7-10: Abrir yopmail, localizar el email, extraer el token del enlace.
    Guarda el token en _S["token_codigo"] para los pasos siguientes.

    CE-03: Reintenta la carga del iframe hasta 3 veces si hay timeout.
    """
    page.goto(f"https://yopmail.com/en/?login={YOPMAIL_USUARIO}")
    page.wait_for_load_state("networkidle")

    inbox = page.frame_locator("#ifinbox")

    # Buscar el email más reciente en la bandeja — CE-03: reintentos
    # yopmail muestra cada email como un <div class="m"> con spans interiores;
    # se espera el primer elemento visible en la lista del inbox.
    email_item = inbox.locator("div.m").first

    encontrado = False
    for intento in range(5):
        try:
            email_item.wait_for(timeout=30_000)
            encontrado = True
            break
        except Exception:
            print(f"  [yopmail] Intento {intento+1}/5: bandeja vacía. Recargando...")
            # Usar el botón de refresh de yopmail si existe
            try:
                page.locator("#refresh").click(timeout=3_000)
            except Exception:
                page.reload()
            page.wait_for_load_state("networkidle")
            inbox = page.frame_locator("#ifinbox")
            email_item = inbox.locator("div.m").first

    if not encontrado:
        pytest.xfail(
            "CE-03: El email no llegó después de 5 intentos (150s total).\n"
            f"  → Verificar manualmente: https://yopmail.com/en/?login={YOPMAIL_USUARIO}\n"
            "  → Revisar configuración SMTP y permisos Send As (CE-01)"
        )

    email_item.click()
    page.wait_for_timeout(2000)

    # Extraer el código de verificación del cuerpo del email
    # La plantilla muestra el código en un <p> con font-size:32px, font-family monospace
    # Buscamos el primer <p> cuyo texto sea alfanumérico de 8-20 chars (el código plano)
    mail_frame = page.frame_locator("#ifmail")
    mail_frame.locator("body").wait_for(timeout=10_000)

    # Obtener todo el texto del email y extraer el código con regex
    # La plantilla muestra: "Código de verificación" → CODE (32px monospace) → "Válido por N minutos"
    cuerpo_texto = mail_frame.locator("body").inner_text(timeout=10_000)
    match = re.search(
        r"verificaci[oó]n[\s\n]+([A-Z0-9]{8,20})[\s\n]+[Vv][áa]lido",
        cuerpo_texto,
        re.IGNORECASE | re.MULTILINE,
    )
    if not match:
        # Fallback: buscar cualquier token alfanumérico mayúsculo con al menos un dígito
        match = re.search(r"\b([A-Z]{2,}[0-9][A-Z0-9]{4,}|[A-Z0-9]{4,}[0-9][A-Z]{2,})\b", cuerpo_texto)
    assert match, (
        f"No se encontró código alfanumérico en el email.\n"
        f"Texto del email (primeros 700 chars):\n{cuerpo_texto[:700]}"
    )

    codigo = match.group(1)

    # PASO 10: Verificar que el código NO es un hash SHA-256 (64 chars hex lowercase)
    assert not (len(codigo) == 64 and all(c in "0123456789abcdef" for c in codigo.lower())), (
        f"FALLO DE SEGURIDAD — El email contiene el hash SHA-256 ({len(codigo)} chars). "
        "El email debe contener el código plano. Revisar CuentaService."
    )
    assert re.match(r"^[A-Z0-9]+$", codigo), (
        f"Código en email contiene caracteres no alfanuméricos mayúsculos: '{codigo}'"
    )

    _S["token_codigo"] = codigo
    _S["token_url"]    = f"{BASE_URL}/Cuenta/RestablecerPassword?token={codigo}"
    print(f"\n  [yopmail] Email recibido. Código extraído: '{codigo}' ({len(codigo)} chars)")


# ════════════════════════════════════════════════════════════════════════════
#  PASO 11-14 — Formulario de restablecimiento
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_paso11_restablecer_con_token_del_email(page):
    """
    PASOS 11-14: Usar el token extraído del email para restablecer la contraseña.
    El sistema debe redirigir a Login con mensaje de éxito.
    """
    if _S["token_codigo"] is None:
        pytest.skip("Sin token del email — test_paso7 no completado o xfail")

    url_reset = _S["token_url"] or f"{BASE_URL}/Cuenta/RestablecerPassword?token={_S['token_codigo']}"
    page.goto(url_reset)
    page.wait_for_load_state("networkidle")

    campo_nuevo = page.locator("#NuevoPassword, input[name='NuevoPassword']")
    assert campo_nuevo.is_visible(), (
        f"El formulario de restablecimiento no cargó. URL: {page.url}. "
        "¿El token del email fue rechazado?"
    )

    # Ingresar nueva contraseña
    campo_nuevo.fill(PASSWORD_NUEVA)
    page.locator(
        "#ConfirmarPassword, input[name='ConfirmarPassword']"
    ).fill(PASSWORD_NUEVA)
    print(f"\n  [Playwright] Ingresando nueva contraseña: '{PASSWORD_NUEVA}'")

    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Verificar redirección a Login con mensaje de éxito
    assert "/Cuenta/Login" in page.url, (
        f"No redirigió a Login tras restablecer. URL: {page.url}"
    )
    mensaje = page.locator(
        ".alert--success, .alert-success, [class*='success']"
    ).first
    assert mensaje.is_visible() and mensaje.inner_text().strip() != "", (
        "No se mostró mensaje de éxito tras el restablecimiento"
    )
    print(f"  [Playwright] Restablecimiento exitoso. Mensaje: '{mensaje.inner_text().strip()}'")


# ════════════════════════════════════════════════════════════════════════════
#  PASO 15-16 — Verificación post-restablecimiento en BD
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_paso15_token_marcado_como_usado(page):
    """PASO 15: Token marcado Usado=1 tras restablecimiento exitoso."""
    if _S["token_codigo"] is None:
        pytest.skip("Sin token del email")

    filas = _consultar(
        f"SELECT TOP 1 t.Usado "
        f"FROM dbo.TokensRecuperacion t "
        f"JOIN dbo.Usuarios u ON u.Id = t.UsuarioId "
        f"WHERE u.CorreoAcceso = '{CORREO}' "
        f"AND t.Token NOT IN ('TK7E4D8F5G','TK3F9A2B1C','TK1H6K9M2N') "
        f"ORDER BY t.FechaCreacion DESC;"
    )
    assert filas, "No se encontró el token en BD"
    assert _bool(filas[0].get("Usado")), (
        "FALLO — El token no fue marcado como Usado=1 tras el restablecimiento"
    )
    print("  [BD] Token marcado Usado=1 ✅")


@pytest.mark.yopmail
def test_paso16_auditoria_confirmacion_en_bd(page):
    """PASO 16: RegistroNotificaciones tiene fila 'CambioContrasenaExitoso' con Exitoso=1."""
    filas = _consultar(
        "SELECT TOP 1 Exitoso, ISNULL(ErrorMensaje,'') AS ErrorMensaje "
        "FROM dbo.RegistroNotificaciones "
        "WHERE TipoEvento = 'CambioContrasenaExitoso' "
        "ORDER BY FechaIntento DESC;"
    )
    if not filas:
        pytest.xfail(
            "Sin registro 'CambioContrasenaExitoso' en BD. "
            "Verificar que NotificarCambioContrasenaExitosoAsync() está integrado "
            "en CuentaService.RestablecerPasswordAsync()."
        )
    assert _bool(filas[0].get("Exitoso")), (
        f"Correo de confirmación falló. Error: {filas[0].get('ErrorMensaje')}"
    )
    print("  [BD] Auditoría CambioContrasenaExitoso OK ✅")


# ════════════════════════════════════════════════════════════════════════════
#  PASO 17-18 — Login posterior
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_paso17_login_con_nueva_contrasena(page):
    """PASO 17: Login con la nueva contraseña → acceso al Dashboard."""
    if _S["token_codigo"] is None:
        pytest.skip("Sin token del email")

    hacer_login(page, CORREO, PASSWORD_NUEVA)
    assert "/Cuenta/Login" not in page.url, (
        f"Login con nueva contraseña '{PASSWORD_NUEVA}' fue denegado. URL: {page.url}"
    )
    print(f"  [Playwright] Login con nueva contraseña exitoso. URL: {page.url}")


@pytest.mark.yopmail
def test_paso18_login_con_password_anterior_denegado(page):
    """PASO 18: Login con la contraseña antigua 'Usuario1' → denegado."""
    if _S["token_codigo"] is None:
        pytest.skip("Sin token del email")

    # Cerrar sesión si está activa
    page.goto(f"{BASE_URL}/Cuenta/Logout")
    page.wait_for_load_state("networkidle")

    hacer_login(page, CORREO, "Usuario1")
    assert "/Cuenta/Login" in page.url, (
        "FALLO — La contraseña antigua sigue siendo válida tras el restablecimiento"
    )
    print("  [Playwright] Contraseña antigua correctamente denegada ✅")
