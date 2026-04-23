"""
Script puntual: valida que cada usuario pueda iniciar sesión con 'Usuario1'.
Si falla, actualiza la contraseña en BD y reintenta.
Al final imprime el reporte completo.
"""

import subprocess
import sys
import tempfile
import os
from dataclasses import dataclass, field
from typing import Literal

from playwright.sync_api import sync_playwright

# ── Configuración ─────────────────────────────────────────────────────────────
BASE_URL  = "http://localhost:5002"
PASSWORD  = "Usuario1"
DB_SERVER = r"(localdb)\MSSQLLocalDB"
DB_NAME   = "GestionPersonal"

# Hash/Salt pre-calculados para 'Usuario1' (PBKDF2/SHA-256, misma fuente que conftest.py)
HASH_USUARIO1 = "0x7DED37B4612147C18EBDFA1F6DEB4709EC9D511DA20641214F1F97612DF2CEAE"
SALT_USUARIO1 = "0xF2B483C7DAC61EC2CA7F1331C95D6800"

USUARIOS = [
    "carlos.rodriguez@yopmail.com",
    "laura.sanchez@yopmail.com",
    "hernan.castillo@yopmail.com",
    "andres.torres@yopmail.com",
    "diana.vargas@yopmail.com",
    "jorge.herrera@yopmail.com",
    "natalia.bermudez@yopmail.com",
    "paula.quintero@yopmail.com",
    "camila.rios@yopmail.com",
    "valentina.ospina@yopmail.com",
    "sebastian.moreno@yopmail.com",
    "ricardo.useche@yopmail.com",
]

# ── Tipos ──────────────────────────────────────────────────────────────────────
Estado = Literal["OK", "RESET+OK", "RESET+FALLO", "NO_EXISTE"]

@dataclass
class ResultadoUsuario:
    correo: str
    estado: Estado = "OK"
    notas: str = ""


# ── Helpers ────────────────────────────────────────────────────────────────────
def intentar_login(page, correo: str, password: str) -> bool:
    """
    Intenta hacer login. Retorna True si el login fue exitoso
    (redirige a Dashboard o CambiarPassword), False si se queda en Login.
    """
    page.goto(f"{BASE_URL}/Cuenta/Login")
    page.wait_for_load_state("networkidle")
    page.fill("#CorreoAcceso", correo)
    page.fill("#Password", password)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")
    url = page.url
    return "/Cuenta/Login" not in url


def resetear_password_db(correo: str) -> tuple[bool, str]:
    """
    Actualiza PasswordHash y PasswordSalt en BD para el correo dado.
    Retorna (éxito, mensaje_error).
    """
    sql = (
        f"UPDATE dbo.Usuarios "
        f"SET PasswordHash={HASH_USUARIO1}, PasswordSalt={SALT_USUARIO1}, DebecambiarPassword=0 "
        f"WHERE CorreoAcceso='{correo}';"
        f"SELECT @@ROWCOUNT AS filas_afectadas;"
    )
    sql_file = os.path.join(tempfile.gettempdir(), f"reset_pwd_{correo.split('@')[0]}.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)

    result = subprocess.run(
        [
            "powershell", "-Command",
            (
                f"Invoke-Sqlcmd -ServerInstance '{DB_SERVER}' "
                f"-Database '{DB_NAME}' -InputFile '{sql_file}'"
            ),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        return False, result.stderr.strip()

    # Si el rowcount es 0, el usuario no existe en BD
    if "0" in result.stdout and "filas_afectadas" in result.stdout:
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        # Busca el valor después del encabezado
        for i, line in enumerate(lines):
            if "filas_afectadas" in line:
                val_line = lines[i + 1] if i + 1 < len(lines) else "?"
                if val_line == "0":
                    return False, "Usuario no encontrado en BD"
    return True, ""


def hacer_logout(page):
    try:
        page.goto(f"{BASE_URL}/Cuenta/Logout")
        page.wait_for_load_state("networkidle")
    except Exception:
        pass


# ── Ejecución principal ────────────────────────────────────────────────────────
def main():
    resultados: list[ResultadoUsuario] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for correo in USUARIOS:
            res = ResultadoUsuario(correo=correo)
            print(f"[→] Validando: {correo}")

            # Intento 1
            ok = intentar_login(page, correo, PASSWORD)

            if ok:
                res.estado = "OK"
                res.notas  = "Login exitoso con Usuario1"
                print(f"    ✅ OK")
            else:
                print(f"    ⚠  Login falló — reseteando contraseña en BD...")
                exito_reset, err_reset = resetear_password_db(correo)

                if not exito_reset:
                    res.estado = "NO_EXISTE" if "no encontrado" in err_reset.lower() else "RESET+FALLO"
                    res.notas  = f"Reset fallido: {err_reset}"
                    print(f"    ❌ {res.notas}")
                    hacer_logout(page)
                    resultados.append(res)
                    continue

                # Intento 2 tras reset
                ok2 = intentar_login(page, correo, PASSWORD)
                if ok2:
                    res.estado = "RESET+OK"
                    res.notas  = "Password reseteada a Usuario1; login exitoso en 2.° intento"
                    print(f"    ✅ RESET+OK")
                else:
                    res.estado = "RESET+FALLO"
                    res.notas  = "Password reseteada pero el login sigue fallando"
                    print(f"    ❌ RESET+FALLO")

            hacer_logout(page)
            resultados.append(res)

        context.close()
        browser.close()

    # ── Reporte ────────────────────────────────────────────────────────────────
    print("\n" + "═" * 70)
    print("  REPORTE DE VALIDACIÓN DE CONTRASEÑAS — Sistema GestiónRH")
    print(f"  Contraseña esperada: {PASSWORD}")
    print("═" * 70)
    print(f"  {'USUARIO':<42} {'ESTADO':<14} NOTAS")
    print("─" * 70)

    totales = {"OK": 0, "RESET+OK": 0, "RESET+FALLO": 0, "NO_EXISTE": 0}
    for r in resultados:
        icono = {"OK": "✅", "RESET+OK": "🔄", "RESET+FALLO": "❌", "NO_EXISTE": "⚠️ "}.get(r.estado, "?")
        print(f"  {icono} {r.correo:<40} {r.estado:<14} {r.notas}")
        totales[r.estado] += 1

    print("─" * 70)
    print(f"  Total usuarios: {len(resultados)}")
    print(f"  ✅ OK (ya tenían Usuario1)  : {totales['OK']}")
    print(f"  🔄 RESET+OK (se corrigió)   : {totales['RESET+OK']}")
    print(f"  ❌ RESET+FALLO              : {totales['RESET+FALLO']}")
    print(f"  ⚠️  NO_EXISTE en BD          : {totales['NO_EXISTE']}")
    print("═" * 70)

    errores = totales["RESET+FALLO"] + totales["NO_EXISTE"]
    sys.exit(1 if errores > 0 else 0)


if __name__ == "__main__":
    main()
