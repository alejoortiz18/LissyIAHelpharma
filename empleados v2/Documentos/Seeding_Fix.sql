-- ============================================================
-- FIX SEEDING — Corrige los 3 empleados que fallaron por
-- acentos en NivelEscolaridad (Técnico → Tecnico,
-- Tecnológico → Tecnologico) y limpia contactos huérfanos.
-- ============================================================
USE GestionPersonal;
GO
SET QUOTED_IDENTIFIER ON;
GO

-- ── Variables de referencia ──────────────────────────────────
DECLARE @SedeId         INT = (SELECT Id FROM dbo.Sedes    WHERE Nombre = N'Sede Medellín');
DECLARE @EmpRegente1    INT = (SELECT Id FROM dbo.Empleados WHERE Cedula = N'20345678'); -- Laura
DECLARE @EmpRegente2    INT = (SELECT Id FROM dbo.Empleados WHERE Cedula = N'30456789'); -- Hernán
DECLARE @UsuJefe        INT = (SELECT Id FROM dbo.Usuarios  WHERE CorreoAcceso = N'carlos.rodriguez@yopmail.com');
DECLARE @UsuAuxiliar    INT = (SELECT Id FROM dbo.Usuarios  WHERE CorreoAcceso = N'andres.torres@yopmail.com');
DECLARE @UsuOp2         INT = (SELECT Id FROM dbo.Usuarios  WHERE CorreoAcceso = N'valentina.ospina@yopmail.com');
DECLARE @UsuOp5         INT = (SELECT Id FROM dbo.Usuarios  WHERE CorreoAcceso = N'paula.quintero@yopmail.com');
DECLARE @PlantillaId    INT = (SELECT TOP 1 Id FROM dbo.PlantillasTurno WHERE Nombre = N'Turno Estándar Lunes-Viernes');
DECLARE @EmpAdecco      INT = (SELECT Id FROM dbo.EmpresasTemporales WHERE Nombre = N'Adecco Colombia S.A.');
DECLARE @EmpManpower    INT = (SELECT Id FROM dbo.EmpresasTemporales WHERE Nombre = N'ManpowerGroup Colombia');

DECLARE @CargoAuxiliar  INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Auxiliar de Farmacia');
DECLARE @CargoAsesor    INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Asesor(a) Comercial');
DECLARE @CargoCajero    INT = (SELECT Id FROM dbo.Cargos WHERE Nombre = N'Cajero(a)');

DECLARE @PwdHash VARBINARY(64)  = 0x9FC07960FA39D8E355209CD3827CF482E45840340EFBC01C946D0DA4F1B721E1314F7E0D5E624503E0C4EAF9D69FF06D9E03A8E811D1B442B72FB60C09E05E90;
DECLARE @PwdSalt VARBINARY(128) = 0x32C63A58F759B94AF63953537A66EFFAC742F0E522CB309BE0DBF26DCDA5DFE6D193A5D891B441E7E796070DC933D5B2F32173C81D2264D3E19468CEF3A79745002539DC8B2C5C8C90A4DB77E675782F24476AFF81A646EA5225720F6B9B04DCB58C11CDCF3F697E72C6FDEC2079229A13C54DEAD431E89967FB6A458CBA87D9;

-- ── 1. Eliminar contactos huérfanos (EmpleadoId de empleados que
--       no existen porque su INSERT falló). Dejar solo el
--       primer contacto por empleado cuando hay duplicados. ────
;WITH ranked AS (
    SELECT Id,
           ROW_NUMBER() OVER (PARTITION BY EmpleadoId ORDER BY Id) AS rn
    FROM   dbo.ContactosEmergencia
)
DELETE FROM dbo.ContactosEmergencia
WHERE Id IN (SELECT Id FROM ranked WHERE rn > 1);

-- ── 2. Insertar los 3 empleados faltantes ────────────────────

-- 2a. Andrés Torres — AuxiliarRegente bajo Regente 1 (Tecnico sin tilde)
IF NOT EXISTS (SELECT 1 FROM dbo.Empleados WHERE Cedula = N'40567890')
BEGIN
    INSERT INTO dbo.Empleados (
        NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
        Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
        SedeId, CargoId, UsuarioId, JefeInmediatoId,
        TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
        Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
    VALUES (
        N'Andrés Felipe Torres Ruiz', N'40567890', '1995-11-05', N'3178901234', N'andres.torres@yopmail.com',
        N'Cll 50 Sur #43-25', N'Medellín', N'Antioquia', N'Tecnico', N'Sura EPS', N'Sura ARL',
        @SedeId, @CargoAuxiliar, @UsuAuxiliar, @EmpRegente1,
        N'Directo', '2022-04-01', NULL, NULL, NULL,
        N'Activo', 0.0, GETUTCDATE(), @UsuJefe);

    INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
    VALUES (SCOPE_IDENTITY(), N'Clara Torres', N'3189012345');

    INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
    VALUES (SCOPE_IDENTITY(), @PlantillaId, '2025-01-01', @UsuJefe, GETUTCDATE());
END;

-- 2b. Valentina Ospina — Operario bajo Regente 1, temporal Adecco (Tecnologico sin tilde)
IF NOT EXISTS (SELECT 1 FROM dbo.Empleados WHERE Cedula = N'60789012')
BEGIN
    INSERT INTO dbo.Empleados (
        NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
        Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
        SedeId, CargoId, UsuarioId, JefeInmediatoId,
        TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
        Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
    VALUES (
        N'Valentina Ospina Restrepo', N'60789012', '1993-04-12', N'3212345678', N'valentina.ospina@yopmail.com',
        N'Cll 10 Sur #43-25', N'Medellín', N'Antioquia', N'Tecnologico', N'Comfama', N'AXA Colpatria',
        @SedeId, @CargoAsesor, @UsuOp2, @EmpRegente1,
        N'Temporal', '2025-01-01', @EmpAdecco, '2025-01-01', '2025-12-31',
        N'Activo', 0.0, GETUTCDATE(), @UsuJefe);

    INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
    VALUES (SCOPE_IDENTITY(), N'Luis Ospina', N'3223456789');

    INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
    VALUES (SCOPE_IDENTITY(), @PlantillaId, '2025-01-01', @UsuJefe, GETUTCDATE());
END;

-- 2c. Paula Quintero — Operario bajo Regente 2, temporal ManpowerGroup (Tecnico sin tilde)
IF NOT EXISTS (SELECT 1 FROM dbo.Empleados WHERE Cedula = N'91012345')
BEGIN
    INSERT INTO dbo.Empleados (
        NombreCompleto, Cedula, FechaNacimiento, Telefono, CorreoElectronico,
        Direccion, Ciudad, Departamento, NivelEscolaridad, Eps, Arl,
        SedeId, CargoId, UsuarioId, JefeInmediatoId,
        TipoVinculacion, FechaIngreso, EmpresaTemporalId, FechaInicioContrato, FechaFinContrato,
        Estado, DiasVacacionesPrevios, FechaCreacion, CreadoPor)
    VALUES (
        N'Paula Andrea Quintero Ríos', N'91012345', '1997-05-20', N'3278901234', N'paula.quintero@yopmail.com',
        N'Cra 70 #34-15', N'Medellín', N'Antioquia', N'Tecnico', N'Comfama', N'Sura ARL',
        @SedeId, @CargoCajero, @UsuOp5, @EmpRegente2,
        N'Temporal', '2025-03-01', @EmpManpower, '2025-03-01', '2025-12-31',
        N'Activo', 0.0, GETUTCDATE(), @UsuJefe);

    INSERT INTO dbo.ContactosEmergencia (EmpleadoId, NombreContacto, TelefonoContacto)
    VALUES (SCOPE_IDENTITY(), N'Ricardo Quintero', N'3289012345');

    INSERT INTO dbo.AsignacionesTurno (EmpleadoId, PlantillaTurnoId, FechaVigencia, ProgramadoPor, FechaCreacion)
    VALUES (SCOPE_IDENTITY(), @PlantillaId, '2025-01-01', @UsuJefe, GETUTCDATE());
END;

-- ── 3. Verificación final ─────────────────────────────────────
SELECT 'Sedes'              AS Tabla, COUNT(*) AS Total FROM dbo.Sedes
UNION ALL SELECT 'Cargos',              COUNT(*) FROM dbo.Cargos
UNION ALL SELECT 'EmpresasTemporales',  COUNT(*) FROM dbo.EmpresasTemporales
UNION ALL SELECT 'Usuarios',            COUNT(*) FROM dbo.Usuarios
UNION ALL SELECT 'Empleados',           COUNT(*) FROM dbo.Empleados
UNION ALL SELECT 'ContactosEmergencia', COUNT(*) FROM dbo.ContactosEmergencia
UNION ALL SELECT 'AsignacionesTurno',   COUNT(*) FROM dbo.AsignacionesTurno;

SELECT e.Id, e.NombreCompleto, e.Cedula, e.NivelEscolaridad, e.TipoVinculacion,
       u.CorreoAcceso, u.Rol,
       jefe.NombreCompleto AS JefeInmediato
FROM   dbo.Empleados e
JOIN   dbo.Usuarios  u    ON u.Id = e.UsuarioId
LEFT JOIN dbo.Empleados jefe ON jefe.Id = e.JefeInmediatoId
ORDER BY e.Id;
GO
