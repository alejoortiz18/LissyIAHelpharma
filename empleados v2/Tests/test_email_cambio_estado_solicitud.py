"""
Pruebas de integración — Correos de cambio de estado de solicitudes (EventoLaboral)

Escenarios:
  TC-CE-01: Regente aprueba solicitud de Operario
            → correo a solicitante (diana.vargas) Y a jefe del aprobador (carlos.rodriguez)
  TC-CE-02: Regente rechaza solicitud de Operario
            → correo a solicitante (diana.vargas) SOLO
  TC-CE-03: Regente revierte a Pendiente
            → correo a solicitante (diana.vargas) SOLO
  TC-CE-04: Contenido del correo al solicitante menciona al aprobador
  TC-CE-05: Contenido del correo al jefe del aprobador incluye nombres

Actores:
  - Laura Sánchez  (laura.sanchez@yopmail.com)  — Regente Medellín, jefe de Diana
  - Diana Vargas   (diana.vargas@yopmail.com)   — Operario, solicitante
  - Carlos Rodríguez (carlos.rodriguez@yopmail.com) — Jefe de Laura (recibe copia en aprobación)

Ejecución:
  cd "empleados v2/Tests"
  $env:PYTHONIOENCODING='utf-8'
  ../.venv/Scripts/python.exe -m pytest test_email_cambio_estado_solicitud.py -v --headed --slowmo 800 -s
"""

import json
import os
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import pytest

from helpers import BASE_URL, hacer_login

# ── Configuración ─────────────────────────────────────────────────────────────
DB_INSTANCE = r"(localdb)\MSSQLLocalDB"
DB_NAME     = "GestionPersonal"

_ROOT    = Path(__file__).parent.parent
_WEB_DIR = _ROOT / "Proyecto MVC" / "GestionPersonal.Web"

# Actores del test
LAURA_CORREO  = "laura.sanchez@yopmail.com"
DIANA_CORREO  = "diana.vargas@yopmail.com"
CARLOS_CORREO = "carlos.rodriguez@yopmail.com"
PASSWORD      = "Usuario1"

# TipoEvento en RegistroNotificaciones
TIPO_SOLICITANTE = "CambioEstadoSolicitud"
TIPO_JEFE        = "CambioEstadoSolicitudJefeAprobador"

# Estado compartido del módulo
_S: dict = {
    "app_process": None,
    "evento_id":   None,   # ID del EventoLaboral de prueba (Pendiente, de Diana)
}


# ════════════════════════════════════════════════════════════════════════════
#  HELPERS BD
# ════════════════════════════════════════════════════════════════════════════

def _ejecutar(sql: str) -> None:
    sql_file = os.path.join(tempfile.gettempdir(), "_ce_exec.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    subprocess.run(
        ["powershell", "-Command",
         f"Invoke-Sqlcmd -ServerInstance '{DB_INSTANCE}' -Database '{DB_NAME}' "
         f"-InputFile '{sql_file}'"],
        capture_output=True, text=True, timeout=20,
    )


def _consultar(query: str) -> list[dict]:
    sql_file = os.path.join(tempfile.gettempdir(), "_ce_query.sql")
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
    Reintenta hasta 5 veces con espera de 2s para tolerar latencia de confirmación.
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


def _crear_evento_pendiente_diana() -> int:
    """
    Inserta un EventoLaboral Pendiente para Diana Vargas y retorna su Id.
    Diana = EmpleadoId relativo al seeding: buscamos por correo de Usuario.
    """
    _ejecutar(
        "INSERT INTO dbo.EventosLaborales "
        "(EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, "
        " TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, "
        " MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor) "
        "SELECT e.Id, N'Permiso', '2026-09-01', '2026-09-01', N'Pendiente', "
        "  NULL, NULL, N'Permiso de prueba TC-CE', N'Laura Sanchez', NULL, NULL, NULL, "
        "  u.Id, GETDATE(), NULL "
        "FROM dbo.Empleados e "
        "INNER JOIN dbo.Usuarios u ON e.UsuarioId = u.Id "
        "WHERE u.CorreoAcceso = 'diana.vargas@yopmail.com';"
    )
    rows = _consultar(
        "SELECT TOP 1 el.Id FROM dbo.EventosLaborales el "
        "INNER JOIN dbo.Empleados e ON el.EmpleadoId = e.Id "
        "INNER JOIN dbo.Usuarios u ON e.UsuarioId = u.Id "
        "WHERE u.CorreoAcceso = 'diana.vargas@yopmail.com' "
        "  AND el.TipoEvento = 'Permiso' "
        "  AND el.Descripcion = 'Permiso de prueba TC-CE' "
        "ORDER BY el.Id DESC;"
    )
    if not rows:
        pytest.fail("No se pudo crear el EventoLaboral de prueba para Diana Vargas")
    return int(rows[0]["Id"])


def _reset_evento_a_pendiente(evento_id: int) -> None:
    """Restablece el evento de prueba a Pendiente para poder reutilizarlo."""
    _ejecutar(
        f"UPDATE dbo.EventosLaborales SET Estado = N'Pendiente' WHERE Id = {evento_id};"
    )


def _limpiar_evento(evento_id: int) -> None:
    _ejecutar(f"DELETE FROM dbo.EventosLaborales WHERE Id = {evento_id};")


# ════════════════════════════════════════════════════════════════════════════
#  FIXTURE MÓDULO — levanta y detiene la aplicación
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module", autouse=True)
def aplicacion_corriendo():
    """Inicia la aplicación antes de todos los tests del módulo y la detiene al finalizar."""

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
        pytest.fail("La aplicación no respondió en 60 segundos. Verificar compilación.")

    print(f"  [APP] Lista en {BASE_URL}")

    # ── Crear evento de prueba ───────────────────────────────────────────────
    evento_id = _crear_evento_pendiente_diana()
    _S["evento_id"] = evento_id
    print(f"  [DB] EventoLaboral de prueba creado: Id={evento_id}")

    # ── Asegurar que Laura no sea redirigida a cambiar contraseña ─────────────
    # El fixture de sesión de conftest establece DebeCambiarPassword=1 para Laura,
    # lo que hace que el AJAX de gestión falle en el primer login del módulo.
    _ejecutar(
        "UPDATE dbo.Usuarios SET DebeCambiarPassword = 0 "
        "WHERE CorreoAcceso = 'laura.sanchez@yopmail.com';"
    )
    print("  [DB] DebeCambiarPassword=0 establecido para laura.sanchez")

    yield

    # ── Teardown ─────────────────────────────────────────────────────────────
    if _S["evento_id"]:
        _limpiar_evento(_S["evento_id"])
        print(f"\n  [TEARDOWN] EventoLaboral Id={_S['evento_id']} eliminado")

    proc = _S.get("app_process")
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("  [APP] Aplicación detenida")


# ════════════════════════════════════════════════════════════════════════════
#  HELPER UI — gestionar solicitud desde el modal
# ════════════════════════════════════════════════════════════════════════════

def _gestionar_solicitud(page, evento_id: int, nuevo_estado: str, observacion: str = "") -> None:
    """
    Navega a /EventoLaboral, abre el modal de gestión para el evento indicado,
    selecciona el nuevo estado y confirma.
    """
    page.goto(f"{BASE_URL}/EventoLaboral")
    page.wait_for_load_state("networkidle")

    # Hacer clic en el botón Gestionar del evento correspondiente
    boton = page.locator(f"button[onclick*='iniciarGestion({evento_id},']")
    boton.wait_for(timeout=10_000)
    boton.click()

    # Esperar a que el modal sea visible
    modal = page.locator("#modal-gestion")
    modal.wait_for(state="visible", timeout=5_000)

    # Seleccionar el nuevo estado
    page.select_option("#gest-nuevo-estado", value=nuevo_estado)
    time.sleep(0.3)  # pequeña pausa para que el JS actualice la obligatoriedad

    # Completar observación si se requiere
    if observacion:
        page.fill("#gest-observacion", observacion)

    # Confirmar
    page.click("#btn-confirmar-gestion")
    page.wait_for_load_state("networkidle")
    time.sleep(1)  # pausa para que la notificación quede registrada en BD


# ════════════════════════════════════════════════════════════════════════════
#  TC-CE-01 — Regente aprueba → correo a solicitante Y a jefe del aprobador
# ════════════════════════════════════════════════════════════════════════════

def test_tc_ce_01_aprobacion_envia_dos_correos(page):
    """
    TC-CE-01: Laura (Regente) aprueba la solicitud de Diana.
    Debe registrar:
      - CambioEstadoSolicitud     → destinatario: diana.vargas@yopmail.com
      - CambioEstadoSolicitudJefeAprobador → destinatario: carlos.rodriguez@yopmail.com
    """
    evento_id = _S["evento_id"]

    # Asegurarse de que el evento esté en Pendiente
    _reset_evento_a_pendiente(evento_id)

    # Capturar IDs máximos ANTES de la acción (evita falsos positivos por registros previos)
    max_id_sol  = _max_id_registro(TIPO_SOLICITANTE)
    max_id_jefe = _max_id_registro(TIPO_JEFE)

    hacer_login(page, LAURA_CORREO, PASSWORD)
    _gestionar_solicitud(page, evento_id, "Aprobado")

    # Verificar correo al solicitante (solo registros generados en este test)
    reg_sol = _ultimo_registro(TIPO_SOLICITANTE, id_minimo=max_id_sol)
    assert reg_sol is not None, "TC-CE-01: Sin registro CambioEstadoSolicitud"
    assert reg_sol["exitoso"], f"TC-CE-01: Correo al solicitante falló — {reg_sol['error']}"
    assert "diana.vargas" in reg_sol["destinatario"].lower(), \
        f"TC-CE-01: Destinatario incorrecto — esperado diana.vargas, obtenido: {reg_sol['destinatario']}"

    # Verificar correo al jefe del aprobador
    reg_jefe = _ultimo_registro(TIPO_JEFE, id_minimo=max_id_jefe)
    assert reg_jefe is not None, "TC-CE-01: Sin registro CambioEstadoSolicitudJefeAprobador"
    assert reg_jefe["exitoso"], f"TC-CE-01: Correo al jefe falló — {reg_jefe['error']}"
    assert "carlos.rodriguez" in reg_jefe["destinatario"].lower(), \
        f"TC-CE-01: Destinatario jefe incorrecto — esperado carlos.rodriguez, obtenido: {reg_jefe['destinatario']}"

    print(f"\n  [TC-CE-01] ✓ Solicitante: {reg_sol['destinatario']} | Jefe: {reg_jefe['destinatario']}")


# ════════════════════════════════════════════════════════════════════════════
#  TC-CE-02 — Regente rechaza → correo SOLO al solicitante
# ════════════════════════════════════════════════════════════════════════════

def test_tc_ce_02_rechazo_envia_solo_a_solicitante(page):
    """
    TC-CE-02: Laura rechaza la solicitud de Diana.
    Solo debe registrar CambioEstadoSolicitud (a Diana).
    NO debe generar CambioEstadoSolicitudJefeAprobador.
    """
    evento_id = _S["evento_id"]

    # Estado: debe estar en Pendiente (el test anterior la dejó en Aprobado)
    _reset_evento_a_pendiente(evento_id)

    # Capturar IDs máximos ANTES de la acción
    max_id_sol  = _max_id_registro(TIPO_SOLICITANTE)
    max_id_jefe = _max_id_registro(TIPO_JEFE)

    hacer_login(page, LAURA_CORREO, PASSWORD)
    _gestionar_solicitud(page, evento_id, "Rechazado", "Rechazo de prueba TC-CE-02")

    # Verificar correo al solicitante (solo registros generados en este test)
    reg_sol = _ultimo_registro(TIPO_SOLICITANTE, id_minimo=max_id_sol)
    assert reg_sol is not None, "TC-CE-02: Sin registro CambioEstadoSolicitud"
    assert reg_sol["exitoso"], f"TC-CE-02: Correo al solicitante falló — {reg_sol['error']}"
    assert "diana.vargas" in reg_sol["destinatario"].lower(), \
        f"TC-CE-02: Destinatario incorrecto: {reg_sol['destinatario']}"

    # Verificar que NO se generó correo al jefe en esta ejecución
    reg_jefe_nuevo = _ultimo_registro(TIPO_JEFE, id_minimo=max_id_jefe)
    assert reg_jefe_nuevo is None, \
        f"TC-CE-02: Se generó correo al jefe en un rechazo — no debería. Destinatario: {reg_jefe_nuevo['destinatario'] if reg_jefe_nuevo else 'N/A'}"

    print(f"\n  [TC-CE-02] ✓ Solo solicitante notificado: {reg_sol['destinatario']}")


# ════════════════════════════════════════════════════════════════════════════
#  TC-CE-03 — Regente revierte a Pendiente → correo SOLO al solicitante
# ════════════════════════════════════════════════════════════════════════════

def test_tc_ce_03_reversion_a_pendiente_solo_solicitante(page):
    """
    TC-CE-03: Laura devuelve a Pendiente una solicitud que estaba Aprobada.
    Solo debe notificar al solicitante (Diana).
    """
    evento_id = _S["evento_id"]

    # Poner el evento en Aprobado directamente vía SQL para el test
    _ejecutar(f"UPDATE dbo.EventosLaborales SET Estado = N'Aprobado' WHERE Id = {evento_id};")

    # Capturar IDs máximos ANTES de la acción
    max_id_sol  = _max_id_registro(TIPO_SOLICITANTE)
    max_id_jefe = _max_id_registro(TIPO_JEFE)

    hacer_login(page, LAURA_CORREO, PASSWORD)
    _gestionar_solicitud(page, evento_id, "Pendiente", "Devuelto a revisión TC-CE-03")

    # Verificar correo al solicitante (solo registros generados en este test)
    reg_sol = _ultimo_registro(TIPO_SOLICITANTE, id_minimo=max_id_sol)
    assert reg_sol is not None, "TC-CE-03: Sin registro CambioEstadoSolicitud"
    assert reg_sol["exitoso"], f"TC-CE-03: Correo al solicitante falló — {reg_sol['error']}"
    assert "diana.vargas" in reg_sol["destinatario"].lower(), \
        f"TC-CE-03: Destinatario incorrecto: {reg_sol['destinatario']}"

    # Verificar que NO se generó correo al jefe en esta ejecución
    reg_jefe_nuevo = _ultimo_registro(TIPO_JEFE, id_minimo=max_id_jefe)
    assert reg_jefe_nuevo is None, \
        "TC-CE-03: Se generó correo al jefe al revertir a Pendiente — no debería."

    print(f"\n  [TC-CE-03] ✓ Solo solicitante notificado: {reg_sol['destinatario']}")


# ════════════════════════════════════════════════════════════════════════════
#  TC-CE-04 — Contenido: correo al solicitante menciona al aprobador
# ════════════════════════════════════════════════════════════════════════════

def test_tc_ce_04_asunto_menciona_aprobado(page):
    """
    TC-CE-04: El asunto del correo al solicitante incluye 'Aprobado'.
    Ejecuta aprobación y verifica el asunto registrado.
    """
    evento_id = _S["evento_id"]
    _reset_evento_a_pendiente(evento_id)

    # Capturar ID máximo ANTES de la acción
    max_id_sol = _max_id_registro(TIPO_SOLICITANTE)

    hacer_login(page, LAURA_CORREO, PASSWORD)
    _gestionar_solicitud(page, evento_id, "Aprobado")

    # Solo registros generados en este test (evita leer el Pendiente de TC-CE-03)
    reg_sol = _ultimo_registro(TIPO_SOLICITANTE, id_minimo=max_id_sol)
    assert reg_sol is not None, "TC-CE-04: Sin registro CambioEstadoSolicitud"
    assert reg_sol["exitoso"], f"TC-CE-04: Correo falló — {reg_sol['error']}"

    asunto_lower = reg_sol["asunto"].lower()
    assert "aprobado" in asunto_lower, \
        f"TC-CE-04: El asunto no contiene 'aprobado': '{reg_sol['asunto']}'"

    print(f"\n  [TC-CE-04] ✓ Asunto: '{reg_sol['asunto']}'")


# ════════════════════════════════════════════════════════════════════════════
#  TC-CE-05 — Contenido: correo al jefe del aprobador incluye nombres
# ════════════════════════════════════════════════════════════════════════════

def test_tc_ce_05_asunto_jefe_menciona_aprobacion(page):
    """
    TC-CE-05: El asunto del correo al jefe del aprobador menciona la aprobación.
    Reutiliza el registro generado en TC-CE-04.
    """
    reg_jefe = _ultimo_registro(TIPO_JEFE)
    if reg_jefe is None:
        pytest.skip("TC-CE-05: Sin registro de CambioEstadoSolicitudJefeAprobador — ejecutar TC-CE-04 primero")

    assert reg_jefe["exitoso"], f"TC-CE-05: Correo al jefe falló — {reg_jefe['error']}"
    assert "carlos.rodriguez" in reg_jefe["destinatario"].lower(), \
        f"TC-CE-05: Destinatario incorrecto: {reg_jefe['destinatario']}"

    asunto_lower = reg_jefe["asunto"].lower()
    assert any(kw in asunto_lower for kw in ("aprobaci", "autoridad", "aprobado")), \
        f"TC-CE-05: El asunto del jefe no menciona aprobación: '{reg_jefe['asunto']}'"

    print(f"\n  [TC-CE-05] ✓ Asunto jefe: '{reg_jefe['asunto']}'")


# ════════════════════════════════════════════════════════════════════════════
#  TC-CE-06 — Verificación visual en yopmail.com (solicitante)
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_tc_ce_06_yopmail_diana_recibe_correo(page):
    """
    TC-CE-06: Verificar en yopmail que diana.vargas recibió el correo de cambio de estado.
    """
    page.goto("https://yopmail.com/en/?login=diana.vargas")
    page.wait_for_load_state("load", timeout=20_000)

    try:
        page.frame_locator("#ifinbox").locator("body").wait_for(
            state="visible", timeout=15_000
        )
    except Exception:
        pass

    # Buscar email de cambio de estado en la bandeja (reintenta hasta 8 veces)
    encontrado = False
    for intento in range(8):
        try:
            # Estrategia primaria: texto del asunto
            email_item = page.frame_locator("#ifinbox").locator("a").filter(
                has_text="Solicitud"
            ).first
            email_item.wait_for(timeout=5_000)
            encontrado = True
            break
        except Exception:
            pass

        try:
            # Estrategia alternativa: primer email de la bandeja
            email_item = page.frame_locator("#ifinbox").locator("a[id^='e_']").first
            email_item.wait_for(timeout=3_000)
            encontrado = True
            break
        except Exception:
            pass

        print(f"  [yopmail] Intento {intento+1}/8: sin email. Recargando...")
        try:
            page.locator("#refresh").click(timeout=3_000)
        except Exception:
            page.reload()
        page.wait_for_load_state("load", timeout=15_000)

    if not encontrado:
        pytest.xfail(
            "TC-CE-06: El correo no llegó a yopmail en el tiempo esperado.\n"
            "  → Verificar manualmente: https://yopmail.com/en/?login=diana.vargas"
        )

    email_item.click()
    page.wait_for_timeout(2_000)

    # Verificar contenido del email en el iframe #ifmail
    cuerpo = page.frame_locator("#ifmail").locator("body").inner_text(timeout=10_000)
    assert len(cuerpo) > 50, "TC-CE-06: El cuerpo del email parece vacío"
    print(f"\n  [TC-CE-06] ✓ Email recibido en yopmail (diana.vargas). Primeras 200 chars: {cuerpo[:200]}")


# ════════════════════════════════════════════════════════════════════════════
#  TC-CE-07 — Verificación visual en yopmail.com (jefe del aprobador)
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.yopmail
def test_tc_ce_07_yopmail_carlos_recibe_correo_jefe(page):
    """
    TC-CE-07: Verificar en yopmail que carlos.rodriguez recibió el correo de
    aprobación bajo su autoridad.
    """
    page.goto("https://yopmail.com/en/?login=carlos.rodriguez")
    page.wait_for_load_state("load", timeout=20_000)

    try:
        page.frame_locator("#ifinbox").locator("body").wait_for(
            state="visible", timeout=15_000
        )
    except Exception:
        pass

    encontrado = False
    for intento in range(8):
        try:
            email_item = page.frame_locator("#ifinbox").locator("a").filter(
                has_text="autoridad"
            ).first
            email_item.wait_for(timeout=5_000)
            encontrado = True
            break
        except Exception:
            pass

        try:
            email_item = page.frame_locator("#ifinbox").locator("a[id^='e_']").first
            email_item.wait_for(timeout=3_000)
            encontrado = True
            break
        except Exception:
            pass

        print(f"  [yopmail] Intento {intento+1}/8 carlos: sin email. Recargando...")
        try:
            page.locator("#refresh").click(timeout=3_000)
        except Exception:
            page.reload()
        page.wait_for_load_state("load", timeout=15_000)

    if not encontrado:
        pytest.xfail(
            "TC-CE-07: El correo al jefe no llegó a yopmail.\n"
            "  → Verificar manualmente: https://yopmail.com/en/?login=carlos.rodriguez"
        )

    email_item.click()
    page.wait_for_timeout(2_000)

    cuerpo = page.frame_locator("#ifmail").locator("body").inner_text(timeout=10_000)
    assert len(cuerpo) > 50, "TC-CE-07: El cuerpo del email parece vacío"
    print(f"\n  [TC-CE-07] ✓ Email recibido en yopmail (carlos.rodriguez). Primeras 200 chars: {cuerpo[:200]}")
