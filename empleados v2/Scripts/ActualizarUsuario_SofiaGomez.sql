-- Usuario: sofia.gomez@yopmail.com | Rol: Analista | Contraseña: Yopmail2026
-- PBKDF2-SHA256, 10000 iteraciones (mismo algoritmo que PasswordHelper.cs)
USE GestionPersonal;
GO

DECLARE @Correo NVARCHAR(200) = N'sofia.gomez@yopmail.com';
DECLARE @PwdHash VARBINARY(32) = 0x0ACE2EA8F9EAAF0937919AA1D83C40DBB314433B719F34130A1676AD8EB25D0F;
DECLARE @PwdSalt VARBINARY(16) = 0xAD2D450B0ACDAC54662654D1A8102A2C;

UPDATE dbo.Usuarios
SET PasswordHash        = @PwdHash,
    PasswordSalt        = @PwdSalt,
    Rol                 = N'Analista',
    Estado              = N'Activo',
    DebecambiarPassword = 0,
    FechaModificacion   = GETUTCDATE()
WHERE CorreoAcceso = @Correo;

IF @@ROWCOUNT = 0
BEGIN
    RAISERROR('No existe el usuario sofia.gomez@yopmail.com. Ejecute antes Seeding_Completo.sql.', 16, 1);
    RETURN;
END

-- Permisos de Maestros / catálogos para el rol Analista
DECLARE @RolId INT = (SELECT Id FROM dbo.RolesSistema WHERE Codigo = N'Analista');

IF @RolId IS NOT NULL
BEGIN
    INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId)
    SELECT @RolId, p.Id
    FROM dbo.PermisosPlataforma p
    WHERE p.Codigo IN (N'Catalogos.Ver', N'Catalogos.Editar')
      AND NOT EXISTS (
          SELECT 1 FROM dbo.RolesSistemaPermisos rsp
          WHERE rsp.RolSistemaId = @RolId AND rsp.PermisoId = p.Id
      );
END

PRINT N'Usuario actualizado. Cierre sesión y vuelva a entrar con Yopmail2026.';
GO
