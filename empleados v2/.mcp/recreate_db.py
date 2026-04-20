"""
1. Elimina GestionPersonalDB (si existe)
2. Crea GestionPersonal con collation correcta
3. Ejecuta el DDL completo del schema (omite CREATE DATABASE y USE)
"""
import pyodbc
import re
import sys

MASTER_CONN = (
    "Driver={ODBC Driver 17 for SQL Server};"
    r"Server=(localdb)\MSSQLLocalDB;"
    "Database=master;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

TARGET_DB = "GestionPersonal"

SQL_FILE = r"c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2\Documentos\GestionRH_Schema.sql"

def run_ddl():
    # ── Paso 1: DROP + CREATE en master (autocommit obligatorio para DDL de BD) ──
    conn = pyodbc.connect(MASTER_CONN, autocommit=True)
    cursor = conn.cursor()

    # Terminar conexiones activas a GestionPersonalDB antes de eliminar
    for db in ("GestionPersonalDB", TARGET_DB):
        cursor.execute(f"""
            IF DB_ID('{db}') IS NOT NULL
            BEGIN
                ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                DROP DATABASE [{db}];
                PRINT 'Eliminada: {db}';
            END
        """)
        print(f"[INFO] DROP IF EXISTS: {db}")

    cursor.execute(
        f"CREATE DATABASE [{TARGET_DB}] COLLATE SQL_Latin1_General_CP1_CI_AS;"
    )
    print(f"[OK]   Base de datos '{TARGET_DB}' creada.")
    conn.close()

    # ── Paso 2: Ejecutar DDL del schema ──────────────────────────────────────
    target_conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        r"Server=(localdb)\MSSQLLocalDB;"
        f"Database={TARGET_DB};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    with open(SQL_FILE, encoding="utf-8") as f:
        raw = f.read()

    blocks = re.split(r"^\s*GO\s*$", raw, flags=re.MULTILINE | re.IGNORECASE)

    skip_patterns = [
        re.compile(r"CREATE\s+DATABASE", re.IGNORECASE),
        re.compile(r"^\s*USE\s+\w+", re.IGNORECASE),
    ]

    conn = pyodbc.connect(target_conn_str, autocommit=False)
    cursor = conn.cursor()

    ok = 0
    skipped = 0
    errors = []

    for i, block in enumerate(blocks):
        stripped = block.strip()
        if not stripped:
            skipped += 1
            continue
        if any(p.search(stripped) for p in skip_patterns):
            skipped += 1
            continue

        label = stripped.splitlines()[0][:80]
        try:
            cursor.execute(stripped)
            conn.commit()
            print(f"[OK]    Bloque {i+1}: {label}")
            ok += 1
        except Exception as e:
            msg = str(e)
            print(f"[ERROR] Bloque {i+1}: {label}\n        {msg}")
            errors.append((i+1, label, msg))
            conn.rollback()

    conn.close()

    print()
    print("=" * 60)
    print(f"  Resultado: {ok} OK  |  {skipped} omitidos  |  {len(errors)} errores")
    print("=" * 60)
    if errors:
        sys.exit(1)

if __name__ == "__main__":
    run_ddl()
