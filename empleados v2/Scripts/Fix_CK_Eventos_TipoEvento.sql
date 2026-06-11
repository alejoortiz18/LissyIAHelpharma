-- Permite tipos de evento dinámicos definidos en dbo.TiposSolicitud (Maestros).
-- El CHECK original solo admitía Vacaciones, Incapacidad y Permiso.
USE GestionPersonal;
GO

IF EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE name = N'CK_Eventos_TipoEvento'
      AND parent_object_id = OBJECT_ID(N'dbo.EventosLaborales'))
BEGIN
    ALTER TABLE dbo.EventosLaborales DROP CONSTRAINT CK_Eventos_TipoEvento;
    PRINT N'Constraint CK_Eventos_TipoEvento eliminado.';
END
GO

-- La validación de códigos activos queda en CatalogoService / EventoLaboralService.
