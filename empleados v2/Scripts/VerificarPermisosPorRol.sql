-- Consulta permisos asignados por rol (validar RolesSistemaPermisos)
USE GestionPersonal;
GO

SELECT r.Codigo AS RolCodigo, r.Nombre AS RolNombre, r.Estado AS RolEstado,
       p.Codigo AS PermisoCodigo, p.Modulo
FROM dbo.RolesSistema r
INNER JOIN dbo.RolesSistemaPermisos rsp ON rsp.RolSistemaId = r.Id
INNER JOIN dbo.PermisosPlataforma p ON p.Id = rsp.PermisoId
ORDER BY r.Codigo, p.Modulo, p.Orden;
GO

-- Permisos de un usuario concreto (cambiar correo)
DECLARE @Correo NVARCHAR(200) = N'sofia.gomez@yopmail.com';

SELECT u.CorreoAcceso, u.Rol AS RolUsuario, r.Codigo AS RolSistemaCodigo, p.Codigo AS Permiso
FROM dbo.Usuarios u
LEFT JOIN dbo.RolesSistema r ON r.Codigo = CAST(u.Rol AS NVARCHAR(50)) AND r.Estado = N'Activo'
LEFT JOIN dbo.RolesSistemaPermisos rsp ON rsp.RolSistemaId = r.Id
LEFT JOIN dbo.PermisosPlataforma p ON p.Id = rsp.PermisoId
WHERE u.CorreoAcceso = @Correo
ORDER BY p.Modulo, p.Orden;
GO
