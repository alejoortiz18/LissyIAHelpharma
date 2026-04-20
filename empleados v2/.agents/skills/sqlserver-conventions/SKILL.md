---
name: sqlserver-conventions
description: Aplica convenciones de diseño y buenas prácticas para SQL Server en proyectos .NET. Úsalo cuando diseñes tablas, escribas queries SQL, definas índices, stored procedures o revises el esquema de la base de datos.
metadata:
  author: custom
  version: "1.0.0"
---

# SQL Server — Convenciones y Buenas Prácticas

Guía de diseño de base de datos SQL Server para proyectos .NET Core con EF Core.

## Naming Conventions

| Objeto            | Convención             | Ejemplo                          |
|-------------------|------------------------|----------------------------------|
| Tablas            | PascalCase, plural     | `Empleados`, `Sedes`, `Cargos`   |
| Columnas          | PascalCase             | `NombreCompleto`, `FechaIngreso` |
| Primary Key       | `Id`                   | `Id INT IDENTITY(1,1)`           |
| Foreign Key col.  | `{Entidad}Id`          | `SedeId`, `CargoId`              |
| Foreign Key const.| `FK_{Tabla}_{Referencia}` | `FK_Empleados_Sedes`          |
| Índices           | `IX_{Tabla}_{Columnas}` | `IX_Empleados_Cedula`           |
| Índice único      | `UX_{Tabla}_{Columnas}` | `UX_Empleados_Cedula`           |
| Stored Procs      | `usp_{Accion}{Entidad}` | `usp_ObtenerEmpleadosPorSede`   |
| Views             | `v_{Nombre}`           | `v_EmpleadosActivos`             |
| Schemas           | minúsculas             | `dbo`, `rrhh`                    |

## Tipos de Datos Recomendados

| Dato                     | Tipo SQL Server         | Notas                                          |
|--------------------------|-------------------------|------------------------------------------------|
| Identificador            | `INT IDENTITY(1,1)`     | Usar `BIGINT` si se esperan > 2 mil millones   |
| Texto corto (<= 200 car) | `NVARCHAR(n)`           | Siempre `NVARCHAR` para soporte Unicode        |
| Texto largo              | `NVARCHAR(MAX)`         | Solo cuando sea necesario; no indexable        |
| Cédula / NIT             | `NVARCHAR(20)`          | No usar INT; puede tener dígito verificador    |
| Fecha sin hora           | `DATE`                  | Ej: `FechaNacimiento`, `FechaIngreso`          |
| Fecha con hora           | `DATETIME2(0)`          | Más preciso y eficiente que `DATETIME`         |
| Dinero / salario         | `DECIMAL(18,2)`         | Nunca `FLOAT` ni `MONEY` para valores exactos  |
| Booleano                 | `BIT NOT NULL`          | Default `0`                                    |
| Estado / Enum            | `NVARCHAR(30) NOT NULL` | Legible; o `TINYINT` con tabla de referencia   |
| Teléfono                 | `NVARCHAR(20)`          | Texto, no numérico                             |

## Diseño de Tablas

```sql
-- Ejemplo: tabla Empleados
CREATE TABLE Empleados (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    NombreCompleto      NVARCHAR(200)                   NOT NULL,
    Cedula              NVARCHAR(20)                    NOT NULL,
    FechaNacimiento     DATE                            NULL,
    Telefono            NVARCHAR(20)                    NULL,
    CorreoElectronico   NVARCHAR(256)                   NULL,
    Estado              NVARCHAR(20)                    NOT NULL  DEFAULT 'Activo',
    TipoVinculacion     NVARCHAR(20)                    NOT NULL,
    FechaIngreso        DATE                            NOT NULL,
    SedeId              INT                             NOT NULL,
    CargoId             INT                             NOT NULL,
    FechaCreacion       DATETIME2(0)                    NOT NULL  DEFAULT GETUTCDATE(),
    FechaModificacion   DATETIME2(0)                    NULL,

    CONSTRAINT PK_Empleados           PRIMARY KEY (Id),
    CONSTRAINT UX_Empleados_Cedula    UNIQUE      (Cedula),
    CONSTRAINT FK_Empleados_Sedes     FOREIGN KEY (SedeId)  REFERENCES Sedes(Id),
    CONSTRAINT FK_Empleados_Cargos    FOREIGN KEY (CargoId) REFERENCES Cargos(Id),
    CONSTRAINT CK_Empleados_Estado    CHECK       (Estado IN ('Activo','Inactivo')),
    CONSTRAINT CK_Empleados_Vinc      CHECK       (TipoVinculacion IN ('Directo','Temporal'))
);
```

## Índices

### Cuándo crear índices
- Columnas en cláusulas `WHERE` frecuentes: `SedeId`, `Estado`, `CargoId`.
- Columnas de `JOIN` que no son FK con índice automático.
- Columnas de ordenamiento frecuente (`FechaIngreso`, `NombreCompleto`).

```sql
-- Índice compuesto para consultas por sede y estado
CREATE NONCLUSTERED INDEX IX_Empleados_SedeId_Estado
    ON Empleados (SedeId, Estado)
    INCLUDE (NombreCompleto, CargoId);

-- Índice para búsqueda por cédula (ya cubierto por UX, pero explícito)
CREATE UNIQUE NONCLUSTERED INDEX UX_Empleados_Cedula
    ON Empleados (Cedula);
```

### Reglas de índices
- No crear índices en columnas de baja cardinalidad (ej: columna BIT con solo 2 valores).
- El índice `INCLUDE` agrega columnas sin ordenarlas, ideal para `SELECT` sin `WHERE` en esas cols.
- Revisar el plan de ejecución (`SET STATISTICS IO ON`) antes de agregar índices especulativos.
- Máximo 5-7 índices por tabla; más índices = más lento el `INSERT/UPDATE/DELETE`.

## Queries SQL — Buenas Prácticas

```sql
-- ✅ Correcto: columnas explícitas, no SELECT *
SELECT e.Id, e.NombreCompleto, e.Cedula, c.Nombre AS Cargo, s.Nombre AS Sede
FROM   Empleados   e
JOIN   Cargos      c ON c.Id = e.CargoId
JOIN   Sedes       s ON s.Id = e.SedeId
WHERE  e.SedeId = @SedeId
  AND  e.Estado = 'Activo'
ORDER BY e.NombreCompleto;

-- ❌ Evitar: SELECT *, sin alias, JOIN implícito
SELECT * FROM Empleados, Sedes WHERE Empleados.SedeId = Sedes.Id;
```

### Reglas de queries
- Siempre usar **columnas explícitas** en `SELECT`; nunca `SELECT *` en producción.
- Usar **parámetros** (`@Parametro`) en lugar de concatenar strings (previene SQL Injection).
- Preferir `JOIN` explícito (`INNER JOIN`, `LEFT JOIN`) sobre joins implícitos en `WHERE`.
- Usar alias descriptivos: `e` para `Empleados`, `s` para `Sedes`, `c` para `Cargos`.
- Filtrar con `WHERE` antes de `JOIN` cuando sea posible (optimiza el plan de ejecución).

## Soft Delete

Para las entidades que requieren desactivación (no borrado físico), usar columna de estado:

```sql
-- Desactivar empleado (nunca DELETE en producción)
UPDATE Empleados
SET    Estado           = 'Inactivo',
       FechaModificacion = GETUTCDATE()
WHERE  Id = @EmpleadoId;
```

Siempre filtrar `WHERE Estado = 'Activo'` en las queries de listado.

## Auditoría

Agregar columnas de auditoría a todas las tablas principales:

```sql
FechaCreacion       DATETIME2(0) NOT NULL DEFAULT GETUTCDATE(),
CreadoPor           INT          NULL REFERENCES Usuarios(Id),
FechaModificacion   DATETIME2(0) NULL,
ModificadoPor       INT          NULL REFERENCES Usuarios(Id)
```

En EF Core, poblar estas columnas en `SaveChangesAsync` con un override:

```csharp
public override async Task<int> SaveChangesAsync(CancellationToken ct = default)
{
    foreach (var entry in ChangeTracker.Entries<EntidadAuditable>())
    {
        if (entry.State == EntityState.Added)
            entry.Entity.FechaCreacion = DateTime.UtcNow;
        if (entry.State is EntityState.Added or EntityState.Modified)
            entry.Entity.FechaModificacion = DateTime.UtcNow;
    }
    return await base.SaveChangesAsync(ct);
}
```

## Collation

Usar `SQL_Latin1_General_CP1_CI_AS` (insensible a mayúsculas/minúsculas) o configurar a nivel de base de datos. Para columnas donde el case importa (contraseñas hasheadas), usar `_CS_AS`.

## Connection String Segura

```json
{
  "ConnectionStrings": {
    "Default": "Server=localhost;Database=GestionRH;Trusted_Connection=True;TrustServerCertificate=True;MultipleActiveResultSets=true;Connect Timeout=30"
  }
}
```

- **Nunca** incluir usuario/contraseña en el código fuente; usar variables de entorno o Azure Key Vault en producción.
- `TrustServerCertificate=True` solo para desarrollo local; en producción configurar certificado válido.
- `MultipleActiveResultSets=true` requerido para EF Core con operaciones async paralelas.

---

## Esquema DDL Completo — GestiónRH

Script de creación de la base de datos del Sistema de Administración de Empleados. Ejecutar en orden (respeta dependencias FK).

```sql
-- ============================================================
-- CREAR BASE DE DATOS
-- ============================================================
CREATE DATABASE GestionRH
    COLLATE SQL_Latin1_General_CP1_CI_AS;
GO

USE GestionRH;
GO

-- ============================================================
-- TABLA: Sedes
-- ============================================================
CREATE TABLE dbo.Sedes (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    Nombre              NVARCHAR(200)                   NOT NULL,
    Ciudad              NVARCHAR(100)                   NOT NULL,
    Direccion           NVARCHAR(300)                   NOT NULL,
    Estado              NVARCHAR(20)                    NOT NULL  CONSTRAINT DF_Sedes_Estado    DEFAULT 'Activa',
    FechaCreacion       DATETIME2(0)                    NOT NULL  CONSTRAINT DF_Sedes_FechaC    DEFAULT GETUTCDATE(),
    FechaModificacion   DATETIME2(0)                    NULL,

    CONSTRAINT PK_Sedes             PRIMARY KEY (Id),
    CONSTRAINT UX_Sedes_Nombre      UNIQUE      (Nombre),
    CONSTRAINT CK_Sedes_Estado      CHECK       (Estado IN ('Activa','Inactiva'))
);
GO

-- ============================================================
-- TABLA: Cargos
-- ============================================================
CREATE TABLE dbo.Cargos (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    Nombre              NVARCHAR(200)                   NOT NULL,
    Estado              NVARCHAR(20)                    NOT NULL  CONSTRAINT DF_Cargos_Estado   DEFAULT 'Activo',
    FechaCreacion       DATETIME2(0)                    NOT NULL  CONSTRAINT DF_Cargos_FechaC   DEFAULT GETUTCDATE(),
    FechaModificacion   DATETIME2(0)                    NULL,

    CONSTRAINT PK_Cargos            PRIMARY KEY (Id),
    CONSTRAINT UX_Cargos_Nombre     UNIQUE      (Nombre),
    CONSTRAINT CK_Cargos_Estado     CHECK       (Estado IN ('Activo','Inactivo'))
);
GO

-- ============================================================
-- TABLA: EmpresasTemporales
-- ============================================================
CREATE TABLE dbo.EmpresasTemporales (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    Nombre              NVARCHAR(200)                   NOT NULL,
    Estado              NVARCHAR(20)                    NOT NULL  CONSTRAINT DF_EmpTemp_Estado  DEFAULT 'Activa',
    FechaCreacion       DATETIME2(0)                    NOT NULL  CONSTRAINT DF_EmpTemp_FechaC  DEFAULT GETUTCDATE(),
    FechaModificacion   DATETIME2(0)                    NULL,

    CONSTRAINT PK_EmpresasTemporales        PRIMARY KEY (Id),
    CONSTRAINT UX_EmpresasTemporales_Nombre UNIQUE      (Nombre),
    CONSTRAINT CK_EmpresasTemporales_Estado CHECK       (Estado IN ('Activa','Inactiva'))
);
GO

-- ============================================================
-- TABLA: PlantillasTurno
-- ============================================================
CREATE TABLE dbo.PlantillasTurno (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    Nombre              NVARCHAR(200)                   NOT NULL,
    Estado              NVARCHAR(20)                    NOT NULL  CONSTRAINT DF_Plantillas_Estado DEFAULT 'Activa',
    FechaCreacion       DATETIME2(0)                    NOT NULL  CONSTRAINT DF_Plantillas_FechaC DEFAULT GETUTCDATE(),
    FechaModificacion   DATETIME2(0)                    NULL,

    CONSTRAINT PK_PlantillasTurno           PRIMARY KEY (Id),
    CONSTRAINT UX_PlantillasTurno_Nombre    UNIQUE      (Nombre),
    CONSTRAINT CK_PlantillasTurno_Estado    CHECK       (Estado IN ('Activa','Inactiva'))
);
GO

-- ============================================================
-- TABLA: PlantillasTurnoDetalle (configuración por día)
-- ============================================================
CREATE TABLE dbo.PlantillasTurnoDetalle (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    PlantillaTurnoId    INT                             NOT NULL,
    DiaSemana           TINYINT                         NOT NULL,   -- 1=Lun, 2=Mar, ..., 7=Dom
    HoraEntrada         TIME(0)                         NULL,       -- NULL = No labora
    HoraSalida          TIME(0)                         NULL,

    CONSTRAINT PK_PlantillasTurnoDetalle        PRIMARY KEY (Id),
    CONSTRAINT UX_PlantillasTurnoDetalle_Dia    UNIQUE      (PlantillaTurnoId, DiaSemana),
    CONSTRAINT FK_PlantillasTurnoDetalle_Plnt   FOREIGN KEY (PlantillaTurnoId) REFERENCES dbo.PlantillasTurno(Id),
    CONSTRAINT CK_PlantillasTurnoDetalle_Dia    CHECK       (DiaSemana BETWEEN 1 AND 7),
    CONSTRAINT CK_PlantillasTurnoDetalle_Horas  CHECK       (
        (HoraEntrada IS NULL AND HoraSalida IS NULL) OR
        (HoraEntrada IS NOT NULL AND HoraSalida IS NOT NULL AND HoraSalida > HoraEntrada)
    )
);
GO

-- ============================================================
-- TABLA: Usuarios (credenciales de acceso)
-- ============================================================
CREATE TABLE dbo.Usuarios (
    Id                      INT             IDENTITY(1,1)   NOT NULL,
    CorreoAcceso            NVARCHAR(256)                   NOT NULL,
    PasswordHash            NVARCHAR(256)                   NOT NULL,   -- bcrypt hash
    Rol                     NVARCHAR(30)                    NOT NULL,
    SedeId                  INT                             NOT NULL,
    DebecambiarPassword     BIT                             NOT NULL  CONSTRAINT DF_Usuarios_CambiarPwd DEFAULT 1,
    Estado                  NVARCHAR(20)                    NOT NULL  CONSTRAINT DF_Usuarios_Estado      DEFAULT 'Activo',
    FechaCreacion           DATETIME2(0)                    NOT NULL  CONSTRAINT DF_Usuarios_FechaC      DEFAULT GETUTCDATE(),
    FechaModificacion       DATETIME2(0)                    NULL,
    UltimoAcceso            DATETIME2(0)                    NULL,

    CONSTRAINT PK_Usuarios              PRIMARY KEY (Id),
    CONSTRAINT UX_Usuarios_Correo       UNIQUE      (CorreoAcceso),
    CONSTRAINT FK_Usuarios_Sedes        FOREIGN KEY (SedeId)      REFERENCES dbo.Sedes(Id),
    CONSTRAINT CK_Usuarios_Rol          CHECK       (Rol IN ('Jefe','Regente','AuxiliarRegente','Operario','Administrador')),
    CONSTRAINT CK_Usuarios_Estado       CHECK       (Estado IN ('Activo','Inactivo'))
);
GO

CREATE NONCLUSTERED INDEX IX_Usuarios_SedeId ON dbo.Usuarios (SedeId);
GO

-- ============================================================
-- TABLA: TokensRecuperacion (recuperación de contraseña)
-- ============================================================
CREATE TABLE dbo.TokensRecuperacion (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    UsuarioId           INT                             NOT NULL,
    Token               NVARCHAR(256)                   NOT NULL,
    FechaExpiracion     DATETIME2(0)                    NOT NULL,
    Usado               BIT                             NOT NULL  CONSTRAINT DF_Tokens_Usado DEFAULT 0,
    FechaCreacion       DATETIME2(0)                    NOT NULL  CONSTRAINT DF_Tokens_FechaC DEFAULT GETUTCDATE(),

    CONSTRAINT PK_TokensRecuperacion        PRIMARY KEY (Id),
    CONSTRAINT UX_TokensRecuperacion_Token  UNIQUE      (Token),
    CONSTRAINT FK_TokensRecuperacion_Usuario FOREIGN KEY (UsuarioId) REFERENCES dbo.Usuarios(Id)
);
GO

-- ============================================================
-- TABLA: Empleados
-- ============================================================
CREATE TABLE dbo.Empleados (
    Id                      INT             IDENTITY(1,1)   NOT NULL,
    -- Datos personales
    NombreCompleto          NVARCHAR(200)                   NOT NULL,
    Cedula                  NVARCHAR(20)                    NOT NULL,
    FechaNacimiento         DATE                            NULL,
    Telefono                NVARCHAR(20)                    NULL,
    CorreoElectronico       NVARCHAR(256)                   NULL,
    -- Residencia
    Direccion               NVARCHAR(300)                   NULL,
    Ciudad                  NVARCHAR(100)                   NULL,
    Departamento            NVARCHAR(100)                   NULL,
    -- Formación
    NivelEscolaridad        NVARCHAR(30)                    NULL,
    -- Seguridad social
    Eps                     NVARCHAR(200)                   NULL,
    Arl                     NVARCHAR(200)                   NULL,
    -- Vinculación
    SedeId                  INT                             NOT NULL,
    CargoId                 INT                             NOT NULL,
    UsuarioId               INT                             NULL,   -- FK a Usuarios (cuenta de acceso)
    JefeInmediatoId         INT                             NULL,   -- FK a otro Empleado con rol Jefe
    TipoVinculacion         NVARCHAR(20)                    NOT NULL,
    FechaIngreso            DATE                            NOT NULL,
    -- Contrato temporal (condicional)
    EmpresaTemporalId       INT                             NULL,
    FechaInicioContrato     DATE                            NULL,
    FechaFinContrato        DATE                            NULL,
    -- Estado
    Estado                  NVARCHAR(20)                    NOT NULL  CONSTRAINT DF_Empleados_Estado  DEFAULT 'Activo',
    -- Saldo vacaciones (días ya tomados antes del sistema)
    DiasVacacionesPrevios   DECIMAL(5,1)                    NOT NULL  CONSTRAINT DF_Empleados_DiasPrev DEFAULT 0,
    -- Auditoría
    FechaCreacion           DATETIME2(0)                    NOT NULL  CONSTRAINT DF_Empleados_FechaC   DEFAULT GETUTCDATE(),
    CreadoPor               INT                             NULL,
    FechaModificacion       DATETIME2(0)                    NULL,
    ModificadoPor           INT                             NULL,

    CONSTRAINT PK_Empleados                 PRIMARY KEY (Id),
    CONSTRAINT UX_Empleados_Cedula          UNIQUE      (Cedula),
    CONSTRAINT FK_Empleados_Sedes           FOREIGN KEY (SedeId)            REFERENCES dbo.Sedes(Id),
    CONSTRAINT FK_Empleados_Cargos          FOREIGN KEY (CargoId)           REFERENCES dbo.Cargos(Id),
    CONSTRAINT FK_Empleados_Usuarios        FOREIGN KEY (UsuarioId)         REFERENCES dbo.Usuarios(Id),
    CONSTRAINT FK_Empleados_JefeInmediato   FOREIGN KEY (JefeInmediatoId)   REFERENCES dbo.Empleados(Id),
    CONSTRAINT FK_Empleados_EmpresaTemp     FOREIGN KEY (EmpresaTemporalId) REFERENCES dbo.EmpresasTemporales(Id),
    CONSTRAINT FK_Empleados_CreadoPor       FOREIGN KEY (CreadoPor)         REFERENCES dbo.Usuarios(Id),
    CONSTRAINT FK_Empleados_ModificadoPor   FOREIGN KEY (ModificadoPor)     REFERENCES dbo.Usuarios(Id),
    CONSTRAINT CK_Empleados_Estado          CHECK       (Estado IN ('Activo','Inactivo')),
    CONSTRAINT CK_Empleados_TipoVinc        CHECK       (TipoVinculacion IN ('Directo','Temporal')),
    CONSTRAINT CK_Empleados_NivelEscol      CHECK       (NivelEscolaridad IN ('Primaria','Bachillerato','Tecnico','Tecnologico','Profesional','Posgrado') OR NivelEscolaridad IS NULL),
    CONSTRAINT CK_Empleados_ContratoTemp    CHECK       (
        TipoVinculacion = 'Directo' OR
        (TipoVinculacion = 'Temporal' AND EmpresaTemporalId IS NOT NULL AND FechaInicioContrato IS NOT NULL AND FechaFinContrato IS NOT NULL)
    ),
    CONSTRAINT CK_Empleados_FechasContrato  CHECK       (FechaFinContrato IS NULL OR FechaFinContrato >= FechaInicioContrato)
);
GO

CREATE NONCLUSTERED INDEX IX_Empleados_SedeId_Estado
    ON dbo.Empleados (SedeId, Estado)
    INCLUDE (NombreCompleto, CargoId, TipoVinculacion);
GO

CREATE NONCLUSTERED INDEX IX_Empleados_CargoId ON dbo.Empleados (CargoId);
GO

-- ============================================================
-- TABLA: ContactosEmergencia
-- ============================================================
CREATE TABLE dbo.ContactosEmergencia (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    EmpleadoId          INT                             NOT NULL,
    NombreContacto      NVARCHAR(200)                   NOT NULL,
    TelefonoContacto    NVARCHAR(20)                    NOT NULL,

    CONSTRAINT PK_ContactosEmergencia       PRIMARY KEY (Id),
    CONSTRAINT FK_ContactosEmergencia_Emp   FOREIGN KEY (EmpleadoId) REFERENCES dbo.Empleados(Id)
);
GO

-- ============================================================
-- TABLA: HistorialDesvinculaciones
-- ============================================================
CREATE TABLE dbo.HistorialDesvinculaciones (
    Id                      INT             IDENTITY(1,1)   NOT NULL,
    EmpleadoId              INT                             NOT NULL,
    MotivoRetiro            NVARCHAR(500)                   NOT NULL,
    FechaDesvinculacion     DATE                            NOT NULL,
    RegistradoPor           INT                             NOT NULL,
    FechaCreacion           DATETIME2(0)                    NOT NULL  CONSTRAINT DF_HistDes_FechaC DEFAULT GETUTCDATE(),

    CONSTRAINT PK_HistorialDesvinculaciones         PRIMARY KEY (Id),
    CONSTRAINT FK_HistorialDesvinc_Empleado         FOREIGN KEY (EmpleadoId)    REFERENCES dbo.Empleados(Id),
    CONSTRAINT FK_HistorialDesvinc_RegistradoPor    FOREIGN KEY (RegistradoPor) REFERENCES dbo.Usuarios(Id)
);
GO

-- ============================================================
-- TABLA: AsignacionesTurno
-- ============================================================
CREATE TABLE dbo.AsignacionesTurno (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    EmpleadoId          INT                             NOT NULL,
    PlantillaTurnoId    INT                             NOT NULL,
    FechaVigencia       DATE                            NOT NULL,
    ProgramadoPor       INT                             NOT NULL,
    FechaCreacion       DATETIME2(0)                    NOT NULL  CONSTRAINT DF_AsigTurno_FechaC DEFAULT GETUTCDATE(),

    CONSTRAINT PK_AsignacionesTurno             PRIMARY KEY (Id),
    CONSTRAINT FK_AsignacionesTurno_Empleado    FOREIGN KEY (EmpleadoId)        REFERENCES dbo.Empleados(Id),
    CONSTRAINT FK_AsignacionesTurno_Plantilla   FOREIGN KEY (PlantillaTurnoId)  REFERENCES dbo.PlantillasTurno(Id),
    CONSTRAINT FK_AsignacionesTurno_Usuario     FOREIGN KEY (ProgramadoPor)     REFERENCES dbo.Usuarios(Id)
);
GO

CREATE NONCLUSTERED INDEX IX_AsignacionesTurno_EmpleadoId
    ON dbo.AsignacionesTurno (EmpleadoId, FechaVigencia DESC);
GO

-- ============================================================
-- TABLA: EventosLaborales
-- ============================================================
CREATE TABLE dbo.EventosLaborales (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    EmpleadoId          INT                             NOT NULL,
    TipoEvento          NVARCHAR(30)                    NOT NULL,
    FechaInicio         DATE                            NOT NULL,
    FechaFin            DATE                            NOT NULL,
    Estado              NVARCHAR(20)                    NOT NULL  CONSTRAINT DF_Eventos_Estado DEFAULT 'Activo',
    -- Campos específicos por tipo
    TipoIncapacidad     NVARCHAR(50)                    NULL,   -- solo Incapacidad
    EntidadExpide       NVARCHAR(200)                   NULL,   -- solo Incapacidad
    Descripcion         NVARCHAR(500)                   NULL,   -- Permiso / justificación
    AutorizadoPor       NVARCHAR(200)                   NOT NULL,
    MotivoAnulacion     NVARCHAR(300)                   NULL,
    -- Adjunto
    RutaDocumento       NVARCHAR(500)                   NULL,
    NombreDocumento     NVARCHAR(200)                   NULL,
    -- Auditoría
    CreadoPor           INT                             NOT NULL,
    FechaCreacion       DATETIME2(0)                    NOT NULL  CONSTRAINT DF_Eventos_FechaC DEFAULT GETUTCDATE(),
    FechaModificacion   DATETIME2(0)                    NULL,
    AnuladoPor          INT                             NULL,

    CONSTRAINT PK_EventosLaborales              PRIMARY KEY (Id),
    CONSTRAINT FK_EventosLaborales_Empleado     FOREIGN KEY (EmpleadoId)  REFERENCES dbo.Empleados(Id),
    CONSTRAINT FK_EventosLaborales_CreadoPor    FOREIGN KEY (CreadoPor)   REFERENCES dbo.Usuarios(Id),
    CONSTRAINT FK_EventosLaborales_AnuladoPor   FOREIGN KEY (AnuladoPor)  REFERENCES dbo.Usuarios(Id),
    CONSTRAINT CK_Eventos_TipoEvento            CHECK       (TipoEvento IN ('Vacaciones','Incapacidad','Permiso')),
    CONSTRAINT CK_Eventos_Estado                CHECK       (Estado IN ('Activo','Finalizado','Anulado')),
    CONSTRAINT CK_Eventos_Fechas                CHECK       (FechaFin >= FechaInicio),
    CONSTRAINT CK_Eventos_TipoIncap             CHECK       (
        TipoIncapacidad IS NULL OR
        TipoIncapacidad IN ('EnfermedadGeneral','AccidenteTrabajo','EnfermedadLaboral','MaternidadPaternidad')
    )
);
GO

CREATE NONCLUSTERED INDEX IX_EventosLaborales_EmpleadoId_Estado
    ON dbo.EventosLaborales (EmpleadoId, Estado)
    INCLUDE (FechaInicio, FechaFin, TipoEvento);
GO

CREATE NONCLUSTERED INDEX IX_EventosLaborales_Fechas
    ON dbo.EventosLaborales (FechaInicio, FechaFin, Estado);
GO

-- ============================================================
-- TABLA: HorasExtras
-- ============================================================
CREATE TABLE dbo.HorasExtras (
    Id                      INT             IDENTITY(1,1)   NOT NULL,
    EmpleadoId              INT                             NOT NULL,
    FechaTrabajada          DATE                            NOT NULL,
    CantidadHoras           DECIMAL(5,1)                    NOT NULL,
    Motivo                  NVARCHAR(500)                   NOT NULL,
    Estado                  NVARCHAR(20)                    NOT NULL  CONSTRAINT DF_HorasExtras_Estado DEFAULT 'Pendiente',
    -- Aprobación / Rechazo
    AprobadoRechazadoPor    INT                             NULL,
    FechaAprobacion         DATETIME2(0)                    NULL,
    MotivoRechazo           NVARCHAR(300)                   NULL,
    -- Auditoría
    CreadoPor               INT                             NOT NULL,
    FechaCreacion           DATETIME2(0)                    NOT NULL  CONSTRAINT DF_HorasExtras_FechaC DEFAULT GETUTCDATE(),

    CONSTRAINT PK_HorasExtras                   PRIMARY KEY (Id),
    CONSTRAINT FK_HorasExtras_Empleado          FOREIGN KEY (EmpleadoId)            REFERENCES dbo.Empleados(Id),
    CONSTRAINT FK_HorasExtras_AprobadoPor       FOREIGN KEY (AprobadoRechazadoPor)  REFERENCES dbo.Usuarios(Id),
    CONSTRAINT FK_HorasExtras_CreadoPor         FOREIGN KEY (CreadoPor)             REFERENCES dbo.Usuarios(Id),
    CONSTRAINT CK_HorasExtras_Estado            CHECK       (Estado IN ('Pendiente','Aprobado','Rechazado')),
    CONSTRAINT CK_HorasExtras_Cantidad          CHECK       (CantidadHoras > 0 AND CantidadHoras <= 24)
);
GO

CREATE NONCLUSTERED INDEX IX_HorasExtras_EmpleadoId_Estado
    ON dbo.HorasExtras (EmpleadoId, Estado)
    INCLUDE (FechaTrabajada, CantidadHoras);
GO
```
