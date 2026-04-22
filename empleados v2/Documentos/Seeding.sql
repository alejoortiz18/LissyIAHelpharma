-- ============================================================
-- SEEDING — Sistema GestionPersonal
-- Base de datos: GestionPersonal (LocalDB)
-- Contraseña temporal de todos los usuarios: Admin2026
--   Hash/Salt generado con PBKDF2/SHA256 (.NET PasswordHelper)
--   Iteraciones: 10000 | Hash: 32 bytes | Salt: 16 bytes
-- Jerarquía:
--   Carlos Rodríguez  ← Jefe
--   ├── Laura Sánchez          ← Regente 1
--   │   ├── Andrés Torres      ← AuxiliarRegente
--   │   ├── Diana Vargas       ← Operario
--   │   └── Valentina Ospina   ← Operario (temporal - Adecco)
--   └── Hernán Castillo        ← Regente 2
--       ├── Sebastián Moreno   ← Operario
--       ├── Natalia Bermúdez   ← Operario
--       └── Paula Quintero     ← Operario (temporal - ManpowerGroup)
-- ============================================================

USE GestionPersonal;
GO

-- ============================================================
-- Limpieza ordenada (respetando FKs) — solo ejecutar si se
-- desea reiniciar el seeding desde cero
-- ============================================================
-- DELETE FROM dbo.HorasExtras;
-- DELETE FROM dbo.EventosLaborales;
-- DELETE FROM dbo.AsignacionesTurno;
-- DELETE FROM dbo.HistorialDesvinculaciones;
-- DELETE FROM dbo.ContactosEmergencia;
-- DELETE FROM dbo.Empleados;
-- DELETE FROM dbo.TokensRecuperacion;
-- DELETE FROM dbo.Usuarios;
-- DELETE FROM dbo.PlantillasTurnoDetalle;
-- DELETE FROM dbo.PlantillasTurno;
-- DELETE FROM dbo.EmpresasTemporales;
-- DELETE FROM dbo.Cargos;
-- DELETE FROM dbo.Sedes;
-- GO

-- ============================================================
-- 1. SEDE
-- ============================================================
INSERT INTO dbo.Sedes (Nombre, Ciudad, Direccion, Estado, FechaCreacion)
VALUES (N'Sede Medellín', N'Medellín', N'Cll 50 #80-50', N'Activa', GETUTCDATE());

DECLARE @SedeId INT = SCOPE_IDENTITY();

-- ============================================================
-- 2. CARGOS (del prototipo)
-- ============================================================
INSERT INTO dbo.Cargos (Nombre, Estado, FechaCreacion)
VALUES
    (N'Jefe de Sede',           N'Activo', GETUTCDATE()),
    (N'Farmacéutico Regente',   N'Activo', GETUTCDATE()),
    (N'Auxiliar de Farmacia',   N'Activo', GETUTCDATE()),
    (N'Auxiliar Administrativo',N'Activo', GETUTCDATE()),
    (N'Cajero(a)',              N'Activo', GETUTCDATE()),
    (N'Asesor(a) Comercial',    N'Activo', GETUTCDATE()),
    (N'Mensajero',              N'Activo', GETUTCDATE()),
    (N'Coordinador de Sede',    N'Activo', GETUTCDATE());

DECLARE @CargoJefe          INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Jefe de Sede');
DECLARE @CargoRegente       INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Farmacéutico Regente');
DECLARE @CargoAuxiliar      INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Auxiliar de Farmacia');
DECLARE @CargoAdministrativo INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Auxiliar Administrativo');
DECLARE @CargoCajero        INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Cajero(a)');
DECLARE @CargoAsesor        INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Asesor(a) Comercial');
DECLARE @CargoMensajero     INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Mensajero');
DECLARE @CargoCoordi        INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Coordinador de Sede');

-- ============================================================
-- 3. EMPRESAS TEMPORALES
-- ============================================================
INSERT INTO dbo.EmpresasTemporales (Nombre, Estado, FechaCreacion)
VALUES
    (N'Adecco Colombia S.A.',    N'Activa', GETUTCDATE()),
    (N'ManpowerGroup Colombia',  N'Activa', GETUTCDATE());

DECLARE @EmpAdecco      INT = (SELECT Id FROM dbo.EmpresasTemporales WHERE Nombre = N'Adecco Colombia S.A.');
DECLARE @EmpManpower    INT = (SELECT Id FROM dbo.EmpresasTemporales WHERE Nombre = N'ManpowerGroup Colombia');

-- ============================================================
-- 4. PLANTILLA DE TURNO (estándar lunes-viernes)
-- ============================================================
INSERT INTO dbo.PlantillasTurno (Nombre, Estado, FechaCreacion)
VALUES (N'Turno Estándar Lunes-Viernes', N'Activa', GETUTCDATE());

DECLARE @PlantillaId INT = SCOPE_IDENTITY();

INSERT INTO dbo.PlantillasTurnoDetalle (PlantillaTurnoId, DiaSemana, HoraEntrada, HoraSalida)
VALUES
    (@PlantillaId, 1, '08:00', '17:00'),  -- Lunes
    (@PlantillaId, 2, '08:00', '17:00'),  -- Martes
    (@PlantillaId, 3, '08:00', '17:00'),  -- Miércoles
    (@PlantillaId, 4, '08:00', '17:00'),  -- Jueves
    (@PlantillaId, 5, '08:00', '17:00'),  -- Viernes
    (@PlantillaId, 6, NULL,    NULL),      -- Sábado (no labora)
    (@PlantillaId, 7, NULL,    NULL);      -- Domingo (no labora)

-- ============================================================
-- 5. USUARIOS (cuentas de acceso al sistema)
--    Contraseña: Admin2026  |  DebeCambiarPassword = 1
--    Hash/Salt: PBKDF2/SHA256 — generado con PasswordHelper.cs
--    Iteraciones: 10000 | Hash: 32 bytes | Salt: 16 bytes
-- ============================================================
DECLARE @PwdHash VARBINARY(256) = 0xC678F46EA40B0B419C75AA263AD9D2BDA049A9CF38AD4383D009407D51660AFB;
DECLARE @PwdSalt VARBINARY(256) = 0xE9119DF914288643380C5EB9CD4404CD;

-- 1. Jefe
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'carlos.rodriguez@yopmail.com', @PwdHash, @PwdSalt, N'Jefe', @SedeId, 1, N'Activo', GETUTCDATE());
DECLARE @UsuJefe INT = SCOPE_IDENTITY();

-- 2. Regente 1
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'laura.sanchez@yopmail.com', @PwdHash, @PwdSalt, N'Regente', @SedeId, 1, N'Activo', GETUTCDATE());
DECLARE @UsuRegente1 INT = SCOPE_IDENTITY();

-- 3. Regente 2
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'hernan.castillo@yopmail.com', @PwdHash, @PwdSalt, N'Regente', @SedeId, 1, N'Activo', GETUTCDATE());
DECLARE @UsuRegente2 INT = SCOPE_IDENTITY();

-- 4. AuxiliarRegente
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'andres.torres@yopmail.com', @PwdHash, @PwdSalt, N'AuxiliarRegente', @SedeId, 1, N'Activo', GETUTCDATE());
DECLARE @UsuAuxiliar INT = SCOPE_IDENTITY();

-- 5-9. Operarios
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'diana.vargas@yopmail.com',     @PwdHash, @PwdSalt, N'Operario', @SedeId, 1, N'Activo', GETUTCDATE());
DECLARE @UsuOp1 INT = SCOPE_IDENTITY();

INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'valentina.ospina@yopmail.com', @PwdHash, @PwdSalt, N'Operario', @SedeId, 1, N'Activo', GETUTCDATE());
DECLARE @UsuOp2 INT = SCOPE_IDENTITY();

INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'sebastian.moreno@yopmail.com', @PwdHash, @PwdSalt, N'Operario', @SedeId, 1, N'Activo', GETUTCDATE());
DECLARE @UsuOp3 INT = SCOPE_IDENTITY();

INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'natalia.bermudez@yopmail.com', @PwdHash, @PwdSalt, N'Operario', @SedeId, 1, N'Activo', GETUTCDATE());
DECLARE @UsuOp4 INT = SCOPE_IDENTITY();

INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'paula.quintero@yopmail.com',   @PwdHash, @PwdSalt, N'Operario', @SedeId, 1, N'Activo', GETUTCDATE());
DECLARE @UsuOp5 INT = SCOPE_IDENTITY();

-- ============================================================
-- 6. EMPLEADOS
--    Orden: primero Jefe (sin JefeInmediato), luego el resto
-- ============================================================

-- 1. Jefe — Carlos Rodríguez
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Carlos Alberto Rodríguez Mora', N'10234567', '1985-03-14', N'3104567890', N'carlos.rodriguez@yopmail.com',
    N'Cra 15 #45-32', N'Medellín', N'Antioquia', N'Profesional', N'Sura EPS', N'Sura ARL',
    @SedeId, @CargoJefe, @UsuJefe, NULL,
    N'Directo', '2019-01-15', NULL, NULL, NULL,
    N'Activo', 30.0, GETUTCDATE(), @UsuJefe);
DECLARE @EmpJefe INT = SCOPE_IDENTITY();

-- Contacto de emergencia — Carlos
INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
VALUES (@EmpJefe, N'María Rodríguez', N'3115678901');

-- 2. Regente 1 — Laura Sánchez
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Laura Patricia Sánchez Gómez', N'20345678', '1990-07-22', N'3123456789', N'laura.sanchez@yopmail.com',
    N'Cll 100 #18-50', N'Medellín', N'Antioquia', N'Profesional', N'Nueva EPS', N'Bolívar ARL',
    @SedeId, @CargoRegente, @UsuRegente1, @EmpJefe,
    N'Directo', '2020-03-01', NULL, NULL, NULL,
    N'Activo', 15.0, GETUTCDATE(), @UsuJefe);
DECLARE @EmpRegente1 INT = SCOPE_IDENTITY();

INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
VALUES (@EmpRegente1, N'Juan Sánchez', N'3134567890');

-- 3. Regente 2 — Hernán Castillo
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Hernán David Castillo Mejía', N'30456789', '1988-09-30', N'3156789012', N'hernan.castillo@yopmail.com',
    N'Av Caracas #32-10', N'Medellín', N'Antioquia', N'Profesional', N'Compensar', N'Sura ARL',
    @SedeId, @CargoRegente, @UsuRegente2, @EmpJefe,
    N'Directo', '2018-06-15', NULL, NULL, NULL,
    N'Activo', 20.0, GETUTCDATE(), @UsuJefe);
DECLARE @EmpRegente2 INT = SCOPE_IDENTITY();

INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
VALUES (@EmpRegente2, N'Rosa Castillo', N'3167890123');

-- 4. AuxiliarRegente — Andrés Torres (bajo Regente 1)
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Andrés Felipe Torres Ruiz', N'40567890', '1995-11-05', N'3178901234', N'andres.torres@yopmail.com',
    N'Cll 50 Sur #43-25', N'Medellín', N'Antioquia', N'Técnico', N'Sura EPS', N'Sura ARL',
    @SedeId, @CargoAuxiliar, @UsuAuxiliar, @EmpRegente1,
    N'Directo', '2022-04-01', NULL, NULL, NULL,
    N'Activo', 0.0, GETUTCDATE(), @UsuJefe);
DECLARE @EmpAuxiliar INT = SCOPE_IDENTITY();

INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
VALUES (@EmpAuxiliar, N'Clara Torres', N'3189012345');

-- 5. Operario — Diana Vargas (bajo Regente 1)
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Diana Marcela Vargas López', N'50678901', '1992-06-18', N'3190123456', N'diana.vargas@yopmail.com',
    N'Cra 50 #80-25', N'Medellín', N'Antioquia', N'Bachillerato', N'Famisanar', N'Positiva',
    @SedeId, @CargoCajero, @UsuOp1, @EmpRegente1,
    N'Directo', '2021-07-01', NULL, NULL, NULL,
    N'Activo', 10.0, GETUTCDATE(), @UsuJefe);

INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
VALUES (SCOPE_IDENTITY(), N'Pedro Vargas', N'3201234567');

-- 6. Operario — Valentina Ospina (bajo Regente 1, temporal Adecco)
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Valentina Ospina Restrepo', N'60789012', '1993-04-12', N'3212345678', N'valentina.ospina@yopmail.com',
    N'Cll 10 Sur #43-25', N'Medellín', N'Antioquia', N'Tecnológico', N'Comfama', N'AXA Colpatria',
    @SedeId, @CargoAsesor, @UsuOp2, @EmpRegente1,
    N'Temporal', '2025-01-01', @EmpAdecco, '2025-01-01', '2025-12-31',
    N'Activo', 0.0, GETUTCDATE(), @UsuJefe);

INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
VALUES (SCOPE_IDENTITY(), N'Luis Ospina', N'3223456789');

-- 7. Operario — Sebastián Moreno (bajo Regente 2)
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Sebastián Moreno Parra', N'70890123', '1998-12-03', N'3234567890', N'sebastian.moreno@yopmail.com',
    N'Cra 28 #12-60', N'Medellín', N'Antioquia', N'Bachillerato', N'Sura EPS', N'Positiva',
    @SedeId, @CargoMensajero, @UsuOp3, @EmpRegente2,
    N'Directo', '2023-03-01', NULL, NULL, NULL,
    N'Activo', 5.0, GETUTCDATE(), @UsuJefe);

INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
VALUES (SCOPE_IDENTITY(), N'Ana Moreno', N'3245678901');

-- 8. Operario — Natalia Bermúdez (bajo Regente 2)
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Natalia Bermúdez Salazar', N'80901234', '1994-08-07', N'3256789012', N'natalia.bermudez@yopmail.com',
    N'Cll 9 #43B-10', N'Medellín', N'Antioquia', N'Profesional', N'Coomeva', N'Bolívar ARL',
    @SedeId, @CargoAdministrativo, @UsuOp4, @EmpRegente2,
    N'Directo', '2021-02-15', NULL, NULL, NULL,
    N'Activo', 8.0, GETUTCDATE(), @UsuJefe);

INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
VALUES (SCOPE_IDENTITY(), N'Jorge Bermúdez', N'3267890123');

-- 9. Operario — Paula Quintero (bajo Regente 2, temporal ManpowerGroup)
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Paula Andrea Quintero Ríos', N'91012345', '1997-05-20', N'3278901234', N'paula.quintero@yopmail.com',
    N'Cra 70 #34-15', N'Medellín', N'Antioquia', N'Técnico', N'Comfama', N'Sura ARL',
    @SedeId, @CargoCajero, @UsuOp5, @EmpRegente2,
    N'Temporal', '2025-03-01', @EmpManpower, '2025-03-01', '2025-12-31',
    N'Activo', 0.0, GETUTCDATE(), @UsuJefe);

INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
VALUES (SCOPE_IDENTITY(), N'Ricardo Quintero', N'3289012345');

-- ============================================================
-- 7. ASIGNACIÓN DE TURNO ESTÁNDAR A TODOS LOS EMPLEADOS
-- ============================================================
INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
SELECT e.Id, @PlantillaId, '2025-01-01', @UsuJefe, GETUTCDATE()
FROM dbo.Empleados e
WHERE e.SedeId = @SedeId AND e.Estado = N'Activo';

-- ============================================================
-- VERIFICACIÓN FINAL
-- ============================================================
SELECT 'Sedes'             AS Tabla, COUNT(*) AS Total FROM dbo.Sedes
UNION ALL
SELECT 'Cargos',            COUNT(*) FROM dbo.Cargos
UNION ALL
SELECT 'EmpresasTemporales',COUNT(*) FROM dbo.EmpresasTemporales
UNION ALL
SELECT 'PlantillasTurno',   COUNT(*) FROM dbo.PlantillasTurno
UNION ALL
SELECT 'Usuarios',          COUNT(*) FROM dbo.Usuarios
UNION ALL
SELECT 'Empleados',         COUNT(*) FROM dbo.Empleados
UNION ALL
SELECT 'ContactosEmergencia',COUNT(*) FROM dbo.ContactosEmergencia
UNION ALL
SELECT 'AsignacionesTurno', COUNT(*) FROM dbo.AsignacionesTurno;
GO
