-- Analista: todos los permisos de plataforma
USE GestionPersonal;
GO

DECLARE @RolId INT = (SELECT Id FROM dbo.RolesSistema WHERE Codigo = N'Analista');
IF @RolId IS NULL
BEGIN
    RAISERROR(N'No existe el rol Analista.', 16, 1);
    RETURN;
END

DELETE FROM dbo.RolesSistemaPermisos WHERE RolSistemaId = @RolId;

INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId)
SELECT @RolId, p.Id FROM dbo.PermisosPlataforma p;

SELECT COUNT(*) AS PermisosAnalista
FROM dbo.RolesSistemaPermisos rsp
WHERE rsp.RolSistemaId = @RolId;
GO
