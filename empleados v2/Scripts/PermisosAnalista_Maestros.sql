-- Analista: todos los permisos de plataforma (Maestros incluido)
USE GestionPersonal;
GO

DECLARE @RolId INT = (SELECT Id FROM dbo.RolesSistema WHERE Codigo = N'Analista');

IF @RolId IS NULL
BEGIN
    RAISERROR('No existe el rol Analista en RolesSistema.', 16, 1);
    RETURN;
END

DELETE FROM dbo.RolesSistemaPermisos WHERE RolSistemaId = @RolId;

INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId)
SELECT @RolId, p.Id FROM dbo.PermisosPlataforma p;
GO
