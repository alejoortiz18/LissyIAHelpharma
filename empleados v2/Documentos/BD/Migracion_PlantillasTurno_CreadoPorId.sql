-- ============================================================
-- Migración: Agregar columna CreadoPorId a dbo.PlantillasTurno
-- Requerimiento: Control jerárquico de plantillas de horario
-- Fecha: 2026-04-29
-- ============================================================

-- 1. Agregar columna CreadoPorId (nullable) con FK a Empleados
ALTER TABLE dbo.PlantillasTurno
    ADD CreadoPorId INT NULL
        CONSTRAINT FK_PlantillasTurno_Empleados_CreadoPorId
            FOREIGN KEY REFERENCES dbo.Empleados(Id)
            ON DELETE SET NULL;
GO

-- 2. Migración de datos: asignar plantillas existentes (CreadoPorId NULL)
--    al primer usuario Administrador registrado (para no perder datos)
DECLARE @AdminEmpleadoId INT;

SELECT TOP 1 @AdminEmpleadoId = e.Id
FROM dbo.Empleados e
INNER JOIN dbo.Usuarios u ON u.Id = e.UsuarioId
WHERE u.Rol = 'Administrador'
ORDER BY e.Id ASC;

IF @AdminEmpleadoId IS NOT NULL
BEGIN
    UPDATE dbo.PlantillasTurno
    SET CreadoPorId = @AdminEmpleadoId
    WHERE CreadoPorId IS NULL;

    PRINT 'Plantillas existentes asignadas al EmpleadoId = ' + CAST(@AdminEmpleadoId AS NVARCHAR);
END
ELSE
    PRINT 'No se encontró administrador. Las plantillas existentes quedan con CreadoPorId = NULL.';
GO
