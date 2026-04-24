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
        f"UPDATE dbo.TokensRecuperacion SET Usado=0 "
        f"WHERE Token='TK1H6K9M2N'; "
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
        f"AND FechaInicio IN ('2026-07-01', '2026-08-01');"
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
