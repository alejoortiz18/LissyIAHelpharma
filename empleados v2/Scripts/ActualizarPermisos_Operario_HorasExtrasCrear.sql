-- Añade HorasExtras.Crear al rol Operario (si falta en BD)
USE GestionPersonal;
GO

DECLARE @RolId INT = (SELECT Id FROM dbo.RolesSistema WHERE Codigo = N'Operario');
DECLARE @PermisoId INT = (SELECT Id FROM dbo.PermisosPlataforma WHERE Codigo = N'HorasExtras.Crear');

IF @RolId IS NULL OR @PermisoId IS NULL
BEGIN
    RAISERROR(N'No se encontró rol Operario o permiso HorasExtras.Crear.', 16, 1);
    RETURN;
END

IF NOT EXISTS (SELECT 1 FROM dbo.RolesSistemaPermisos WHERE RolSistemaId = @RolId AND PermisoId = @PermisoId)
    INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId) VALUES (@RolId, @PermisoId);

SELECT p.Codigo
FROM dbo.RolesSistemaPermisos rsp
JOIN dbo.PermisosPlataforma p ON p.Id = rsp.PermisoId
WHERE rsp.RolSistemaId = @RolId
ORDER BY p.Codigo;
GO
