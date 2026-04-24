-- ============================================================
-- SEEDING MAESTROS — GestionPersonal
-- Base de datos: GestionPersonal (SQL Server / LocalDB)
--
-- Propósito:
--   Limpieza total de datos operativos y transaccionales,
--   conservando únicamente los datos maestros del sistema más
--   un único usuario Administrador de plataforma.
--
-- Resultado tras ejecutar este script:
--   • Tablas transaccionales: vacías (Empleados, Usuarios,
--     EventosLaborales, HorasExtras, AsignacionesTurno, etc.)
--   • Tablas maestras:        pobladas (Sedes, Cargos,
--     EmpresasTemporales, PlantillasTurno, PlantillasTurnoDetalle)
--   • Usuario administrador:
--       Correo   : admin@yopmail.com
--       Contraseña: Usuario1
--       Rol      : Administrador
--
-- Algoritmo de contraseña: PBKDF2 / SHA-256 / 10 000 iteraciones
--   Hash : 32 bytes  (VARBINARY(256))
--   Salt : 16 bytes  (VARBINARY(256))
--   Implementación: GestionPersonal.Helpers.Security.PasswordHelper
--
-- NOTA SedeId del Administrador:
--   La tabla Usuarios requiere SedeId NOT NULL. Se asigna
--   Sede Medellín como placeholder. El código de la aplicación
--   omite el filtro de sede para el rol Administrador, por lo
--   que este valor no tiene efecto operativo.
-- ============================================================

USE GestionPersonal;
GO
SET QUOTED_IDENTIFIER ON;
GO

-- ============================================================
-- 0. LIMPIEZA TOTAL (orden respeta FKs)
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

-- Reiniciar secuencias de identidad
DBCC CHECKIDENT ('dbo.TokensRecuperacion',        RESEED, 0);
DBCC CHECKIDENT ('dbo.HorasExtras',               RESEED, 0);
DBCC CHECKIDENT ('dbo.EventosLaborales',           RESEED, 0);
DBCC CHECKIDENT ('dbo.AsignacionesTurno',          RESEED, 0);
DBCC CHECKIDENT ('dbo.HistorialDesvinculaciones',  RESEED, 0);
DBCC CHECKIDENT ('dbo.ContactosEmergencia',        RESEED, 0);
DBCC CHECKIDENT ('dbo.Empleados',                  RESEED, 0);
DBCC CHECKIDENT ('dbo.Usuarios',                   RESEED, 0);
DBCC CHECKIDENT ('dbo.PlantillasTurnoDetalle',     RESEED, 0);
DBCC CHECKIDENT ('dbo.PlantillasTurno',            RESEED, 0);
DBCC CHECKIDENT ('dbo.EmpresasTemporales',         RESEED, 0);
DBCC CHECKIDENT ('dbo.Cargos',                     RESEED, 0);
DBCC CHECKIDENT ('dbo.Sedes',                      RESEED, 0);
GO

-- ============================================================
-- 1. SEDES (2)
-- ============================================================

INSERT INTO dbo.Sedes (Nombre, Ciudad, Direccion, Estado, FechaCreacion)
VALUES
    (N'Sede Medellín', N'Medellín', N'Cll 50 #80-50, Centro Comercial Oviedo', N'Activa', '2018-01-01'),
    (N'Sede Bogotá',   N'Bogotá',   N'Cra 15 #93-47, Zona Rosa',               N'Activa', '2020-06-01');
GO

-- ============================================================
-- 2. CARGOS
--    Alineados con la jerarquía organizacional oficial
--    (ver Documentos/Pruebas/Playwright/Plan-Permisos-Roles-Refinados.md)
--
--    CargoId | Cargo                               | RolUsuario
--    --------|-------------------------------------|--------------------
--          1 | Director Técnico                    | DirectorTecnico
--          2 | Regente de Farmacia                 | Regente
--          3 | Auxiliar de Farmacia                | Operario
--          4 | Auxiliar Regente                    | AuxiliarRegente
--          5 | Analista de Servicios Farmacéuticos | Analista
--          6 | Direccionador                       | Direccionador
-- ============================================================

INSERT INTO dbo.Cargos (Nombre, Estado, FechaCreacion)
VALUES
    (N'Director Técnico',                    N'Activo', '2018-01-01'),
    (N'Regente de Farmacia',                 N'Activo', '2018-01-01'),
    (N'Auxiliar de Farmacia',                N'Activo', '2018-01-01'),
    (N'Auxiliar Regente',                    N'Activo', '2018-01-01'),
    (N'Analista de Servicios Farmacéuticos', N'Activo', '2018-01-01'),
    (N'Direccionador',                       N'Activo', '2018-01-01');
GO

-- ============================================================
-- 3. EMPRESAS TEMPORALES (3)
-- ============================================================

INSERT INTO dbo.EmpresasTemporales (Nombre, Estado, FechaCreacion)
VALUES
    (N'Adecco Colombia S.A.',     N'Activa',   '2018-01-01'),
    (N'ManpowerGroup Colombia',   N'Activa',   '2018-01-01'),
    (N'Staffing Colombia S.A.S.', N'Inactiva', '2019-06-01');  -- empresa con la que ya no se trabaja
GO

-- ============================================================
-- 4. PLANTILLAS DE TURNO (3)
-- ============================================================

-- 4a. Turno Estándar Lunes-Viernes
INSERT INTO dbo.PlantillasTurno (Nombre, Estado, FechaCreacion)
VALUES (N'Turno Estándar Lunes-Viernes', N'Activa', '2018-01-01');
DECLARE @PTEstandar INT = SCOPE_IDENTITY();

INSERT INTO dbo.PlantillasTurnoDetalle (PlantillaTurnoId, DiaSemana, HoraEntrada, HoraSalida)
VALUES
    (@PTEstandar, 1, '08:00', '17:00'),  -- Lunes
    (@PTEstandar, 2, '08:00', '17:00'),  -- Martes
    (@PTEstandar, 3, '08:00', '17:00'),  -- Miércoles
    (@PTEstandar, 4, '08:00', '17:00'),  -- Jueves
    (@PTEstandar, 5, '08:00', '17:00'),  -- Viernes
    (@PTEstandar, 6, NULL,    NULL   ),  -- Sábado — no labora
    (@PTEstandar, 7, NULL,    NULL   );  -- Domingo — no labora

-- 4b. Turno Fin de Semana
INSERT INTO dbo.PlantillasTurno (Nombre, Estado, FechaCreacion)
VALUES (N'Turno Fin de Semana', N'Activa', '2020-01-01');
DECLARE @PTFinSem INT = SCOPE_IDENTITY();

INSERT INTO dbo.PlantillasTurnoDetalle (PlantillaTurnoId, DiaSemana, HoraEntrada, HoraSalida)
VALUES
    (@PTFinSem, 1, NULL,    NULL   ),  -- Lunes    — no labora
    (@PTFinSem, 2, NULL,    NULL   ),  -- Martes   — no labora
    (@PTFinSem, 3, NULL,    NULL   ),  -- Miércoles— no labora
    (@PTFinSem, 4, NULL,    NULL   ),  -- Jueves   — no labora
    (@PTFinSem, 5, NULL,    NULL   ),  -- Viernes  — no labora
    (@PTFinSem, 6, '08:00', '17:00'), -- Sábado
    (@PTFinSem, 7, '08:00', '14:00'); -- Domingo

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
    (@PTRotativo, 7, NULL,    NULL   );  -- día de descanso
GO

-- ============================================================
-- 5. USUARIO ADMINISTRADOR
--    Correo   : admin@yopmail.com
--    Contraseña: Usuario1
--    Algoritmo : PBKDF2 / SHA-256 / 10 000 iteraciones
--    Hash      : 32 bytes | Salt: 16 bytes
-- ============================================================

DECLARE @SedeMed INT = (SELECT Id FROM dbo.Sedes WHERE Nombre = N'Sede Medellín');

-- Hash PBKDF2/SHA-256 de "Usuario1" con el salt fijo abajo
-- Generado con GestionPersonal.Helpers.Security.PasswordHelper
DECLARE @PwdHash VARBINARY(256) = 0x7DED37B4612147C18EBDFA1F6DEB4709EC9D511DA20641214F1F97612DF2CEAE;
DECLARE @PwdSalt VARBINARY(256) = 0xF2B483C7DAC61EC2CA7F1331C95D6800;

INSERT INTO dbo.Usuarios
    (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
VALUES
    (
        N'admin@yopmail.com',
        @PwdHash,
        @PwdSalt,
        N'Administrador',
        @SedeMed,       -- placeholder — el código omite filtro de sede para Administrador
        0,              -- no requiere cambiar contraseña en el primer login
        N'Activo',
        GETUTCDATE()
    );
GO

-- ============================================================
-- Verificación final
-- ============================================================

SELECT 'Sedes'                  AS Tabla, COUNT(*) AS Registros FROM dbo.Sedes
UNION ALL
SELECT 'Cargos',                           COUNT(*) FROM dbo.Cargos
UNION ALL
SELECT 'EmpresasTemporales',               COUNT(*) FROM dbo.EmpresasTemporales
UNION ALL
SELECT 'PlantillasTurno',                  COUNT(*) FROM dbo.PlantillasTurno
UNION ALL
SELECT 'PlantillasTurnoDetalle',           COUNT(*) FROM dbo.PlantillasTurnoDetalle
UNION ALL
SELECT 'Usuarios',                         COUNT(*) FROM dbo.Usuarios
UNION ALL
SELECT 'Empleados',                        COUNT(*) FROM dbo.Empleados
UNION ALL
SELECT 'EventosLaborales',                 COUNT(*) FROM dbo.EventosLaborales
UNION ALL
SELECT 'HorasExtras',                      COUNT(*) FROM dbo.HorasExtras
UNION ALL
SELECT 'AsignacionesTurno',                COUNT(*) FROM dbo.AsignacionesTurno;
GO

-- Vista rápida del usuario creado
SELECT Id, CorreoAcceso, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion
FROM dbo.Usuarios;
GO
