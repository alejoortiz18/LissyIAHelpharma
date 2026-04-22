import os
import subprocess
import tempfile

import pytest

BASE_URL = "http://localhost:5002"

# Valores de Admin2026 (PBKDF2/SHA256, 10 000 iter.) del Migracion_PasswordVarbinary256.sql
_HASH_ADMIN2026 = "0xC678F46EA40B0B419C75AA263AD9D2BDA049A9CF38AD4383D009407D51660AFB"
_SALT_ADMIN2026 = "0xE9119DF914288643380C5EB9CD4404CD"


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "login: pruebas del flujo de autenticación"
    )


@pytest.fixture(scope="session", autouse=True)
def reset_estado_db():
    """
    Restaura el estado inicial de los usuarios de prueba antes de todos los tests.
      - carlos.rodriguez : contraseña Admin2026, DebeCambiarPassword=False → va a Dashboard
      - laura.sanchez    : contraseña Admin2026, DebeCambiarPassword=True  → va a CambiarPassword
    Garantiza que los tests sean idempotentes y puedan re-ejecutarse sin reseteo manual.
    """
    sql = (
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_ADMIN2026}, "
        f"PasswordSalt={_SALT_ADMIN2026}, "
        f"DebecambiarPassword=0 "
        f"WHERE CorreoAcceso='carlos.rodriguez@helpharma.com'; "
        f"UPDATE dbo.Usuarios SET "
        f"PasswordHash={_HASH_ADMIN2026}, "
        f"PasswordSalt={_SALT_ADMIN2026}, "
        f"DebecambiarPassword=1 "
        f"WHERE CorreoAcceso='laura.sanchez@helpharma.com';"
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
