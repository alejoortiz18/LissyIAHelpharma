"""
MCP Server para SQL Server - GestionPersonal
Conexión con Windows Authentication (LocalDB)
"""
import pyodbc
import json
from mcp.server.fastmcp import FastMCP

# ─── Configuración de conexión ───────────────────────────────────────────────
SERVER   = r"(localdb)\MSSQLLocalDB"
DATABASE = "GestionPersonal"
DRIVER   = "ODBC Driver 17 for SQL Server"

CONNECTION_STRING = (
    f"Driver={{{DRIVER}}};"
    f"Server={SERVER};"
    f"Database={DATABASE};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

mcp = FastMCP("GestionPersonal - SQL Server")

# ─── Helper ──────────────────────────────────────────────────────────────────

def get_connection() -> pyodbc.Connection:
    return pyodbc.connect(CONNECTION_STRING)


def rows_to_list(cursor: pyodbc.Cursor) -> list[dict]:
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# ─── Herramientas ────────────────────────────────────────────────────────────

@mcp.tool()
def list_tables() -> str:
    """Lista todas las tablas de usuario en la base de datos GestionPersonal."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT TABLE_SCHEMA, TABLE_NAME "
            "FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_TYPE = 'BASE TABLE' "
            "ORDER BY TABLE_SCHEMA, TABLE_NAME"
        )
        tables = rows_to_list(cursor)
    return json.dumps(tables, ensure_ascii=False, default=str)


@mcp.tool()
def describe_table(table_name: str, schema: str = "dbo") -> str:
    """
    Devuelve las columnas de una tabla: nombre, tipo, nulable y clave primaria.

    Args:
        table_name: Nombre de la tabla.
        schema: Esquema de la tabla (por defecto 'dbo').
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                c.COLUMN_NAME,
                c.DATA_TYPE,
                c.CHARACTER_MAXIMUM_LENGTH,
                c.IS_NULLABLE,
                CASE WHEN kcu.COLUMN_NAME IS NOT NULL THEN 'YES' ELSE 'NO' END AS IS_PRIMARY_KEY
            FROM INFORMATION_SCHEMA.COLUMNS c
            LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                ON  tc.TABLE_SCHEMA = c.TABLE_SCHEMA
                AND tc.TABLE_NAME   = c.TABLE_NAME
                AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
            LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                ON  kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
                AND kcu.COLUMN_NAME     = c.COLUMN_NAME
            WHERE c.TABLE_SCHEMA = ?
              AND c.TABLE_NAME   = ?
            ORDER BY c.ORDINAL_POSITION
            """,
            (schema, table_name),
        )
        columns = rows_to_list(cursor)
    return json.dumps(columns, ensure_ascii=False, default=str)


@mcp.tool()
def run_query(sql: str, max_rows: int = 200) -> str:
    """
    Ejecuta una consulta SQL SELECT y devuelve los resultados como JSON.
    Solo se permiten sentencias SELECT/WITH para evitar modificaciones accidentales.

    Args:
        sql: Sentencia SQL a ejecutar (solo SELECT/WITH).
        max_rows: Número máximo de filas a devolver (máximo 500).
    """
    normalized = sql.strip().upper()
    if not (normalized.startswith("SELECT") or normalized.startswith("WITH")):
        return json.dumps({"error": "Solo se permiten sentencias SELECT o WITH."})

    max_rows = min(max_rows, 500)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = rows_to_list(cursor)[:max_rows]
    return json.dumps(rows, ensure_ascii=False, default=str)


@mcp.tool()
def run_statement(sql: str) -> str:
    """
    Ejecuta una sentencia SQL de escritura (INSERT, UPDATE, DELETE, CREATE, etc.)
    y devuelve el número de filas afectadas.

    Args:
        sql: Sentencia SQL a ejecutar.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows_affected = cursor.rowcount
        conn.commit()
    return json.dumps({"rows_affected": rows_affected}, ensure_ascii=False)


@mcp.tool()
def get_schema_overview() -> str:
    """
    Devuelve un resumen completo del esquema: tablas, columnas, PK y FK.
    Útil para entender la estructura completa de la base de datos.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Tablas y columnas
        cursor.execute(
            """
            SELECT
                t.TABLE_SCHEMA,
                t.TABLE_NAME,
                c.COLUMN_NAME,
                c.DATA_TYPE,
                c.IS_NULLABLE,
                CASE WHEN kcu.COLUMN_NAME IS NOT NULL THEN 'YES' ELSE 'NO' END AS IS_PRIMARY_KEY
            FROM INFORMATION_SCHEMA.TABLES t
            JOIN INFORMATION_SCHEMA.COLUMNS c
                ON  c.TABLE_SCHEMA = t.TABLE_SCHEMA
                AND c.TABLE_NAME   = t.TABLE_NAME
            LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                ON  tc.TABLE_SCHEMA    = t.TABLE_SCHEMA
                AND tc.TABLE_NAME      = t.TABLE_NAME
                AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
            LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                ON  kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
                AND kcu.COLUMN_NAME     = c.COLUMN_NAME
            WHERE t.TABLE_TYPE = 'BASE TABLE'
            ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME, c.ORDINAL_POSITION
            """
        )
        schema = rows_to_list(cursor)

        # Claves foráneas
        cursor.execute(
            """
            SELECT
                fk.name                              AS FK_NAME,
                tp.name                              AS PARENT_TABLE,
                cp.name                              AS PARENT_COLUMN,
                tr.name                              AS REFERENCED_TABLE,
                cr.name                              AS REFERENCED_COLUMN
            FROM sys.foreign_keys fk
            JOIN sys.foreign_key_columns fkc
                ON fkc.constraint_object_id = fk.object_id
            JOIN sys.tables  tp ON tp.object_id = fkc.parent_object_id
            JOIN sys.columns cp ON cp.object_id = fkc.parent_object_id
                               AND cp.column_id = fkc.parent_column_id
            JOIN sys.tables  tr ON tr.object_id = fkc.referenced_object_id
            JOIN sys.columns cr ON cr.object_id = fkc.referenced_object_id
                               AND cr.column_id = fkc.referenced_column_id
            ORDER BY tp.name, cp.name
            """
        )
        fks = rows_to_list(cursor)

    result = {"tables_and_columns": schema, "foreign_keys": fks}
    return json.dumps(result, ensure_ascii=False, default=str)


# ─── Punto de entrada ────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
