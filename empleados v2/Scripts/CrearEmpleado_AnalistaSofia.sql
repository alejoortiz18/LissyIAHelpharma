-- Crea el registro en Empleados vinculado al usuario Analista sofia.gomez@yopmail.com
USE GestionPersonal;
GO
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
GO

DECLARE @Correo NVARCHAR(200) = N'sofia.gomez@yopmail.com';

DECLARE @UsuarioId INT;
DECLARE @SedeId INT;
DECLARE @CargoAnalistaId INT;

SELECT @UsuarioId = u.Id, @SedeId = u.SedeId
FROM dbo.Usuarios u
WHERE u.CorreoAcceso = @Correo AND u.Rol = N'Analista';

IF @UsuarioId IS NULL
BEGIN
    RAISERROR(N'No existe usuario Analista con correo sofia.gomez@yopmail.com.', 16, 1);
    RETURN;
END

IF EXISTS (SELECT 1 FROM dbo.Empleados WHERE UsuarioId = @UsuarioId)
BEGIN
    PRINT N'El empleado del analista ya existe. No se realizaron cambios.';
    RETURN;
END

SELECT @CargoAnalistaId = Id
FROM dbo.Cargos
WHERE Nombre LIKE N'Analista de Servicios Farmac%';

IF @CargoAnalistaId IS NULL
    RAISERROR(N'No existe cargo Analista de Servicios Farmacéuticos en datos maestros.', 16, 1);

IF @CargoAnalistaId IS NULL
BEGIN
    RAISERROR(N'No hay cargos en datos maestros.', 16, 1);
    RETURN;
END

INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, JefeInmediatoId,
    TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
VALUES (
    N'Sofía Isabel Gómez Luna', N'55666677', '1990-06-10', N'3150001111', @Correo,
    N'Cll 33 #70-20', N'Medellín', N'Antioquia', N'Profesional', N'Comfama', N'Sura ARL',
    @SedeId, @CargoAnalistaId, @UsuarioId, NULL,
    N'Directo', '2024-01-01', NULL, '2024-01-01', NULL,
    N'Activo', 0.0, GETUTCDATE(), @UsuarioId);

DECLARE @EmpleadoId INT = SCOPE_IDENTITY();

INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
VALUES (@EmpleadoId, N'Camilo Gómez', N'3160003333');

PRINT N'Empleado creado (Id=' + CAST(@EmpleadoId AS NVARCHAR(20)) + N') vinculado a usuario Id=' + CAST(@UsuarioId AS NVARCHAR(20)) + N'.';
GO

SELECT u.Id AS UsuarioId, u.CorreoAcceso, u.Rol, e.Id AS EmpleadoId, e.NombreCompleto, c.Nombre AS Cargo
FROM dbo.Usuarios u
LEFT JOIN dbo.Empleados e ON e.UsuarioId = u.Id
LEFT JOIN dbo.Cargos c ON c.Id = e.CargoId
WHERE u.CorreoAcceso = N'sofia.gomez@yopmail.com';
GO
