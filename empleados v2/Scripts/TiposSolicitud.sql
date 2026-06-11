-- Catálogo de tipos de solicitud laboral (ejecutar en base GestionPersonal)
IF OBJECT_ID(N'dbo.TiposSolicitud', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.TiposSolicitud (
        Id              INT            IDENTITY(1,1) NOT NULL,
        Nombre          NVARCHAR(200)  NOT NULL,
        Codigo          NVARCHAR(50)   NOT NULL,
        EsVacaciones    BIT            NOT NULL CONSTRAINT DF_TiposSolicitud_EsVacaciones DEFAULT (0),
        Estado          NVARCHAR(20)   NOT NULL CONSTRAINT DF_TiposSolicitud_Estado DEFAULT (N'Activo'),
        FechaCreacion   DATETIME2(0)   NOT NULL CONSTRAINT DF_TiposSolicitud_FechaCreacion DEFAULT (GETUTCDATE()),
        FechaModificacion DATETIME2(0) NULL,
        CONSTRAINT PK_TiposSolicitud PRIMARY KEY (Id),
        CONSTRAINT UX_TiposSolicitud_Codigo UNIQUE (Codigo)
    );
END
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
