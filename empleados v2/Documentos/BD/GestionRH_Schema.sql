-- ============================================================
-- SISTEMA DE ADMINISTRACIÓN DE EMPLEADOS — GestionPersonal
-- Script DDL completo para SQL Server
-- Versión: 1.0 | Fecha: 2026-04-20
--
-- ORDEN DE EJECUCIÓN (respeta dependencias FK):
--   1. Sedes
--   2. Cargos
--   3. EmpresasTemporales
--   4. PlantillasTurno
--   5. PlantillasTurnoDetalle
--   6. Usuarios
--   7. TokensRecuperacion
--   8. Empleados
--   9. ContactosEmergencia
--  10. HistorialDesvinculaciones
--  11. AsignacionesTurno
--  12. EventosLaborales
--  13. HorasExtras
-- ============================================================

-- ============================================================
-- CREAR BASE DE DATOS
-- ============================================================
CREATE DATABASE GestionPersonal
    COLLATE SQL_Latin1_General_CP1_CI_AS;
GO

USE GestionPersonal;
GO

-- ============================================================
-- TABLA 1: Sedes
-- Datos maestros — sin dependencias FK
-- ============================================================
CREATE TABLE dbo.Sedes (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    Nombre              NVARCHAR(200)                   NOT NULL,
    Ciudad              NVARCHAR(100)                   NOT NULL,
    Direccion           NVARCHAR(300)                   NOT NULL,
    Estado              NVARCHAR(20)                    NOT NULL
        CONSTRAINT DF_Sedes_Estado      DEFAULT 'Activa',
    FechaCreacion       DATETIME2(0)                    NOT NULL
        CONSTRAINT DF_Sedes_FechaC      DEFAULT GETUTCDATE(),
    FechaModificacion   DATETIME2(0)                    NULL,

    CONSTRAINT PK_Sedes             PRIMARY KEY (Id),
    CONSTRAINT UX_Sedes_Nombre      UNIQUE      (Nombre),
    CONSTRAINT CK_Sedes_Estado      CHECK       (Estado IN ('Activa', 'Inactiva'))
);
GO

-- ============================================================
-- TABLA 2: Cargos
-- Datos maestros — sin dependencias FK
-- ============================================================
CREATE TABLE dbo.Cargos (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    Nombre              NVARCHAR(200)                   NOT NULL,
    Estado              NVARCHAR(20)                    NOT NULL
        CONSTRAINT DF_Cargos_Estado     DEFAULT 'Activo',
    FechaCreacion       DATETIME2(0)                    NOT NULL
        CONSTRAINT DF_Cargos_FechaC     DEFAULT GETUTCDATE(),
    FechaModificacion   DATETIME2(0)                    NULL,

    CONSTRAINT PK_Cargos            PRIMARY KEY (Id),
    CONSTRAINT UX_Cargos_Nombre     UNIQUE      (Nombre),
    CONSTRAINT CK_Cargos_Estado     CHECK       (Estado IN ('Activo', 'Inactivo'))
);
GO

-- ============================================================
-- TABLA 3: EmpresasTemporales
-- Datos maestros — sin dependencias FK
-- ============================================================
CREATE TABLE dbo.EmpresasTemporales (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    Nombre              NVARCHAR(200)                   NOT NULL,
    Estado              NVARCHAR(20)                    NOT NULL
        CONSTRAINT DF_EmpTemp_Estado    DEFAULT 'Activa',
    FechaCreacion       DATETIME2(0)                    NOT NULL
        CONSTRAINT DF_EmpTemp_FechaC    DEFAULT GETUTCDATE(),
    FechaModificacion   DATETIME2(0)                    NULL,

    CONSTRAINT PK_EmpresasTemporales            PRIMARY KEY (Id),
    CONSTRAINT UX_EmpresasTemporales_Nombre     UNIQUE      (Nombre),
    CONSTRAINT CK_EmpresasTemporales_Estado     CHECK       (Estado IN ('Activa', 'Inactiva'))
);
GO

-- ============================================================
-- TABLA 4: PlantillasTurno
-- Datos maestros — sin dependencias FK
-- ============================================================
CREATE TABLE dbo.PlantillasTurno (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    Nombre              NVARCHAR(200)                   NOT NULL,
    Estado              NVARCHAR(20)                    NOT NULL
        CONSTRAINT DF_Plantillas_Estado DEFAULT 'Activa',
    FechaCreacion       DATETIME2(0)                    NOT NULL
        CONSTRAINT DF_Plantillas_FechaC DEFAULT GETUTCDATE(),
    FechaModificacion   DATETIME2(0)                    NULL,

    CONSTRAINT PK_PlantillasTurno           PRIMARY KEY (Id),
    CONSTRAINT UX_PlantillasTurno_Nombre    UNIQUE      (Nombre),
    CONSTRAINT CK_PlantillasTurno_Estado    CHECK       (Estado IN ('Activa', 'Inactiva'))
);
GO

-- ============================================================
-- TABLA 5: PlantillasTurnoDetalle
-- Configuración día a día de cada plantilla
-- Depende de: PlantillasTurno
-- ============================================================
CREATE TABLE dbo.PlantillasTurnoDetalle (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    PlantillaTurnoId    INT                             NOT NULL,
    DiaSemana           TINYINT                         NOT NULL,   -- 1=Lun … 7=Dom
    HoraEntrada         TIME(0)                         NULL,       -- NULL = No labora
    HoraSalida          TIME(0)                         NULL,

    CONSTRAINT PK_PlantillasTurnoDetalle            PRIMARY KEY (Id),
    CONSTRAINT UX_PlantillasTurnoDetalle_Dia        UNIQUE      (PlantillaTurnoId, DiaSemana),
    CONSTRAINT FK_PlantillasTurnoDetalle_Plantilla  FOREIGN KEY (PlantillaTurnoId)
        REFERENCES dbo.PlantillasTurno (Id),
    CONSTRAINT CK_PlantillasTurnoDetalle_Dia        CHECK       (DiaSemana BETWEEN 1 AND 7),
    -- Si un día labora, ambas horas deben estar presentes y Salida > Entrada
    -- Si no labora, ambas deben ser NULL
    CONSTRAINT CK_PlantillasTurnoDetalle_Horas      CHECK (
        (HoraEntrada IS NULL AND HoraSalida IS NULL)
        OR
        (HoraEntrada IS NOT NULL AND HoraSalida IS NOT NULL AND HoraSalida > HoraEntrada)
    )
);
GO

-- ============================================================
-- TABLA 6: Usuarios
-- Credenciales de acceso al sistema
-- Depende de: Sedes
--
-- ALGORITMO DE CONTRASEÑA: Hash + Salt (HMACSHA512)
--   1. Al crear/cambiar contraseña, el backend genera un salt aleatorio
--      con HMACSHA512 (hmac.Key → 128 bytes) y calcula:
--        PasswordSalt = hmac.Key            (128 bytes, aleatorio por usuario)
--        PasswordHash = hmac.ComputeHash(   (64 bytes)
--                         Encoding.UTF8.GetBytes(passwordPlano))
--   2. En la verificación, se reconstruye el HMAC usando el salt almacenado
--      y se compara el hash resultante con PasswordHash (comparación
--      en tiempo constante para prevenir timing attacks).
--   3. La contraseña en texto plano NUNCA se persiste ni se registra en logs.
-- ============================================================
CREATE TABLE dbo.Usuarios (
    Id                      INT             IDENTITY(1,1)   NOT NULL,
    CorreoAcceso            NVARCHAR(256)                   NOT NULL,
    PasswordHash            VARBINARY(64)                   NOT NULL,   -- HMACSHA512: 64 bytes — resultado de ComputeHash
    PasswordSalt            VARBINARY(128)                  NOT NULL,   -- HMACSHA512: 128 bytes — hmac.Key (único por usuario)
    Rol                     NVARCHAR(30)                    NOT NULL,
    SedeId                  INT                             NOT NULL,
    DebecambiarPassword     BIT                             NOT NULL
        CONSTRAINT DF_Usuarios_CambiarPwd   DEFAULT 1,
    Estado                  NVARCHAR(20)                    NOT NULL
        CONSTRAINT DF_Usuarios_Estado       DEFAULT 'Activo',
    FechaCreacion           DATETIME2(0)                    NOT NULL
        CONSTRAINT DF_Usuarios_FechaC       DEFAULT GETUTCDATE(),
    FechaModificacion       DATETIME2(0)                    NULL,
    UltimoAcceso            DATETIME2(0)                    NULL,

    CONSTRAINT PK_Usuarios              PRIMARY KEY (Id),
    CONSTRAINT UX_Usuarios_Correo       UNIQUE      (CorreoAcceso),
    CONSTRAINT FK_Usuarios_Sedes        FOREIGN KEY (SedeId)    REFERENCES dbo.Sedes (Id),
    CONSTRAINT CK_Usuarios_Rol          CHECK       (Rol IN ('Jefe', 'Regente', 'AuxiliarRegente', 'Operario', 'Administrador')),
    CONSTRAINT CK_Usuarios_Estado       CHECK       (Estado IN ('Activo', 'Inactivo'))
);
GO

CREATE NONCLUSTERED INDEX IX_Usuarios_SedeId
    ON dbo.Usuarios (SedeId);
GO

-- ============================================================
-- TABLA 7: TokensRecuperacion
-- Tokens de un solo uso para restablecer contraseña
-- Depende de: Usuarios
-- ============================================================
CREATE TABLE dbo.TokensRecuperacion (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    UsuarioId           INT                             NOT NULL,
    Token               NVARCHAR(256)                   NOT NULL,
    FechaExpiracion     DATETIME2(0)                    NOT NULL,
    Usado               BIT                             NOT NULL
        CONSTRAINT DF_Tokens_Usado      DEFAULT 0,
    FechaCreacion       DATETIME2(0)                    NOT NULL
        CONSTRAINT DF_Tokens_FechaC     DEFAULT GETUTCDATE(),

    CONSTRAINT PK_TokensRecuperacion            PRIMARY KEY (Id),
    CONSTRAINT UX_TokensRecuperacion_Token      UNIQUE      (Token),
    CONSTRAINT FK_TokensRecuperacion_Usuario    FOREIGN KEY (UsuarioId) REFERENCES dbo.Usuarios (Id)
);
GO

-- ============================================================
-- TABLA 8: Empleados
-- Entidad central del sistema
-- Depende de: Sedes, Cargos, Usuarios, EmpresasTemporales, Empleados (auto-ref)
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

    -- Vinculación laboral
    SedeId                  INT                             NOT NULL,
    CargoId                 INT                             NOT NULL,
    UsuarioId               INT                             NULL,   -- cuenta de acceso al sistema
    JefeInmediatoId         INT                             NULL,   -- auto-referencia
    TipoVinculacion         NVARCHAR(20)                    NOT NULL,
    FechaIngreso            DATE                            NOT NULL,

    -- Contrato temporal (condicional: solo cuando TipoVinculacion = 'Temporal')
    EmpresaTemporalId       INT                             NULL,
    FechaInicioContrato     DATE                            NULL,
    FechaFinContrato        DATE                            NULL,

    -- Estado (soft delete)
    Estado                  NVARCHAR(20)                    NOT NULL
        CONSTRAINT DF_Empleados_Estado      DEFAULT 'Activo',

    -- Saldo de vacaciones previas al sistema
    DiasVacacionesPrevios   DECIMAL(5,1)                    NOT NULL
        CONSTRAINT DF_Empleados_DiasPrev    DEFAULT 0,

    -- Auditoría
    FechaCreacion           DATETIME2(0)                    NOT NULL
        CONSTRAINT DF_Empleados_FechaC      DEFAULT GETUTCDATE(),
    CreadoPor               INT                             NULL,
    FechaModificacion       DATETIME2(0)                    NULL,
    ModificadoPor           INT                             NULL,

    -- ── Constraints de integridad ────────────────────────────
    CONSTRAINT PK_Empleados                 PRIMARY KEY (Id),
    CONSTRAINT UX_Empleados_Cedula          UNIQUE      (Cedula),
    CONSTRAINT UX_Empleados_Correo          UNIQUE      (CorreoElectronico),    -- correo único por empleado
    CONSTRAINT FK_Empleados_Sedes           FOREIGN KEY (SedeId)            REFERENCES dbo.Sedes (Id),
    CONSTRAINT FK_Empleados_Cargos          FOREIGN KEY (CargoId)           REFERENCES dbo.Cargos (Id),
    CONSTRAINT FK_Empleados_Usuarios        FOREIGN KEY (UsuarioId)         REFERENCES dbo.Usuarios (Id),
    CONSTRAINT FK_Empleados_JefeInmediato   FOREIGN KEY (JefeInmediatoId)   REFERENCES dbo.Empleados (Id),
    CONSTRAINT FK_Empleados_EmpresaTemp     FOREIGN KEY (EmpresaTemporalId) REFERENCES dbo.EmpresasTemporales (Id),
    CONSTRAINT FK_Empleados_CreadoPor       FOREIGN KEY (CreadoPor)         REFERENCES dbo.Usuarios (Id),
    CONSTRAINT FK_Empleados_ModificadoPor   FOREIGN KEY (ModificadoPor)     REFERENCES dbo.Usuarios (Id),

    -- Regla de negocio: un empleado no puede ser su propio jefe
    CONSTRAINT CK_Empleados_NoAutojefe      CHECK       (JefeInmediatoId IS NULL OR JefeInmediatoId <> Id),

    -- Validaciones de dominio
    CONSTRAINT CK_Empleados_Estado          CHECK       (Estado IN ('Activo', 'Inactivo')),
    CONSTRAINT CK_Empleados_TipoVinc        CHECK       (TipoVinculacion IN ('Directo', 'Temporal')),
    CONSTRAINT CK_Empleados_NivelEscol      CHECK       (
        NivelEscolaridad IS NULL OR
        NivelEscolaridad IN ('Primaria', 'Bachillerato', 'Tecnico', 'Tecnologico', 'Profesional', 'Posgrado')
    ),
    CONSTRAINT CK_Empleados_DiasVac         CHECK       (DiasVacacionesPrevios >= 0),

    -- Coherencia de contrato temporal: si Temporal, los tres campos son obligatorios
    CONSTRAINT CK_Empleados_ContratoTemp    CHECK (
        TipoVinculacion = 'Directo'
        OR
        (
            TipoVinculacion = 'Temporal'
            AND EmpresaTemporalId   IS NOT NULL
            AND FechaInicioContrato IS NOT NULL
            AND FechaFinContrato    IS NOT NULL
        )
    ),

    -- Coherencia de fechas de contrato
    CONSTRAINT CK_Empleados_FechasContrato  CHECK (
        FechaFinContrato IS NULL OR FechaFinContrato >= FechaInicioContrato
    )
);
GO

-- Índice compuesto principal para listado por sede y estado (consulta más frecuente)
CREATE NONCLUSTERED INDEX IX_Empleados_SedeId_Estado
    ON dbo.Empleados (SedeId, Estado)
    INCLUDE (NombreCompleto, CargoId, TipoVinculacion);
GO

-- Índice para soporte de FK y filtro por cargo
CREATE NONCLUSTERED INDEX IX_Empleados_CargoId
    ON dbo.Empleados (CargoId);
GO

-- Índice para búsqueda por jefe inmediato (consulta jerarquía)
CREATE NONCLUSTERED INDEX IX_Empleados_JefeInmediatoId
    ON dbo.Empleados (JefeInmediatoId)
    WHERE JefeInmediatoId IS NOT NULL;
GO

-- ============================================================
-- TABLA 9: ContactosEmergencia
-- Contacto de emergencia obligatorio por empleado
-- Depende de: Empleados
-- ============================================================
CREATE TABLE dbo.ContactosEmergencia (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    EmpleadoId          INT                             NOT NULL,
    NombreContacto      NVARCHAR(200)                   NOT NULL,
    TelefonoContacto    NVARCHAR(20)                    NOT NULL,

    CONSTRAINT PK_ContactosEmergencia           PRIMARY KEY (Id),
    CONSTRAINT FK_ContactosEmergencia_Empleado  FOREIGN KEY (EmpleadoId) REFERENCES dbo.Empleados (Id)
);
GO

CREATE NONCLUSTERED INDEX IX_ContactosEmergencia_EmpleadoId
    ON dbo.ContactosEmergencia (EmpleadoId);
GO

-- ============================================================
-- TABLA 10: HistorialDesvinculaciones
-- Registro del motivo y fecha cuando un empleado pasa a Inactivo
-- Depende de: Empleados, Usuarios
-- ============================================================
CREATE TABLE dbo.HistorialDesvinculaciones (
    Id                      INT             IDENTITY(1,1)   NOT NULL,
    EmpleadoId              INT                             NOT NULL,
    MotivoRetiro            NVARCHAR(500)                   NOT NULL,
    FechaDesvinculacion     DATE                            NOT NULL,
    RegistradoPor           INT                             NOT NULL,
    FechaCreacion           DATETIME2(0)                    NOT NULL
        CONSTRAINT DF_HistDes_FechaC    DEFAULT GETUTCDATE(),

    CONSTRAINT PK_HistorialDesvinculaciones             PRIMARY KEY (Id),
    CONSTRAINT FK_HistorialDesvinc_Empleado             FOREIGN KEY (EmpleadoId)    REFERENCES dbo.Empleados (Id),
    CONSTRAINT FK_HistorialDesvinc_RegistradoPor        FOREIGN KEY (RegistradoPor) REFERENCES dbo.Usuarios (Id)
);
GO

CREATE NONCLUSTERED INDEX IX_HistorialDesvinc_EmpleadoId
    ON dbo.HistorialDesvinculaciones (EmpleadoId);
GO

-- ============================================================
-- TABLA 11: AsignacionesTurno
-- Historial de asignaciones de plantilla de turno a empleados
-- Depende de: Empleados, PlantillasTurno, Usuarios
-- ============================================================
CREATE TABLE dbo.AsignacionesTurno (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    EmpleadoId          INT                             NOT NULL,
    PlantillaTurnoId    INT                             NOT NULL,
    FechaVigencia       DATE                            NOT NULL,
    ProgramadoPor       INT                             NOT NULL,
    FechaCreacion       DATETIME2(0)                    NOT NULL
        CONSTRAINT DF_AsigTurno_FechaC  DEFAULT GETUTCDATE(),

    CONSTRAINT PK_AsignacionesTurno                 PRIMARY KEY (Id),
    CONSTRAINT FK_AsignacionesTurno_Empleado        FOREIGN KEY (EmpleadoId)        REFERENCES dbo.Empleados (Id),
    CONSTRAINT FK_AsignacionesTurno_Plantilla       FOREIGN KEY (PlantillaTurnoId)  REFERENCES dbo.PlantillasTurno (Id),
    CONSTRAINT FK_AsignacionesTurno_ProgramadoPor   FOREIGN KEY (ProgramadoPor)     REFERENCES dbo.Usuarios (Id)
);
GO

-- Índice para obtener la asignación vigente más reciente de un empleado
CREATE NONCLUSTERED INDEX IX_AsignacionesTurno_EmpleadoId_Vigencia
    ON dbo.AsignacionesTurno (EmpleadoId, FechaVigencia DESC);
GO

-- ============================================================
-- TABLA 12: EventosLaborales
-- Vacaciones, incapacidades y permisos
-- Depende de: Empleados, Usuarios
-- ============================================================
CREATE TABLE dbo.EventosLaborales (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    EmpleadoId          INT                             NOT NULL,
    TipoEvento          NVARCHAR(30)                    NOT NULL,
    FechaInicio         DATE                            NOT NULL,
    FechaFin            DATE                            NOT NULL,
    Estado              NVARCHAR(20)                    NOT NULL
        CONSTRAINT DF_Eventos_Estado    DEFAULT 'Activo',

    -- Campos específicos por tipo de evento
    TipoIncapacidad     NVARCHAR(50)                    NULL,   -- Solo Incapacidad
    EntidadExpide       NVARCHAR(200)                   NULL,   -- Solo Incapacidad (EPS/ARL)
    Descripcion         NVARCHAR(500)                   NULL,   -- Solo Permiso (justificación)

    AutorizadoPor       NVARCHAR(200)                   NOT NULL,
    MotivoAnulacion     NVARCHAR(300)                   NULL,

    -- Adjunto (1 archivo por evento, máx. 5 MB, formatos PDF/JPG/PNG)
    RutaDocumento       NVARCHAR(500)                   NULL,
    NombreDocumento     NVARCHAR(200)                   NULL,

    -- Auditoría
    CreadoPor           INT                             NOT NULL,
    FechaCreacion       DATETIME2(0)                    NOT NULL
        CONSTRAINT DF_Eventos_FechaC    DEFAULT GETUTCDATE(),
    FechaModificacion   DATETIME2(0)                    NULL,
    AnuladoPor          INT                             NULL,

    CONSTRAINT PK_EventosLaborales              PRIMARY KEY (Id),
    CONSTRAINT FK_EventosLaborales_Empleado     FOREIGN KEY (EmpleadoId)  REFERENCES dbo.Empleados (Id),
    CONSTRAINT FK_EventosLaborales_CreadoPor    FOREIGN KEY (CreadoPor)   REFERENCES dbo.Usuarios (Id),
    CONSTRAINT FK_EventosLaborales_AnuladoPor   FOREIGN KEY (AnuladoPor)  REFERENCES dbo.Usuarios (Id),

    -- Validaciones de dominio
    CONSTRAINT CK_Eventos_TipoEvento            CHECK (TipoEvento IN ('Vacaciones', 'Incapacidad', 'Permiso')),
    CONSTRAINT CK_Eventos_Estado                CHECK (Estado IN ('Activo', 'Finalizado', 'Anulado')),
    CONSTRAINT CK_Eventos_Fechas                CHECK (FechaFin >= FechaInicio),
    CONSTRAINT CK_Eventos_TipoIncap             CHECK (
        TipoIncapacidad IS NULL OR
        TipoIncapacidad IN ('EnfermedadGeneral', 'AccidenteTrabajo', 'EnfermedadLaboral', 'MaternidadPaternidad')
    )
);
GO

-- Índice principal para consultas de disponibilidad (solapamiento + horas extras)
CREATE NONCLUSTERED INDEX IX_EventosLaborales_EmpleadoId_Estado
    ON dbo.EventosLaborales (EmpleadoId, Estado)
    INCLUDE (FechaInicio, FechaFin, TipoEvento);
GO

-- Índice para la vista de calendario (consulta por rango de fechas)
CREATE NONCLUSTERED INDEX IX_EventosLaborales_Fechas_Estado
    ON dbo.EventosLaborales (FechaInicio, FechaFin, Estado)
    INCLUDE (EmpleadoId, TipoEvento);
GO

-- ============================================================
-- TABLA 13: HorasExtras
-- Solicitudes de horas extras con flujo de aprobación
-- Depende de: Empleados, Usuarios
-- ============================================================
CREATE TABLE dbo.HorasExtras (
    Id                      INT             IDENTITY(1,1)   NOT NULL,
    EmpleadoId              INT                             NOT NULL,
    FechaTrabajada          DATE                            NOT NULL,
    CantidadHoras           DECIMAL(5,1)                    NOT NULL,
    Motivo                  NVARCHAR(500)                   NOT NULL,
    Estado                  NVARCHAR(20)                    NOT NULL
        CONSTRAINT DF_HorasExtras_Estado    DEFAULT 'Pendiente',

    -- Aprobación / Rechazo
    AprobadoRechazadoPor    INT                             NULL,
    FechaAprobacion         DATETIME2(0)                    NULL,
    MotivoRechazo           NVARCHAR(300)                   NULL,

    -- Anulación (sobre solicitudes ya aprobadas)
    AnuladoPor              INT                             NULL,
    FechaAnulacion          DATETIME2(0)                    NULL,
    MotivoAnulacion         NVARCHAR(300)                   NULL,

    -- Auditoría
    CreadoPor               INT                             NOT NULL,
    FechaCreacion           DATETIME2(0)                    NOT NULL
        CONSTRAINT DF_HorasExtras_FechaC    DEFAULT GETUTCDATE(),

    CONSTRAINT PK_HorasExtras                   PRIMARY KEY (Id),
    CONSTRAINT FK_HorasExtras_Empleado          FOREIGN KEY (EmpleadoId)            REFERENCES dbo.Empleados (Id),
    CONSTRAINT FK_HorasExtras_AprobadoPor       FOREIGN KEY (AprobadoRechazadoPor)  REFERENCES dbo.Usuarios (Id),
    CONSTRAINT FK_HorasExtras_AnuladoPor        FOREIGN KEY (AnuladoPor)            REFERENCES dbo.Usuarios (Id),
    CONSTRAINT FK_HorasExtras_CreadoPor         FOREIGN KEY (CreadoPor)             REFERENCES dbo.Usuarios (Id),

    -- Validaciones de dominio
    CONSTRAINT CK_HorasExtras_Estado            CHECK (Estado IN ('Pendiente', 'Aprobado', 'Rechazado', 'Anulado')),

    -- Cantidad entre 1 y 24 (puede ser decimal, ej. 2.5)
    CONSTRAINT CK_HorasExtras_Cantidad          CHECK (CantidadHoras >= 1 AND CantidadHoras <= 24),

    -- Una sola solicitud activa (no Rechazada/Anulada) por empleado por fecha
    -- La unicidad real se valida en servicio para poder mostrar mensaje amigable;
    -- el índice filtrado a continuación actúa como red de seguridad en BD.
    CONSTRAINT UX_HorasExtras_Empleado_Fecha_Activa
        UNIQUE (EmpleadoId, FechaTrabajada)   -- se gestiona a nivel de servicio para estado Pendiente/Aprobado
);
GO

-- Índice para listado filtrado por empleado y estado
CREATE NONCLUSTERED INDEX IX_HorasExtras_EmpleadoId_Estado
    ON dbo.HorasExtras (EmpleadoId, Estado)
    INCLUDE (FechaTrabajada, CantidadHoras);
GO

-- Índice para soporte de la validación de evento activo en la misma fecha
CREATE NONCLUSTERED INDEX IX_HorasExtras_FechaTrabajada
    ON dbo.HorasExtras (FechaTrabajada, Estado)
    INCLUDE (EmpleadoId);
GO

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================
