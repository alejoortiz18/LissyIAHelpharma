-- ============================================================
-- Roles del sistema y permisos de plataforma
-- Ejecutar en GestionPersonal (producción / local)
-- ============================================================
USE GestionPersonal;
GO

IF OBJECT_ID(N'dbo.RolesSistemaPermisos', N'U') IS NOT NULL
    DROP TABLE dbo.RolesSistemaPermisos;
GO
IF OBJECT_ID(N'dbo.RolesSistema', N'U') IS NOT NULL
    DROP TABLE dbo.RolesSistema;
GO
IF OBJECT_ID(N'dbo.PermisosPlataforma', N'U') IS NOT NULL
    DROP TABLE dbo.PermisosPlataforma;
GO

CREATE TABLE dbo.PermisosPlataforma (
    Id              INT             IDENTITY(1,1)   NOT NULL,
    Codigo          NVARCHAR(80)                    NOT NULL,
    Modulo          NVARCHAR(50)                    NOT NULL,
    Nombre          NVARCHAR(200)                   NOT NULL,
    Descripcion     NVARCHAR(500)                   NULL,
    Orden           INT                             NOT NULL
        CONSTRAINT DF_Permisos_Orden DEFAULT 0,

    CONSTRAINT PK_PermisosPlataforma          PRIMARY KEY (Id),
    CONSTRAINT UX_PermisosPlataforma_Codigo   UNIQUE (Codigo)
);
GO

CREATE TABLE dbo.RolesSistema (
    Id                  INT             IDENTITY(1,1)   NOT NULL,
    Codigo              NVARCHAR(50)                    NOT NULL,
    Nombre              NVARCHAR(200)                   NOT NULL,
    Descripcion         NVARCHAR(500)                   NULL,
    EsRolSistema        BIT                             NOT NULL
        CONSTRAINT DF_RolesSistema_EsSistema DEFAULT 0,
    Estado              NVARCHAR(20)                    NOT NULL
        CONSTRAINT DF_RolesSistema_Estado DEFAULT 'Activo',
    FechaCreacion       DATETIME2(0)                    NOT NULL
        CONSTRAINT DF_RolesSistema_FechaC DEFAULT GETUTCDATE(),
    FechaModificacion   DATETIME2(0)                    NULL,

    CONSTRAINT PK_RolesSistema            PRIMARY KEY (Id),
    CONSTRAINT UX_RolesSistema_Codigo     UNIQUE (Codigo),
    CONSTRAINT CK_RolesSistema_Estado   CHECK (Estado IN ('Activo', 'Inactivo'))
);
GO

CREATE TABLE dbo.RolesSistemaPermisos (
    RolSistemaId    INT NOT NULL,
    PermisoId       INT NOT NULL,

    CONSTRAINT PK_RolesSistemaPermisos PRIMARY KEY (RolSistemaId, PermisoId),
    CONSTRAINT FK_RSP_Rol FOREIGN KEY (RolSistemaId) REFERENCES dbo.RolesSistema (Id) ON DELETE CASCADE,
    CONSTRAINT FK_RSP_Permiso FOREIGN KEY (PermisoId) REFERENCES dbo.PermisosPlataforma (Id) ON DELETE CASCADE
);
GO

-- Catálogo de permisos
INSERT INTO dbo.PermisosPlataforma (Codigo, Modulo, Nombre, Descripcion, Orden) VALUES
(N'Dashboard.Ver', N'Dashboard', N'Ver dashboard', N'Acceso al panel principal con indicadores', 10),
(N'Empleados.VerListado', N'Empleados', N'Ver listado de empleados', N'Listado y búsqueda de personal', 20),
(N'Empleados.VerPerfilPropio', N'Empleados', N'Ver perfil propio', N'Solo el perfil del usuario autenticado', 21),
(N'Empleados.Crear', N'Empleados', N'Crear empleados', N'Alta de nuevos empleados y usuarios', 22),
(N'Empleados.Editar', N'Empleados', N'Editar empleados', N'Modificar datos de empleados', 23),
(N'Empleados.Desvincular', N'Empleados', N'Desvincular empleados', N'Proceso de desvinculación', 24),
(N'EventosLaborales.Ver', N'Eventos laborales', N'Ver eventos', N'Calendario y listado de novedades', 30),
(N'EventosLaborales.Crear', N'Eventos laborales', N'Crear eventos', N'Registrar permisos, incapacidades, etc.', 31),
(N'EventosLaborales.Editar', N'Eventos laborales', N'Editar eventos', N'Modificar eventos existentes', 32),
(N'EventosLaborales.Anular', N'Eventos laborales', N'Anular eventos', N'Anulación de eventos registrados', 33),
(N'Turnos.Ver', N'Turnos', N'Ver turnos', N'Consultar horarios y asignaciones', 40),
(N'Turnos.Asignar', N'Turnos', N'Asignar turnos', N'Asignar plantillas a empleados', 41),
(N'Turnos.Plantillas', N'Turnos', N'Gestionar plantillas', N'Crear y editar plantillas de turno', 42),
(N'HorasExtras.Ver', N'Horas extras', N'Ver horas extras', N'Consultar registros de horas extras', 50),
(N'HorasExtras.Crear', N'Horas extras', N'Crear horas extras', N'Registrar horas extras', 51),
(N'HorasExtras.Aprobar', N'Horas extras', N'Aprobar horas extras', N'Aprobar o rechazar solicitudes', 52),
(N'Solicitudes.Ver', N'Solicitudes', N'Ver solicitudes', N'Mis solicitudes (operario/direccionador)', 60),
(N'Solicitudes.Crear', N'Solicitudes', N'Crear solicitudes', N'Enviar solicitudes al área de gestión', 61),
(N'Catalogos.Ver', N'Catálogos', N'Ver catálogos', N'Sedes, cargos y empresas (Director/Admin)', 70),
(N'Catalogos.Editar', N'Catálogos', N'Editar catálogos', N'CRUD de catálogos operativos', 71),
(N'DatosMaestros.Gestionar', N'Datos maestros', N'Gestionar datos maestros', N'Sedes, cargos, empresas y roles (Lissy)', 80),
(N'RolesSistema.Gestionar', N'Roles del sistema', N'Gestionar roles y permisos', N'Definir qué puede hacer cada rol', 81);
GO

-- Roles predefinidos (código = valor en Usuarios.Rol)
INSERT INTO dbo.RolesSistema (Codigo, Nombre, Descripcion, EsRolSistema, Estado) VALUES
(N'Administrador',    N'Administrador',       N'Rol técnico con acceso amplio a la plataforma', 1, 'Activo'),
(N'Analista',        N'Analista',            N'Autoridad superior, visión multi-sede', 1, 'Activo'),
(N'DirectorTecnico', N'Director Técnico',    N'Jefe de área / supervisión técnica', 1, 'Activo'),
(N'Regente',         N'Regente',             N'Responsable de sede / farmacia', 1, 'Activo'),
(N'AuxiliarRegente', N'Auxiliar de Regente', N'Apoyo al regente en operación de sede', 1, 'Activo'),
(N'Operario',        N'Operario',            N'Personal operativo — perfil y solicitudes', 1, 'Activo'),
(N'Direccionador',   N'Direccionador',       N'Personal operativo con enfoque en dirección', 1, 'Activo');
GO

DECLARE @RolId INT;

-- Administrador: todos los permisos
SELECT @RolId = Id FROM dbo.RolesSistema WHERE Codigo = N'Administrador';
INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId)
SELECT @RolId, Id FROM dbo.PermisosPlataforma;

-- Analista: todos los permisos (autoridad superior operativa)
SELECT @RolId = Id FROM dbo.RolesSistema WHERE Codigo = N'Analista';
INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId)
SELECT @RolId, Id FROM dbo.PermisosPlataforma;

-- Director técnico
SELECT @RolId = Id FROM dbo.RolesSistema WHERE Codigo = N'DirectorTecnico';
INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId)
SELECT @RolId, Id FROM dbo.PermisosPlataforma
WHERE Codigo IN (
    N'Dashboard.Ver', N'Empleados.VerListado', N'Empleados.Crear', N'Empleados.Editar', N'Empleados.Desvincular',
    N'EventosLaborales.Ver', N'EventosLaborales.Crear', N'EventosLaborales.Editar', N'EventosLaborales.Anular',
    N'Turnos.Ver', N'Turnos.Asignar', N'Turnos.Plantillas',
    N'HorasExtras.Ver', N'HorasExtras.Crear', N'HorasExtras.Aprobar',
    N'Catalogos.Ver', N'Catalogos.Editar'
);

-- Regente
SELECT @RolId = Id FROM dbo.RolesSistema WHERE Codigo = N'Regente';
INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId)
SELECT @RolId, Id FROM dbo.PermisosPlataforma
WHERE Codigo IN (
    N'Dashboard.Ver', N'Empleados.VerListado', N'Empleados.Editar',
    N'EventosLaborales.Ver', N'EventosLaborales.Crear', N'EventosLaborales.Editar',
    N'Turnos.Ver', N'Turnos.Asignar',
    N'HorasExtras.Ver', N'HorasExtras.Crear'
);

-- Auxiliar regente
SELECT @RolId = Id FROM dbo.RolesSistema WHERE Codigo = N'AuxiliarRegente';
INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId)
SELECT @RolId, Id FROM dbo.PermisosPlataforma
WHERE Codigo IN (
    N'Dashboard.Ver', N'Empleados.VerListado', N'Empleados.Editar',
    N'EventosLaborales.Ver', N'EventosLaborales.Crear', N'EventosLaborales.Editar',
    N'Turnos.Ver', N'Turnos.Asignar',
    N'HorasExtras.Ver', N'HorasExtras.Crear'
);

-- Operario
SELECT @RolId = Id FROM dbo.RolesSistema WHERE Codigo = N'Operario';
INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId)
SELECT @RolId, Id FROM dbo.PermisosPlataforma
WHERE Codigo IN (
    N'Empleados.VerPerfilPropio', N'Solicitudes.Ver', N'Solicitudes.Crear',
    N'HorasExtras.Ver', N'HorasExtras.Crear'
);

-- Direccionador
SELECT @RolId = Id FROM dbo.RolesSistema WHERE Codigo = N'Direccionador';
INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId)
SELECT @RolId, Id FROM dbo.PermisosPlataforma
WHERE Codigo IN (
    N'Empleados.VerPerfilPropio', N'Solicitudes.Ver', N'Solicitudes.Crear',
    N'HorasExtras.Ver', N'HorasExtras.Crear'
);
GO
