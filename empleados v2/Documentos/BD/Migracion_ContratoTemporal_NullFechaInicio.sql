-- ============================================================
-- Migración: Contrato Temporal → FechaInicioContrato = NULL
-- Fecha: 2026-04-26
-- Motivo: Nueva regla de negocio: los empleados Temporales
--         NO tienen FechaInicioContrato (solo aplica a Directos).
--         Se actualiza CK_Empleados_ContratoTemp para quitar
--         AND FechaInicioContrato IS NOT NULL del caso Temporal.
--         Se actualiza CK_Empleados_FechasContrato para que la
--         comparación de fechas sea válida cuando FechaInicioContrato
--         es NULL.
-- ============================================================

-- 1. Actualizar CK_Empleados_ContratoTemp
ALTER TABLE dbo.Empleados DROP CONSTRAINT CK_Empleados_ContratoTemp;
GO

ALTER TABLE dbo.Empleados ADD CONSTRAINT CK_Empleados_ContratoTemp CHECK (
    TipoVinculacion = 'Directo'
    OR (
        TipoVinculacion = 'Temporal'
        AND EmpresaTemporalId IS NOT NULL
        AND FechaFinContrato   IS NOT NULL
    )
);
GO

-- 2. Actualizar CK_Empleados_FechasContrato
--    Antes: FechaFinContrato IS NULL OR FechaFinContrato >= FechaInicioContrato
--    Ahora: también se permite FechaInicioContrato NULL (empleados Temporales)
ALTER TABLE dbo.Empleados DROP CONSTRAINT CK_Empleados_FechasContrato;
GO

ALTER TABLE dbo.Empleados ADD CONSTRAINT CK_Empleados_FechasContrato CHECK (
    FechaFinContrato IS NULL
    OR FechaInicioContrato IS NULL
    OR FechaFinContrato >= FechaInicioContrato
);
GO
