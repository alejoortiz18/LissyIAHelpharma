-- ============================================================
-- Migración: TokensRecuperacion — columna Token a SHA-256
-- Propósito : Los tokens de recuperación se almacenan como
--             hash SHA-256 (hex de 64 chars) en lugar de
--             texto plano. El código plano solo se envía
--             por correo al usuario.
-- ⚠ IMPORTANTE: Esta migración invalida todos los tokens
--   activos existentes. Ejecutar en ventana de mantenimiento.
-- ============================================================

USE GestionRH;
GO

-- 1. Ampliar la columna si actualmente es NVARCHAR(<64)
IF EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME  = 'TokensRecuperacion'
      AND COLUMN_NAME = 'Token'
      AND CHARACTER_MAXIMUM_LENGTH < 64)
BEGIN
    ALTER TABLE dbo.TokensRecuperacion
        ALTER COLUMN Token NVARCHAR(64) NOT NULL;

    PRINT 'Columna Token ampliada a NVARCHAR(64).';
END
ELSE
    PRINT 'Columna Token ya tiene el tamaño correcto (≥ 64). No se modificó.';
GO

-- 2. Invalidar tokens en texto plano que ya no sean válidos
--    (longitud distinta de 64 = no son hashes SHA-256)
UPDATE dbo.TokensRecuperacion
   SET Usado = 1
 WHERE LEN(Token) <> 64;

PRINT CONCAT(@@ROWCOUNT, ' token(s) en texto plano marcados como usados (invalidados).');
GO

-- 3. Índice de búsqueda rápida por token activo
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID('dbo.TokensRecuperacion')
      AND name = 'IX_TokensRecuperacion_Token_Activo')
BEGIN
    CREATE NONCLUSTERED INDEX IX_TokensRecuperacion_Token_Activo
        ON dbo.TokensRecuperacion (Token)
        WHERE Usado = 0;

    PRINT 'Índice IX_TokensRecuperacion_Token_Activo creado.';
END
ELSE
    PRINT 'Índice IX_TokensRecuperacion_Token_Activo ya existe.';
GO
