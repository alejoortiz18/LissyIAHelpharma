-- Usuarios de prueba para validar permisos por rol
-- Contraseña común: Yopmail2026 (mismo hash que sofia.gomez@yopmail.com)
USE GestionPersonal;
GO
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
GO

DECLARE @PwdHash VARBINARY(32) = 0x0ACE2EA8F9EAAF0937919AA1D83C40DBB314433B719F34130A1676AD8EB25D0F;
DECLARE @PwdSalt VARBINARY(16) = 0xAD2D450B0ACDAC54662654D1A8102A2C;

DECLARE @SedeId INT = (SELECT TOP (1) Id FROM dbo.Sedes ORDER BY Id);
DECLARE @CargoOperarioId INT = (SELECT TOP (1) Id FROM dbo.Cargos WHERE Nombre LIKE N'%Auxiliar de Farmacia%' OR Nombre LIKE N'%Operario%' ORDER BY Id);
DECLARE @CargoRegenteId INT = (SELECT TOP (1) Id FROM dbo.Cargos WHERE Nombre LIKE N'%Regente%' ORDER BY Id);
DECLARE @CargoDirId INT = (SELECT TOP (1) Id FROM dbo.Cargos WHERE Nombre LIKE N'%Direccionador%' ORDER BY Id);
DECLARE @UOp INT, @UReg INT, @UDir INT;

IF @SedeId IS NULL
BEGIN
    RAISERROR(N'No hay sedes en datos maestros.', 16, 1);
    RETURN;
END

IF @CargoOperarioId IS NULL SET @CargoOperarioId = (SELECT TOP (1) Id FROM dbo.Cargos ORDER BY Id);
IF @CargoRegenteId IS NULL SET @CargoRegenteId = @CargoOperarioId;
IF @CargoDirId IS NULL SET @CargoDirId = @CargoOperarioId;

-- Rol Operario: solo ver horas extras (sin crear) — línea base para prueba
DECLARE @RolOperarioId INT = (SELECT Id FROM dbo.RolesSistema WHERE Codigo = N'Operario');
IF @RolOperarioId IS NOT NULL
BEGIN
    DELETE FROM dbo.RolesSistemaPermisos WHERE RolSistemaId = @RolOperarioId;
    INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId)
    SELECT @RolOperarioId, p.Id FROM dbo.PermisosPlataforma p
    WHERE p.Codigo IN (
        N'Empleados.VerPerfilPropio', N'Solicitudes.Ver', N'Solicitudes.Crear', N'HorasExtras.Ver'
    );
END

-- ── Operario de prueba ─────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM dbo.Usuarios WHERE CorreoAcceso = N'prueba.operario@yopmail.com')
BEGIN
    INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
    VALUES (N'prueba.operario@yopmail.com', @PwdHash, @PwdSalt, N'Operario', @SedeId, 0, N'Activo', GETUTCDATE());

    SET @UOp = SCOPE_IDENTITY();
    INSERT INTO dbo.Empleados (
        NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
        Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
        SedeId, CargoId, UsuarioId, JefeInmediatoId,
        TipoVinculacion, FechaIngreso, FechaInicioContrato, Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
    VALUES (
        N'Prueba Operario Permisos', N'99001122', '1995-01-15', N'3001110001', N'prueba.operario@yopmail.com',
        N'Calle 1', N'Medellín', N'Antioquia', N'Tecnico', N'Sura', N'Sura ARL',
        @SedeId, @CargoOperarioId, @UOp, NULL,
        N'Directo', '2024-06-01', '2024-06-01', N'Activo', 0, GETUTCDATE(), @UOp);
END

-- ── Regente de prueba ──────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM dbo.Usuarios WHERE CorreoAcceso = N'prueba.regente@yopmail.com')
BEGIN
    INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
    VALUES (N'prueba.regente@yopmail.com', @PwdHash, @PwdSalt, N'Regente', @SedeId, 0, N'Activo', GETUTCDATE());

    SET @UReg = SCOPE_IDENTITY();
    INSERT INTO dbo.Empleados (
        NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
        Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
        SedeId, CargoId, UsuarioId, JefeInmediatoId,
        TipoVinculacion, FechaIngreso, FechaInicioContrato, Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
    VALUES (
        N'Prueba Regente Permisos', N'99002233', '1988-03-20', N'3001110002', N'prueba.regente@yopmail.com',
        N'Calle 2', N'Medellín', N'Antioquia', N'Profesional', N'Sura', N'Sura ARL',
        @SedeId, @CargoRegenteId, @UReg, NULL,
        N'Directo', '2020-01-01', '2020-01-01', N'Activo', 0, GETUTCDATE(), @UReg);
END

-- ── Direccionador de prueba ────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM dbo.Usuarios WHERE CorreoAcceso = N'prueba.direccion@yopmail.com')
BEGIN
    INSERT INTO dbo.Usuarios (CorreoAcceso, PasswordHash, PasswordSalt, Rol, SedeId, DebecambiarPassword, Estado, FechaCreacion)
    VALUES (N'prueba.direccion@yopmail.com', @PwdHash, @PwdSalt, N'Direccionador', @SedeId, 0, N'Activo', GETUTCDATE());

    SET @UDir = SCOPE_IDENTITY();
    INSERT INTO dbo.Empleados (
        NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
        Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
        SedeId, CargoId, UsuarioId, JefeInmediatoId,
        TipoVinculacion, FechaIngreso, FechaInicioContrato, Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
    VALUES (
        N'Prueba Direccionador', N'99003344', '1992-07-08', N'3001110003', N'prueba.direccion@yopmail.com',
        N'Calle 3', N'Medellín', N'Antioquia', N'Tecnico', N'Sura', N'Sura ARL',
        @SedeId, @CargoDirId, @UDir, NULL,
        N'Directo', '2023-01-01', '2023-01-01', N'Activo', 0, GETUTCDATE(), @UDir);
END

PRINT N'Usuarios de prueba listos. Contraseña: Yopmail2026';
PRINT N'  prueba.operario@yopmail.com  (Operario - sin HorasExtras.Crear)';
PRINT N'  prueba.regente@yopmail.com     (Regente)';
PRINT N'  prueba.direccion@yopmail.com   (Direccionador)';
GO

SELECT u.CorreoAcceso, u.Rol, e.NombreCompleto
FROM dbo.Usuarios u
LEFT JOIN dbo.Empleados e ON e.UsuarioId = u.Id
WHERE u.CorreoAcceso LIKE N'prueba.%'
ORDER BY u.CorreoAcceso;
GO

SELECT p.Codigo
FROM dbo.RolesSistema r
JOIN dbo.RolesSistemaPermisos rsp ON rsp.RolSistemaId = r.Id
JOIN dbo.PermisosPlataforma p ON p.Id = rsp.PermisoId
WHERE r.Codigo = N'Operario'
ORDER BY p.Codigo;
GO
