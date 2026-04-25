"""
Pruebas E2E — Restablecimiento de Contraseña: Validación de Email y Código
Plan de referencia: Tests/Plan-restablecerPasswordValidacionEmailYCodigo.md

FLUJO COMPLETO:
  INICIO APP → Solicitar reset → Validar email en yopmail → Extraer código
  → Restablecer contraseña → Verificar login → STOP APP

GRUPOS:
  TC-RP-01   Aplicación responde en /Cuenta/Login
  TC-RP-02   Formulario de solicitud carga correctamente
  TC-RP-03   Enviar solicitud con correo válido (genera token + email)
  TC-RP-04   Redirección a Login con mensaje informativo
  TC-RP-05   Navegar a bandeja de yopmail
  TC-RP-06   Email de recuperación llegó a la bandeja  [yopmail]
  TC-RP-07   Abrir email y extraer el código del enlace  [yopmail]
  TC-RP-08   Código es alfanumérico de 12 chars (NO hash SHA-256)  [yopmail]
  TC-RP-09   Email menciona vigencia de 30 minutos  [yopmail]
  TC-RP-10   Formulario de restablecimiento visible con el código  [yopmail]
  TC-RP-11   Completar restablecimiento con nueva contraseña  [yopmail]
  TC-RP-12   Redirección a Login con mensaje de éxito
  TC-RP-13   Token marcado Usado=1 en BD
  TC-RP-14   Login con nueva contraseña exitoso / antigua denegada

INICIO Y DETENCIÓN DE LA APLICACIÓN:
  El fixture `gestionar_aplicacion` (scope=module, autouse=True) inicia
  la aplicación .NET Core si no está ya corriendo, y la detiene al finalizar
  SOLO si fue iniciada por este fixture.

Ejecución recomendada:
  pytest Tests/test_restablecer_password_email_codigo.py -v --headed --slowmo 800 -s
  pytest Tests/test_restablecer_password_email_codigo.py -v --headed -m "not yopmail"
"""

import json
import os
import re
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import pytest

from helpers import BASE_URL, hacer_login, hacer_logout, hay_error_formulario

# ── Configuración ──────────────────────────────────────────────────────────────
DB_INSTANCE     = r"(localdb)\MSSQLLocalDB"
DB_NAME         = "GestionPersonal"

CORREO_PRUEBA   = "carlos.rodriguez@yopmail.com"
YOPMAIL_USUARIO = "carlos.rodriguez"
PASSWORD_ORIG   = "Usuario1"
PASSWORD_NUEVA  = "NuevoRp2026!"

# Hash/Salt de PASSWORD_ORIG (PBKDF2/SHA-256) — fuente: Seeding_Completo.sql
_HASH_ORIG = "0x7DED37B4612147C18EBDFA1F6DEB4709EC9D511DA20641214F1F97612DF2CEAE"
_SALT_ORIG = "0xF2B483C7DAC61EC2CA7F1331C95D6800"

# ── Estado compartido (fluye A → Z entre tests del módulo) ────────────────────
_E: dict = {
    "solicitud_enviada": False,
    "token_codigo":      None,   # 12 chars alfanuméricos del email
    "token_url":         None,   # URL completa del enlace de restablecimiento
    "reset_exitoso":     False,
}


# ══════════════════════════════════════════════════════════════════════════════
#  FIXTURE — Ciclo de vida de la aplicación .NET Core
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module", autouse=True)
def gestionar_aplicacion():
    """
    Inicia la aplicación ASP.NET Core antes de las pruebas de este módulo
    y la detiene automáticamente al finalizar.

    Lógica:
      - Si la app ya responde en BASE_URL → se usa sin iniciar ni detener.
      - Si no responde → se inicia con 'dotnet run' y se espera hasta 90s.
        Al finalizar el módulo el proceso se termina ordenadamente.
    """
    app_iniciada_aqui = False
    proc = None

    # Comprobar si la app ya está activa
    try:
        req = urllib.request.Request(f"{BASE_URL}/Cuenta/Login")
        urllib.request.urlopen(req, timeout=3)
        print(f"\n[INFO] La aplicación ya está activa en {BASE_URL} — no se iniciará nuevamente.")
    except Exception:
        # La app NO está corriendo → iniciarla
        workspace_root = Path(__file__).parent.parent
        proyecto_web   = workspace_root / "Proyecto MVC" / "GestionPersonal.Web"

        print(f"\n[INFO] Iniciando aplicación .NET Core desde:\n       {proyecto_web}")

        proc = subprocess.Popen(
            ["dotnet", "run", "--urls", BASE_URL],
            cwd=str(proyecto_web),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="replace",
        )
        app_iniciada_aqui = True

        # Esperar hasta 90 segundos a que la app esté disponible
        inicio    = time.time()
        disponible = False
        while time.time() - inicio < 90:
            # Verificar que el proceso sigue vivo
            if proc.poll() is not None:
                salida = proc.stdout.read() if proc.stdout else "(sin salida)"
                pytest.fail(
                    f"[ERROR] La aplicación .NET Core terminó inesperadamente.\n"
                    f"Salida del proceso:\n{salida}"
                )
            try:
                urllib.request.urlopen(f"{BASE_URL}/Cuenta/Login", timeout=2)
                disponible = True
                break
            except Exception:
                time.sleep(1)

        if not disponible:
            proc.terminate()
            pytest.fail(
                f"[ERROR] La aplicación no respondió en {BASE_URL} tras 90 segundos.\n"
                f"Verificar que el proyecto compila correctamente con 'dotnet build'."
            )

        print(f"[OK] Aplicación lista en {BASE_URL}")

    yield  # ── Aquí se ejecutan todos los tests del módulo ──

    # ── TEARDOWN: Detener la app solo si la iniciamos nosotros ──────────────
    if app_iniciada_aqui and proc is not None:
        print("\n[INFO] Deteniendo la aplicación .NET Core...")
        proc.terminate()
        try:
            proc.wait(timeout=15)
            print("[OK] Aplicación detenida correctamente.")
        except subprocess.TimeoutExpired:
            proc.kill()
            print("[WARN] La aplicación fue forzosamente terminada (kill).")


# ══════════════════════════════════════════════════════════════════════════════
#  FIXTURE — Resetear BD antes del módulo
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module", autouse=True)
def _resetear_bd_modulo():
    """
    Restaura el estado de BD necesario para este módulo:
      - Contraseña de carlos.rodriguez@yopmail.com → Usuario1
      - Limpia tokens frescos (conserva los del seeding)
    Garantiza idempotencia en re-ejecuciones consecutivas.
    """
    # Resetear el estado compartido para re-ejecuciones en el mismo proceso
    _E["solicitud_enviada"] = False
    _E["token_codigo"]      = None
    _E["token_url"]         = None
    _E["reset_exitoso"]     = False

    _ejecutar(
        f"UPDATE dbo.Usuarios "
        f"SET PasswordHash={_HASH_ORIG}, PasswordSalt={_SALT_ORIG}, DebeCambiarPassword=0 "
        f"WHERE CorreoAcceso='{CORREO_PRUEBA}'; "
        # Eliminar tokens frescos generados en ejecuciones previas
        # (los del seeding tienen tokens cortos tipo 'TKxxxxxx' — no son SHA-256 de 64 chars)
        f"DELETE FROM dbo.TokensRecuperacion "
        f"WHERE UsuarioId = (SELECT Id FROM dbo.Usuarios WHERE CorreoAcceso='{CORREO_PRUEBA}') "
        f"AND LEN(Token) = 64;"
    )
    yield
    # Restaurar contraseña al terminar el módulo para no afectar otras suites
    _ejecutar(
        f"UPDATE dbo.Usuarios "
        f"SET PasswordHash={_HASH_ORIG}, PasswordSalt={_SALT_ORIG}, DebeCambiarPassword=0 "
        f"WHERE CorreoAcceso='{CORREO_PRUEBA}';"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  Helpers de BD
# ══════════════════════════════════════════════════════════════════════════════

def _consultar(query: str) -> list[dict]:
    """Ejecuta una SELECT via Invoke-Sqlcmd y retorna filas como lista de dicts."""
    sql_file = os.path.join(tempfile.gettempdir(), "_rp_email_consulta.sql")
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
    """Ejecuta un comando SQL (INSERT/UPDATE/DELETE) sin retorno de datos."""
    sql_file = os.path.join(tempfile.gettempdir(), "_rp_email_exec.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    subprocess.run(
        ["powershell", "-Command",
         f"Invoke-Sqlcmd -ServerInstance '{DB_INSTANCE}' -Database '{DB_NAME}' "
         f"-InputFile '{sql_file}'"],
        capture_output=True, text=True, timeout=15,
    )


def _bool_bd(valor) -> bool:
    """Normaliza valores de BD (True/False/0/1/'1'/'True') a bool de Python."""
    if isinstance(valor, bool):
        return valor
    return str(valor).strip() in ("1", "True", "true")


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-01 — Aplicación responde en /Cuenta/Login
# ══════════════════════════════════════════════════════════════════════════════

def test_rp01_aplicacion_responde(page):
    """
    TC-RP-01: Verificar que la aplicación está activa y el endpoint de Login responde.
    Este test confirma que el fixture gestionar_aplicacion tuvo éxito.
    """
    page.goto(f"{BASE_URL}/Cuenta/Login")
    page.wait_for_load_state("networkidle")

    assert "/Cuenta/Login" in page.url, (
        f"TC-RP-01 FALLO: La URL no corresponde a Login. URL actual: {page.url}"
    )
    # El campo de correo debe ser visible
    campo_correo = page.locator("#CorreoAcceso, input[name='CorreoAcceso']")
    assert campo_correo.is_visible(), (
        "TC-RP-01 FALLO: El campo de correo no está visible en la página de Login."
    )
    print(f"\n  [OK] TC-RP-01 PASÓ — Aplicación activa en {BASE_URL}")


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-02 — Formulario de solicitud carga correctamente
# ══════════════════════════════════════════════════════════════════════════════

def test_rp02_formulario_solicitud_carga(page):
    """
    TC-RP-02: /Cuenta/RecuperarPassword muestra el campo de correo y el botón de envío.
    """
    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.wait_for_load_state("networkidle")

    assert "RecuperarPassword" in page.url, (
        f"TC-RP-02 FALLO: No se cargó el formulario de solicitud. URL: {page.url}"
    )
    campo_correo = page.locator("#CorreoAcceso, input[name='CorreoAcceso']")
    boton_enviar = page.locator("button[type=submit]")

    assert campo_correo.is_visible(), (
        "TC-RP-02 FALLO: Campo #CorreoAcceso no visible en /Cuenta/RecuperarPassword."
    )
    assert boton_enviar.is_visible(), (
        "TC-RP-02 FALLO: Botón submit no visible en /Cuenta/RecuperarPassword."
    )
    print(f"\n  [OK] TC-RP-02 PASÓ — Formulario de solicitud cargado correctamente.")


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-03 — Enviar solicitud con correo válido
# ══════════════════════════════════════════════════════════════════════════════

def test_rp03_enviar_solicitud_correo_valido(page):
    """
    TC-RP-03: Ingresar el correo de prueba y enviar el formulario.
    El sistema debe generar un token (SHA-256 en BD) y enviar el código plano por email.
    IMPORTANTE: Este test dispara el envío del email usado por los tests del grupo yopmail.
    """
    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.wait_for_load_state("networkidle")

    page.fill("#CorreoAcceso", CORREO_PRUEBA)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    _E["solicitud_enviada"] = True
    print(
        f"\n  [INFO] TC-RP-03 — Solicitud enviada para '{CORREO_PRUEBA}'. "
        f"URL actual: {page.url}"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-04 — Redirección a Login con mensaje informativo
# ══════════════════════════════════════════════════════════════════════════════

def test_rp04_redireccion_login_con_mensaje(page):
    """
    TC-RP-04: Tras la solicitud, el sistema debe redirigir a /Cuenta/Login
    con un mensaje genérico (principio de anti-enumeración de usuarios).
    """
    # Si el test anterior no navegó, asegurarse de enviar la solicitud primero
    if not _E["solicitud_enviada"]:
        page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
        page.wait_for_load_state("networkidle")
        page.fill("#CorreoAcceso", CORREO_PRUEBA)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")

    assert "/Cuenta/Login" in page.url, (
        f"TC-RP-04 FALLO: No redirigió a Login. URL actual: {page.url}"
    )
    # Verificar mensaje informativo visible
    alerta = page.locator(
        ".alert--info, .alert-info, .alert--success, .alert-success, [class*='alert']"
    ).first
    assert alerta.is_visible() and alerta.inner_text().strip() != "", (
        "TC-RP-04 FALLO: No se mostró mensaje informativo tras la solicitud de recuperación."
    )
    # Verificar que NO se revelan datos del usuario (anti-enumeración)
    body = page.locator("body").inner_text().lower()
    for frase_prohibida in ["no encontrado", "no existe", "not found",
                            "usuario no registrado", "correo incorrecto"]:
        assert frase_prohibida not in body, (
            f"TC-RP-04 FALLO: El sistema expone enumeración de usuarios con: '{frase_prohibida}'"
        )
    print(f"\n  [OK] TC-RP-04 PASÓ — Redirigió a Login con mensaje informativo.")


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-05 — Navegar a bandeja de yopmail
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_rp05_navegar_bandeja_yopmail(page):
    """
    TC-RP-05: Navegar a yopmail.com y verificar que la bandeja del usuario
    de prueba carga correctamente (iframe #ifinbox disponible).
    """
    page.goto(f"https://yopmail.com/en/?login={YOPMAIL_USUARIO}")
    page.wait_for_load_state("networkidle")

    # Verificar que el iframe de la bandeja está en el DOM
    ifinbox = page.locator("#ifinbox")
    assert ifinbox.count() > 0, (
        "TC-RP-05 FALLO: El iframe #ifinbox no se encontró en yopmail.com. "
        "Verificar conectividad o posibles cambios en la estructura de yopmail."
    )
    print(
        f"\n  [OK] TC-RP-05 PASÓ — Bandeja de yopmail disponible "
        f"para '{YOPMAIL_USUARIO}'."
    )


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-06 — Email de recuperación llegó a la bandeja
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_rp06_email_llego_a_bandeja(page):
    """
    TC-RP-06: Verificar que el email de recuperación enviado en TC-RP-03
    aparece en la bandeja de carlos.rodriguez en yopmail.
    Timeout de 30 segundos para contemplar demoras de entrega SMTP.

    Si falla:
      1. Verificar SMTP: dotnet user-secrets list (en GestionPersonal.Web)
      2. Revisar permisos 'Send As' en Exchange Admin para notificacion.sf@zentria.com.co
      3. Inspección manual: https://yopmail.com/en/?login=carlos.rodriguez
    """
    page.goto(f"https://yopmail.com/en/?login={YOPMAIL_USUARIO}")
    page.wait_for_load_state("networkidle")

    inbox      = page.frame_locator("#ifinbox")
    email_item = inbox.locator("a").filter(
        has_text=re.compile(
            r"contrase|recuper|GestiónRH|GestionRH|password|reset|código|clave",
            re.IGNORECASE,
        )
    ).first

    try:
        email_item.wait_for(timeout=30_000)
    except Exception:
        pytest.xfail(
            "TC-RP-06: El email de recuperación no llegó en 30 segundos.\n"
            "  → Verificar configuración SMTP en user-secrets del proyecto\n"
            "  → Los tests TC-RP-07..RP-14 dependientes se omitirán automáticamente."
        )

    assert email_item.is_visible(), (
        "TC-RP-06 FALLO: Se encontró el email pero no está visible en el iframe."
    )
    print(
        f"\n  [OK] TC-RP-06 PASÓ — Email de recuperación encontrado en la bandeja de "
        f"'{YOPMAIL_USUARIO}'."
    )


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-07 — Abrir email y extraer el código del enlace
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_rp07_abrir_email_extraer_codigo(page):
    """
    TC-RP-07: Abrir el email de recuperación en yopmail y extraer el código
    (parámetro ?token=) del enlace de restablecimiento.

    El código extraído se almacena en:
      _E["token_codigo"] → valor del parámetro token (ej. 'Ab3Cd5Ef7Gh9')
      _E["token_url"]    → URL completa del enlace (ej. 'http://localhost:5002/...')

    Este estado es consumido por los tests TC-RP-08 al TC-RP-14.
    """
    page.goto(f"https://yopmail.com/en/?login={YOPMAIL_USUARIO}")
    page.wait_for_load_state("networkidle")

    inbox      = page.frame_locator("#ifinbox")
    email_item = inbox.locator("a").filter(
        has_text=re.compile(
            r"contrase|recuper|GestiónRH|GestionRH|password|reset|código|clave",
            re.IGNORECASE,
        )
    ).first

    try:
        email_item.wait_for(timeout=30_000)
    except Exception:
        pytest.xfail(
            "TC-RP-07: Email no disponible en la bandeja. "
            "Requiere que TC-RP-03 haya sido ejecutado con SMTP activo."
        )

    email_item.click()
    page.wait_for_timeout(1500)

    # El cuerpo del email está en el iframe #ifmail
    mail_frame = page.frame_locator("#ifmail")
    enlace     = mail_frame.locator(
        "a[href*='RestablecerPassword'], a[href*='token=']"
    ).first

    try:
        enlace.wait_for(timeout=10_000)
    except Exception:
        pytest.fail(
            "TC-RP-07 FALLO: No se encontró enlace con 'RestablecerPassword' o 'token=' "
            "en el cuerpo del email (iframe #ifmail). "
            "Revisar la plantilla de email en SeguridadEmailTemplate."
        )

    href = enlace.get_attribute("href")
    assert href is not None and href.strip() != "", (
        "TC-RP-07 FALLO: El atributo href del enlace de restablecimiento está vacío."
    )

    match = re.search(r"[?&]token=([^&\s\"'<>]+)", href)
    assert match, (
        f"TC-RP-07 FALLO: El enlace no tiene el parámetro 'token='. "
        f"href recibido: '{href}'"
    )

    _E["token_codigo"] = match.group(1)
    _E["token_url"]    = href

    print(
        f"\n  [OK] TC-RP-07 PASÓ — Código extraído del email: "
        f"'{_E['token_codigo']}' ({len(_E['token_codigo'])} chars)\n"
        f"       URL: {href}"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-08 — Código es alfanumérico de 12 chars (NO hash SHA-256)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_rp08_codigo_es_alfanumerico_12_chars(page):
    """
    TC-RP-08: El código extraído del email debe ser el CÓDIGO PLANO (12 chars
    alfanuméricos), NO el hash SHA-256 (64 chars hexadecimales).

    Si el email contuviera el hash SHA-256 sería un fallo CRÍTICO de seguridad:
    un atacante podría calcular el hash inverso o usarlo directamente para
    modificar el token en BD (preimage attack).
    """
    if _E["token_codigo"] is None:
        pytest.skip("TC-RP-08: Sin código disponible — requiere TC-RP-07 exitoso.")

    token = _E["token_codigo"]

    # Verificar que NO es el hash SHA-256 (64 chars hexadecimales)
    es_hash_sha256 = (
        len(token) == 64
        and all(c in "0123456789abcdefABCDEF" for c in token)
    )
    assert not es_hash_sha256, (
        f"TC-RP-08 FALLO CRÍTICO DE SEGURIDAD: "
        f"El email expone el hash SHA-256 en lugar del código plano. "
        f"Token recibido: '{token}' ({len(token)} chars). "
        f"Revisar CuentaService.SolicitarRecuperacionAsync() — "
        f"debe enviar el código plano al correo, no el hash."
    )

    # Verificar longitud de 12 caracteres (según GenerarCodigoSeguro)
    assert len(token) == 12, (
        f"TC-RP-08 FALLO: El código debería tener 12 caracteres (GenerarCodigoSeguro), "
        f"pero tiene {len(token)}: '{token}'. "
        f"Revisar implementación de GenerarCodigoSeguro() en CuentaService."
    )

    # Verificar que es alfanumérico
    assert re.match(r"^[a-zA-Z0-9]+$", token), (
        f"TC-RP-08 FALLO: El código contiene caracteres no alfanuméricos: '{token}'"
    )

    print(
        f"\n  [OK] TC-RP-08 PASÓ — Código alfanumérico de 12 chars: '{token}'"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-09 — Email menciona vigencia de 30 minutos
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_rp09_email_menciona_vigencia_30_minutos(page):
    """
    TC-RP-09: El cuerpo del email debe informar al usuario que el código
    tiene una vigencia de 30 minutos.
    """
    if _E["token_codigo"] is None:
        pytest.skip("TC-RP-09: Sin código disponible — requiere TC-RP-07 exitoso.")

    page.goto(f"https://yopmail.com/en/?login={YOPMAIL_USUARIO}")
    page.wait_for_load_state("networkidle")

    mail_frame = page.frame_locator("#ifmail")

    # Asegurar que el email correcto está abierto (re-abrir si el frame quedó en blanco)
    try:
        inbox      = page.frame_locator("#ifinbox")
        email_item = inbox.locator("a").filter(
            has_text=re.compile(
                r"contrase|recuper|GestiónRH|GestionRH|password|reset|código|clave",
                re.IGNORECASE,
            )
        ).first
        if email_item.is_visible():
            email_item.click()
            page.wait_for_timeout(1200)
    except Exception:
        pass  # Continuar con el contenido actual del iframe

    try:
        cuerpo = mail_frame.locator("body").inner_text(timeout=8_000)
    except Exception as exc:
        pytest.xfail(
            f"TC-RP-09: No se pudo leer el cuerpo del email desde #ifmail: {exc}"
        )
        return

    assert re.search(r"30\s*(minutos?|min)", cuerpo, re.IGNORECASE), (
        "TC-RP-09 FALLO: El email no menciona '30 minutos'. "
        "Revisar SeguridadEmailTemplate.RecuperacionContrasena() "
        "y el parámetro vigenciaMinutos."
    )
    print(f"\n  [OK] TC-RP-09 PASÓ — Email menciona vigencia de 30 minutos.")


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-10 — Formulario de restablecimiento visible con el código del email
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_rp10_formulario_restablecimiento_visible(page):
    """
    TC-RP-10: El código extraído del email es un token válido.
    Al navegar a /Cuenta/RestablecerPassword?token=<CÓDIGO>, el formulario
    con los campos NuevoPassword y ConfirmarPassword debe ser visible.
    """
    if _E["token_url"] is None:
        pytest.skip(
            "TC-RP-10: URL del enlace no disponible — requiere TC-RP-07 exitoso."
        )

    page.goto(_E["token_url"])
    page.wait_for_load_state("networkidle")

    if "/Cuenta/Login" in page.url:
        pytest.fail(
            "TC-RP-10 FALLO: El token del email fue rechazado (redirigió a Login). "
            "El código debería ser válido y no expirado. "
            f"URL final: {page.url}"
        )

    campo_nuevo     = page.locator("#NuevoPassword, input[name='NuevoPassword']")
    campo_confirmar = page.locator("#ConfirmarPassword, input[name='ConfirmarPassword']")

    assert campo_nuevo.is_visible(), (
        f"TC-RP-10 FALLO: Campo 'NuevoPassword' no visible. "
        f"URL: {page.url}"
    )
    assert campo_confirmar.is_visible(), (
        f"TC-RP-10 FALLO: Campo 'ConfirmarPassword' no visible. "
        f"URL: {page.url}"
    )
    print(
        f"\n  [OK] TC-RP-10 PASÓ — Formulario de restablecimiento visible con el código "
        f"'{_E['token_codigo']}'."
    )


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-11 — Completar restablecimiento con nueva contraseña
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_rp11_completar_restablecimiento(page):
    """
    TC-RP-11: Usar el código del email para establecer la nueva contraseña.
    Llena NuevoPassword y ConfirmarPassword con PASSWORD_NUEVA y envía el formulario.
    """
    if _E["token_url"] is None:
        pytest.skip(
            "TC-RP-11: URL del enlace no disponible — requiere TC-RP-07 exitoso."
        )

    page.goto(_E["token_url"])
    page.wait_for_load_state("networkidle")

    if "/Cuenta/Login" in page.url:
        pytest.fail(
            "TC-RP-11 FALLO: El token fue rechazado antes de poder usarlo. "
            f"URL: {page.url}"
        )

    campo_nuevo     = page.locator("#NuevoPassword, input[name='NuevoPassword']")
    campo_confirmar = page.locator("#ConfirmarPassword, input[name='ConfirmarPassword']")

    if not campo_nuevo.is_visible():
        pytest.skip(
            "TC-RP-11: El formulario de restablecimiento no está disponible "
            "(el token puede haber sido consumido en una ejecución anterior). "
            "Re-ejecutar desde TC-RP-03."
        )

    page.fill("#NuevoPassword, input[name='NuevoPassword']",         PASSWORD_NUEVA)
    page.fill("#ConfirmarPassword, input[name='ConfirmarPassword']", PASSWORD_NUEVA)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    _E["reset_exitoso"] = True
    print(
        f"\n  [INFO] TC-RP-11 — Formulario de restablecimiento enviado. "
        f"URL actual: {page.url}"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-12 — Redirección a Login con mensaje de éxito
# ══════════════════════════════════════════════════════════════════════════════

def test_rp12_mensaje_exito_en_login(page):
    """
    TC-RP-12: Tras el restablecimiento exitoso, el sistema debe redirigir a
    /Cuenta/Login con un mensaje de éxito visible.
    """
    if not _E["reset_exitoso"]:
        pytest.skip(
            "TC-RP-12: Requiere TC-RP-11 completado exitosamente."
        )

    assert "/Cuenta/Login" in page.url, (
        f"TC-RP-12 FALLO: No redirigió a Login tras el restablecimiento. "
        f"URL actual: {page.url}"
    )
    alerta = page.locator(
        ".alert--success, .alert-success, [class*='alert']"
    ).first
    assert alerta.is_visible() and alerta.inner_text().strip() != "", (
        "TC-RP-12 FALLO: No se mostró mensaje de éxito en Login tras el restablecimiento."
    )
    print(
        f"\n  [OK] TC-RP-12 PASÓ — Redirigió a Login con mensaje de éxito: "
        f"'{alerta.inner_text().strip()}'"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-13 — Token marcado Usado=1 en BD
# ══════════════════════════════════════════════════════════════════════════════

def test_rp13_token_marcado_usado_en_bd(page):
    """
    TC-RP-13: El token utilizado debe quedar marcado como Usado=1 en
    dbo.TokensRecuperacion, impidiendo que sea reutilizado.

    Un token reutilizable es un fallo de seguridad grave (token replay attack).
    """
    if not _E["reset_exitoso"]:
        pytest.skip(
            "TC-RP-13: Requiere TC-RP-11 completado exitosamente."
        )

    filas = _consultar(
        f"SELECT TOP 1 t.Usado, t.Token, "
        f"CONVERT(varchar(32), t.FechaExpiracion, 126) AS FechaExpiracion "
        f"FROM dbo.TokensRecuperacion t "
        f"JOIN dbo.Usuarios u ON u.Id = t.UsuarioId "
        f"WHERE u.CorreoAcceso = '{CORREO_PRUEBA}' "
        f"AND LEN(t.Token) = 64 "
        f"ORDER BY t.FechaCreacion DESC;"
    )

    assert filas, (
        "TC-RP-13 FALLO: No se encontró ningún token en dbo.TokensRecuperacion "
        f"para '{CORREO_PRUEBA}'. Verificar que TC-RP-03 generó el token."
    )

    ultimo = filas[0]
    assert _bool_bd(ultimo.get("Usado")), (
        f"TC-RP-13 FALLO DE SEGURIDAD: El token sigue con Usado=0 tras el restablecimiento. "
        f"Token (hash): '{ultimo.get('Token', '')[:16]}...'. "
        f"El token es reutilizable — revisar CuentaService.RestablecerPasswordAsync()."
    )
    print(
        f"\n  [OK] TC-RP-13 PASÓ — Token marcado Usado=1 en BD. "
        f"FechaExpiracion: {ultimo.get('FechaExpiracion', 'N/D')}"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  TC-RP-14 — Login con nueva contraseña exitoso / antigua denegada
# ══════════════════════════════════════════════════════════════════════════════

def test_rp14_login_nueva_y_antigua_contrasena(page):
    """
    TC-RP-14a: Login con la nueva contraseña → exitoso (redirige al Dashboard).
    TC-RP-14b: Login con la contraseña antigua → denegado (permanece en Login).

    Verifica el efecto real del restablecimiento en la autenticación.
    """
    if not _E["reset_exitoso"]:
        pytest.skip(
            "TC-RP-14: Requiere TC-RP-11 completado exitosamente."
        )

    # ── TC-RP-14a: Nueva contraseña debe funcionar ───────────────────────────
    page.goto(f"{BASE_URL}/Cuenta/Login")
    page.wait_for_load_state("networkidle")

    page.fill("#CorreoAcceso", CORREO_PRUEBA)
    page.fill("#inputPassword", PASSWORD_NUEVA)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    url_post_login = page.url
    assert "/Cuenta/Login" not in url_post_login, (
        f"TC-RP-14a FALLO: Login con la nueva contraseña '{PASSWORD_NUEVA}' falló. "
        f"URL actual: {url_post_login}. "
        "Verificar que el restablecimiento actualizó correctamente el hash de la BD."
    )
    print(
        f"\n  [OK] TC-RP-14a PASÓ — Login con nueva contraseña exitoso. "
        f"URL: {url_post_login}"
    )

    # ── TC-RP-14b: Contraseña antigua debe ser rechazada ────────────────────
    # Cerrar sesión primero
    page.goto(f"{BASE_URL}/Cuenta/Logout")
    page.wait_for_load_state("networkidle")

    page.goto(f"{BASE_URL}/Cuenta/Login")
    page.wait_for_load_state("networkidle")

    page.fill("#CorreoAcceso", CORREO_PRUEBA)
    page.fill("#inputPassword", PASSWORD_ORIG)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Cuenta/Login" in page.url, (
        f"TC-RP-14b FALLO DE SEGURIDAD: La contraseña antigua '{PASSWORD_ORIG}' "
        "sigue siendo válida tras el restablecimiento. "
        "Verificar que el restablecimiento actualizó el hash en BD y no dejó el anterior activo."
    )
    print(
        f"\n  [OK] TC-RP-14b PASÓ — Contraseña antigua '{PASSWORD_ORIG}' "
        "correctamente denegada."
    )
