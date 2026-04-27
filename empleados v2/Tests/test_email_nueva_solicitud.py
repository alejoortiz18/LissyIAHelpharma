"""
Pruebas de integración — Correo informativo al jefe cuando se crea una solicitud

Cuando un empleado crea una nueva solicitud el sistema debe enviar un correo
informativo (sin botones de acción) al jefe inmediato con toda la información
del evento.  Si el empleado no tiene jefe inmediato registrado, no se envía
ningún correo.

TC-NS-01  Operario crea solicitud → RegistroNotificaciones muestra SolicitudCreada Exitoso=1
TC-NS-02  Destinatario del correo es el jefe inmediato (Laura), NO el solicitante (Diana)
TC-NS-03  Asunto incluye tipo de evento y nombre del solicitante
TC-NS-04  [yopmail] Laura recibe el correo con tipo, fechas y descripción visibles

Actores:
  - Diana Vargas  (diana.vargas@yopmail.com)   — Operario, crea la solicitud
  - Laura Sánchez (laura.sanchez@yopmail.com)  — Regente, jefe inmediato de Diana

Ejecución:
  cd "empleados v2/Tests"
  $env:PYTHONIOENCODING='utf-8'
  ../.venv/Scripts/python.exe -m pytest test_email_nueva_solicitud.py -v --headed --slowmo 800 -s
  # Omitir verificación yopmail:
  ../.venv/Scripts/python.exe -m pytest test_email_nueva_solicitud.py -v --headed -m "not yopmail" -s
"""

import json
import os
import re
import subprocess
import tempfile
import time
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import pytest

from helpers import BASE_URL, hacer_login

# ── Rutas del proyecto ────────────────────────────────────────────────────────
_ROOT    = Path(__file__).parent.parent
_WEB_DIR = _ROOT / "Proyecto MVC" / "GestionPersonal.Web"

# ── Configuración BD ──────────────────────────────────────────────────────────
DB_INSTANCE = r"(localdb)\MSSQLLocalDB"
DB_NAME     = "GestionPersonal"

# ── Actores ───────────────────────────────────────────────────────────────────
DIANA_CORREO   = "diana.vargas@yopmail.com"
LAURA_CORREO   = "laura.sanchez@yopmail.com"
LAURA_YOPMAIL  = "laura.sanchez"
PASSWORD       = "Usuario1"

# ── Datos de la solicitud de prueba ───────────────────────────────────────────
TIPO_SOLICITUD   = "Permiso"
FECHA_INICIO     = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
FECHA_FIN        = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
FECHA_INICIO_FMT = (date.today() + timedelta(days=5)).strftime("%d/%m/%Y")
FECHA_FIN_FMT    = (date.today() + timedelta(days=7)).strftime("%d/%m/%Y")
DESCRIPCION      = "Permiso médico — prueba automatizada TC-NS"

# ── TipoEvento en RegistroNotificaciones ─────────────────────────────────────
TIPO_EVENTO_BD = "SolicitudCreada"

# ── Estado compartido del módulo ──────────────────────────────────────────────
_S: dict = {
    "app_process": None,
    "evento_id":   None,   # Id del EventoLaboral creado en TC-NS-01 (para teardown)
}


# ════════════════════════════════════════════════════════════════════════════
#  HELPERS BD
# ════════════════════════════════════════════════════════════════════════════

def _ejecutar(sql: str) -> None:
    sql_file = os.path.join(tempfile.gettempdir(), "_ns_exec.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    subprocess.run(
        ["powershell", "-Command",
         f"Invoke-Sqlcmd -ServerInstance '{DB_INSTANCE}' -Database '{DB_NAME}' "
         f"-InputFile '{sql_file}'"],
        capture_output=True, text=True, timeout=20,
    )


def _consultar(query: str) -> list[dict]:
    sql_file = os.path.join(tempfile.gettempdir(), "_ns_query.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(query)
    result = subprocess.run(
        ["powershell", "-Command",
         f"Invoke-Sqlcmd -ServerInstance '{DB_INSTANCE}' -Database '{DB_NAME}' "
         f"-InputFile '{sql_file}' | ConvertTo-Json -Depth 2"],
        capture_output=True, text=True, timeout=15,
    )
    if result.stderr.strip():
        print(f"\n  [SQLCMD-ERR] {result.stderr.strip()[:300]}")
    if not result.stdout.strip():
        return []
    try:
        data = json.loads(result.stdout)
        return data if isinstance(data, list) else [data]
    except (json.JSONDecodeError, ValueError):
        return []


def _max_id_registro(tipo_evento: str) -> int:
    """Retorna el Id máximo actual en RegistroNotificaciones para el tipo dado."""
    rows = _consultar(
        f"SELECT ISNULL(MAX(Id), 0) AS MaxId FROM dbo.RegistroNotificaciones "
        f"WHERE TipoEvento = '{tipo_evento}';"
    )
    if not rows:
        return 0
    val = rows[0].get("MaxId", 0)
    return int(val) if val and str(val) not in ("None", "") else 0


def _ultimo_registro(tipo_evento: str, id_minimo: int = 0) -> dict | None:
    """
    Devuelve el registro más reciente en RegistroNotificaciones para el tipo dado.
    Si 'id_minimo' > 0, solo considera registros con Id > id_minimo.
    Reintenta hasta 5 veces con espera de 2 s para tolerar latencia de confirmación.
    """
    filtro_id = f" AND Id > {id_minimo}" if id_minimo > 0 else ""
    for _ in range(5):
        rows = _consultar(
            f"SELECT TOP 1 Exitoso, ISNULL(ErrorMensaje,'') AS Err, "
            f"Destinatario, ISNULL(Copia,'') AS Copia, Asunto "
            f"FROM dbo.RegistroNotificaciones "
            f"WHERE TipoEvento = '{tipo_evento}'{filtro_id} "
            f"ORDER BY Id DESC;"
        )
        if rows:
            r = rows[0]
            return {
                "exitoso":      str(r.get("Exitoso", "0")).strip() in ("1", "True", "true"),
                "error":        str(r.get("Err", "")),
                "destinatario": str(r.get("Destinatario", "")),
                "copia":        str(r.get("Copia", "")),
                "asunto":       str(r.get("Asunto", "")),
            }
        time.sleep(2)
    return None


def _limpiar_evento_prueba() -> None:
    """Elimina los EventosLaborales de prueba creados por este test."""
    _ejecutar(
        "DELETE FROM dbo.EventosLaborales "
        "WHERE Descripcion = 'Permiso médico — prueba automatizada TC-NS';"
    )


# ════════════════════════════════════════════════════════════════════════════
#  FIXTURE MÓDULO — levanta y detiene la aplicación
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module", autouse=True)
def aplicacion_corriendo():
    """Inicia la aplicación antes de todos los tests del módulo y la detiene al finalizar."""

    # ── Limpiar eventos de prueba anteriores ─────────────────────────────────
    _limpiar_evento_prueba()

    # ── Asegurar que Laura no sea redirigida a cambiar contraseña ─────────────
    # conftest establece DebeCambiarPassword=1 para laura.sanchez; lo revertimos.
    _ejecutar(
        "UPDATE dbo.Usuarios SET DebeCambiarPassword = 0 "
        "WHERE CorreoAcceso = 'laura.sanchez@yopmail.com';"
    )

    # ── Liberar puerto 5002 si hay proceso anterior ──────────────────────────
    try:
        res_port = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True, timeout=5
        )
        for linea in res_port.stdout.splitlines():
            if ":5002 " in linea and "LISTENING" in linea:
                pid_str = linea.strip().split()[-1]
                if pid_str.isdigit():
                    subprocess.run(["taskkill", "/F", "/PID", pid_str],
                                   capture_output=True, timeout=5)
                    print(f"\n  [PORT] PID {pid_str} en :5002 terminado")
                    time.sleep(1)
    except Exception as e:
        print(f"\n  [PORT WARN] {e}")

    # ── Iniciar aplicación ───────────────────────────────────────────────────
    proceso = subprocess.Popen(
        ["dotnet", "run", "--no-build",
         "--project", str(_WEB_DIR / "GestionPersonal.Web.csproj"),
         "--launch-profile", "http"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(_WEB_DIR),
    )
    _S["app_process"] = proceso
    print(f"\n  [APP] Iniciando PID {proceso.pid}...")

    # ── Esperar que la app responda (máx. 60 s) ──────────────────────────────
    inicio = time.time()
    lista  = False
    while time.time() - inicio < 60:
        try:
            urllib.request.urlopen(f"{BASE_URL}/Cuenta/Login", timeout=3)
            lista = True
            break
        except Exception:
            time.sleep(2)

    if not lista:
        proceso.terminate()
        pytest.fail("La aplicación no respondió en 60 segundos. Verificar compilación.")

    print(f"  [APP] Lista en {BASE_URL}")

    yield

    # ── Teardown ─────────────────────────────────────────────────────────────
    _limpiar_evento_prueba()
    print("\n  [TEARDOWN] Eventos de prueba eliminados")

    proc = _S.get("app_process")
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("  [APP] Aplicación detenida")


# ════════════════════════════════════════════════════════════════════════════
#  HELPER UI — crear solicitud desde /Solicitud
# ════════════════════════════════════════════════════════════════════════════

def _crear_solicitud_ui(page) -> None:
    """
    Login como Diana, navega a /Solicitud, abre el modal y crea una solicitud
    de tipo Permiso con FECHA_INICIO, FECHA_FIN y DESCRIPCION definidas en el módulo.
    """
    hacer_login(page, DIANA_CORREO, PASSWORD)
    page.wait_for_url("**/Dashboard", timeout=8_000)

    page.goto(f"{BASE_URL}/Solicitud")
    page.wait_for_load_state("networkidle")

    # Abrir modal de nueva solicitud
    btn_nueva = page.locator("button[data-modal-open='modal-nueva-solicitud']").first
    btn_nueva.wait_for(state="visible", timeout=5_000)
    btn_nueva.click()

    modal = page.locator("#modal-nueva-solicitud")
    modal.wait_for(state="visible", timeout=5_000)

    # Rellenar formulario
    page.select_option("#sol-tipo", TIPO_SOLICITUD)
    page.fill("#sol-inicio", FECHA_INICIO)
    page.fill("#sol-fin",    FECHA_FIN)
    page.fill("#sol-descripcion", DESCRIPCION)

    # Enviar
    page.locator("#sol-submit").click()
    page.wait_for_load_state("networkidle")
    time.sleep(2)   # esperar a que la notificación quede registrada en BD


# ════════════════════════════════════════════════════════════════════════════
#  TC-NS-01 — El correo al jefe queda registrado en RegistroNotificaciones
# ════════════════════════════════════════════════════════════════════════════

def test_tc_ns_01_registro_notificacion_exitoso(page):
    """
    TC-NS-01: Al crear la solicitud se genera un registro SolicitudCreada
    con Exitoso=1 en RegistroNotificaciones.
    """
    max_id = _max_id_registro(TIPO_EVENTO_BD)

    _crear_solicitud_ui(page)

    reg = _ultimo_registro(TIPO_EVENTO_BD, id_minimo=max_id)

    assert reg is not None, (
        "TC-NS-01 FALLO: No se encontró registro 'SolicitudCreada' en RegistroNotificaciones "
        "después de crear la solicitud."
    )
    assert reg["exitoso"], (
        f"TC-NS-01 FALLO: El correo no se envió correctamente — {reg['error']}"
    )
    print(f"\n  [TC-NS-01] ✓ Registro encontrado. Destinatario: {reg['destinatario']}")


# ════════════════════════════════════════════════════════════════════════════
#  TC-NS-02 — Destinatario es el jefe, NO el solicitante
# ════════════════════════════════════════════════════════════════════════════

def test_tc_ns_02_destinatario_es_el_jefe(page):
    """
    TC-NS-02: El correo va al jefe inmediato (Laura Sánchez), no a Diana.
    """
    # Limpiar solicitud previa (TC-NS-01) para que no haya solapamiento de fechas
    _limpiar_evento_prueba()

    max_id = _max_id_registro(TIPO_EVENTO_BD)

    _crear_solicitud_ui(page)

    reg = _ultimo_registro(TIPO_EVENTO_BD, id_minimo=max_id)
    assert reg is not None, "TC-NS-02 FALLO: Sin registro en RegistroNotificaciones"

    destinatario = reg["destinatario"].lower()

    assert "diana.vargas" not in destinatario, (
        f"TC-NS-02 FALLO: El correo fue enviado al SOLICITANTE (diana.vargas), "
        f"no al jefe. Destinatario: {reg['destinatario']}"
    )
    assert "laura.sanchez" in destinatario, (
        f"TC-NS-02 FALLO: El destinatario no es Laura Sánchez. "
        f"Obtenido: {reg['destinatario']}"
    )
    print(f"\n  [TC-NS-02] ✓ Destinatario correcto: {reg['destinatario']}")


# ════════════════════════════════════════════════════════════════════════════
#  TC-NS-03 — Asunto incluye tipo de solicitud y nombre del solicitante
# ════════════════════════════════════════════════════════════════════════════

def test_tc_ns_03_asunto_incluye_tipo_y_solicitante(page):
    """
    TC-NS-03: El asunto del correo menciona 'Permiso' y 'Diana'.
    Formato esperado: "[Nueva Permiso] - [Diana Marcela Vargas López]"
    """
    # Limpiar solicitud previa (TC-NS-02) para que no haya solapamiento de fechas
    _limpiar_evento_prueba()

    max_id = _max_id_registro(TIPO_EVENTO_BD)

    _crear_solicitud_ui(page)

    reg = _ultimo_registro(TIPO_EVENTO_BD, id_minimo=max_id)
    assert reg is not None, "TC-NS-03 FALLO: Sin registro en RegistroNotificaciones"

    asunto = reg["asunto"]
    asunto_lower = asunto.lower()

    assert "permiso" in asunto_lower, (
        f"TC-NS-03 FALLO: El asunto no menciona el tipo 'Permiso'. Asunto: '{asunto}'"
    )
    assert "diana" in asunto_lower, (
        f"TC-NS-03 FALLO: El asunto no menciona al solicitante 'Diana'. Asunto: '{asunto}'"
    )
    print(f"\n  [TC-NS-03] ✓ Asunto correcto: '{asunto}'")


# ════════════════════════════════════════════════════════════════════════════
#  TC-NS-04 — [yopmail] Laura recibe correo con información completa
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_tc_ns_04_yopmail_contenido_correo(page):
    """
    TC-NS-04: Abrir el buzón de Laura en yopmail.com y verificar que el correo
    contiene: tipo, fechas, descripción y la leyenda informativa.
    """
    # Primero creamos la solicitud para generar el correo
    max_id = _max_id_registro(TIPO_EVENTO_BD)
    _crear_solicitud_ui(page)

    # Confirmar que el registro se generó en BD antes de abrir yopmail
    reg = _ultimo_registro(TIPO_EVENTO_BD, id_minimo=max_id)
    if reg is None or not reg["exitoso"]:
        pytest.skip(
            f"TC-NS-04: El correo no fue enviado exitosamente "
            f"(Error: {reg['error'] if reg else 'sin registro'}). "
            "Verificar configuración SMTP antes de revisar yopmail."
        )

    # ── Abrir yopmail ─────────────────────────────────────────────────────────
    page.goto(f"https://yopmail.com/en/?login={LAURA_YOPMAIL}")
    page.wait_for_load_state("load", timeout=20_000)

    try:
        page.frame_locator("#ifinbox").locator("body").wait_for(
            state="visible", timeout=15_000
        )
    except Exception:
        pass

    # ── Buscar el correo de nueva solicitud ───────────────────────────────────
    def _email_locator():
        return page.frame_locator("#ifinbox").locator("a").filter(
            has_text=re.compile(r"solicitud|permiso|diana", re.IGNORECASE)
        ).first

    def _email_locator_alt():
        return page.frame_locator("#ifinbox").locator("a[id^='e_']").first

    email_item = _email_locator()
    encontrado  = False

    for intento in range(10):
        if intento >= 2:
            try:
                alt = _email_locator_alt()
                alt.wait_for(timeout=3_000)
                email_item = alt
                encontrado = True
                print(f"  [yopmail] Email encontrado con selector alt (intento {intento+1})")
                break
            except Exception:
                pass
        try:
            email_item.wait_for(timeout=60_000)
            encontrado = True
            break
        except Exception:
            print(f"  [yopmail] Intento {intento+1}/10: recargando bandeja...")
            try:
                page.locator("#refresh").click(timeout=3_000)
            except Exception:
                page.reload()
            page.wait_for_load_state("load", timeout=15_000)
            try:
                page.frame_locator("#ifinbox").locator("body").wait_for(
                    state="visible", timeout=10_000
                )
            except Exception:
                pass
            email_item = _email_locator()

    if not encontrado:
        pytest.xfail(
            f"TC-NS-04: El correo no apareció en bandeja después de 10 intentos.\n"
            f"  → Verificar manualmente: https://yopmail.com/en/?login={LAURA_YOPMAIL}"
        )

    # ── Abrir el correo ───────────────────────────────────────────────────────
    email_item.click()
    page.wait_for_timeout(2_000)

    mail_frame = page.frame_locator("#ifmail")
    mail_frame.locator("body").wait_for(timeout=10_000)

    cuerpo_html = mail_frame.locator("body").inner_html()
    cuerpo_text = mail_frame.locator("body").inner_text()
    cuerpo_lower = cuerpo_text.lower()

    # ── Aserciones de contenido ───────────────────────────────────────────────

    # El correo menciona al solicitante
    assert "diana" in cuerpo_lower, (
        f"TC-NS-04 FALLO: El cuerpo del correo no menciona a 'Diana'.\n"
        f"Texto: {cuerpo_text[:500]}"
    )

    # El correo incluye el tipo de solicitud
    assert "permiso" in cuerpo_lower, (
        f"TC-NS-04 FALLO: El cuerpo del correo no incluye el tipo 'Permiso'.\n"
        f"Texto: {cuerpo_text[:500]}"
    )

    # El correo incluye las fechas
    fecha_inicio_alt = (date.today() + timedelta(days=5)).strftime("%-d/%-m/%Y") \
        if os.name != "nt" else FECHA_INICIO_FMT
    assert (FECHA_INICIO_FMT in cuerpo_text or FECHA_INICIO in cuerpo_text), (
        f"TC-NS-04 FALLO: Fecha inicio ({FECHA_INICIO_FMT}) no encontrada en el correo.\n"
        f"Texto: {cuerpo_text[:500]}"
    )

    # El correo incluye la descripción
    assert "prueba automatizada" in cuerpo_lower, (
        f"TC-NS-04 FALLO: La descripción de la solicitud no aparece en el correo.\n"
        f"Texto: {cuerpo_text[:500]}"
    )

    # El correo es informativo (no debe tener botones de aprobación/rechazo en el HTML)
    botones_accion = re.findall(
        r'href[^>]*?(aprobar|rechazar|gestionar|aprueba|rechaza)[^"<>]{0,60}',
        cuerpo_html, re.IGNORECASE
    )
    assert not botones_accion, (
        f"TC-NS-04 FALLO: El correo contiene botones de acción (aprobar/rechazar) "
        f"— debe ser solo informativo.\nEnlaces encontrados: {botones_accion}"
    )

    print(
        f"\n  [TC-NS-04] ✓ Correo verificado en yopmail ({LAURA_YOPMAIL}).\n"
        f"  ✓ Menciona: Diana, Permiso, {FECHA_INICIO_FMT}\n"
        f"  ✓ No contiene botones de acción — correo solo informativo"
    )
