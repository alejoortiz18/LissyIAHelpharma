import os
import subprocess
import tempfile

import pytest

BASE_URL = "http://localhost:5002"

# Hash precalculado para la contraseña genérica 'Usuario1' (PBKDF2/SHA-256)
# Fuente: Documentos/BD/Seeding_Completo.sql — reglas de negocio
_HASH_USUARIO1 = "0x7DED37B4612147C18EBDFA1F6DEB4709EC9D511DA20641214F1F97612DF2CEAE"
_SALT_USUARIO1 = "0xF2B483C7DAC61EC2CA7F1331C95D6800"


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "login: pruebas del flujo de autenticación"
    )
    config.addinivalue_line(
        "markers", "recuperacion: pruebas del flujo de recuperación de contraseña"
    )
    config.addinivalue_line(
        "markers", "yopmail: pruebas que requieren verificación en yopmail.com"
    )


@pytest.fixture(scope="session", autouse=True)
def reset_estado_db():
    """
    Restaura el estado inicial de los usuarios y tokens de prueba antes de todos los tests.

    Usuarios:
      - carlos.rodriguez@yopmail.com : contraseña Usuario1, DebeCambiarPassword=0 → Dashboard
      - laura.sanchez@yopmail.com   : contraseña Usuario1, DebeCambiarPassword=1 → CambiarPassword
      - diana.vargas@yopmail.com    : contraseña Usuario1, DebeCambiarPassword=0 → Dashboard
      - natalia.bermudez@yopmail.com: contraseña Usuario1 (para re-ejecutar TC-14)

    Tokens:
      - TK1H6K9M2N : reset a Usado=0 (token vigente para TC-14)

    Garantiza idempotencia — la suite puede re-ejecutarse sin reseteo manual.
    Dominio obligatorio: @yopmail.com (regla de negocio).
    """
    sql = (
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_USUARIO1}, "
        f"PasswordSalt={_SALT_USUARIO1}, "
        f"DebecambiarPassword=0 "
        f"WHERE CorreoAcceso='carlos.rodriguez@yopmail.com'; "
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_USUARIO1}, "
        f"PasswordSalt={_SALT_USUARIO1}, "
        f"DebecambiarPassword=1 "
        f"WHERE CorreoAcceso='laura.sanchez@yopmail.com'; "
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_USUARIO1}, "
        f"PasswordSalt={_SALT_USUARIO1}, "
        f"DebecambiarPassword=0 "
        f"WHERE CorreoAcceso='diana.vargas@yopmail.com'; "
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_USUARIO1}, "
        f"PasswordSalt={_SALT_USUARIO1}, "
        f"DebecambiarPassword=0 "
        f"WHERE CorreoAcceso='andres.torres@yopmail.com'; "
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_USUARIO1}, "
        f"PasswordSalt={_SALT_USUARIO1}, "
        f"DebecambiarPassword=1 "
        f"WHERE CorreoAcceso='natalia.bermudez@yopmail.com'; "
        # El token se almacena como hash SHA-256 de 'TK1H6K9M2N'
        f"UPDATE dbo.TokensRecuperacion SET Usado=0, "
        f"FechaExpiracion='2099-12-31 23:59:00' "
        f"WHERE Token='6730ac0c93c8353faa2e834123cf3e4636dc3ce39f6654760a27e92484ed2235'; "
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_USUARIO1}, "
        f"PasswordSalt={_SALT_USUARIO1}, "
        f"DebecambiarPassword=0 "
        f"WHERE CorreoAcceso='sofia.gomez@yopmail.com'; "
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_USUARIO1}, "
        f"PasswordSalt={_SALT_USUARIO1}, "
        f"DebecambiarPassword=0 "
        f"WHERE CorreoAcceso='pedro.ramirez@yopmail.com'; "
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_USUARIO1}, "
        f"PasswordSalt={_SALT_USUARIO1}, "
        f"DebecambiarPassword=0 "
        f"WHERE CorreoAcceso='admin@yopmail.com'; "
        f"UPDATE dbo.HorasExtras SET Estado=N'Pendiente', "
        f"AprobadoRechazadoPor=NULL, FechaAprobacion=NULL, MotivoRechazo=NULL "
        f"WHERE Estado IN (N'Aprobado', N'Rechazado') "
        f"AND EmpleadoId IN ("
        f"  SELECT e.Id FROM dbo.Empleados e "
        f"  INNER JOIN dbo.Usuarios u ON e.UsuarioId = u.Id "
        f"  WHERE u.CorreoAcceso IN ("
        f"    'andres.torres@yopmail.com', 'diana.vargas@yopmail.com'"
        f"  )"
        f"); "
        # Limpiar eventos insertados por TC-PR-64 (Analista) y TC-PR-90 (Administrador)
        # Para garantizar idempotencia en re-ejecuciones consecutivas
        f"DELETE FROM dbo.EventosLaborales "
        f"WHERE EmpleadoId = 1 AND TipoEvento = 'Permiso' "
        f"AND FechaInicio IN ('2026-07-01', '2026-08-01'); "
        # Vacaciones de prueba creadas por TC-SOL-VAC-06
        f"DELETE FROM dbo.EventosLaborales "
        f"WHERE EmpleadoId = 5 AND TipoEvento = 'Vacaciones'; "
        # Seed FechaInicioContrato para tests de saldo vacaciones
        f"UPDATE dbo.Empleados SET FechaInicioContrato = '2020-01-01' WHERE Id IN (1, 5); "
        # Migración: empleados Directo sin FechaInicioContrato (creados antes de la regla)
        f"UPDATE dbo.Empleados SET FechaInicioContrato = FechaIngreso "
        f"WHERE TipoVinculacion = 'Directo' AND FechaInicioContrato IS NULL; "
        # Migración: empleados Temporal con FechaInicioContrato (creados con un bug anterior)
        f"UPDATE dbo.Empleados SET FechaInicioContrato = NULL "
        f"WHERE TipoVinculacion = 'Temporal' AND FechaInicioContrato IS NOT NULL;"
    )
    sql_file = os.path.join(tempfile.gettempdir(), "reset_test_usuarios.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)

    result = subprocess.run(
        [
            "powershell", "-Command",
            (
                f"Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
                f"-Database 'GestionPersonal' -InputFile '{sql_file}'"
            ),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        pytest.fail(f"No se pudo resetear la BD de prueba: {result.stderr}")

    yield


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


def _run_sql(sql: str) -> None:
    """Ejecuta un bloque SQL contra (localdb)\\MSSQLLocalDB usando Invoke-Sqlcmd."""
    import tempfile, os
    sql_file = os.path.join(tempfile.gettempdir(), "reset_vinculacion.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    result = subprocess.run(
        [
            "powershell", "-Command",
            (
                f"Invoke-Sqlcmd -ServerInstance '(localdb)\\MSSQLLocalDB' "
                f"-Database 'GestionPersonal' -InputFile '{sql_file}'"
            ),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        pytest.fail(f"SQL falló: {result.stderr}")


_SQL_CAMILA_TEMPORAL = """
DECLARE @EmpId INT = (SELECT TOP 1 Id FROM dbo.EmpresasTemporales WHERE Nombre LIKE '%Adecco%');
IF @EmpId IS NULL
    SET @EmpId = (SELECT TOP 1 Id FROM dbo.EmpresasTemporales);
UPDATE dbo.Empleados
SET TipoVinculacion     = N'Temporal',
    EmpresaTemporalId   = @EmpId,
    FechaInicioContrato = NULL,
    FechaFinContrato    = '2026-07-01'
WHERE Cedula = N'99887766';
"""

_SQL_CAMILA_DIRECTO = """
UPDATE dbo.Empleados
SET TipoVinculacion     = N'Directo',
    EmpresaTemporalId   = NULL,
    FechaInicioContrato = NULL,
    FechaFinContrato    = NULL
WHERE Cedula = N'99887766';
"""


@pytest.fixture
def reset_empleado_temporal():
    """
    Asegura que Camila Ríos Vargas (CC 99887766) esté en estado Temporal
    antes del test, y la restaura a Temporal al finalizar (idempotencia).
    """
    _run_sql(_SQL_CAMILA_TEMPORAL)
    yield
    _run_sql(_SQL_CAMILA_TEMPORAL)


@pytest.fixture(scope="session", autouse=False)
def restaurar_camila_directo():
    """Restaura a Camila a Directo al finalizar toda la suite de vinculación."""
    yield
    _run_sql(_SQL_CAMILA_DIRECTO)


# ── Fixture para tests de creación de empleado ───────────────────────────────

_CEDULAS_PRUEBA_CREACION = ("'12345001'", "'12345002'")


def _borrar_empleados_prueba() -> None:
    """Elimina los empleados de prueba creados por test_creacion_usuario.py."""
    cedulas = ", ".join(_CEDULAS_PRUEBA_CREACION)
    correos = (
        "'directo.12345001@yopmail.com'",
        "'temporal.12345002@yopmail.com'",
    )
    correos_in = ", ".join(correos)
    sql = (
        # 1. Contactos de emergencia (FK → Empleados)
        f"DELETE ce FROM dbo.ContactosEmergencia ce "
        f"INNER JOIN dbo.Empleados e ON ce.EmpleadoId = e.Id "
        f"WHERE e.Cedula IN ({cedulas}); "
        # 2. Romper FK Empleados.UsuarioId → Usuarios antes de borrar Usuarios
        f"UPDATE dbo.Empleados SET UsuarioId = NULL WHERE Cedula IN ({cedulas}); "
        # 3. Borrar Empleados
        f"DELETE FROM dbo.Empleados WHERE Cedula IN ({cedulas}); "
        # 4. Borrar Usuarios por correo (pueden quedar huérfanos si paso 3 falló)
        f"DELETE FROM dbo.Usuarios WHERE CorreoAcceso IN ({correos_in});"
    )
    _run_sql(sql)


@pytest.fixture(autouse=False)
def limpiar_empleado_prueba():
    """Elimina los empleados de prueba ANTES y DESPUÉS de cada test que la use."""
    _borrar_empleados_prueba()
    yield
    _borrar_empleados_prueba()
