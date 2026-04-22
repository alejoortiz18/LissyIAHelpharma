-- ============================================================
-- MIGRACIÓN: Ampliar columnas de password a VARBINARY(256)
--            y actualizar todas las contraseñas a "Admin2026"
--            (hash PBKDF2/SHA256, 10000 iteraciones)
--
-- Base de datos: GestionPersonal (LocalDB)
-- Ejecutar UNA sola vez sobre la BD ya existente.
-- ============================================================

USE GestionPersonal;
GO

-- 1. Ampliar columnas (de 64/128 a 256 bytes)
ALTER TABLE dbo.Usuarios
    ALTER COLUMN PasswordHash VARBINARY(256) NOT NULL;
GO

ALTER TABLE dbo.Usuarios
    ALTER COLUMN PasswordSalt VARBINARY(256) NOT NULL;
GO

-- 2. Actualizar TODOS los usuarios con el nuevo hash de "Admin2026"
--    Algoritmo: PBKDF2/SHA256 | Iteraciones: 10000
--    Hash : 32 bytes  | Salt : 16 bytes
DECLARE @PwdHash VARBINARY(256) = 0xC678F46EA40B0B419C75AA263AD9D2BDA049A9CF38AD4383D009407D51660AFB;
DECLARE @PwdSalt VARBINARY(256) = 0xE9119DF914288643380C5EB9CD4404CD;

UPDATE dbo.Usuarios
SET PasswordHash = @PwdHash,
    PasswordSalt = @PwdSalt;
GO

-- 3. Verificar resultado
SELECT Id, CorreoAcceso, Rol,
       LEN(PasswordHash) AS BytesHash,
       LEN(PasswordSalt) AS BytesSalt,
       Estado
FROM dbo.Usuarios;
GO
