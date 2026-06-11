-- =============================================================================
-- Despliegue producción: Eventos Laborales (GestionPersonal)
-- Ejecutar en la BD que usa IIS (appsettings / variable ConnectionStrings__Default)
-- Orden seguro: idempotente (se puede re-ejecutar)
-- =============================================================================
SET NOCOUNT ON;
GO

PRINT N'--- 1. Catálogo TiposSolicitud ---';
IF OBJECT_ID(N'dbo.TiposSolicitud', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.TiposSolicitud (
        Id                INT            IDENTITY(1,1) NOT NULL,
        Nombre            NVARCHAR(200)  NOT NULL,
        Codigo            NVARCHAR(50)   NOT NULL,
        EsVacaciones      BIT            NOT NULL CONSTRAINT DF_TiposSolicitud_EsVacaciones DEFAULT (0),
        Estado            NVARCHAR(20)   NOT NULL CONSTRAINT DF_TiposSolicitud_Estado DEFAULT (N'Activo'),
        FechaCreacion     DATETIME2(0)   NOT NULL CONSTRAINT DF_TiposSolicitud_FechaCreacion DEFAULT (GETUTCDATE()),
        FechaModificacion DATETIME2(0)   NULL,
        CONSTRAINT PK_TiposSolicitud PRIMARY KEY (Id),
        CONSTRAINT UX_TiposSolicitud_Codigo UNIQUE (Codigo)
    );
    PRINT N'Tabla TiposSolicitud creada.';
END
ELSE
    PRINT N'Tabla TiposSolicitud ya existe.';
GO

MERGE dbo.TiposSolicitud AS t
USING (VALUES
    (N'Vacaciones',  N'Vacaciones',  1),
    (N'Incapacidad', N'Incapacidad', 0),
    (N'Permiso',     N'Permiso',     0)
) AS s (Nombre, Codigo, EsVacaciones)
ON t.Codigo = s.Codigo
WHEN NOT MATCHED BY TARGET THEN
    INSERT (Nombre, Codigo, EsVacaciones, Estado)
    VALUES (s.Nombre, s.Codigo, s.EsVacaciones, N'Activo');
GO

PRINT N'--- 2. Columna DiasDisfrutar en EventosLaborales ---';
IF COL_LENGTH(N'dbo.EventosLaborales', N'DiasDisfrutar') IS NULL
BEGIN
    ALTER TABLE dbo.EventosLaborales ADD DiasDisfrutar INT NULL;
    PRINT N'Columna DiasDisfrutar agregada.';
END
ELSE
    PRINT N'Columna DiasDisfrutar ya existe.';
GO

PRINT N'--- 3. Ampliar TipoEvento (códigos dinámicos hasta 50) ---';
DECLARE @maxLen INT = (
    SELECT c.max_length / 2
    FROM sys.columns c
    WHERE c.object_id = OBJECT_ID(N'dbo.EventosLaborales')
      AND c.name = N'TipoEvento'
);
IF @maxLen IS NOT NULL AND @maxLen < 50
BEGIN
    ALTER TABLE dbo.EventosLaborales
        ALTER COLUMN TipoEvento NVARCHAR(50) NOT NULL;
    PRINT N'TipoEvento ampliado a NVARCHAR(50).';
END
ELSE
    PRINT N'TipoEvento ya tiene longitud >= 50.';
GO

PRINT N'--- 4. Quitar CHECK fijo de tipos (Vacaciones/Incapacidad/Permiso) ---';
IF EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE name = N'CK_Eventos_TipoEvento'
      AND parent_object_id = OBJECT_ID(N'dbo.EventosLaborales'))
BEGIN
    ALTER TABLE dbo.EventosLaborales DROP CONSTRAINT CK_Eventos_TipoEvento;
    PRINT N'CK_Eventos_TipoEvento eliminado.';
END
ELSE
    PRINT N'CK_Eventos_TipoEvento no existe (OK).';
GO

PRINT N'--- 5. Ampliar CHECK de Estado (solicitudes Pendiente/Aprobado/...) ---';
IF EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE name = N'CK_Eventos_Estado'
      AND parent_object_id = OBJECT_ID(N'dbo.EventosLaborales'))
BEGIN
    ALTER TABLE dbo.EventosLaborales DROP CONSTRAINT CK_Eventos_Estado;
END
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE name = N'CK_Eventos_Estado'
      AND parent_object_id = OBJECT_ID(N'dbo.EventosLaborales'))
BEGIN
    ALTER TABLE dbo.EventosLaborales
    ADD CONSTRAINT CK_Eventos_Estado
    CHECK (Estado IN (
        N'Activo', N'Finalizado', N'Anulado',
        N'Pendiente', N'Aprobado', N'Rechazado', N'Cancelado', N'EnRevision'));
    PRINT N'CK_Eventos_Estado recreado con estados ampliados.';
END
GO

PRINT N'--- 6. Verificación ---';
SELECT N'TiposSolicitud' AS Objeto, COUNT(*) AS Filas FROM dbo.TiposSolicitud
UNION ALL
SELECT N'EventosLaborales', COUNT(*) FROM dbo.EventosLaborales;

SELECT c.name AS Columna, t.name AS Tipo, c.max_length / 2 AS MaxChars
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
WHERE c.object_id = OBJECT_ID(N'dbo.EventosLaborales')
  AND c.name IN (N'TipoEvento', N'DiasDisfrutar', N'Estado');

SELECT name AS CheckConstraint
FROM sys.check_constraints
WHERE parent_object_id = OBJECT_ID(N'dbo.EventosLaborales');
GO

PRINT N'Despliegue Eventos Laborales completado.';
GO
