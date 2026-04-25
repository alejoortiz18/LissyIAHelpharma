-- ============================================================
-- Migración: Ampliar CHECK CONSTRAINT de EstadoEvento
-- Tabla: dbo.EventosLaborales
-- Nuevos valores: Pendiente, Aprobado, Rechazado, Cancelado, EnRevision
-- Generada: 2026-04-25
-- ============================================================

-- Eliminar el constraint existente (ajusta el nombre si es diferente)
IF EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE name = 'CK_Eventos_Estado'
      AND parent_object_id = OBJECT_ID('dbo.EventosLaborales')
)
    ALTER TABLE dbo.EventosLaborales DROP CONSTRAINT CK_Eventos_Estado;
GO

-- Recrear con todos los valores válidos
ALTER TABLE dbo.EventosLaborales
ADD CONSTRAINT CK_Eventos_Estado
CHECK (Estado IN ('Activo','Finalizado','Anulado','Pendiente','Aprobado','Rechazado','Cancelado','EnRevision'));
GO
