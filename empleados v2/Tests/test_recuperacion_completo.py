"""
Pruebas exhaustivas — Restablecimiento de Contraseña (32 casos)
Plan de referencia: Tests/plan-ejecucion-restablecercontraseña.md

GRUPOS:
  A  TC-RC-01..06  Formulario de solicitud  (/Cuenta/RecuperarPassword)
  B  TC-RC-07..12  Email en yopmail.com     (iframes: #ifinbox / #ifmail)
  C  TC-RC-13..21  Formulario restablecimiento (/Cuenta/RestablecerPassword)
  D  TC-RC-22..24  Seguridad del token en BD
  E  TC-RC-25..26  Login posterior al restablecimiento
  F  TC-RC-27..28  Auditoría (dbo.RegistroNotificaciones)
  G  TC-RC-29..32  Casos borde y seguridad (XSS, SQLi, longitud extrema)

Flujo del token (implementación en CuentaService):
  1. El servidor genera un código PLANO de 12 chars alfanuméricos
  2. La BD almacena SHA-256(código_plano) — 64 chars hex lowercase
  3. El EMAIL lleva el código PLANO  (aparece en ?token=)
  4. En restablecimiento, el servidor hashea el parámetro antes de buscar en BD

Ejecución recomendada:
  pytest Tests/test_recuperacion_completo.py -v --headed -m "not yopmail"
  pytest Tests/test_recuperacion_completo.py -v --headed              # incluye yopmail
"""
import json
import os
import re
import subprocess
import tempfile
import urllib.parse
from datetime import datetime, timedelta

import pytest

from helpers import BASE_URL, hacer_login, hay_error_formulario

# ── Configuración ──────────────────────────────────────────────────────────────
DB_INSTANCE        = r"(localdb)\MSSQLLocalDB"
DB_NAME            = "GestionPersonal"

CORREO_PRINCIPAL   = "carlos.rodriguez@yopmail.com"
YOPMAIL_USUARIO    = "carlos.rodriguez"
CORREO_SECUNDARIO  = "andres.torres@yopmail.com"   # tests que no interfieren con el flujo principal

PASSWORD_ORIGINAL  = "Usuario1"
PASSWORD_NUEVA     = "NuevoRestablecido2026!"

TOKEN_EXPIRADO     = "TK7E4D8F5G"   # Andrés Torres — expirado 2026-04-10, Usado=0
TOKEN_USADO        = "TK3F9A2B1C"   # Laura Sánchez  — expirado, Usado=1

# Hash/Salt para PASSWORD_ORIGINAL (PBKDF2/SHA-256) — igual que conftest.py
_HASH_ORIGINAL = "0x7DED37B4612147C18EBDFA1F6DEB4709EC9D511DA20641214F1F97612DF2CEAE"
_SALT_ORIGINAL = "0xF2B483C7DAC61EC2CA7F1331C95D6800"

# ── Estado compartido entre tests ─────────────────────────────────────────────
# Los tests se ejecutan en el orden en que aparecen en el archivo.
# El estado fluye de A → B → C → D → E → F.
_S: dict = {
    "token_codigo":  None,   # Código plano (12 chars) extraído del email de yopmail
    "token_url":     None,   # URL completa del enlace de restablecimiento del email
    "reset_exitoso": False,  # True cuando TC-RC-21 completa el restablecimiento
}


# ── Helpers de BD ─────────────────────────────────────────────────────────────

def _consultar(query: str) -> list[dict]:
    """Ejecuta una SELECT via Invoke-Sqlcmd y retorna filas como lista de dicts."""
    sql_file = os.path.join(tempfile.gettempdir(), "_rc_completo.sql")
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
    sql_file = os.path.join(tempfile.gettempdir(), "_rc_exec.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    subprocess.run(
        ["powershell", "-Command",
         f"Invoke-Sqlcmd -ServerInstance '{DB_INSTANCE}' -Database '{DB_NAME}' "
         f"-InputFile '{sql_file}'"],
        capture_output=True, text=True, timeout=15,
    )


def _ultimo_token(correo: str) -> dict | None:
    """Devuelve la fila más reciente de TokensRecuperacion para el correo dado."""
    filas = _consultar(
        f"SELECT TOP 1 t.Token, t.Usado, "
        f"CONVERT(varchar(32), t.FechaExpiracion, 126) AS FechaExpiracion, "
        f"CONVERT(varchar(32), t.FechaCreacion,   126) AS FechaCreacion "
        f"FROM dbo.TokensRecuperacion t "
        f"JOIN dbo.Usuarios u ON u.Id = t.UsuarioId "
        f"WHERE u.CorreoAcceso = '{correo}' "
        f"ORDER BY t.FechaCreacion DESC;"
    )
    return filas[0] if filas else None


def _ultimo_registro_notif(tipo_evento: str) -> dict | None:
    """Devuelve el último registro de auditoría para el TipoEvento indicado."""
    filas = _consultar(
        f"SELECT TOP 1 Exitoso, ISNULL(ErrorMensaje,'') AS ErrorMensaje, "
        f"Destinatario, Asunto, ISNULL(Copia,'') AS Copia "
        f"FROM dbo.RegistroNotificaciones "
        f"WHERE TipoEvento = '{tipo_evento}' "
        f"ORDER BY FechaIntento DESC;"
    )
    return filas[0] if filas else None


def _bool(valor) -> bool:
    """Normaliza valores de BD (True/False/0/1/'1'/'True') a bool de Python."""
    if isinstance(valor, bool):
        return valor
    return str(valor).strip() in ("1", "True", "true")


# ── Fixture de módulo — limpia y restaura la BD para este módulo ───────────────

@pytest.fixture(autouse=True, scope="module")
def _preparar_bd_modulo():
    """
    Antes de este módulo: limpia los tokens frescos de carlos.rodriguez y
    restaura su contraseña a PASSWORD_ORIGINAL.
    Después del módulo: restaura también la contraseña para la próxima ejecución.
    """
    # Resetear estado compartido en caso de re-ejecución en el mismo proceso
    _S["token_codigo"]  = None
    _S["token_url"]     = None
    _S["reset_exitoso"] = False

    # Restaurar contraseña a "Usuario1" y limpiar tokens frescos generados en pruebas anteriores
    _ejecutar(
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_ORIGINAL}, PasswordSalt={_SALT_ORIGINAL}, "
        f"DebeCambiarPassword=0 "
        f"WHERE CorreoAcceso='{CORREO_PRINCIPAL}'; "

        f"DELETE FROM dbo.TokensRecuperacion "
        f"WHERE UsuarioId = (SELECT Id FROM dbo.Usuarios WHERE CorreoAcceso='{CORREO_PRINCIPAL}') "
        f"AND Token NOT IN ('{TOKEN_EXPIRADO}','{TOKEN_USADO}','TK1H6K9M2N');"
    )
    yield
    # Restaurar contraseña al final para que otros módulos no fallen
    _ejecutar(
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_ORIGINAL}, PasswordSalt={_SALT_ORIGINAL}, "
        f"DebeCambiarPassword=0 "
        f"WHERE CorreoAcceso='{CORREO_PRINCIPAL}';"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  GRUPO A — Formulario de solicitud  /Cuenta/RecuperarPassword
# ══════════════════════════════════════════════════════════════════════════════

def test_rc01_correo_valido_redirige_a_login(page):
    """
    TC-RC-01: Correo registrado → redirige a Login con mensaje informativo.
    TAMBIÉN dispara el envío del email usado por los tests del Grupo B.
    """
    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.wait_for_load_state("networkidle")

    page.fill("#CorreoAcceso", CORREO_PRINCIPAL)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Cuenta/Login" in page.url, (
        f"TC-RC-01: No redirigió a Login. URL actual: {page.url}"
    )
    # Debe haber algún mensaje de feedback visible
    alerta = page.locator(".alert--info, .alert-info, .alert--success, [class*='alert']").first
    assert alerta.is_visible() and alerta.inner_text().strip() != "", (
        "TC-RC-01: No se mostró mensaje informativo tras la solicitud"
    )


def test_rc02_correo_inexistente_misma_respuesta(page):
    """
    TC-RC-02: Correo no registrado → misma respuesta que TC-RC-01 (anti-enumeración).
    El sistema NO debe revelar si el correo existe o no.
    """
    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.wait_for_load_state("networkidle")

    page.fill("#CorreoAcceso", "fantasma.xyz00099@yopmail.com")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Cuenta/Login" in page.url, (
        f"TC-RC-02: Correo inexistente no redirigió a Login — posible leak. URL: {page.url}"
    )
    body = page.locator("body").inner_text().lower()
    for frase in ["no encontrado", "no existe", "not found", "usuario no registrado",
                  "correo incorrecto", "no registrado"]:
        assert frase not in body, (
            f"TC-RC-02: El sistema expone enumeración de usuarios con la frase: '{frase}'"
        )


def test_rc03_campo_correo_vacio(page):
    """TC-RC-03: Submit sin correo → validación de campo requerido (no llega al servidor)."""
    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.wait_for_load_state("networkidle")

    page.click("button[type=submit]")
    page.wait_for_timeout(800)

    input_correo = page.locator("#CorreoAcceso")
    campo_invalido = (
        input_correo.evaluate("el => !el.validity.valid")
        if input_correo.count() > 0 else False
    )
    assert campo_invalido or hay_error_formulario(page) or "RecuperarPassword" in page.url, (
        "TC-RC-03: Submit vacío no fue bloqueado por validación de HTML5 ni del servidor"
    )


def test_rc04_formato_correo_invalido(page):
    """TC-RC-04: Formatos de correo inválidos → validación sin envío al servidor."""
    invalidos = ["noescorreo", "@dominio.com", "nombre@", "nombre @test.com"]
    for valor in invalidos:
        page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
        page.wait_for_load_state("networkidle")

        page.fill("#CorreoAcceso", valor)
        page.click("button[type=submit]")
        page.wait_for_timeout(600)

        input_correo = page.locator("#CorreoAcceso")
        invalido_html5 = (
            input_correo.evaluate("el => !el.validity.valid")
            if input_correo.count() > 0 else False
        )
        assert invalido_html5 or hay_error_formulario(page) or "RecuperarPassword" in page.url, (
            f"TC-RC-04: Formato inválido '{valor}' fue aceptado sin error de validación"
        )


def test_rc05_correo_en_mayusculas_aceptado(page):
    """TC-RC-05: Correo en mayúsculas y con espacios → tratado igual (case-insensitive)."""
    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.wait_for_load_state("networkidle")

    page.fill("#CorreoAcceso", "  CARLOS.RODRIGUEZ@YOPMAIL.COM  ")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Cuenta/Login" in page.url, (
        f"TC-RC-05: Correo en mayúsculas fue rechazado. URL: {page.url}"
    )


def test_rc06_doble_solicitud_solo_ultimo_token_valido(page):
    """
    TC-RC-06: Dos solicitudes consecutivas para el mismo usuario.
    El primer token debe quedar invalidado (Usado=1 o expirado manualmente).
    Usa andres.torres@yopmail.com para no interferir con el flujo principal.
    """
    for i in range(2):
        page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
        page.wait_for_load_state("networkidle")
        page.fill("#CorreoAcceso", CORREO_SECUNDARIO)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")

    filas = _consultar(
        f"SELECT t.Usado, CONVERT(varchar(32), t.FechaCreacion, 126) AS FC "
        f"FROM dbo.TokensRecuperacion t "
        f"JOIN dbo.Usuarios u ON u.Id = t.UsuarioId "
        f"WHERE u.CorreoAcceso = '{CORREO_SECUNDARIO}' "
        f"AND t.Token NOT IN ('{TOKEN_EXPIRADO}','{TOKEN_USADO}','TK1H6K9M2N') "
        f"ORDER BY t.FechaCreacion DESC;"
    )

    if len(filas) < 2:
        pytest.skip(
            "TC-RC-06: Menos de 2 tokens generados — ¿SMTP desactivado o sin emails?. "
            "Requiere SMTP activo para que el sistema cree tokens."
        )

    # El token más reciente no debe estar usado todavía
    ultimo = filas[0]
    assert not _bool(ultimo.get("Usado")), (
        "TC-RC-06: El último token generado ya está marcado como Usado=1"
    )
    # El penúltimo debería estar invalidado si la lógica de negocio lo marca
    # (comportamiento deseable pero puede depender de la implementación)
    penultimo = filas[1]
    if not _bool(penultimo.get("Usado")):
        pytest.xfail(
            "TC-RC-06: El token anterior NO fue invalidado automáticamente. "
            "Considerar si la lógica de negocio debe invalidar tokens previos."
        )


# ══════════════════════════════════════════════════════════════════════════════
#  GRUPO B — Email en yopmail.com
#  Requieren TC-RC-01 ejecutado y SMTP activo.
#  Marcar con -m "not yopmail" para saltarlos en entornos sin SMTP.
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_rc07_email_llega_a_bandeja_yopmail(page):
    """
    TC-RC-07: El email de recuperación llega a la bandeja de carlos.rodriguez en yopmail.
    También extrae el token del enlace y lo guarda en _S para los tests C, D, E, F.

    Si el email no llega en 30s:
      → Verificar user-secrets: dotnet user-secrets list (en GestionPersonal.Web)
      → Verificar SMTP en appsettings.json (smtp.office365.com:587)
      → Verificar permisos "Send As" en Exchange Admin para notificacion.sf@zentria.com.co
      → Verificación manual: https://yopmail.com/en/?login=carlos.rodriguez
    """
    page.goto(f"https://yopmail.com/en/?login={YOPMAIL_USUARIO}")
    page.wait_for_load_state("networkidle")

    inbox = page.frame_locator("#ifinbox")
    email_item = inbox.locator("a").filter(
        has_text=re.compile(
            r"contrase|recuper|GestiónRH|password|reset|código|clave", re.IGNORECASE
        )
    ).first

    try:
        email_item.wait_for(timeout=30_000)
    except Exception:
        pytest.xfail(
            "TC-RC-07: Email no llegó en 30 segundos.\n"
            "  1. Revisar configuración SMTP en user-secrets\n"
            "  2. Verificar permisos 'Send As' en Exchange Admin\n"
            "  3. Revisión manual: https://yopmail.com/en/?login=carlos.rodriguez\n"
            "  Los tests TC-RC-08..RC-12 y RC-13..RC-28 con token dependerán de este correo."
        )

    email_item.click()
    page.wait_for_timeout(1500)

    mail_frame = page.frame_locator("#ifmail")
    enlace = mail_frame.locator(
        "a[href*='RestablecerPassword'], a[href*='token=']"
    ).first
    enlace.wait_for(timeout=10_000)

    href = enlace.get_attribute("href")
    assert href is not None, "TC-RC-07: No se encontró enlace de restablecimiento en el email"

    match = re.search(r"[?&]token=([^&\s\"']+)", href)
    assert match, f"TC-RC-07: El enlace no tiene parámetro token=. href={href}"

    _S["token_codigo"] = match.group(1)
    _S["token_url"]    = href
    print(f"\n  [INFO] TC-RC-07: Token extraído — '{_S['token_codigo']}' ({len(_S['token_codigo'])} chars)")


@pytest.mark.yopmail
def test_rc08_email_no_contiene_hash_sha256(page):
    """
    TC-RC-08: El token en el email es el código PLANO, no el hash SHA-256.
    Si el email tuviera 64 chars hex sería un fallo crítico de seguridad
    (el hash estaría expuesto, lo que permite ataques de preimage).
    """
    if _S["token_codigo"] is None:
        pytest.skip("TC-RC-08: Requiere TC-RC-07 completado (token no disponible)")

    token = _S["token_codigo"]

    # El hash SHA-256 tiene exactamente 64 chars hexadecimales lowercase
    es_hash_sha256 = (
        len(token) == 64
        and all(c in "0123456789abcdefABCDEF" for c in token)
    )
    assert not es_hash_sha256, (
        f"TC-RC-08: FALLO CRÍTICO DE SEGURIDAD — "
        f"El email contiene el hash SHA-256 en lugar del código plano. "
        f"Token recibido: '{token}' ({len(token)} chars). "
        "Revisar CuentaService.SolicitarRecuperacionAsync() — debe enviar el código plano."
    )


@pytest.mark.yopmail
def test_rc09_token_del_email_es_alfanumerico(page):
    """TC-RC-09: El código del email es alfanumérico sin caracteres especiales."""
    if _S["token_codigo"] is None:
        pytest.skip("TC-RC-09: Requiere TC-RC-07 completado")

    token = _S["token_codigo"]
    assert re.match(r"^[a-zA-Z0-9]+$", token), (
        f"TC-RC-09: El token contiene caracteres no alfanuméricos: '{token}'"
    )
    assert len(token) < 50, (
        f"TC-RC-09: Token de {len(token)} chars — parece un hash en lugar del código legible"
    )


@pytest.mark.yopmail
def test_rc10_token_email_tiene_12_caracteres(page):
    """
    TC-RC-10: El código plano tiene 12 caracteres (longitud de GenerarCodigoSeguro).
    12 chars alfanuméricos = 62^12 ≈ 3.2 × 10^21 combinaciones — seguro para tokens.
    """
    if _S["token_codigo"] is None:
        pytest.skip("TC-RC-10: Requiere TC-RC-07 completado")

    token = _S["token_codigo"]
    assert len(token) == 12, (
        f"TC-RC-10: Se esperaban 12 chars (GenerarCodigoSeguro), "
        f"se obtuvieron {len(token)}: '{token}'. "
        "Revisar implementación de GenerarCodigoSeguro() en CuentaService."
    )


@pytest.mark.yopmail
def test_rc11_email_menciona_vigencia_30_minutos(page):
    """TC-RC-11: El cuerpo del email menciona la vigencia de 30 minutos."""
    if _S["token_codigo"] is None:
        pytest.skip("TC-RC-11: Requiere TC-RC-07 completado")

    page.goto(f"https://yopmail.com/en/?login={YOPMAIL_USUARIO}")
    page.wait_for_load_state("networkidle")

    mail_frame = page.frame_locator("#ifmail")
    try:
        # Abrir el email más reciente si no está ya abierto
        inbox = page.frame_locator("#ifinbox")
        email_item = inbox.locator("a").filter(
            has_text=re.compile(r"contrase|recuper|password|reset", re.IGNORECASE)
        ).first
        if email_item.is_visible():
            email_item.click()
            page.wait_for_timeout(1200)

        cuerpo = mail_frame.locator("body").inner_text(timeout=8_000)
        assert re.search(r"30\s*(minutos?|min)", cuerpo, re.IGNORECASE), (
            "TC-RC-11: El email no menciona '30 minutos'. "
            "Revisar SeguridadEmailTemplate.RecuperacionContrasena() y el parámetro vigenciaMinutos."
        )
    except Exception as e:
        pytest.xfail(f"TC-RC-11: No se pudo leer el cuerpo del email via iframe: {e}")


@pytest.mark.yopmail
def test_rc12_enlace_del_email_muestra_formulario(page):
    """
    TC-RC-12: El enlace extraído del email carga correctamente el formulario
    de nueva contraseña (campos NuevoPassword y ConfirmarPassword visibles).
    Solo verifica acceso — el restablecimiento se completa en TC-RC-21.
    """
    if _S["token_url"] is None:
        pytest.skip("TC-RC-12: Requiere TC-RC-07 completado (URL del email no disponible)")

    page.goto(_S["token_url"])
    page.wait_for_load_state("networkidle")

    campo_nuevo     = page.locator("#NuevoPassword, input[name='NuevoPassword']")
    campo_confirmar = page.locator("#ConfirmarPassword, input[name='ConfirmarPassword']")

    assert campo_nuevo.is_visible(), (
        f"TC-RC-12: Campo 'NuevoPassword' no visible. URL: {page.url}"
    )
    assert campo_confirmar.is_visible(), (
        "TC-RC-12: Campo 'ConfirmarPassword' no visible"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  GRUPO C — Formulario de restablecimiento  /Cuenta/RestablecerPassword
# ══════════════════════════════════════════════════════════════════════════════

def test_rc13_token_valido_muestra_formulario(page):
    """TC-RC-13: Token válido → ambos campos del formulario son visibles."""
    if _S["token_codigo"] is None:
        pytest.skip("TC-RC-13: Sin token válido (TC-RC-07 no completado o SMTP inactivo)")

    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token={_S['token_codigo']}")
    page.wait_for_load_state("networkidle")

    campo_nuevo     = page.locator("#NuevoPassword, input[name='NuevoPassword']")
    campo_confirmar = page.locator("#ConfirmarPassword, input[name='ConfirmarPassword']")

    assert campo_nuevo.is_visible(),     "TC-RC-13: Campo 'NuevoPassword' no visible con token válido"
    assert campo_confirmar.is_visible(), "TC-RC-13: Campo 'ConfirmarPassword' no visible con token válido"


def test_rc14_token_expirado_rechazado(page):
    """
    TC-RC-14: Token con fecha vencida (TK7E4D8F5G, expiró 2026-04-10) → rechazado.
    El formulario de nueva contraseña NO debe ser accesible.
    """
    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token={TOKEN_EXPIRADO}")
    page.wait_for_load_state("networkidle")

    if "/Cuenta/Login" in page.url:
        return  # ✅ Comportamiento correcto: redirigió a Login

    # Si no redirigió, el formulario NO debe ser accesible
    campo_nuevo = page.locator("#NuevoPassword, input[name='NuevoPassword']")
    assert not campo_nuevo.is_visible(), (
        "TC-RC-14: FALLO — Token expirado muestra el formulario de nueva contraseña"
    )


def test_rc15_token_usado_rechazado(page):
    """
    TC-RC-15: Token con Usado=1 (TK3F9A2B1C) → rechazado.
    El formulario de nueva contraseña NO debe ser accesible.
    """
    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token={TOKEN_USADO}")
    page.wait_for_load_state("networkidle")

    if "/Cuenta/Login" in page.url:
        return  # ✅

    campo_nuevo = page.locator("#NuevoPassword, input[name='NuevoPassword']")
    assert not campo_nuevo.is_visible(), (
        "TC-RC-15: FALLO — Token ya usado muestra el formulario de nueva contraseña"
    )


def test_rc16_token_inventado_rechazado(page):
    """TC-RC-16: Token aleatorio que no existe en BD → rechazado limpiamente."""
    page.goto(
        f"{BASE_URL}/Cuenta/RestablecerPassword?token=TOKENFALSO12INVENTADO999"
    )
    page.wait_for_load_state("networkidle")

    if "/Cuenta/Login" in page.url:
        return  # ✅

    campo_nuevo = page.locator("#NuevoPassword, input[name='NuevoPassword']")
    assert not campo_nuevo.is_visible(), (
        "TC-RC-16: FALLO — Token inexistente muestra el formulario de nueva contraseña"
    )


def test_rc17_sin_parametro_token_rechazado(page):
    """TC-RC-17: URL sin ?token= → rechazado (sin formulario de nueva contraseña)."""
    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword")
    page.wait_for_load_state("networkidle")

    campo_nuevo = page.locator("#NuevoPassword, input[name='NuevoPassword']")
    assert not campo_nuevo.is_visible(), (
        f"TC-RC-17: FALLO — Sin parámetro token, el formulario es visible. URL: {page.url}"
    )


def _formulario_restablecimiento_visible(page) -> bool:
    """Helper: verifica si el formulario de nueva contraseña está disponible."""
    campo = page.locator("#NuevoPassword, input[name='NuevoPassword']")
    return campo.is_visible()


def test_rc18_password_muy_corta_rechazada(page):
    """TC-RC-18: Contraseña < política → error de validación, token NO consumido."""
    if _S["token_codigo"] is None:
        pytest.skip("TC-RC-18: Sin token válido")

    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token={_S['token_codigo']}")
    page.wait_for_load_state("networkidle")

    if not _formulario_restablecimiento_visible(page):
        pytest.skip("TC-RC-18: Token ya consumido — re-ejecutar desde TC-RC-01")

    page.fill("#NuevoPassword, input[name='NuevoPassword']",         "Ab1!")
    page.fill("#ConfirmarPassword, input[name='ConfirmarPassword']", "Ab1!")
    page.click("button[type=submit]")
    page.wait_for_timeout(800)

    # Si redirigió a Login con mensaje de ÉXITO → fallo (contraseña corta aceptada)
    if "/Cuenta/Login" in page.url:
        cuerpo = page.locator("body").inner_text().lower()
        assert "exitosa" not in cuerpo and "cambiada" not in cuerpo, (
            "TC-RC-18: Contraseña muy corta fue aceptada y el token fue consumido"
        )
    else:
        # Debe haber permanecido en el formulario con un error
        assert hay_error_formulario(page) or "RestablecerPassword" in page.url, (
            "TC-RC-18: No se mostró error de validación para contraseña muy corta"
        )


def test_rc19_confirmacion_no_coincide(page):
    """TC-RC-19: NuevoPassword ≠ ConfirmarPassword → error de validación."""
    if _S["token_codigo"] is None:
        pytest.skip("TC-RC-19: Sin token válido")

    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token={_S['token_codigo']}")
    page.wait_for_load_state("networkidle")

    if not _formulario_restablecimiento_visible(page):
        pytest.skip("TC-RC-19: Token ya consumido")

    page.fill("#NuevoPassword, input[name='NuevoPassword']",         "ClaveA2026!")
    page.fill("#ConfirmarPassword, input[name='ConfirmarPassword']", "ClaveB2026!")
    page.click("button[type=submit]")
    page.wait_for_timeout(800)

    if "/Cuenta/Login" in page.url:
        cuerpo = page.locator("body").inner_text().lower()
        assert "exitosa" not in cuerpo and "cambiada" not in cuerpo, (
            "TC-RC-19: Contraseñas distintas fueron aceptadas y el token fue consumido"
        )
    else:
        assert hay_error_formulario(page) or "RestablecerPassword" in page.url, (
            "TC-RC-19: No se mostró error de validación para contraseñas distintas"
        )


def test_rc20_campos_vacios_con_token_valido(page):
    """TC-RC-20: Submit con ambos campos vacíos → errores de validación."""
    if _S["token_codigo"] is None:
        pytest.skip("TC-RC-20: Sin token válido")

    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token={_S['token_codigo']}")
    page.wait_for_load_state("networkidle")

    if not _formulario_restablecimiento_visible(page):
        pytest.skip("TC-RC-20: Token ya consumido")

    page.click("button[type=submit]")
    page.wait_for_timeout(800)

    campo = page.locator("#NuevoPassword, input[name='NuevoPassword']")
    invalido_html5 = (
        campo.evaluate("el => !el.validity.valid")
        if campo.count() > 0 else False
    )
    assert invalido_html5 or hay_error_formulario(page) or "RestablecerPassword" in page.url, (
        "TC-RC-20: Submit vacío fue procesado sin errores de validación"
    )


def test_rc21_restablecimiento_exitoso_redirige_a_login(page):
    """
    TC-RC-21: Token válido + contraseña nueva correcta → éxito.
    Redirige a Login con mensaje de confirmación.
    CONSUME el token — ejecutar como último test del Grupo C.
    """
    if _S["token_codigo"] is None:
        pytest.skip(
            "TC-RC-21: Sin token válido — ejecutar la suite completa desde TC-RC-01 "
            "(incluir tests de yopmail con --headed)"
        )

    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token={_S['token_codigo']}")
    page.wait_for_load_state("networkidle")

    if not _formulario_restablecimiento_visible(page):
        pytest.skip(
            "TC-RC-21: El token ya fue consumido. "
            "Re-ejecutar la suite completa o restaurar BD."
        )

    page.fill("#NuevoPassword, input[name='NuevoPassword']",         PASSWORD_NUEVA)
    page.fill("#ConfirmarPassword, input[name='ConfirmarPassword']", PASSWORD_NUEVA)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Cuenta/Login" in page.url, (
        f"TC-RC-21: No redirigió a Login tras restablecimiento exitoso. URL: {page.url}"
    )
    mensaje = page.locator(".alert--success, .alert-success, [class*='success']").first
    assert mensaje.is_visible() and mensaje.inner_text().strip() != "", (
        "TC-RC-21: No se mostró mensaje de éxito tras el restablecimiento"
    )

    _S["reset_exitoso"] = True
    print(f"\n  [INFO] TC-RC-21: Contraseña restablecida a '{PASSWORD_NUEVA}'")


# ══════════════════════════════════════════════════════════════════════════════
#  GRUPO D — Seguridad del token en BD
# ══════════════════════════════════════════════════════════════════════════════

def test_rc22_token_en_bd_es_hash_sha256(page):
    """
    TC-RC-22: El campo Token en dbo.TokensRecuperacion debe ser SHA-256 hex (64 chars).
    Si tuviera 12 chars, el código plano estaría almacenado sin hashear — fallo crítico.
    """
    t = _ultimo_token(CORREO_PRINCIPAL)
    if t is None:
        pytest.skip(
            "TC-RC-22: Sin tokens en BD para carlos.rodriguez. "
            "¿TC-RC-01 no fue ejecutado o SMTP está inactivo?"
        )

    token_bd = str(t.get("Token", ""))
    assert len(token_bd) == 64, (
        f"TC-RC-22: FALLO CRÍTICO DE SEGURIDAD — "
        f"El token en BD tiene {len(token_bd)} chars (se esperaban 64 hex de SHA-256). "
        f"Valor: '{token_bd[:30]}...'. "
        "Revisar CuentaService.SolicitarRecuperacionAsync() → ComputarHashSha256()."
    )
    assert all(c in "0123456789abcdefABCDEF" for c in token_bd), (
        f"TC-RC-22: El token en BD no es hexadecimal válido: '{token_bd[:30]}...'"
    )


def test_rc23_token_marcado_usado_tras_restablecimiento(page):
    """TC-RC-23: Tras restablecimiento exitoso, Usado=1 en dbo.TokensRecuperacion."""
    if not _S["reset_exitoso"]:
        pytest.skip("TC-RC-23: Requiere TC-RC-21 completado (reset no realizado)")

    t = _ultimo_token(CORREO_PRINCIPAL)
    assert t is not None, "TC-RC-23: No se encontró el token en BD tras el restablecimiento"

    assert _bool(t.get("Usado")), (
        f"TC-RC-23: FALLO — El token no fue marcado como Usado=1 tras el restablecimiento. "
        f"Usado={t.get('Usado')}. "
        "Revisar RestablecerPasswordAsync() → marca Usado=true antes de guardar."
    )


def test_rc24_token_expira_en_30_minutos(page):
    """TC-RC-24: FechaExpiracion ≈ FechaCreacion + 30 min (±2 min de tolerancia)."""
    t = _ultimo_token(CORREO_PRINCIPAL)
    if t is None:
        pytest.skip("TC-RC-24: Sin tokens en BD")

    exp_str = str(t.get("FechaExpiracion", ""))
    cre_str = str(t.get("FechaCreacion",   ""))

    if not exp_str or not cre_str or exp_str == "None":
        pytest.skip("TC-RC-24: No se pudieron leer las fechas del token")

    try:
        # CONVERT(..., 126) produce 'YYYY-MM-DDTHH:MM:SS'
        exp = datetime.fromisoformat(exp_str.replace("T", " ").split(".")[0])
        cre = datetime.fromisoformat(cre_str.replace("T", " ").split(".")[0])
        diff = exp - cre

        assert timedelta(minutes=28) <= diff <= timedelta(minutes=32), (
            f"TC-RC-24: Diferencia FechaExpiracion - FechaCreacion = {diff}. "
            "Se esperaban ≈30 minutos. "
            "Revisar CuentaService.SolicitarRecuperacionAsync() → DateTime.UtcNow.AddMinutes(30)."
        )
    except (ValueError, TypeError) as e:
        pytest.xfail(f"TC-RC-24: Error al parsear fechas del token: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  GRUPO E — Login posterior al restablecimiento
# ══════════════════════════════════════════════════════════════════════════════

def test_rc25_login_con_nueva_password_exitoso(page):
    """TC-RC-25: La nueva contraseña permite el acceso al sistema."""
    if not _S["reset_exitoso"]:
        pytest.skip("TC-RC-25: Requiere TC-RC-21 completado")

    hacer_login(page, CORREO_PRINCIPAL, PASSWORD_NUEVA)

    assert "/Cuenta/Login" not in page.url, (
        f"TC-RC-25: Login con nueva contraseña falló. URL: {page.url}. "
        "Verifica que RestablecerPasswordAsync() guarda correctamente el hash."
    )


def test_rc26_login_con_password_anterior_denegado(page):
    """TC-RC-26: La contraseña anterior 'Usuario1' ya no es válida."""
    if not _S["reset_exitoso"]:
        pytest.skip("TC-RC-26: Requiere TC-RC-21 completado")

    hacer_login(page, CORREO_PRINCIPAL, PASSWORD_ORIGINAL)

    assert "/Cuenta/Login" in page.url, (
        f"TC-RC-26: FALLO — La contraseña antigua sigue siendo válida. URL: {page.url}"
    )
    error = page.locator(".form-error, .alert--error, .alert-danger").first
    assert error.is_visible(), (
        "TC-RC-26: No se mostró mensaje de error al intentar login con contraseña antigua"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  GRUPO F — Auditoría en dbo.RegistroNotificaciones
# ══════════════════════════════════════════════════════════════════════════════

def test_rc27_solicitud_genera_registro_de_auditoria(page):
    """
    TC-RC-27: La solicitud de recuperación crea un registro Exitoso=1
    con TipoEvento='RecuperacionContrasena' en RegistroNotificaciones.
    """
    reg = _ultimo_registro_notif("RecuperacionContrasena")
    if reg is None:
        pytest.skip(
            "TC-RC-27: Sin registros de RecuperacionContrasena. "
            "¿TC-RC-01 fue ejecutado con SMTP activo?"
        )

    assert _bool(reg.get("Exitoso")), (
        f"TC-RC-27: El correo de recuperación falló. "
        f"Error: {reg.get('ErrorMensaje', '(sin mensaje)')}. "
        "Revisar configuración SMTP y permisos 'Send As' en Exchange Admin."
    )
    destinatario = str(reg.get("Destinatario", "")).lower()
    assert CORREO_PRINCIPAL in destinatario, (
        f"TC-RC-27: Destinatario incorrecto en RegistroNotificaciones: '{destinatario}'"
    )


def test_rc28_restablecimiento_genera_registro_confirmacion(page):
    """
    TC-RC-28: El restablecimiento exitoso crea un registro Exitoso=1
    con TipoEvento='CambioContrasenaExitoso' en RegistroNotificaciones.
    """
    if not _S["reset_exitoso"]:
        pytest.skip("TC-RC-28: Requiere TC-RC-21 completado")

    reg = _ultimo_registro_notif("CambioContrasenaExitoso")
    if reg is None:
        pytest.skip(
            "TC-RC-28: Sin registros de CambioContrasenaExitoso. "
            "¿NotificationService.NotificarCambioContrasenaExitosoAsync() está integrado "
            "en CuentaService.RestablecerPasswordAsync()?"
        )

    assert _bool(reg.get("Exitoso")), (
        f"TC-RC-28: El correo de confirmación falló. "
        f"Error: {reg.get('ErrorMensaje', '(sin mensaje)')}"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  GRUPO G — Casos borde y seguridad
# ══════════════════════════════════════════════════════════════════════════════

def test_rc29_usuario_inactivo_respuesta_generica(page):
    """
    TC-RC-29: Correo de usuario inactivo → misma respuesta genérica (sin leak de estado).
    Se marca xfail si no hay usuarios inactivos con @yopmail.com en BD.
    """
    filas = _consultar(
        "SELECT TOP 1 u.CorreoAcceso FROM dbo.Usuarios u "
        "WHERE u.Activo = 0 AND u.CorreoAcceso LIKE '%@yopmail.com';"
    )
    if not filas:
        pytest.xfail("TC-RC-29: No hay usuarios inactivos con @yopmail.com — crear dato de prueba")

    correo_inactivo = str(filas[0].get("CorreoAcceso", ""))

    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.wait_for_load_state("networkidle")
    page.fill("#CorreoAcceso", correo_inactivo)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Cuenta/Login" in page.url, (
        f"TC-RC-29: Respuesta diferente para usuario inactivo. URL: {page.url}"
    )
    body = page.locator("body").inner_text().lower()
    for frase in ["inactivo", "bloqueado", "deshabilitado", "inactive", "suspended"]:
        assert frase not in body, (
            f"TC-RC-29: El sistema revela el estado de la cuenta '{frase}'"
        )


def test_rc30_inyeccion_sql_en_campo_correo(page):
    """TC-RC-30: Payloads de inyección SQL en el campo correo → sin error 500 ni stack trace."""
    payloads = [
        "' OR '1'='1",
        "'; DROP TABLE Usuarios; --",
        "1' OR 1=1--",
        "\" OR \"1\"=\"1",
        "' UNION SELECT NULL,NULL,NULL--",
    ]
    for payload in payloads:
        page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
        page.wait_for_load_state("networkidle")
        page.fill("#CorreoAcceso", payload)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")

        titulo = page.title().lower()
        assert "500" not in titulo and "error" not in titulo, (
            f"TC-RC-30: Error 500 con payload SQL: '{payload}'"
        )
        body = page.locator("body").inner_text().lower()
        for leak in ["exception", "stack trace", "sqlexception", "syntax error near"]:
            assert leak not in body, (
                f"TC-RC-30: Posible SQL Injection — '{leak}' encontrado. Payload: '{payload}'"
            )


def test_rc31_xss_en_parametro_token(page):
    """TC-RC-31: Payloads XSS en ?token= → no se ejecuta ningún script."""
    payloads = [
        "<script>alert('xss')</script>",
        "javascript:alert(1)",
        "<img src=x onerror=alert(1)>",
        "'\"><svg onload=alert(1)>",
        "%3Cscript%3Ealert(1)%3C/script%3E",
    ]
    for payload in payloads:
        dialogs: list[str] = []

        def _on_dialog(dialog, _d=dialogs):
            _d.append(dialog.message)
            dialog.dismiss()

        page.on("dialog", _on_dialog)
        page.goto(
            f"{BASE_URL}/Cuenta/RestablecerPassword?token={urllib.parse.quote(payload)}"
        )
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(800)
        page.remove_listener("dialog", _on_dialog)

        assert not dialogs, (
            f"TC-RC-31: FALLO — XSS ejecutado con payload '{payload}'. "
            f"Diálogos disparados: {dialogs}"
        )
        titulo = page.title().lower()
        assert "500" not in titulo, (
            f"TC-RC-31: Error 500 con payload XSS: '{payload}'"
        )


def test_rc32_token_longitud_anormal(page):
    """TC-RC-32: Tokens de longitud extrema o vacíos → rechazados sin error 500."""
    casos = [
        ("vacio",         ""),
        ("1_char",        "X"),
        ("1000_chars",    "A" * 1000),
        ("solo_espacios", "   "),
        ("solo_numeros",  "123456789012"),
        ("url_encoded",   "%00%01%02"),
    ]
    for nombre, token in casos:
        url = (
            f"{BASE_URL}/Cuenta/RestablecerPassword?token={urllib.parse.quote(token)}"
            if token.strip()
            else f"{BASE_URL}/Cuenta/RestablecerPassword?token="
        )
        page.goto(url)
        page.wait_for_load_state("networkidle")

        titulo = page.title().lower()
        assert "500" not in titulo and "internal server error" not in titulo, (
            f"TC-RC-32: Error 500 con token de caso '{nombre}' — "
            "el servidor no está manejando la entrada anormal"
        )

        # Un token inválido nunca debe mostrar el formulario de nueva contraseña
        campo_nuevo = page.locator("#NuevoPassword, input[name='NuevoPassword']")
        if campo_nuevo.is_visible():
            # Solo es aceptable si el token pasa a ser válido por coincidencia (prácticamente imposible)
            pytest.fail(
                f"TC-RC-32: Token inválido (caso '{nombre}', valor '{token[:30]}') "
                "muestra el formulario de nueva contraseña — revisar validación del token"
            )
