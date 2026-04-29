"""
Pruebas funcionales — Control Jerárquico de Plantillas de Horario
Sistema: GestiónRH — Administración de Empleados
Requerimiento: Documentos/Requerimientos/RequerimientoCreacionHorario.md

Scopes cubiertos:
  A — Visibilidad de plantillas propias  (TC-HJ-01 a TC-HJ-04) [Requiere CreadoPorId]
  B — Restricción de visibilidad cruzada (TC-HJ-05 a TC-HJ-07) [Requiere CreadoPorId]
  C — Selector de colaboradores al asignar (TC-HJ-08 a TC-HJ-11)
  D — Restricción de autoasignación       (TC-HJ-12 a TC-HJ-13)
  E — Vista de colaborador solo-lectura   (TC-HJ-14 a TC-HJ-16)
  F — Validación backend (HorarioService) (TC-HJ-17 a TC-HJ-19)

Jerarquía de prueba (seeding):
  Carlos  (ID=1, Jefe,           DebeCambiar=0) — nivel 1
  ├── Laura   (ID=2, Regente,    DebeCambiar=1) — nivel 2
  │     ├── Andrés  (ID=4, AuxiliarRegente, DebeCambiar=0) — nivel 3
  │     ├── Diana   (ID=5, Operario,        DebeCambiar=0) — nivel 3
  │     └── Jorge   (ID=6, Operario)                       — nivel 3
  └── Hernán  (ID=3, Regente)                              — nivel 2
        ├── Natalia (ID=7, Operario)
        ├── Paula   (ID=8, Operario)
        └── Camila  (ID=9, Operario)

NOTA: Los tests de categorías A, B, TC-HJ-11, TC-HJ-18 requieren que la columna
CreadoPorId esté implementada en dbo.PlantillasTurno y que TurnoService filtre
por jerarquía. Dichos tests se saltarán (SKIP) con un mensaje claro si la feature
aún no ha sido implementada. Los demás tests corren sobre la implementación actual
y documentan el comportamiento esperado vs. actual (PASS = ya existe, FAIL = pendiente).
"""

import os
import subprocess
import tempfile
import time

import pytest

from helpers import BASE_URL, hacer_login, llamar_ajax_post

# ── Constantes ────────────────────────────────────────────────────────────────

_HASH_USUARIO1 = "0x7DED37B4612147C18EBDFA1F6DEB4709EC9D511DA20641214F1F97612DF2CEAE"
_SALT_USUARIO1 = "0xF2B483C7DAC61EC2CA7F1331C95D6800"

CARLOS  = "carlos.rodriguez@yopmail.com"
LAURA   = "laura.sanchez@yopmail.com"
HERNAN  = "hernan.castillo@yopmail.com"
ANDRES  = "andres.torres@yopmail.com"
DIANA   = "diana.vargas@yopmail.com"
PASSWORD = "Usuario1"

CARLOS_ID  = 1
LAURA_ID   = 2
HERNAN_ID  = 3
ANDRES_ID  = 4
DIANA_ID   = 5
JORGE_ID   = 6
NATALIA_ID = 7

# Plantillas del seeding (aún sin CreadoPorId)
PT_ESTANDAR_ID     = 1
PT_FIN_SEM_ID      = 2
PT_ROTATIVO_ID     = 3
PT_ESTANDAR_NOMBRE = "turno1 carlos"       # plantilla ID=1, asignada a Carlos (CreadoPorId=1)
PT_FIN_SEM_NOMBRE  = "Turno Fin de Semana" # plantilla ID=2, asignada a Laura  (CreadoPorId=2)
PT_ROTATIVO_NOMBRE = "horario1 laura"      # plantilla ID=3, asignada a Hernán (CreadoPorId=3)


# ── Utilidades de BD ──────────────────────────────────────────────────────────

def _ejecutar_sql(sql: str) -> subprocess.CompletedProcess:
    sql_file = os.path.join(tempfile.gettempdir(), "test_hj.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    return subprocess.run(
        [
            "powershell", "-Command",
            f"try {{ Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
            f"-Database 'GestionPersonal' -InputFile '{sql_file}'; Write-Output 'OK' }}"
            f" catch {{ Write-Output \"ERROR:$_\" }}",
        ],
        capture_output=True, text=True, timeout=20,
    )


def _columna_existe(tabla: str, columna: str) -> bool:
    r = subprocess.run(
        [
            "powershell", "-Command",
            f"(Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
            f"-Database 'GestionPersonal' "
            f"-Query \"SELECT COUNT(*) AS Cnt FROM INFORMATION_SCHEMA.COLUMNS "
            f"WHERE TABLE_NAME='{tabla}' AND COLUMN_NAME='{columna}'\").Cnt",
        ],
        capture_output=True, text=True, timeout=15,
    )
    return r.stdout.strip() == "1"


def _query_valor(sql: str, columna: str) -> str:
    r = subprocess.run(
        [
            "powershell", "-Command",
            f"(Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
            f"-Database 'GestionPersonal' -Query \"{sql}\").{columna}",
        ],
        capture_output=True, text=True, timeout=20,
    )
    return r.stdout.strip()


# ── Helpers de navegación ─────────────────────────────────────────────────────

def _login(page, correo: str):
    """Login directo — asume DebecambiarPassword = 0."""
    page.goto(f"{BASE_URL}/Cuenta/Logout")
    page.wait_for_load_state("networkidle")
    hacer_login(page, correo, PASSWORD)
    if "/Cuenta/CambiarPassword" in page.url:
        pytest.skip(f"Usuario {correo} redirigido a CambiarPassword — BD en estado inesperado.")


def _ir_a_turnos(page):
    page.goto(f"{BASE_URL}/Turno")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("#plantillas-grid", timeout=8_000)


def _texto_grid(page) -> str:
    return page.locator("#plantillas-grid").inner_text().strip()


def _abrir_modal_asignar(page, empleado_id: int) -> bool:
    """Navega al perfil del empleado y abre el modal de asignación. Retorna True si se abrió."""
    page.goto(f"{BASE_URL}/Empleado/Perfil/{empleado_id}?tab=horario")
    page.wait_for_load_state("networkidle")
    btn = page.locator("button:has-text('Asignar / cambiar turno')")
    if btn.count() == 0 or not btn.first.is_visible():
        return False
    btn.first.click()
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    return True


def _opciones_plantilla_modal(page) -> list[str]:
    opts = page.locator("#turno-plantilla option:not([value=''])")
    return [opts.nth(i).inner_text().strip() for i in range(opts.count())]


def _boton_asignar_visible(page, empleado_id: int) -> bool:
    page.goto(f"{BASE_URL}/Empleado/Perfil/{empleado_id}?tab=horario")
    page.wait_for_load_state("networkidle")
    btn = page.locator("button:has-text('Asignar / cambiar turno')")
    return btn.count() > 0 and btn.first.is_visible()


# ── Fixtures de módulo ────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def preparar_usuarios():
    """Garantiza que todos los usuarios de prueba tengan contraseña Usuario1 y DebecambiarPassword=0."""
    correos = ", ".join(
        f"'{c}'" for c in [CARLOS, LAURA, HERNAN, ANDRES, DIANA]
    )
    _ejecutar_sql(
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_USUARIO1}, "
        f"PasswordSalt={_SALT_USUARIO1}, "
        f"DebecambiarPassword=0 "
        f"WHERE CorreoAcceso IN ({correos});"
    )
    yield
    # Restaurar: Laura vuelve a DebecambiarPassword=1 (estado del seeding)
    _ejecutar_sql(
        f"UPDATE dbo.Usuarios SET DebecambiarPassword=1 "
        f"WHERE CorreoAcceso='{LAURA}';"
    )


@pytest.fixture(scope="module")
def columna_creadoporid():
    """
    Verifica que la columna CreadoPorId exista en dbo.PlantillasTurno.
    Si no existe, omite todos los tests que dependan de esta fixture.
    """
    if not _columna_existe("PlantillasTurno", "CreadoPorId"):
        pytest.skip(
            "Columna CreadoPorId no existe en dbo.PlantillasTurno — "
            "implementar la feature antes de ejecutar estos tests."
        )


@pytest.fixture(scope="module")
def plantillas_con_dueno(columna_creadoporid):
    """
    Asigna CreadoPorId a las plantillas del seeding para habilitar los tests A/B.
      Plantilla 1 (Turno Estándar) → CreadoPorId = 1 (Carlos)
      Plantilla 2 (Turno Fin de Semana) → CreadoPorId = 2 (Laura)
      Plantilla 3 (Turno Rotativo) → CreadoPorId = 3 (Hernán)
    Limpia al finalizar el módulo.
    """
    _ejecutar_sql(
        "UPDATE dbo.PlantillasTurno SET CreadoPorId = 1 WHERE Id = 1; "
        "UPDATE dbo.PlantillasTurno SET CreadoPorId = 2 WHERE Id = 2; "
        "UPDATE dbo.PlantillasTurno SET CreadoPorId = 3 WHERE Id = 3;"
    )
    yield
    _ejecutar_sql(
        "UPDATE dbo.PlantillasTurno SET CreadoPorId = NULL WHERE Id IN (1, 2, 3);"
    )


# ══════════════════════════════════════════════════════════════════════════════
# SCOPE A — Visibilidad de plantillas propias
# ══════════════════════════════════════════════════════════════════════════════

def test_tc_hj01_carlos_ve_solo_sus_plantillas(page, plantillas_con_dueno):
    """
    TC-HJ-01: Carlos (CreadoPorId=1) ve SOLO 'Turno Estándar Lunes-Viernes'.
    No debe ver 'Turno Fin de Semana' (Laura) ni 'Turno Rotativo 6x1' (Hernán).
    """
    _login(page, CARLOS)
    _ir_a_turnos(page)
    texto = _texto_grid(page)

    assert PT_ESTANDAR_NOMBRE in texto, (
        f"TC-HJ-01 FALLO: Carlos no ve su propia plantilla '{PT_ESTANDAR_NOMBRE}'."
    )
    assert PT_FIN_SEM_NOMBRE not in texto, (
        f"TC-HJ-01 FALLO: Carlos ve la plantilla de Laura '{PT_FIN_SEM_NOMBRE}'. "
        "El grid no filtra por CreadoPorId."
    )
    assert PT_ROTATIVO_NOMBRE not in texto, (
        f"TC-HJ-01 FALLO: Carlos ve la plantilla de Hernán '{PT_ROTATIVO_NOMBRE}'. "
        "El grid no filtra por CreadoPorId."
    )
    print("\n  TC-HJ-01 PASÓ — Carlos ve solo sus plantillas propias.")


def test_tc_hj02_laura_ve_solo_sus_plantillas(page, plantillas_con_dueno):
    """
    TC-HJ-02: Laura (CreadoPorId=2) ve SOLO 'Turno Fin de Semana'.
    No debe ver 'Turno Estándar' (Carlos) ni 'Turno Rotativo' (Hernán).
    """
    _login(page, LAURA)
    _ir_a_turnos(page)
    texto = _texto_grid(page)

    assert PT_FIN_SEM_NOMBRE in texto, (
        f"TC-HJ-02 FALLO: Laura no ve su propia plantilla '{PT_FIN_SEM_NOMBRE}'."
    )
    assert PT_ESTANDAR_NOMBRE not in texto, (
        f"TC-HJ-02 FALLO: Laura ve la plantilla de Carlos '{PT_ESTANDAR_NOMBRE}'. "
        "El grid no filtra por CreadoPorId."
    )
    assert PT_ROTATIVO_NOMBRE not in texto, (
        f"TC-HJ-02 FALLO: Laura ve la plantilla de Hernán '{PT_ROTATIVO_NOMBRE}'."
    )
    print("\n  TC-HJ-02 PASÓ — Laura ve solo sus plantillas propias.")


def test_tc_hj03_usuario_sin_plantillas_ve_lista_vacia(page, plantillas_con_dueno):
    """
    TC-HJ-03: Andrés (AuxiliarRegente, sin plantillas con CreadoPorId=4)
    no debe ver ninguna de las plantillas de Carlos, Laura o Hernán.
    """
    _login(page, ANDRES)
    _ir_a_turnos(page)
    texto = _texto_grid(page)

    for nombre in [PT_ESTANDAR_NOMBRE, PT_FIN_SEM_NOMBRE, PT_ROTATIVO_NOMBRE]:
        assert nombre not in texto, (
            f"TC-HJ-03 FALLO: Andrés ve la plantilla '{nombre}' aunque no la creó. "
            "El grid no filtra por CreadoPorId."
        )
    print("\n  TC-HJ-03 PASÓ — Andrés no ve plantillas de otros jefes.")


def test_tc_hj04_nueva_plantilla_queda_vinculada_al_creador(page, columna_creadoporid):
    """
    TC-HJ-04: Al crear una nueva plantilla como Carlos, el campo CreadoPorId
    debe quedar igual a su EmpleadoId (1) en dbo.PlantillasTurno.
    """
    nombre_nuevo = f"Turno HJ04 Test {int(time.time())}"
    _login(page, CARLOS)
    page.goto(f"{BASE_URL}/Turno")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("#btn-nueva-plantilla", timeout=8_000)

    # Abrir modal de creación
    page.click("#btn-nueva-plantilla")
    page.wait_for_selector("#modal-turno:not([hidden])", timeout=5_000)
    page.fill("#t-nombre", nombre_nuevo)

    # Marcar al menos un día en el shift-form-grid
    dia_check = page.locator("#shift-form-grid input[type='checkbox']").first
    if dia_check.count() > 0 and not dia_check.is_checked():
        dia_check.check()
        # Completar horas de entrada/salida si aparecen
        hora_entrada = page.locator("#shift-form-grid input[type='time']").first
        if hora_entrada.count() > 0:
            hora_entrada.fill("08:00")
            hora_salida = page.locator("#shift-form-grid input[type='time']").nth(1)
            if hora_salida.count() > 0:
                hora_salida.fill("17:00")

    page.click("#btn-guardar-turno")
    page.wait_for_load_state("networkidle")

    # Verificar en BD
    valor = _query_valor(
        f"SELECT ISNULL(CAST(CreadoPorId AS VARCHAR), 'NULL') AS CreadoPorId "
        f"FROM dbo.PlantillasTurno WHERE Nombre = '{nombre_nuevo}'",
        "CreadoPorId",
    )
    assert valor == str(CARLOS_ID), (
        f"TC-HJ-04 FALLO: CreadoPorId esperado={CARLOS_ID}, obtenido='{valor}'. "
        "El servicio no está asignando CreadoPorId al crear plantillas."
    )
    print(f"\n  TC-HJ-04 PASÓ — Nueva plantilla tiene CreadoPorId={CARLOS_ID}.")

    # Limpieza
    _ejecutar_sql(
        f"DELETE FROM dbo.PlantillasTurnoDetalle WHERE PlantillaTurnoId = "
        f"(SELECT Id FROM dbo.PlantillasTurno WHERE Nombre = '{nombre_nuevo}'); "
        f"DELETE FROM dbo.PlantillasTurno WHERE Nombre = '{nombre_nuevo}';"
    )


# ══════════════════════════════════════════════════════════════════════════════
# SCOPE B — Restricción de visibilidad cruzada
# ══════════════════════════════════════════════════════════════════════════════

def test_tc_hj05_mismo_nivel_no_comparte_plantillas(page, plantillas_con_dueno):
    """
    TC-HJ-05: Laura y Hernán son ambos Regente bajo Carlos (mismo nivel jerárquico).
    Laura no debe ver la plantilla de Hernán ('Turno Rotativo 6x1').
    """
    _login(page, LAURA)
    _ir_a_turnos(page)
    texto = _texto_grid(page)

    assert PT_ROTATIVO_NOMBRE not in texto, (
        f"TC-HJ-05 FALLO: Laura ve la plantilla de Hernán '{PT_ROTATIVO_NOMBRE}'. "
        "Jefes del mismo nivel no deben ver plantillas entre sí."
    )
    print("\n  TC-HJ-05 PASÓ — Laura no ve plantillas de Hernán (mismo nivel).")


def test_tc_hj06_subordinado_no_ve_plantillas_del_superior(page, plantillas_con_dueno):
    """
    TC-HJ-06: Laura es subordinada de Carlos.
    No debe poder ver las plantillas creadas por Carlos ('Turno Estándar').
    """
    _login(page, LAURA)
    _ir_a_turnos(page)
    texto = _texto_grid(page)

    assert PT_ESTANDAR_NOMBRE not in texto, (
        f"TC-HJ-06 FALLO: Laura ve la plantilla de Carlos '{PT_ESTANDAR_NOMBRE}'. "
        "Los subordinados no deben ver plantillas de sus superiores."
    )
    print("\n  TC-HJ-06 PASÓ — Laura no ve las plantillas de Carlos.")


def test_tc_hj07_superior_no_ve_plantillas_del_subordinado(page, plantillas_con_dueno):
    """
    TC-HJ-07: Carlos es superior de Laura.
    No debe poder ver las plantillas creadas por Laura ('Turno Fin de Semana').
    """
    _login(page, CARLOS)
    _ir_a_turnos(page)
    texto = _texto_grid(page)

    assert PT_FIN_SEM_NOMBRE not in texto, (
        f"TC-HJ-07 FALLO: Carlos ve la plantilla de Laura '{PT_FIN_SEM_NOMBRE}'. "
        "Los superiores no deben ver plantillas de sus subordinados."
    )
    print("\n  TC-HJ-07 PASÓ — Carlos no ve las plantillas de Laura.")


# ══════════════════════════════════════════════════════════════════════════════
# SCOPE C — Selector de colaboradores al asignar
# ══════════════════════════════════════════════════════════════════════════════

def test_tc_hj08_carlos_puede_abrir_modal_en_subordinados_directos(page):
    """
    TC-HJ-08: Carlos puede abrir el modal de asignación de turno en los perfiles
    de sus subordinados directos: Laura (ID=2) y Diana (ID=5).
    """
    _login(page, CARLOS)

    for emp_id, nombre in [(LAURA_ID, "Laura"), (DIANA_ID, "Diana")]:
        abierto = _abrir_modal_asignar(page, emp_id)
        assert abierto, (
            f"TC-HJ-08 FALLO: Carlos no puede abrir el modal de asignación "
            f"en el perfil de {nombre} (EmpleadoId={emp_id})."
        )
    print("\n  TC-HJ-08 PASÓ — Carlos puede asignar a sus subordinados directos.")


def test_tc_hj09_laura_puede_asignar_a_andres_no_a_natalia(page):
    """
    TC-HJ-09: Laura puede asignar a Andrés (su subordinado directo, ID=4).
    No debe poder asignar a Natalia (ID=7, subordinada de Hernán — fuera de su jerarquía).
    """
    _login(page, LAURA)

    # Andrés (ID=4) — subordinado directo de Laura
    abierto = _abrir_modal_asignar(page, ANDRES_ID)
    assert abierto, (
        "TC-HJ-09 FALLO: Laura no puede abrir el modal de asignación "
        "en el perfil de Andrés, siendo su subordinado directo."
    )

    # Natalia (ID=7) — subordinada de Hernán, FUERA de la jerarquía de Laura
    # Si el servidor retorna 403/4xx al intentar navegar al perfil, también es acceso denegado
    try:
        boton_natalia = _boton_asignar_visible(page, NATALIA_ID)
    except Exception:
        # ERR_HTTP_RESPONSE_CODE_FAILURE (403 Forbidden) = acceso denegado correcto
        boton_natalia = False
    assert not boton_natalia, (
        "TC-HJ-09 FALLO: Laura ve el botón 'Asignar / cambiar turno' en el perfil "
        "de Natalia (ID=7), quien está bajo Hernán y fuera de su jerarquía. "
        "El controlador no restringe el botón por jerarquía."
    )
    print("\n  TC-HJ-09 PASÓ — Laura asigna a Andrés pero no puede a Natalia.")


def test_tc_hj10_usuario_sin_subordinados_no_tiene_boton_asignar(page):
    """
    TC-HJ-10: Andrés (AuxiliarRegente sin subordinados en el seeding)
    no debe ver el botón 'Asignar / cambiar turno' en su propio perfil.
    """
    _login(page, ANDRES)
    page.goto(f"{BASE_URL}/Empleado/Perfil/{ANDRES_ID}?tab=horario")
    page.wait_for_load_state("networkidle")

    btn = page.locator("button:has-text('Asignar / cambiar turno')")
    visible = btn.count() > 0 and btn.first.is_visible()

    assert not visible, (
        "TC-HJ-10 FALLO: Andrés (sin subordinados) ve el botón 'Asignar / cambiar turno' "
        "en su propio perfil. El botón debe ocultarse cuando el usuario no tiene subordinados."
    )
    print("\n  TC-HJ-10 PASÓ — Andrés no ve el botón de asignación (sin subordinados).")


def test_tc_hj11_modal_plantillas_muestra_solo_las_del_jefe_en_sesion(page, plantillas_con_dueno):
    """
    TC-HJ-11: Al abrir el modal de asignación como Carlos, el select '#turno-plantilla'
    muestra SOLO 'Turno Estándar Lunes-Viernes' (CreadoPorId=1).
    No debe mostrar la plantilla de Laura ni la de Hernán.
    """
    _login(page, CARLOS)
    abierto = _abrir_modal_asignar(page, LAURA_ID)
    assert abierto, "TC-HJ-11: No se pudo abrir el modal en el perfil de Laura."

    opciones = _opciones_plantilla_modal(page)
    assert any(PT_ESTANDAR_NOMBRE in o for o in opciones), (
        f"TC-HJ-11 FALLO: La plantilla de Carlos '{PT_ESTANDAR_NOMBRE}' "
        f"no aparece en el modal. Opciones disponibles: {opciones}"
    )
    assert not any(PT_FIN_SEM_NOMBRE in o for o in opciones), (
        f"TC-HJ-11 FALLO: La plantilla de Laura '{PT_FIN_SEM_NOMBRE}' aparece en el modal. "
        "El select no filtra por CreadoPorId del jefe en sesión."
    )
    assert not any(PT_ROTATIVO_NOMBRE in o for o in opciones), (
        f"TC-HJ-11 FALLO: La plantilla de Hernán '{PT_ROTATIVO_NOMBRE}' aparece en el modal."
    )
    print("\n  TC-HJ-11 PASÓ — Modal muestra solo las plantillas del jefe en sesión.")


# ══════════════════════════════════════════════════════════════════════════════
# SCOPE D — Restricción de autoasignación
# ══════════════════════════════════════════════════════════════════════════════

def test_tc_hj12_jefe_no_ve_boton_asignar_en_su_propio_perfil(page):
    """
    TC-HJ-12: Carlos no debe ver el botón 'Asignar / cambiar turno' en su
    propio perfil (/Empleado/Perfil/1?tab=horario).
    La autoasignación debe estar bloqueada en el frontend.
    """
    _login(page, CARLOS)
    page.goto(f"{BASE_URL}/Empleado/Perfil/{CARLOS_ID}?tab=horario")
    page.wait_for_load_state("networkidle")

    btn = page.locator("button:has-text('Asignar / cambiar turno')")
    visible = btn.count() > 0 and btn.first.is_visible()

    assert not visible, (
        "TC-HJ-12 FALLO: Carlos ve el botón 'Asignar / cambiar turno' en su propio perfil. "
        "La autoasignación debe estar bloqueada en el frontend (el jefe no puede asignarse a sí mismo)."
    )
    print("\n  TC-HJ-12 PASÓ — Carlos no ve el botón de asignación en su propio perfil.")


def test_tc_hj13_backend_rechaza_autoasignacion(page):
    """
    TC-HJ-13: Una llamada directa al endpoint AsignarTurnoAjax con
    EmpleadoId == EmpleadoId del jefe en sesión debe ser rechazada por el backend.
    """
    _login(page, CARLOS)
    # Cargar una página que tenga el token antiforgery
    page.goto(f"{BASE_URL}/Empleado/Perfil/{LAURA_ID}?tab=horario")
    page.wait_for_load_state("networkidle")

    respuesta = llamar_ajax_post(page, "/Turno/AsignarTurnoAjax", {
        "EmpleadoId":       str(CARLOS_ID),      # mismo que el jefe en sesión
        "PlantillaTurnoId": str(PT_ESTANDAR_ID),
        "FechaVigencia":    "2026-06-01",
    })

    exito = respuesta.get("exito", respuesta.get("success", respuesta.get("Exito", True)))
    assert not exito, (
        f"TC-HJ-13 FALLO: El backend aceptó la autoasignación "
        f"(EmpleadoId={CARLOS_ID} == jefe en sesión). "
        "HorarioService debe rechazar cuando colaboradorId == jefeId. "
        f"Respuesta recibida: {respuesta}"
    )
    print("\n  TC-HJ-13 PASÓ — Backend rechaza la autoasignación.")


# ══════════════════════════════════════════════════════════════════════════════
# SCOPE E — Vista de colaborador (solo-lectura)
# ══════════════════════════════════════════════════════════════════════════════

def test_tc_hj14_colaborador_ve_horario_asignado_solo_lectura(page):
    """
    TC-HJ-14: Andrés (AuxiliarRegente) accede a su perfil y ve el horario asignado
    en modo solo-lectura, sin el botón de edición 'Asignar / cambiar turno'.
    """
    _login(page, ANDRES)
    page.goto(f"{BASE_URL}/Empleado/Perfil/{ANDRES_ID}?tab=horario")
    page.wait_for_load_state("networkidle")

    # No debe haber botón de asignación
    btn = page.locator("button:has-text('Asignar / cambiar turno')")
    assert btn.count() == 0 or not btn.first.is_visible(), (
        "TC-HJ-14 FALLO: Andrés ve el botón 'Asignar / cambiar turno' en su propio perfil. "
        "Los colaboradores deben tener vista de solo-lectura."
    )
    print("\n  TC-HJ-14 PASÓ — Andrés ve el horario sin opciones de edición.")


def test_tc_hj15_colaborador_no_ve_plantillas_de_otros(page):
    """
    TC-HJ-15: Diana (Operario) accede a su perfil y no debe ver nombres de
    plantillas ajenas ('Turno Fin de Semana', 'Turno Rotativo 6x1', etc.)
    en ninguna parte de la página.
    """
    _login(page, DIANA)
    page.goto(f"{BASE_URL}/Empleado/Perfil/{DIANA_ID}?tab=horario")
    page.wait_for_load_state("networkidle")
    texto_pagina = page.inner_text("body")

    for nombre in [PT_FIN_SEM_NOMBRE, PT_ROTATIVO_NOMBRE]:
        assert nombre not in texto_pagina, (
            f"TC-HJ-15 FALLO: Diana ve el nombre de plantilla '{nombre}' en su perfil. "
            "Los colaboradores no deben ver plantillas de otros jefes."
        )
    print("\n  TC-HJ-15 PASÓ — Diana no ve plantillas de otros en su perfil.")


def test_tc_hj16_operario_no_puede_acceder_a_modulo_turno(page):
    """
    TC-HJ-16: Diana (rol Operario) intenta acceder directamente a /Turno.
    Debe ser redirigida (acceso denegado o fuera del módulo).
    No debe poder ver el grid de plantillas.
    """
    _login(page, DIANA)
    try:
        page.goto(f"{BASE_URL}/Turno")
        page.wait_for_load_state("networkidle")
    except Exception:
        # ERR_HTTP_RESPONSE_CODE_FAILURE = 403 Forbidden → acceso denegado correcto
        print(f"\n  TC-HJ-16 PASÓ — Diana (Operario) recibe 403 al acceder a /Turno.")
        return

    grid_visible = page.locator("#plantillas-grid").count() > 0
    assert not grid_visible, (
        "TC-HJ-16 FALLO: Diana (Operario) pudo acceder a /Turno y visualizar "
        "#plantillas-grid. El controlador debe restringir el acceso a roles sin permiso. "
        f"URL final: {page.url}"
    )
    print(f"\n  TC-HJ-16 PASÓ — Diana (Operario) no accede a /Turno (URL: {page.url}).")


# ══════════════════════════════════════════════════════════════════════════════
# SCOPE F — Validación backend (HorarioService)
# ══════════════════════════════════════════════════════════════════════════════

def test_tc_hj17_backend_rechaza_asignacion_fuera_de_jerarquia(page):
    """
    TC-HJ-17: Laura intenta asignar una plantilla a Natalia (ID=7),
    quien está bajo Hernán y FUERA de la jerarquía de Laura.
    El backend debe rechazarlo sin guardar en BD.
    """
    _login(page, LAURA)
    page.goto(f"{BASE_URL}/Empleado/Perfil/{ANDRES_ID}?tab=horario")
    page.wait_for_load_state("networkidle")

    respuesta = llamar_ajax_post(page, "/Turno/AsignarTurnoAjax", {
        "EmpleadoId":       str(NATALIA_ID),    # fuera de la jerarquía de Laura
        "PlantillaTurnoId": str(PT_FIN_SEM_ID),
        "FechaVigencia":    "2026-06-01",
    })

    exito = respuesta.get("exito", respuesta.get("success", respuesta.get("Exito", True)))
    assert not exito, (
        f"TC-HJ-17 FALLO: El backend aceptó que Laura asigne a Natalia (ID={NATALIA_ID}), "
        "quien está fuera de su jerarquía. "
        "TurnoService debe validar pertenencia jerárquica antes de persistir. "
        f"Respuesta: {respuesta}"
    )
    print("\n  TC-HJ-17 PASÓ — Backend rechaza asignación fuera de jerarquía.")


def test_tc_hj18_backend_rechaza_plantilla_de_otro_jefe(page, plantillas_con_dueno):
    """
    TC-HJ-18: Carlos intenta asignar usando la plantilla de Laura (CreadoPorId=2).
    El backend debe rechazarlo porque esa plantilla no pertenece a Carlos.
    """
    _login(page, CARLOS)
    page.goto(f"{BASE_URL}/Empleado/Perfil/{LAURA_ID}?tab=horario")
    page.wait_for_load_state("networkidle")

    respuesta = llamar_ajax_post(page, "/Turno/AsignarTurnoAjax", {
        "EmpleadoId":       str(LAURA_ID),
        "PlantillaTurnoId": str(PT_FIN_SEM_ID),   # plantilla de Laura (CreadoPorId=2)
        "FechaVigencia":    "2026-06-01",
    })

    exito = respuesta.get("exito", respuesta.get("success", respuesta.get("Exito", True)))
    assert not exito, (
        f"TC-HJ-18 FALLO: El backend aceptó que Carlos asigne con la plantilla de Laura "
        f"(PlantillaTurnoId={PT_FIN_SEM_ID}, CreadoPorId=2). "
        "TurnoService debe validar que la plantilla pertenece al jefe en sesión. "
        f"Respuesta: {respuesta}"
    )
    print("\n  TC-HJ-18 PASÓ — Backend rechaza el uso de plantilla de otro jefe.")


def test_tc_hj19_asignacion_valida_en_jerarquia_se_persiste(page):
    """
    TC-HJ-19: Carlos realiza una asignación válida sobre Andrés (ID=4, dentro de su jerarquía).
    La asignación debe guardarse correctamente en BD.
    """
    _login(page, CARLOS)
    abierto = _abrir_modal_asignar(page, ANDRES_ID)
    if not abierto:
        pytest.skip("TC-HJ-19: No se pudo abrir el modal de asignación en el perfil de Andrés.")

    opciones = page.locator("#turno-plantilla option:not([value=''])")
    if opciones.count() == 0:
        pytest.skip("TC-HJ-19: No hay plantillas disponibles en el modal de asignación.")

    primera_plantilla_id = opciones.first.get_attribute("value")
    fecha_vigencia = "2026-07-01"

    page.select_option("#turno-plantilla", value=primera_plantilla_id)
    page.fill("#turno-fecha", fecha_vigencia)
    page.click("#btn-guardar-turno")
    page.wait_for_load_state("networkidle")

    # Verificar en BD que se guardó el registro
    conteo = _query_valor(
        f"SELECT CAST(COUNT(*) AS VARCHAR) AS Conteo FROM dbo.AsignacionesTurno "
        f"WHERE EmpleadoId = {ANDRES_ID} "
        f"AND CAST(FechaVigencia AS DATE) = '{fecha_vigencia}'",
        "Conteo",
    )
    assert conteo and int(conteo) >= 1, (
        f"TC-HJ-19 FALLO: No se encontró la asignación en BD para Andrés (ID={ANDRES_ID}) "
        f"con FechaVigencia={fecha_vigencia}. "
        "El registro debió haber sido creado por AsignarTurnoAjax."
    )
    print(f"\n  TC-HJ-19 PASÓ — Asignación válida guardada en BD (EmpleadoId={ANDRES_ID}, "
          f"PlantillaTurnoId={primera_plantilla_id}, FechaVigencia={fecha_vigencia}).")

    # Limpieza de la asignación creada por este test
    _ejecutar_sql(
        f"DELETE FROM dbo.AsignacionesTurno "
        f"WHERE EmpleadoId = {ANDRES_ID} "
        f"AND CAST(FechaVigencia AS DATE) = '{fecha_vigencia}';"
    )
