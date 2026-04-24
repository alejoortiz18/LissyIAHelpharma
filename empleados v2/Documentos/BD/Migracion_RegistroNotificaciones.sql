-- ============================================================
-- Migración: Tabla RegistroNotificaciones
-- Propósito : Auditoría de todos los intentos de envío de
--             correo realizados por INotificationService.
-- ============================================================

USE GestionRH;
GO

IF OBJECT_ID('dbo.RegistroNotificaciones', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.RegistroNotificaciones
    (
        Id              BIGINT          NOT NULL IDENTITY(1,1),
        TipoEvento      NVARCHAR(100)   NOT NULL,          -- EVT-01 … EVT-12
        DestinatarioA   NVARCHAR(254)   NOT NULL,
        DestinatarioCc  NVARCHAR(254)   NULL,
        Asunto          NVARCHAR(500)   NOT NULL,
        Exitoso         BIT             NOT NULL DEFAULT 0,
        ErrorMensaje    NVARCHAR(1000)  NULL,
        GeneradoPor     NVARCHAR(254)   NOT NULL,
        FechaEnvio      DATETIME2(0)    NOT NULL DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_RegistroNotificaciones PRIMARY KEY CLUSTERED (Id)
    );

    -- Índice para consultas de auditoría por fecha y tipo de evento
    CREATE NONCLUSTERED INDEX IX_RegistroNotificaciones_FechaEnvio
        ON dbo.RegistroNotificaciones (FechaEnvio DESC)
        INCLUDE (TipoEvento, Exitoso);

    PRINT 'Tabla RegistroNotificaciones creada.';
END
ELSE
    PRINT 'La tabla RegistroNotificaciones ya existe. No se realizaron cambios.';
GO
