import pyodbc
conn = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    r"Server=(localdb)\MSSQLLocalDB;"
    "Database=GestionPersonal;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)
print("Conexion a GestionPersonal exitosa")
conn.close()
