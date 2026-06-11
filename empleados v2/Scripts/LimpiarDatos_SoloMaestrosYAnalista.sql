-- ============================================================
-- Limpieza: elimina usuarios, empleados y operación.
-- Conserva datos maestros + un único usuario Analista.
--
-- Usuario resultante:
--   Correo: sofia.gomez@yopmail.com
--   Contraseña: Yopmail2026
--   Rol: Analista
--
-- Se conservan: Sedes, Cargos, EmpresasTemporales, PlantillasTurno,
-- PlantillasTurnoDetalle, TiposSolicitud, RolesSistema, PermisosPlataforma,
-- RolesSistemaPermisos.
-- ============================================================
USE GestionPersonal;
GO
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
GO

SET NOCOUNT ON;
BEGIN TRANSACTION;

BEGIN TRY
    -- ── 1. Datos operativos / transaccionales ─────────────────
    IF OBJECT_ID(N'dbo.RegistroNotificaciones', N'U') IS NOT NULL
        DELETE FROM dbo.RegistroNotificaciones;

    DELETE FROM dbo.TokensRecuperacion;
    DELETE FROM dbo.HorasExtras;
    DELETE FROM dbo.EventosLaborales;
    DELETE FROM dbo.AsignacionesTurno;
    DELETE FROM dbo.HistorialDesvinculaciones;
    DELETE FROM dbo.ContactosEmergencia;

    -- Empleados (jerarquía auto-referenciada)
    UPDATE dbo.Empleados SET JefeInmediatoId = NULL;
    DELETE FROM dbo.Empleados;

    -- Todos los usuarios
    DELETE FROM dbo.Usuarios;

    -- ── 2. Reiniciar identidades (solo tablas operativas) ─────
    IF OBJECT_ID(N'dbo.RegistroNotificaciones', N'U') IS NOT NULL
        DBCC CHECKIDENT (N'dbo.RegistroNotificaciones', RESEED, 0);

    DBCC CHECKIDENT (N'dbo.TokensRecuperacion', RESEED, 0);
    DBCC CHECKIDENT (N'dbo.HorasExtras', RESEED, 0);
    DBCC CHECKIDENT (N'dbo.EventosLaborales', RESEED, 0);
    DBCC CHECKIDENT (N'dbo.AsignacionesTurno', RESEED, 0);
    DBCC CHECKIDENT (N'dbo.HistorialDesvinculaciones', RESEED, 0);
    DBCC CHECKIDENT (N'dbo.ContactosEmergencia', RESEED, 0);
    DBCC CHECKIDENT (N'dbo.Empleados', RESEED, 0);
    DBCC CHECKIDENT (N'dbo.Usuarios', RESEED, 0);

    -- ── 3. Único usuario Analista ─────────────────────────────
    DECLARE @SedeId INT = (
        SELECT TOP (1) Id FROM dbo.Sedes
        WHERE Estado = N'Activa'
        ORDER BY Id
    );

    IF @SedeId IS NULL
    BEGIN
        SELECT TOP (1) @SedeId = Id FROM dbo.Sedes ORDER BY Id;
    END

    IF @SedeId IS NULL
    BEGIN
        RAISERROR(N'No hay sedes en datos maestros. Cree al menos una sede antes de ejecutar este script.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END

    DECLARE @PwdHash VARBINARY(32) = 0x0ACE2EA8F9EAAF0937919AA1D83C40DBB314433B719F34130A1676AD8EB25D0F;
    DECLARE @PwdSalt VARBINARY(16) = 0xAD2D450B0ACDAC54662654D1A8102A2C;

    INSERT INTO dbo.Usuarios (
        CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId,
        DebecambiarPassword, Estado, FechaCreacion, UltimoAcceso)
    VALUES (
        N'sofia.gomez@yopmail.com', @PwdHash, @PwdSalt, N'Analista', @SedeId,
        0, N'Activo', GETUTCDATE(), NULL
    );

    DECLARE @UsuarioAnalistaId INT = SCOPE_IDENTITY();

    DECLARE @CargoAnalistaId INT = (
        SELECT Id FROM dbo.Cargos WHERE Nombre LIKE N'Analista de Servicios Farmac%'
    );
    IF @CargoAnalistaId IS NULL
    BEGIN
        RAISERROR(N'No existe cargo Analista de Servicios Farmacéuticos en datos maestros.', 16, 1);
        RETURN;
    END

    INSERT INTO dbo.Empleados (
        NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
        Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
        SedeId, CargoId, UsuarioId, JefeInmediatoId,
        TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
        Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
    VALUES (
        N'Sofía Isabel Gómez Luna', N'55666677', '1990-06-10', N'3150001111', N'sofia.gomez@yopmail.com',
        N'Cll 33 #70-20', N'Medellín', N'Antioquia', N'Profesional', N'Comfama', N'Sura ARL',
        @SedeId, @CargoAnalistaId, @UsuarioAnalistaId, NULL,
        N'Directo', '2024-01-01', NULL, '2024-01-01', NULL,
        N'Activo', 0.0, GETUTCDATE(), @UsuarioAnalistaId);

    DECLARE @EmpleadoAnalistaId INT = SCOPE_IDENTITY();

    INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
    VALUES (@EmpleadoAnalistaId, N'Camilo Gómez', N'3160003333');

    -- Permisos completos para Analista
    DECLARE @RolId INT = (SELECT Id FROM dbo.RolesSistema WHERE Codigo = N'Analista');

    IF @RolId IS NOT NULL
    BEGIN
        DELETE FROM dbo.RolesSistemaPermisos WHERE RolSistemaId = @RolId;
        INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId)
        SELECT @RolId, p.Id FROM dbo.PermisosPlataforma p;
    END

    COMMIT TRANSACTION;

    PRINT N'Limpieza completada.';
    PRINT N'  - Datos maestros: conservados';
    PRINT N'  - Empleados y operación: eliminados';
    PRINT N'  - Usuario único: sofia.gomez@yopmail.com (Analista) / Yopmail2026';
    PRINT N'  - Empleado vinculado: Sofía Isabel Gómez Luna';
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH
GO

-- Verificación rápida
SELECT N'Usuarios' AS Tabla, COUNT(*) AS Registros FROM dbo.Usuarios
UNION ALL SELECT N'Empleados', COUNT(*) FROM dbo.Empleados
UNION ALL SELECT N'ContactosEmergencia', COUNT(*) FROM dbo.ContactosEmergencia
UNION ALL SELECT N'Sedes', COUNT(*) FROM dbo.Sedes
UNION ALL SELECT N'Cargos', COUNT(*) FROM dbo.Cargos
UNION ALL SELECT N'EmpresasTemporales', COUNT(*) FROM dbo.EmpresasTemporales
UNION ALL SELECT N'TiposSolicitud', COUNT(*) FROM dbo.TiposSolicitud
UNION ALL SELECT N'EventosLaborales', COUNT(*) FROM dbo.EventosLaborales;
GO
