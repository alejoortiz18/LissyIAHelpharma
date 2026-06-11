USE GestionPersonal;
GO
SET QUOTED_IDENTIFIER ON;
GO

DECLARE @SedeId INT = (SELECT TOP (1) Id FROM dbo.Sedes ORDER BY Id);
DECLARE @CargoOp INT = (SELECT TOP (1) Id FROM dbo.Cargos ORDER BY Id);
DECLARE @CargoDir INT = (SELECT TOP (1) Id FROM dbo.Cargos WHERE Nombre LIKE N'%Direccionador%' ORDER BY Id);
IF @CargoDir IS NULL SET @CargoDir = @CargoOp;

INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, TipoVinculacion, FechaIngreso, FechaInicioContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
SELECT N'Prueba Operario Permisos', N'99001122', '1995-01-15', N'3001110001', u.CorreoAcceso,
    N'Calle 1', N'Medellin', N'Antioquia', N'Tecnico', N'Sura', N'Sura ARL',
    @SedeId, @CargoOp, u.Id, N'Directo', '2024-06-01', '2024-06-01', N'Activo', 0, GETUTCDATE(), u.Id
FROM dbo.Usuarios u
WHERE u.CorreoAcceso = N'prueba.operario@yopmail.com'
  AND NOT EXISTS (SELECT 1 FROM dbo.Empleados e WHERE e.UsuarioId = u.Id);

INSERT INTO dbo.Empleados (
    NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
    Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
    SedeId, CargoId, UsuarioId, TipoVinculacion, FechaIngreso, FechaInicioContrato,
    Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
SELECT N'Prueba Direccionador', N'99003344', '1992-07-08', N'3001110003', u.CorreoAcceso,
    N'Calle 3', N'Medellin', N'Antioquia', N'Tecnico', N'Sura', N'Sura ARL',
    @SedeId, @CargoDir, u.Id, N'Directo', '2023-01-01', '2023-01-01', N'Activo', 0, GETUTCDATE(), u.Id
FROM dbo.Usuarios u
WHERE u.CorreoAcceso = N'prueba.direccion@yopmail.com'
  AND NOT EXISTS (SELECT 1 FROM dbo.Empleados e WHERE e.UsuarioId = u.Id);

SELECT u.CorreoAcceso, e.Id AS EmpleadoId, e.NombreCompleto
FROM dbo.Usuarios u
LEFT JOIN dbo.Empleados e ON e.UsuarioId = u.Id
WHERE u.CorreoAcceso LIKE N'prueba.%';
GO
