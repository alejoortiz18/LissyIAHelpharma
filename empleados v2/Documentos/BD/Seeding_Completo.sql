-- ============================================================
-- SEEDING COMPLETO — Sistema GestionPersonal
-- Base de datos: GestionPersonal (SQL Server / LocalDB)
-- Contraseña de todos los usuarios: Usuario1
--   Algoritmo: HMACSHA512 (PasswordHelper.cs)
--   PasswordHash: 64 bytes | PasswordSalt: 128 bytes
--
-- JERARQUÍA:
--   Carlos Rodríguez   → DirectorTecnico  (Sede Medellín, accede a todo)
--   Sofía Gómez         → Analista          (Sede Medellín, acceso total multi-sede)
--   Pedro Ramírez       → Direccionador     (Sede Bogotá, solo información propia)
--   ├── Laura Sánchez           → Regente  (Sede Medellín)
--   │   ├── Andrés Torres       → AuxiliarRegente
--   │   ├── Diana Vargas        → Operario
--   │   ├── Valentina Ospina    → Operario (temporal → vencimiento contrato, DESVINCULADA)
--   │   └── Jorge Herrera       → Operario (nuevo tras desvinculación de Valentina)
--   └── Hernán Castillo         → Regente  (Sede Bogotá)
--       ├── Sebastián Moreno    → Operario (despido con justa causa, DESVINCULADO)
--       ├── Natalia Bermúdez    → Operario
--       ├── Paula Quintero      → Operario (temporal ManpowerGroup → pasa a DIRECTO)
--       └── Camila Ríos         → Operario (nueva tras desvinculación de Sebastián)
--
-- DESVINCULADOS:
--   Valentina Ospina   → Vencimiento contrato temporal (Adecco) - no renovado
--   Sebastián Moreno   → Despido con justa causa
--   Ricardo Useche     → Renuncia voluntaria (empleado adicional de historial)
--
-- ÓRDEN DE EJECUCIÓN:
--   1. Limpieza (tablas dependientes primero)
--   2. Sedes (2)
--   3. Cargos
--   4. Empresas Temporales
--   5. Plantillas de Turno (3)
--   6. Usuarios (13 activos + 3 inactivos = 16)
--   7. Empleados (13 activos + 3 inactivos = 16)
--   8. Contactos de Emergencia
--   9. Historial Desvinculaciones (3)
--  10. Asignaciones de Turno (con historial de cambios)
--  11. Eventos Laborales (todos los tipos y estados)
--  12. Horas Extras (todos los estados del flujo)
--  13. Tokens de Recuperación (3 casos)
-- ============================================================
USE GestionPersonal;
GO
SET QUOTED_IDENTIFIER ON;
GO

-- ============================================================
-- 0. LIMPIEZA ORDENADA (respeta FKs)
-- ============================================================
DELETE FROM dbo.TokensRecuperacion;
DELETE FROM dbo.HorasExtras;
DELETE FROM dbo.EventosLaborales;
DELETE FROM dbo.AsignacionesTurno;
DELETE FROM dbo.HistorialDesvinculaciones;
DELETE FROM dbo.ContactosEmergencia;
DELETE FROM dbo.Empleados;
DELETE FROM dbo.Usuarios;
DELETE FROM dbo.PlantillasTurnoDetalle;
DELETE FROM dbo.PlantillasTurno;
DELETE FROM dbo.EmpresasTemporales;
DELETE FROM dbo.Cargos;
DELETE FROM dbo.Sedes;
GO

-- Reiniciar identidades
DBCC CHECKIDENT ('dbo.TokensRecuperacion',   RESEED, 0);
DBCC CHECKIDENT ('dbo.HorasExtras',          RESEED, 0);
DBCC CHECKIDENT ('dbo.EventosLaborales',     RESEED, 0);
DBCC CHECKIDENT ('dbo.AsignacionesTurno',    RESEED, 0);
DBCC CHECKIDENT ('dbo.HistorialDesvinculaciones', RESEED, 0);
DBCC CHECKIDENT ('dbo.ContactosEmergencia',  RESEED, 0);
DBCC CHECKIDENT ('dbo.Empleados',            RESEED, 0);
DBCC CHECKIDENT ('dbo.Usuarios',             RESEED, 0);
DBCC CHECKIDENT ('dbo.PlantillasTurnoDetalle', RESEED, 0);
DBCC CHECKIDENT ('dbo.PlantillasTurno',      RESEED, 0);
DBCC CHECKIDENT ('dbo.EmpresasTemporales',   RESEED, 0);
DBCC CHECKIDENT ('dbo.Cargos',               RESEED, 0);
DBCC CHECKIDENT ('dbo.Sedes',                RESEED, 0);
GO

-- ============================================================
-- 1. SEDES (2)
-- ============================================================
INSERT INTO dbo.Sedes (Nombre, Ciudad, Direccion, Estado, FechaCreacion)
VALUES
    (N'Sede Medellín', N'Medellín', N'Cll 50 #80-50, Centro Comercial Oviedo', N'Activa', '2018-01-01'),
    (N'Sede Bogotá',   N'Bogotá',   N'Cra 15 #93-47, Zona Rosa',               N'Activa', '2020-06-01');

DECLARE @SedeMed INT = (SELECT Id FROM dbo.Sedes WHERE Nombre = N'Sede Medellín');
DECLARE @SedeBog INT = (SELECT Id FROM dbo.Sedes WHERE Nombre = N'Sede Bogotá');

-- ============================================================
-- 2. CARGOS (6 cargos — jerarquía oficial)
-- ============================================================
INSERT INTO dbo.Cargos (Nombre, Estado, FechaCreacion)
VALUES
    (N'Director Técnico',                    N'Activo', '2018-01-01'),  -- CargoId 1 — RolUsuario.DirectorTecnico
    (N'Regente de Farmacia',                 N'Activo', '2018-01-01'),  -- CargoId 2 — RolUsuario.Regente
    (N'Auxiliar de Farmacia',                N'Activo', '2018-01-01'),  -- CargoId 3 — RolUsuario.Operario
    (N'Auxiliar Regente',                    N'Activo', '2018-01-01'),  -- CargoId 4 — RolUsuario.AuxiliarRegente
    (N'Analista de Servicios Farmacéuticos', N'Activo', '2018-01-01'),  -- CargoId 5 — RolUsuario.Analista
    (N'Direccionador',                       N'Activo', '2018-01-01');  -- CargoId 6 — RolUsuario.Direccionador

DECLARE @CargoDT       INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Director Técnico');
DECLARE @CargoReg      INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Regente de Farmacia');
DECLARE @CargoAux      INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Auxiliar de Farmacia');
DECLARE @CargoAuxReg   INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Auxiliar Regente');
DECLARE @CargoAnalista INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Analista de Servicios Farmacéuticos');
DECLARE @CargoDirecc   INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Direccionador');

-- ============================================================
-- 3. EMPRESAS TEMPORALES
-- ============================================================
INSERT INTO dbo.EmpresasTemporales (Nombre, Estado, FechaCreacion)
VALUES
    (N'Adecco Colombia S.A.',    N'Activa',   '2018-01-01'),
    (N'ManpowerGroup Colombia',  N'Activa',   '2018-01-01'),
    (N'Staffing Colombia S.A.S.',N'Inactiva', '2019-06-01');   -- empresa con la que ya no se trabaja

DECLARE @EmpAdecco   INT = (SELECT Id FROM dbo.EmpresasTemporales WHERE Nombre = N'Adecco Colombia S.A.');
DECLARE @EmpManpower INT = (SELECT Id FROM dbo.EmpresasTemporales WHERE Nombre = N'ManpowerGroup Colombia');

-- ============================================================
-- 4. PLANTILLAS DE TURNO (3)
-- ============================================================

-- 4a. Turno Estándar Lunes-Viernes
INSERT INTO dbo.PlantillasTurno (Nombre, Estado, FechaCreacion)
VALUES (N'Turno Estándar Lunes-Viernes', N'Activa', '2018-01-01');
DECLARE @PTEstandar INT = SCOPE_IDENTITY();

INSERT INTO dbo.PlantillasTurnoDetalle (PlantillaTurnoId, DiaSemana, HoraEntrada, HoraSalida)
VALUES
    (@PTEstandar, 1, '08:00', '17:00'),
    (@PTEstandar, 2, '08:00', '17:00'),
    (@PTEstandar, 3, '08:00', '17:00'),
    (@PTEstandar, 4, '08:00', '17:00'),
    (@PTEstandar, 5, '08:00', '17:00'),
    (@PTEstandar, 6, NULL,    NULL   ),
    (@PTEstandar, 7, NULL,    NULL   );

-- 4b. Turno Fin de Semana
INSERT INTO dbo.PlantillasTurno (Nombre, Estado, FechaCreacion)
VALUES (N'Turno Fin de Semana', N'Activa', '2020-01-01');
DECLARE @PTFinSem INT = SCOPE_IDENTITY();

INSERT INTO dbo.PlantillasTurnoDetalle (PlantillaTurnoId, DiaSemana, HoraEntrada, HoraSalida)
VALUES
    (@PTFinSem, 1, NULL,    NULL   ),
    (@PTFinSem, 2, NULL,    NULL   ),
    (@PTFinSem, 3, NULL,    NULL   ),
    (@PTFinSem, 4, NULL,    NULL   ),
    (@PTFinSem, 5, NULL,    NULL   ),
    (@PTFinSem, 6, '08:00', '17:00'),
    (@PTFinSem, 7, '08:00', '14:00');

-- 4c. Turno Rotativo 6x1
INSERT INTO dbo.PlantillasTurno (Nombre, Estado, FechaCreacion)
VALUES (N'Turno Rotativo 6x1', N'Activa', '2021-03-01');
DECLARE @PTRotativo INT = SCOPE_IDENTITY();

INSERT INTO dbo.PlantillasTurnoDetalle (PlantillaTurnoId, DiaSemana, HoraEntrada, HoraSalida)
VALUES
    (@PTRotativo, 1, '07:00', '15:00'),
    (@PTRotativo, 2, '07:00', '15:00'),
    (@PTRotativo, 3, '07:00', '15:00'),
    (@PTRotativo, 4, '07:00', '15:00'),
    (@PTRotativo, 5, '07:00', '15:00'),
    (@PTRotativo, 6, '07:00', '15:00'),
    (@PTRotativo, 7, NULL,    NULL   );

-- ============================================================
-- 5. USUARIOS
--    Contraseña: Usuario1 (PBKDF2/SHA256, 10000 iter)
--    PasswordHash: 32 bytes | PasswordSalt: 16 bytes
-- ============================================================
DECLARE @PwdHash VARBINARY(32) = 0x7DED37B4612147C18EBDFA1F6DEB4709EC9D511DA20641214F1F97612DF2CEAE;
DECLARE @PwdSalt VARBINARY(16) = 0xF2B483C7DAC61EC2CA7F1331C95D6800;

-- ── Usuarios activos ──────────────────────────────────────────

-- U01. Carlos Rodríguez — DirectorTecnico (ya completó cambio de contraseña)
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion, UltimoAcceso)
VALUES (N'carlos.rodriguez@yopmail.com', @PwdHash, @PwdSalt, N'DirectorTecnico', @SedeMed, 0, N'Activo', '2019-01-15', '2026-04-22');
DECLARE @UJefe INT = SCOPE_IDENTITY();

-- U02. Laura Sánchez — Regente Medellín
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion, UltimoAcceso)
VALUES (N'laura.sanchez@yopmail.com', @PwdHash, @PwdSalt, N'Regente', @SedeMed, 1, N'Activo', '2020-03-01', '2026-04-21');
DECLARE @UReg1 INT = SCOPE_IDENTITY();

-- U03. Hernán Castillo — Regente Bogotá
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion, UltimoAcceso)
VALUES (N'hernan.castillo@yopmail.com', @PwdHash, @PwdSalt, N'Regente', @SedeBog, 1, N'Activo', '2020-06-15', '2026-04-22');
DECLARE @UReg2 INT = SCOPE_IDENTITY();

-- U04. Andrés Torres — AuxiliarRegente (Medellín)
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'andres.torres@yopmail.com', @PwdHash, @PwdSalt, N'AuxiliarRegente', @SedeMed, 1, N'Activo', '2022-04-01');
DECLARE @UAux INT = SCOPE_IDENTITY();

-- U05. Diana Vargas — Operario (Medellín)
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'diana.vargas@yopmail.com', @PwdHash, @PwdSalt, N'Operario', @SedeMed, 1, N'Activo', '2021-07-01');
DECLARE @UDiana INT = SCOPE_IDENTITY();

-- U06. Jorge Herrera — Operario (Medellín, reemplaza a Valentina)
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'jorge.herrera@yopmail.com', @PwdHash, @PwdSalt, N'Operario', @SedeMed, 1, N'Activo', '2026-02-03');
DECLARE @UJorge INT = SCOPE_IDENTITY();

-- U07. Natalia Bermúdez — Operario (Bogotá)
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'natalia.bermudez@yopmail.com', @PwdHash, @PwdSalt, N'Operario', @SedeBog, 1, N'Activo', '2021-02-15');
DECLARE @UNata INT = SCOPE_IDENTITY();

-- U08. Paula Quintero — Operario (Bogotá, antes temporal ahora directo)
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'paula.quintero@yopmail.com', @PwdHash, @PwdSalt, N'Operario', @SedeBog, 1, N'Activo', '2025-03-01');
DECLARE @UPaula INT = SCOPE_IDENTITY();

-- U09. Camila Ríos — Operario (Bogotá, reemplaza a Sebastián)
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'camila.rios@yopmail.com', @PwdHash, @PwdSalt, N'Operario', @SedeBog, 1, N'Activo', '2025-07-01');
DECLARE @UCamila INT = SCOPE_IDENTITY();

-- ── Usuarios inactivos (empleados desvinculados) ──────────────

-- U10. Valentina Ospina — Inactivo (vencimiento contrato temporal)
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion, FechaModificacion)
VALUES (N'valentina.ospina@yopmail.com', @PwdHash, @PwdSalt, N'Operario', @SedeMed, 1, N'Inactivo', '2024-01-15', '2026-01-31');
DECLARE @UVale INT = SCOPE_IDENTITY();

-- U11. Sebastián Moreno — Inactivo (despido justa causa)
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion, FechaModificacion)
VALUES (N'sebastian.moreno@yopmail.com', @PwdHash, @PwdSalt, N'Operario', @SedeBog, 1, N'Inactivo', '2023-03-01', '2025-06-30');
DECLARE @USeba INT = SCOPE_IDENTITY();

-- U12. Ricardo Useche — Inactivo (renuncia voluntaria, empleado de historia)
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion, FechaModificacion)
VALUES (N'ricardo.useche@yopmail.com', @PwdHash, @PwdSalt, N'Operario', @SedeMed, 1, N'Inactivo', '2021-08-01', '2024-09-30');
DECLARE @URicardo INT = SCOPE_IDENTITY();

-- U13. Sofía Gómez — Analista (Medellín, acceso total multi-sede)
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'sofia.gomez@yopmail.com', @PwdHash, @PwdSalt, N'Analista', @SedeMed, 0, N'Activo', '2024-01-01');
DECLARE @UAnalista INT = SCOPE_IDENTITY();

-- U14. Pedro Ramírez — Direccionador (Bogotá, solo información propia)
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'pedro.ramirez@yopmail.com', @PwdHash, @PwdSalt, N'Direccionador', @SedeBog, 0, N'Activo', '2024-03-01');
DECLARE @UDirecc INT = SCOPE_IDENTITY();

-- U15. Administrador de plataforma (sin EmpleadoId)
INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES (N'admin@yopmail.com', @PwdHash, @PwdSalt, N'Administrador', @SedeMed, 0, N'Activo', '2018-01-01');
DECLARE @UAdmin INT = SCOPE_IDENTITY();

-- ============================================================
-- 6. EMPLEADOS
--    Orden: Jefe → Regentes → subordinados activos → inactivos
-- ============================================================

-- E01. Carlos Alberto Rodríguez Mora — Jefe
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Carlos Alberto Rodríguez Mora', N'10234567', '1985-03-14', N'3104567890', N'carlos.rodriguez@yopmail.com',
    N'Cra 15 #45-32', N'Medellín', N'Antioquia', N'Profesional', N'Sura EPS', N'Sura ARL',
    @SedeMed, @CargoDT, @UJefe, NULL,
    N'Directo', '2019-01-15', NULL, NULL, NULL,
    N'Activo', 30.0, '2019-01-15', @UJefe);
DECLARE @EJefe INT = SCOPE_IDENTITY();

-- E02. Laura Patricia Sánchez Gómez — Regente Medellín
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Laura Patricia Sánchez Gómez', N'20345678', '1990-07-22', N'3123456789', N'laura.sanchez@yopmail.com',
    N'Cll 100 #18-50', N'Medellín', N'Antioquia', N'Profesional', N'Nueva EPS', N'Bolívar ARL',
    @SedeMed, @CargoReg, @UReg1, @EJefe,
    N'Directo', '2020-03-01', NULL, NULL, NULL,
    N'Activo', 15.0, '2020-03-01', @UJefe);
DECLARE @EReg1 INT = SCOPE_IDENTITY();


-- E03. Hernán David Castillo Mejía — Regente Bogotá
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Hernán David Castillo Mejía', N'30456789', '1988-09-30', N'3156789012', N'hernan.castillo@yopmail.com',
    N'Av El Dorado #68C-61', N'Bogotá', N'Cundinamarca', N'Profesional', N'Compensar', N'Sura ARL',
    @SedeBog, @CargoReg, @UReg2, @EJefe,  -- ya usa @CargoReg = Regente de Farmacia
    N'Directo', '2020-06-15', NULL, NULL, NULL,
    N'Activo', 20.0, '2020-06-15', @UJefe);
DECLARE @EReg2 INT = SCOPE_IDENTITY();

-- E04. Andrés Felipe Torres Ruiz — AuxiliarRegente (Medellín, bajo Laura)
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Andrés Felipe Torres Ruiz', N'40567890', '1995-11-05', N'3178901234', N'andres.torres@yopmail.com',
    N'Cll 50 Sur #43-25', N'Medellín', N'Antioquia', N'Tecnico', N'Sura EPS', N'Sura ARL',
    @SedeMed, @CargoAuxReg, @UAux, @EReg1,
    N'Directo', '2022-04-01', NULL, NULL, NULL,
    N'Activo', 0.0, '2022-04-01', @UJefe);
DECLARE @EAndres INT = SCOPE_IDENTITY();

-- E05. Diana Marcela Vargas López — Operario / Auxiliar de Farmacia (Medellín, bajo Laura)
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Diana Marcela Vargas López', N'50678901', '1992-06-18', N'3190123456', N'diana.vargas@yopmail.com',
    N'Cra 50 #80-25', N'Medellín', N'Antioquia', N'Bachillerato', N'Famisanar', N'Positiva',
    @SedeMed, @CargoAux, @UDiana, @EReg1,
    N'Directo', '2021-07-01', NULL, NULL, NULL,
    N'Activo', 10.0, '2021-07-01', @UJefe);
DECLARE @EDiana INT = SCOPE_IDENTITY();

-- E06. Jorge Armando Herrera Quintana — Operario / Auxiliar de Farmacia (Medellín, bajo Laura)
--      Ingresó en 2026 para reemplazar a Valentina Ospina
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Jorge Armando Herrera Quintana', N'11223344', '1996-03-21', N'3016543210', N'jorge.herrera@yopmail.com',
    N'Cll 45 #72-30', N'Medellín', N'Antioquia', N'Tecnologico', N'Sura EPS', N'AXA Colpatria',
    @SedeMed, @CargoAux, @UJorge, @EReg1,
    N'Directo', '2026-02-03', NULL, NULL, NULL,
    N'Activo', 0.0, '2026-02-03', @UReg1);
DECLARE @EJorge INT = SCOPE_IDENTITY();

-- E07. Natalia Bermúdez Salazar — Operario / Auxiliar de Farmacia (Bogotá, bajo Hernán)
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Natalia Bermúdez Salazar', N'80901234', '1994-08-07', N'3256789012', N'natalia.bermudez@yopmail.com',
    N'Cll 9 #43B-10', N'Bogotá', N'Cundinamarca', N'Profesional', N'Coomeva', N'Bolívar ARL',
    @SedeBog, @CargoAux, @UNata, @EReg2,
    N'Directo', '2021-02-15', NULL, NULL, NULL,
    N'Activo', 8.0, '2021-02-15', @UJefe);
DECLARE @ENata INT = SCOPE_IDENTITY();

-- E08. Paula Andrea Quintero Ríos — Operario Cajera (Bogotá, bajo Hernán)
--      CASO: Inició como TEMPORAL con ManpowerGroup → pasó a DIRECTO en 2026
--      El empleado actual refleja su estado ACTUAL (directo).
--      El historial de cambio de contrato se documenta en AsignacionesTurno y descripción.
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor, FechaModificacion, ModificadoPor)
VALUES (
    N'Paula Andrea Quintero Ríos', N'91012345', '1997-05-20', N'3278901234', N'paula.quintero@yopmail.com',
    N'Cra 70 #34-15', N'Bogotá', N'Cundinamarca', N'Tecnico', N'Comfama', N'Sura ARL',
    @SedeBog, @CargoAux, @UPaula, @EReg2,
    N'Directo', '2025-03-01', NULL, NULL, NULL,   -- Actualizado: ya no es Temporal
    N'Activo', 0.0, '2025-03-01', @UJefe, '2026-01-01', @UJefe);
DECLARE @EPaula INT = SCOPE_IDENTITY();

-- E09. Camila Andrea Ríos Vargas — Operario / Auxiliar de Farmacia (Bogotá, bajo Hernán)
--      Ingresó en 2025 para reemplazar a Sebastián Moreno
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Camila Andrea Ríos Vargas', N'99887766', '2000-11-12', N'3012223344', N'camila.rios@yopmail.com',
    N'Av Boyacá #12-45', N'Bogotá', N'Cundinamarca', N'Bachillerato', N'Sanitas', N'Positiva',
    @SedeBog, @CargoAux, @UCamila, @EReg2,
    N'Directo', '2025-07-01', NULL, NULL, NULL,
    N'Activo', 0.0, '2025-07-01', @UReg2);
DECLARE @ECamila INT = SCOPE_IDENTITY();

-- ── Empleados INACTIVOS ────────────────────────────────────────

-- E10. Valentina Ospina Restrepo — INACTIVA (vencimiento contrato temporal Adecco, no renovado)
--      Trabajó como Asesor Comercial bajo Laura Sánchez en Medellín
--      Contrato: 15/01/2024 – 31/01/2026 (2 años)
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor, FechaModificacion, ModificadoPor)
VALUES (
    N'Valentina Ospina Restrepo', N'60789012', '1993-04-12', N'3212345678', N'valentina.ospina@yopmail.com',
    N'Cll 10 Sur #43-25', N'Medellín', N'Antioquia', N'Tecnologico', N'Comfama', N'AXA Colpatria',
    @SedeMed, @CargoAux, @UVale, @EReg1,
    N'Temporal', '2024-01-15', @EmpAdecco, '2024-01-15', '2026-01-31',
    N'Inactivo', 5.0, '2024-01-15', @UJefe, '2026-01-31', @UJefe);
DECLARE @EVale INT = SCOPE_IDENTITY();

-- E11. Sebastián Andrés Moreno Parra — INACTIVO (despido con justa causa)
--      Trabajó como Mensajero bajo Hernán Castillo en Bogotá
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor, FechaModificacion, ModificadoPor)
VALUES (
    N'Sebastián Andrés Moreno Parra', N'70890123', '1998-12-03', N'3234567890', N'sebastian.moreno@yopmail.com',
    N'Cra 28 #12-60', N'Bogotá', N'Cundinamarca', N'Bachillerato', N'Sura EPS', N'Positiva',
    @SedeBog, @CargoAux, @USeba, @EReg2,
    N'Directo', '2023-03-01', NULL, NULL, NULL,
    N'Inactivo', 5.0, '2023-03-01', @UJefe, '2025-06-30', @UJefe);
DECLARE @ESeba INT = SCOPE_IDENTITY();

-- E12. Ricardo Enrique Useche Paredes — INACTIVO (renuncia voluntaria)
--      Trabajó como Cajero bajo Laura Sánchez en Medellín
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor, FechaModificacion, ModificadoPor)
VALUES (
    N'Ricardo Enrique Useche Paredes', N'33445566', '1991-02-17', N'3005551234', N'ricardo.useche@yopmail.com',
    N'Cll 80 #45-20', N'Medellín', N'Antioquia', N'Bachillerato', N'Nueva EPS', N'Bolívar ARL',
    @SedeMed, @CargoAux, @URicardo, @EReg1,
    N'Directo', '2021-08-01', NULL, NULL, NULL,
    N'Inactivo', 12.0, '2021-08-01', @UJefe, '2024-09-30', @UJefe);
DECLARE @ERicardo INT = SCOPE_IDENTITY();

-- E13. Sofía Isabel Gómez Luna — Analista (Medellín, acceso total multi-sede)
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Sofía Isabel Gómez Luna', N'55666677', '1990-06-10', N'3150001111', N'sofia.gomez@yopmail.com',
    N'Cll 33 #70-20', N'Medellín', N'Antioquia', N'Profesional', N'Comfama', N'Sura ARL',
    @SedeMed, @CargoAnalista, @UAnalista, NULL,
    N'Directo', '2024-01-01', NULL, '2024-01-01', NULL,
    N'Activo', 0.0, '2024-01-01', @UJefe);
DECLARE @EAnalista INT = SCOPE_IDENTITY();

-- E14. Pedro Emilio Ramírez Vega — Direccionador (Bogotá, solo información propia)
INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Pedro Emilio Ramírez Vega', N'55443322', '1995-09-15', N'3150002222', N'pedro.ramirez@yopmail.com',
    N'Cra 15 #30-10', N'Bogotá', N'Cundinamarca', N'Tecnologico', N'Sura EPS', N'Positiva',
    @SedeBog, @CargoDirecc, @UDirecc, @EReg2,
    N'Directo', '2024-03-01', NULL, '2024-03-01', NULL,
    N'Activo', 0.0, '2024-03-01', @UJefe);
DECLARE @EDirecc INT = SCOPE_IDENTITY();

-- ============================================================
-- 7. CONTACTOS DE EMERGENCIA
-- ============================================================
INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
VALUES
    (@EJefe,    N'María Isabel Rodríguez',  N'3115678901'),
    (@EReg1,    N'Juan Carlos Sánchez',     N'3134567890'),
    (@EReg2,    N'Rosa Elena Castillo',     N'3167890123'),
    (@EAndres,  N'Clara Inés Torres',       N'3189012345'),
    (@EDiana,   N'Pedro Pablo Vargas',      N'3201234567'),
    (@EJorge,   N'Marta Lucía Herrera',     N'3027654321'),
    (@ENata,    N'Jorge Eduardo Bermúdez',  N'3267890123'),
    (@EPaula,   N'Ricardo Quintero López',  N'3289012345'),
    (@ECamila,  N'Luis Carlos Ríos',        N'3034445566'),
    -- Inactivos también conservan contacto (historial perpetuo)
    (@EVale,    N'Luis Fernando Ospina',    N'3223456789'),
    (@ESeba,    N'Ana María Moreno',        N'3245678901'),
    (@ERicardo, N'Gloria Useche',           N'3112223334'),
    -- Nuevos roles
    (@EAnalista, N'Camilo Gómez',          N'3160003333'),
    (@EDirecc,   N'Ana Ramírez',            N'3170004444');

-- ============================================================
-- 8. HISTORIAL DE DESVINCULACIONES (3)
-- ============================================================

-- 8a. Valentina Ospina — Vencimiento contrato temporal (no renovado por empresa)
INSERT INTO dbo.HistorialDesvinculaciones (EmpleadoId, MotivoRetiro, FechaDesvinculacion, RegistradoPor, FechaCreacion)
VALUES (@EVale,
    N'Vencimiento de contrato temporal con Adecco Colombia S.A. No se renovó por ajuste de planta.',
    '2026-01-31', @UJefe, '2026-01-31');

-- 8b. Sebastián Moreno — Despido con justa causa
INSERT INTO dbo.HistorialDesvinculaciones (EmpleadoId, MotivoRetiro, FechaDesvinculacion, RegistradoPor, FechaCreacion)
VALUES (@ESeba,
    N'Despido con justa causa: incumplimiento reiterado del reglamento interno y ausencias injustificadas.',
    '2025-06-30', @UJefe, '2025-06-30');

-- 8c. Ricardo Useche — Renuncia voluntaria
INSERT INTO dbo.HistorialDesvinculaciones (EmpleadoId, MotivoRetiro, FechaDesvinculacion, RegistradoPor, FechaCreacion)
VALUES (@ERicardo,
    N'Renuncia voluntaria. El empleado presentó carta de renuncia el 15/09/2024 con preaviso de 15 días.',
    '2024-09-30', @UReg1, '2024-09-30');

-- ============================================================
-- 9. ASIGNACIONES DE TURNO (con historial de cambios)
-- ============================================================
-- Regla: solo una asignación activa por empleado a la vez.
-- El historial se refleja insertando múltiples registros por empleado
-- con fechas de vigencia diferentes (la más reciente es la activa).

-- Carlos — siempre Estándar
INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@EJefe, @PTEstandar, '2019-01-15', @UJefe, '2019-01-15');

-- Laura — Estándar desde inicio
INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@EReg1, @PTEstandar, '2020-03-01', @UJefe, '2020-03-01');

-- Hernán — Estándar desde inicio
INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@EReg2, @PTEstandar, '2020-06-15', @UJefe, '2020-06-15');

-- Andrés — Estándar desde inicio, cambió a Rotativo en 2024 (más responsabilidades)
INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@EAndres, @PTEstandar, '2022-04-01', @UReg1, '2022-04-01');

INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@EAndres, @PTRotativo, '2024-01-15', @UReg1, '2024-01-15');  -- Turno actual

-- Diana — Estándar siempre
INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@EDiana, @PTEstandar, '2021-07-01', @UReg1, '2021-07-01');

-- Jorge — Estándar desde ingreso (nuevo empleado 2026)
INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@EJorge, @PTEstandar, '2026-02-03', @UReg1, '2026-02-03');

-- Natalia — Estándar desde inicio, cambió a Fin de Semana en 2023
INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@ENata, @PTEstandar, '2021-02-15', @UReg2, '2021-02-15');

INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@ENata, @PTFinSem, '2023-06-01', @UReg2, '2023-06-01');  -- Turno actual

-- Paula — Estándar desde inicio (el cambio de temporal a directo no afecta el turno)
INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@EPaula, @PTEstandar, '2025-03-01', @UReg2, '2025-03-01');

-- Camila — Rotativo desde ingreso
INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@ECamila, @PTRotativo, '2025-07-01', @UReg2, '2025-07-01');

-- Valentina (INACTIVA) — Fin de Semana durante su contrato
INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@EVale, @PTFinSem, '2024-01-15', @UReg1, '2024-01-15');

-- Sebastián (INACTIVO) — Rotativo desde ingreso
INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@ESeba, @PTRotativo, '2023-03-01', @UReg2, '2023-03-01');

-- Ricardo (INACTIVO) — Estándar, cambió a Fin de Semana, volvió a Estándar
INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@ERicardo, @PTEstandar, '2021-08-01', @UReg1, '2021-08-01');

INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@ERicardo, @PTFinSem, '2022-06-01', @UReg1, '2022-06-01');

INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
VALUES (@ERicardo, @PTEstandar, '2023-09-01', @UReg1, '2023-09-01');  -- Última asignación activa

-- ============================================================
-- 10. EVENTOS LABORALES
--     Incluye todos los tipos (Vacaciones, Incapacidad, Permiso)
--     y todos los estados (Activo, Finalizado, Anulado)
-- ============================================================

-- ── Carlos Rodríguez (Jefe) ───────────────────────────────────

-- Vacaciones 2024 (Finalizadas)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EJefe, N'Vacaciones', '2024-12-23', '2025-01-05', N'Finalizado', NULL, NULL, NULL, N'Junta Directiva Helpharma', NULL, NULL, NULL, @UJefe, '2024-12-20', NULL);

-- Vacaciones 2025 (Finalizadas)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EJefe, N'Vacaciones', '2025-12-22', '2026-01-04', N'Finalizado', NULL, NULL, NULL, N'Junta Directiva Helpharma', NULL, NULL, NULL, @UJefe, '2025-12-18', NULL);

-- ── Laura Sánchez (Regente Medellín) ─────────────────────────

-- Permiso por cita médica (Finalizado)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EReg1, N'Permiso', '2024-09-10', '2024-09-10', N'Finalizado', NULL, NULL, N'Cita médica de control programada', N'Carlos Rodríguez', NULL, NULL, NULL, @UJefe, '2024-09-09', NULL);

-- Vacaciones 2025 (Finalizadas)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EReg1, N'Vacaciones', '2025-07-14', '2025-07-25', N'Finalizado', NULL, NULL, NULL, N'Carlos Rodríguez', NULL, NULL, NULL, @UJefe, '2025-07-10', NULL);

-- Permiso activo — cita médica próxima semana
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EReg1, N'Permiso', '2026-04-25', '2026-04-25', N'Activo', NULL, NULL, N'Control ginecológico programado', N'Carlos Rodríguez', NULL, NULL, NULL, @UJefe, '2026-04-22', NULL);

-- ── Hernán Castillo (Regente Bogotá) ─────────────────────────

-- Incapacidad por Enfermedad General (Finalizada)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EReg2, N'Incapacidad', '2023-11-06', '2023-11-10', N'Finalizado', N'EnfermedadGeneral', N'Compensar EPS', NULL, N'Carlos Rodríguez', NULL, NULL, NULL, @UJefe, '2023-11-06', NULL);

-- Vacaciones activas
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EReg2, N'Vacaciones', '2026-04-14', '2026-04-27', N'Activo', NULL, NULL, NULL, N'Carlos Rodríguez', NULL, NULL, NULL, @UJefe, '2026-04-10', NULL);

-- ── Andrés Torres (AuxiliarRegente Medellín) ─────────────────

-- Incapacidad Enfermedad General (Finalizada)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EAndres, N'Incapacidad', '2024-03-04', '2024-03-08', N'Finalizado', N'EnfermedadGeneral', N'Sura EPS', NULL, N'Laura Sánchez', NULL, NULL, NULL, @UReg1, '2024-03-04', NULL);

-- Permiso anulado (solicitó permiso pero lo canceló)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EAndres, N'Permiso', '2024-11-15', '2024-11-15', N'Anulado', NULL, NULL, N'Diligencias notariales', N'Laura Sánchez', N'El empleado resolvió la diligencia fuera del horario laboral', NULL, NULL, @UReg1, '2024-11-14', @UReg1);

-- Vacaciones 2025 (Finalizadas)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EAndres, N'Vacaciones', '2025-08-04', '2025-08-15', N'Finalizado', NULL, NULL, NULL, N'Laura Sánchez', NULL, NULL, NULL, @UReg1, '2025-07-28', NULL);

-- ── Diana Vargas (Operario Cajera Medellín) ───────────────────

-- Permiso por calamidad doméstica (Finalizado)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EDiana, N'Permiso', '2023-08-21', '2023-08-22', N'Finalizado', NULL, NULL, N'Fallecimiento de familiar de primer grado (tío paterno)', N'Laura Sánchez', NULL, NULL, NULL, @UReg1, '2023-08-21', NULL);

-- Incapacidad Accidente de Trabajo (Finalizada)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EDiana, N'Incapacidad', '2025-02-10', '2025-02-21', N'Finalizado', N'AccidenteTrabajo', N'Positiva ARL', NULL, N'Laura Sánchez', NULL, NULL, NULL, @UReg1, '2025-02-10', NULL);

-- ── Natalia Bermúdez (Operario Administrativo Bogotá) ─────────

-- Incapacidad Maternidad (Finalizada)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@ENata, N'Incapacidad', '2024-06-03', '2024-09-30', N'Finalizado', N'MaternidadPaternidad', N'Coomeva EPS', NULL, N'Hernán Castillo', NULL, NULL, NULL, @UReg2, '2024-06-03', NULL);

-- Permiso lactancia activo
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@ENata, N'Permiso', '2026-04-21', '2026-04-21', N'Activo', NULL, NULL, N'Permiso de lactancia materna (2 horas diarias según Ley 1823 de 2017)', N'Hernán Castillo', NULL, NULL, NULL, @UReg2, '2026-04-20', NULL);

-- ── Paula Quintero (Operario Cajera Bogotá — antes temporal) ──

-- Incapacidad Enfermedad Laboral (Activa)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EPaula, N'Incapacidad', '2026-04-18', '2026-04-24', N'Activo', N'EnfermedadLaboral', N'Comfama', NULL, N'Hernán Castillo', NULL, NULL, NULL, @UReg2, '2026-04-18', NULL);

-- ── Valentina Ospina (INACTIVA — vencimiento contrato) ────────

-- Permiso durante su contrato (Finalizado)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EVale, N'Permiso', '2024-07-15', '2024-07-15', N'Finalizado', NULL, NULL, N'Renovación de documentos de identidad', N'Laura Sánchez', NULL, NULL, NULL, @UReg1, '2024-07-14', NULL);

-- Incapacidad Enfermedad General (Finalizada)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@EVale, N'Incapacidad', '2025-03-10', '2025-03-14', N'Finalizado', N'EnfermedadGeneral', N'Comfama', NULL, N'Laura Sánchez', NULL, NULL, NULL, @UReg1, '2025-03-10', NULL);

-- ── Sebastián Moreno (INACTIVO — despido justa causa) ─────────

-- Incapacidad Accidente de Trabajo (Finalizada)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@ESeba, N'Incapacidad', '2024-08-05', '2024-08-16', N'Finalizado', N'AccidenteTrabajo', N'Positiva ARL', NULL, N'Hernán Castillo', NULL, NULL, NULL, @UReg2, '2024-08-05', NULL);

-- Permiso anulado
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@ESeba, N'Permiso', '2025-01-20', '2025-01-20', N'Anulado', NULL, NULL, N'Cita médica particular', N'Hernán Castillo', N'El empleado no presentó la cita a tiempo; la autorización fue revocada', NULL, NULL, @UReg2, '2025-01-19', @UReg2);

-- ── Ricardo Useche (INACTIVO — renuncia voluntaria) ───────────

-- Vacaciones 2022 (Finalizadas)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@ERicardo, N'Vacaciones', '2022-12-26', '2023-01-06', N'Finalizado', NULL, NULL, NULL, N'Laura Sánchez', NULL, NULL, NULL, @UReg1, '2022-12-20', NULL);

-- Incapacidad Enfermedad General (Finalizada)
INSERT INTO dbo.EventosLaborales (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado, TipoIncapacidad, EntidadExpide, Descripcion, AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento, CreadoPor, FechaCreacion, AnuladoPor)
VALUES (@ERicardo, N'Incapacidad', '2024-05-06', '2024-05-10', N'Finalizado', N'EnfermedadGeneral', N'Nueva EPS', NULL, N'Laura Sánchez', NULL, NULL, NULL, @UReg1, '2024-05-06', NULL);

-- ============================================================
-- 11. HORAS EXTRAS — todos los estados del flujo
-- ============================================================

-- ── Carlos Rodríguez (Jefe) ───────────────────────────────────
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@EJefe, '2026-02-28', 3.0, N'Cierre de indicadores trimestrales y reporte a Junta Directiva', N'Aprobado', @UJefe, '2026-03-01', NULL, NULL, NULL, NULL, @UJefe, '2026-03-01');

-- ── Laura Sánchez (Regente Medellín) ─────────────────────────
-- Aprobada
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@EReg1, '2026-03-15', 2.0, N'Capacitación a nuevo personal de Medellín', N'Aprobado', @UJefe, '2026-03-16', NULL, NULL, NULL, NULL, @UJefe, '2026-03-16');

-- ── Hernán Castillo (Regente Bogotá) ─────────────────────────
-- Pendiente
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@EReg2, '2026-04-20', 1.5, N'Revisión de cierre contable mensual de Bogotá', N'Pendiente', NULL, NULL, NULL, NULL, NULL, NULL, @UJefe, '2026-04-21');

-- ── Andrés Torres (AuxiliarRegente Medellín) ─────────────────
-- Pendiente de aprobación
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@EAndres, '2026-04-19', 2.0, N'Inventario mensual de medicamentos controlados', N'Pendiente', NULL, NULL, NULL, NULL, NULL, NULL, @UReg1, '2026-04-20');

-- Aprobada histórica
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@EAndres, '2025-11-29', 4.0, N'Auditoría de inventario de fin de mes', N'Aprobado', @UReg1, '2025-11-30', NULL, NULL, NULL, NULL, @UReg1, '2025-11-30');

-- ── Diana Vargas (Operario Cajera Medellín) ───────────────────
-- Aprobada
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@EDiana, '2026-04-12', 3.0, N'Cierre de caja y cuadre de efectivo por faltante detectado', N'Aprobado', @UReg1, '2026-04-13', NULL, NULL, NULL, NULL, @UReg1, '2026-04-13');

-- Rechazada
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@EDiana, '2026-03-22', 2.0, N'Apoyo en campaña de ventas de temporada', N'Rechazado', @UReg1, '2026-03-23', N'No se contaba con presupuesto autorizado para horas extras en esa fecha', NULL, NULL, NULL, @UReg1, '2026-03-23');

-- ── Natalia Bermúdez (Operario Administrativo Bogotá) ─────────
-- Aprobada
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@ENata, '2026-03-28', 3.0, N'Capacitación al nuevo personal de Bogotá', N'Aprobado', @UReg2, '2026-03-29', NULL, NULL, NULL, NULL, @UReg2, '2026-03-29');

-- Anulada (fue aprobada pero luego se anuló porque la capacitación se reprogramó)
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@ENata, '2026-02-14', 2.5, N'Entrenamiento al personal en sistema de facturación', N'Anulado', @UReg2, '2026-02-15', NULL, @UJefe, '2026-02-20', N'Capacitación reprogramada para horario regular; horas no aplican para pago extra', @UReg2, '2026-02-15');

-- ── Paula Quintero (Operario Cajera Bogotá) ───────────────────
-- Pendiente (trabaja con contrato directo desde enero 2026)
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@EPaula, '2026-04-17', 2.0, N'Reemplazo por ausencia de compañera en turno de caja', N'Pendiente', NULL, NULL, NULL, NULL, NULL, NULL, @UReg2, '2026-04-18');

-- Aprobada histórica (cuando era temporal, antes del cambio a directo)
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@EPaula, '2025-11-08', 3.0, N'Recepción de pedido especial de vacunas y cadena de frío', N'Aprobado', @UReg2, '2025-11-09', NULL, NULL, NULL, NULL, @UReg2, '2025-11-09');

-- ── Valentina Ospina (INACTIVA — durante su contrato temporal) ──
-- Rechazada
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@EVale, '2025-04-05', 4.0, N'Apoyo en punto de venta adicional los fines de semana', N'Rechazado', @UReg1, '2025-04-06', N'No se autorizó por restricciones del contrato temporal con Adecco Colombia', NULL, NULL, NULL, @UReg1, '2025-04-06');

-- Aprobada
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@EVale, '2025-08-09', 2.0, N'Cobertura de turno por ausencia de compañera', N'Aprobado', @UReg1, '2025-08-10', NULL, NULL, NULL, NULL, @UReg1, '2025-08-10');

-- ── Sebastián Moreno (INACTIVO — durante su contrato) ─────────
-- Aprobada
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@ESeba, '2024-04-08', 2.5, N'Recepción de pedido especial de vacunas y verificación de cadena de frío', N'Aprobado', @UReg2, '2024-04-09', NULL, NULL, NULL, NULL, @UReg2, '2024-04-09');

-- Rechazada
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@ESeba, '2025-03-15', 3.0, N'Entrega de pedidos urgentes en zonas periféricas', N'Rechazado', @UReg2, '2025-03-16', N'Las entregas fueron realizadas en horario regular según la planilla', NULL, NULL, NULL, @UReg2, '2025-03-16');

-- ── Ricardo Useche (INACTIVO — renuncia voluntaria) ───────────
-- Aprobada
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@ERicardo, '2023-12-30', 2.0, N'Cierre contable de fin de año y arqueo de caja', N'Aprobado', @UReg1, '2023-12-31', NULL, NULL, NULL, NULL, @UReg1, '2023-12-31');

-- Anulada (fue aprobada pero el Jefe la anuló)
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@ERicardo, '2024-06-15', 1.5, N'Apoyo en inventario semestral de medicamentos', N'Anulado', @UReg1, '2024-06-16', NULL, @UJefe, '2024-07-01', N'Inventario fue reclasificado como actividad de horario regular según circular interna', @UReg1, '2024-06-16');

-- ── Camila Ríos (nueva — solo una pendiente) ──────────────────
INSERT INTO dbo.HorasExtras (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado, AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo, AnuladoPor, FechaAnulacion, MotivoAnulacion, CreadoPor, FechaCreacion)
VALUES (@ECamila, '2026-04-21', 2.0, N'Entrega urgente de medicamentos a domicilio por paciente de alto costo', N'Pendiente', NULL, NULL, NULL, NULL, NULL, NULL, @UReg2, '2026-04-22');

-- ============================================================
-- 12. TOKENS DE RECUPERACIÓN DE CONTRASEÑA (3 casos)
-- ============================================================

-- Token usado (Laura Sánchez lo usó para cambiar su contraseña)
INSERT INTO dbo.TokensRecuperacion (UsuarioId, Token, FechaExpiracion, Usado, FechaCreacion)
VALUES (@UReg1, N'TK3F9A2B1C', '2026-03-20 10:00:00', 1, '2026-03-20 08:00:00');

-- Token expirado sin usar (Andrés Torres lo solicitó pero no lo usó a tiempo)
INSERT INTO dbo.TokensRecuperacion (UsuarioId, Token, FechaExpiracion, Usado, FechaCreacion)
VALUES (@UAux, N'TK7E4D8F5G', '2026-04-10 15:00:00', 0, '2026-04-10 13:00:00');

-- Token vigente (Natalia Bermúdez tiene solicitud activa de recuperación)
INSERT INTO dbo.TokensRecuperacion (UsuarioId, Token, FechaExpiracion, Usado, FechaCreacion)
VALUES (@UNata, N'TK1H6K9M2N', '2026-04-24 09:00:00', 0, '2026-04-22 09:00:00');

-- ============================================================
-- 13. VERIFICACIÓN FINAL
-- ============================================================
SELECT 'Sedes'                      AS Tabla, COUNT(*) AS Total FROM dbo.Sedes
UNION ALL SELECT 'Cargos',                           COUNT(*) FROM dbo.Cargos
UNION ALL SELECT 'EmpresasTemporales',               COUNT(*) FROM dbo.EmpresasTemporales
UNION ALL SELECT 'PlantillasTurno',                  COUNT(*) FROM dbo.PlantillasTurno
UNION ALL SELECT 'PlantillasTurnoDetalle',           COUNT(*) FROM dbo.PlantillasTurnoDetalle
UNION ALL SELECT 'Usuarios (total)',                 COUNT(*) FROM dbo.Usuarios
UNION ALL SELECT 'Usuarios Activos',                 COUNT(*) FROM dbo.Usuarios WHERE Estado = N'Activo'
UNION ALL SELECT 'Usuarios Inactivos',               COUNT(*) FROM dbo.Usuarios WHERE Estado = N'Inactivo'
UNION ALL SELECT 'Empleados (total)',                COUNT(*) FROM dbo.Empleados
UNION ALL SELECT 'Empleados Activos',                COUNT(*) FROM dbo.Empleados WHERE Estado = N'Activo'
UNION ALL SELECT 'Empleados Inactivos',              COUNT(*) FROM dbo.Empleados WHERE Estado = N'Inactivo'
UNION ALL SELECT 'ContactosEmergencia',              COUNT(*) FROM dbo.ContactosEmergencia
UNION ALL SELECT 'HistorialDesvinculaciones',        COUNT(*) FROM dbo.HistorialDesvinculaciones
UNION ALL SELECT 'AsignacionesTurno (total)',        COUNT(*) FROM dbo.AsignacionesTurno
UNION ALL SELECT 'EventosLaborales (total)',         COUNT(*) FROM dbo.EventosLaborales
UNION ALL SELECT 'EventosLaborales Activos',         COUNT(*) FROM dbo.EventosLaborales WHERE Estado = N'Activo'
UNION ALL SELECT 'EventosLaborales Finalizados',     COUNT(*) FROM dbo.EventosLaborales WHERE Estado = N'Finalizado'
UNION ALL SELECT 'EventosLaborales Anulados',        COUNT(*) FROM dbo.EventosLaborales WHERE Estado = N'Anulado'
UNION ALL SELECT 'HorasExtras (total)',              COUNT(*) FROM dbo.HorasExtras
UNION ALL SELECT 'HorasExtras Pendientes',           COUNT(*) FROM dbo.HorasExtras WHERE Estado = N'Pendiente'
UNION ALL SELECT 'HorasExtras Aprobadas',            COUNT(*) FROM dbo.HorasExtras WHERE Estado = N'Aprobado'
UNION ALL SELECT 'HorasExtras Rechazadas',           COUNT(*) FROM dbo.HorasExtras WHERE Estado = N'Rechazado'
UNION ALL SELECT 'HorasExtras Anuladas',             COUNT(*) FROM dbo.HorasExtras WHERE Estado = N'Anulado'
UNION ALL SELECT 'TokensRecuperacion',               COUNT(*) FROM dbo.TokensRecuperacion;
GO

-- Detalle de empleados con su historial de turno
SELECT
    e.NombreCompleto,
    e.Estado         AS EstadoEmpleado,
    pt.Nombre        AS Turno,
    a.FechaVigencia,
    u.NombreCompleto AS ProgramadoPor
FROM dbo.AsignacionesTurno a
JOIN dbo.Empleados     e  ON e.Id = a.EmpleadoId
JOIN dbo.PlantillasTurno pt ON pt.Id = a.PlantillaTurnoId
JOIN dbo.Empleados     u  ON u.UsuarioId = a.ProgramadoPor
ORDER BY e.NombreCompleto, a.FechaVigencia;
GO

-- Resumen del historial de Paula (caso temporal → directo)
SELECT
    'EMPLEADO'     AS Tipo, e.NombreCompleto, CAST(e.TipoVinculacion AS NVARCHAR(50)) AS Detalle, CAST(e.FechaIngreso AS NVARCHAR(50)) AS Fecha
FROM dbo.Empleados e WHERE e.Cedula = N'91012345'
UNION ALL
SELECT 'EVENTO', emp.NombreCompleto, ev.TipoEvento + ' (' + ev.Estado + ')', CAST(ev.FechaInicio AS NVARCHAR(50))
FROM dbo.EventosLaborales ev JOIN dbo.Empleados emp ON emp.Id = ev.EmpleadoId WHERE emp.Cedula = N'91012345'
UNION ALL
SELECT 'HORA EXTRA', emp.NombreCompleto, h.Motivo + ' (' + h.Estado + ')', CAST(h.FechaTrabajada AS NVARCHAR(50))
FROM dbo.HorasExtras h JOIN dbo.Empleados emp ON emp.Id = h.EmpleadoId WHERE emp.Cedula = N'91012345'
ORDER BY Fecha;
GO
