"""
Ejecuta el DDL de GestionRH_Schema.sql contra GestionPersonalDB.
- Omite CREATE DATABASE y USE (la BD ya existe como GestionPersonalDB)
- Ejecuta cada bloque GO por separado
- Informa el resultado de cada bloque
"""
import pyodbc
import re
import sys

CONN_STRING = (
    "Driver={ODBC Driver 17 for SQL Server};"
    r"Server=(localdb)\MSSQLLocalDB;"
    "Database=GestionPersonal;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

SQL_FILE = r"c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2\Documentos\GestionRH_Schema.sql"

def main():
    with open(SQL_FILE, encoding="utf-8") as f:
        raw = f.read()

    # Dividir en bloques por GO
    blocks = re.split(r"^\s*GO\s*$", raw, flags=re.MULTILINE | re.IGNORECASE)

    # Filtrar bloques vacíos y los que crean/usan otra BD
    skip_patterns = [
        re.compile(r"CREATE\s+DATABASE", re.IGNORECASE),
        re.compile(r"^\s*USE\s+\w+", re.IGNORECASE),
    ]

    conn = pyodbc.connect(CONN_STRING, autocommit=False)
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
            print(f"[SKIP]  Bloque {i+1} (CREATE DATABASE / USE)")
            skipped += 1
            continue

        # Extraer primera línea como etiqueta
        label = stripped.splitlines()[0][:80]
        try:
            cursor.execute(stripped)
            conn.commit()
            print(f"[OK]    Bloque {i+1}: {label}")
            ok += 1
        except pyodbc.ProgrammingError as e:
            # Ignorar errores de "objeto ya existe" (2714, 1913, 1911)
            code = e.args[0] if e.args else ""
            msg  = str(e)
            if any(c in msg for c in ["2714", "1913", "1911", "already an object"]):
                print(f"[EXIST] Bloque {i+1}: {label} — ya existe, se omite")
                skipped += 1
                conn.rollback()
            else:
                print(f"[ERROR] Bloque {i+1}: {label}\n        {msg}")
                errors.append((i+1, label, msg))
                conn.rollback()
        except Exception as e:
            print(f"[ERROR] Bloque {i+1}: {label}\n        {e}")
            errors.append((i+1, label, str(e)))
            conn.rollback()

    conn.close()

    print()
    print("=" * 60)
    print(f"  Resultado: {ok} OK  |  {skipped} omitidos  |  {len(errors)} errores")
    print("=" * 60)
    if errors:
        sys.exit(1)

if __name__ == "__main__":
    main()
