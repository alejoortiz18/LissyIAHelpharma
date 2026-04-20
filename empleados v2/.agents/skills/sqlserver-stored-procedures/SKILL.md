---
name: sqlserver-stored-procedures
description: Aplica mejores prácticas para escribir Stored Procedures en SQL Server. Úsalo cuando crees, modifiques o revises SPs para garantizar seguridad, rendimiento, manejo de errores y consistencia transaccional.
metadata:
  author: custom
  version: "1.0.0"
---

# SQL Server — Stored Procedures: Mejores Prácticas

## Estructura Base Obligatoria

Todo SP debe seguir esta estructura mínima sin excepción:

```sql
CREATE OR ALTER PROCEDURE dbo.usp_[Accion][Entidad]
    @Param1   TIPO          [= DEFAULT],
    @Param2   TIPO          [= DEFAULT]
AS
BEGIN
    SET NOCOUNT ON;           -- evita mensajes "N rows affected" innecesarios
    SET XACT_ABORT ON;        -- rollback automático ante errores graves en transacciones

    -- lógica aquí

END;
GO
```

| Directiva        | Por qué es obligatoria |
|------------------|------------------------|
| `SET NOCOUNT ON` | Evita tráfico innecesario al cliente; mejora rendimiento en apps .NET |
| `SET XACT_ABORT ON` | Garantiza rollback automático si la transacción queda abierta por error |
| `CREATE OR ALTER` | Permite re-ejecutar el script sin verificar existencia previa |
| Schema `dbo.`    | Siempre calificar con schema para evitar resolución implícita |

---

## Nomenclatura

| Tipo              | Prefijo / Patrón           | Ejemplo                              |
|-------------------|----------------------------|--------------------------------------|
| Stored Procedure  | `usp_{Verbo}{Entidad}`     | `usp_ObtenerEmpleadosPorSede`        |
| Función escalar   | `ufn_{Nombre}`             | `ufn_CalcularDiasVacaciones`         |
| Función de tabla  | `uft_{Nombre}`             | `uft_EmpleadosActivosPorSede`        |
| Trigger           | `tr_{Tabla}_{Evento}`      | `tr_Empleados_AfterUpdate`           |

**Verbos estándar:** `Obtener`, `Crear`, `Actualizar`, `Desactivar`, `Activar`, `Validar`, `Calcular`, `Exportar`.

**Nunca usar** el prefijo `sp_` (está reservado por SQL Server y causa búsqueda en `master`).

---

## Manejo de Errores con TRY/CATCH

```sql
CREATE OR ALTER PROCEDURE dbo.usp_CrearEmpleado
    @NombreCompleto     NVARCHAR(200),
    @Cedula             NVARCHAR(20),
    @SedeId             INT,
    @CargoId            INT,
    @FechaIngreso       DATE,
    @TipoVinculacion    NVARCHAR(20),
    @NuevoId            INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    -- Validación de parámetros de entrada
    IF @NombreCompleto IS NULL OR LTRIM(RTRIM(@NombreCompleto)) = ''
    BEGIN
        RAISERROR('El nombre completo es obligatorio.', 16, 1);
        RETURN;
    END;

    IF EXISTS (SELECT 1 FROM dbo.Empleados WHERE Cedula = @Cedula)
    BEGIN
        RAISERROR('Ya existe un empleado con la cédula %s.', 16, 1, @Cedula);
        RETURN;
    END;

    BEGIN TRY
        BEGIN TRANSACTION;

            INSERT INTO dbo.Empleados
                (NombreCompleto, Cedula, SedeId, CargoId, FechaIngreso, TipoVinculacion, Estado, FechaCreacion)
            VALUES
                (@NombreCompleto, @Cedula, @SedeId, @CargoId, @FechaIngreso, @TipoVinculacion, 'Activo', GETUTCDATE());

            SET @NuevoId = SCOPE_IDENTITY();

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        -- Re-lanzar el error original con información de contexto
        DECLARE @Mensaje  NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @Severidad INT           = ERROR_SEVERITY();
        DECLARE @Estado    INT           = ERROR_STATE();

        RAISERROR(@Mensaje, @Severidad, @Estado);
    END CATCH;
END;
GO
```

---

## SP de Solo Lectura (SELECT)

Para queries de lectura **no usar transacciones**; usar `NOLOCK` con criterio:

```sql
CREATE OR ALTER PROCEDURE dbo.usp_ObtenerEmpleadosPorSede
    @SedeId     INT,
    @Estado     NVARCHAR(20) = 'Activo',   -- parámetro opcional con default
    @Pagina     INT          = 1,
    @TamanoPagina INT        = 25
AS
BEGIN
    SET NOCOUNT ON;

    -- Validar paginación
    IF @Pagina < 1         SET @Pagina = 1;
    IF @TamanoPagina NOT IN (10, 25, 50, 100) SET @TamanoPagina = 25;

    SELECT
        e.Id,
        e.NombreCompleto,
        e.Cedula,
        e.Estado,
        e.TipoVinculacion,
        e.FechaIngreso,
        c.Nombre        AS Cargo,
        s.Nombre        AS Sede,
        COUNT(*) OVER() AS TotalRegistros      -- para paginación en el cliente
    FROM  dbo.Empleados e
    JOIN  dbo.Cargos    c ON c.Id = e.CargoId
    JOIN  dbo.Sedes     s ON s.Id = e.SedeId
    WHERE e.SedeId = @SedeId
      AND e.Estado  = @Estado
    ORDER BY e.NombreCompleto
    OFFSET (@Pagina - 1) * @TamanoPagina ROWS
    FETCH NEXT @TamanoPagina ROWS ONLY;

END;
GO
```

**Reglas para SPs de lectura:**
- Siempre columnas explícitas — nunca `SELECT *`.
- Incluir `ORDER BY` cuando se usa `OFFSET/FETCH` (obligatorio en SQL Server).
- Pasar `@Pagina` y `@TamanoPagina` como parámetros; no paginar en la aplicación.
- Usar `COUNT(*) OVER()` para devolver el total sin una segunda consulta.

---

## SP de Actualización (UPDATE)

```sql
CREATE OR ALTER PROCEDURE dbo.usp_ActualizarEmpleado
    @Id                 INT,
    @NombreCompleto     NVARCHAR(200),
    @Telefono           NVARCHAR(20)    = NULL,
    @CorreoElectronico  NVARCHAR(256)   = NULL,
    @CargoId            INT,
    @ModificadoPor      INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF NOT EXISTS (SELECT 1 FROM dbo.Empleados WHERE Id = @Id AND Estado = 'Activo')
    BEGIN
        RAISERROR('Empleado no encontrado o inactivo.', 16, 1);
        RETURN;
    END;

    BEGIN TRY
        BEGIN TRANSACTION;

            UPDATE dbo.Empleados
            SET    NombreCompleto    = @NombreCompleto,
                   Telefono         = @Telefono,
                   CorreoElectronico = @CorreoElectronico,
                   CargoId          = @CargoId,
                   ModificadoPor    = @ModificadoPor,
                   FechaModificacion = GETUTCDATE()
            WHERE  Id = @Id;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        DECLARE @Msg NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR(@Msg, 16, 1);
    END CATCH;
END;
GO
```

---

## SP con Soft Delete (Desactivar)

```sql
CREATE OR ALTER PROCEDURE dbo.usp_DesactivarEmpleado
    @EmpleadoId         INT,
    @MotivoRetiro       NVARCHAR(500),
    @FechaDesvinculacion DATE,
    @RealizadoPor       INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF NOT EXISTS (SELECT 1 FROM dbo.Empleados WHERE Id = @EmpleadoId AND Estado = 'Activo')
    BEGIN
        RAISERROR('El empleado no existe o ya está inactivo.', 16, 1);
        RETURN;
    END;

    IF @MotivoRetiro IS NULL OR LTRIM(RTRIM(@MotivoRetiro)) = ''
    BEGIN
        RAISERROR('El motivo de retiro es obligatorio.', 16, 1);
        RETURN;
    END;

    BEGIN TRY
        BEGIN TRANSACTION;

            UPDATE dbo.Empleados
            SET    Estado           = 'Inactivo',
                   FechaModificacion = GETUTCDATE(),
                   ModificadoPor    = @RealizadoPor
            WHERE  Id = @EmpleadoId;

            -- Registrar desvinculación en tabla de historial
            INSERT INTO dbo.HistorialDesvinculaciones
                (EmpleadoId, MotivoRetiro, FechaDesvinculacion, RegistradoPor, FechaCreacion)
            VALUES
                (@EmpleadoId, @MotivoRetiro, @FechaDesvinculacion, @RealizadoPor, GETUTCDATE());

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        DECLARE @Msg NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR(@Msg, 16, 1);
    END CATCH;
END;
GO
```

---

## Validaciones de Parámetros — Reglas Fijas

```sql
-- 1. Valor obligatorio nulo o vacío
IF @Param IS NULL OR LTRIM(RTRIM(@Param)) = ''
    RAISERROR('El campo X es obligatorio.', 16, 1);

-- 2. Existencia de FK antes de insertar
IF NOT EXISTS (SELECT 1 FROM dbo.Sedes WHERE Id = @SedeId AND Estado = 'Activa')
    RAISERROR('La sede especificada no existe o está inactiva.', 16, 1);

-- 3. Duplicado unique constraint (más descriptivo que el error nativo)
IF EXISTS (SELECT 1 FROM dbo.Empleados WHERE Cedula = @Cedula)
    RAISERROR('Ya existe un empleado registrado con esa cédula.', 16, 1);

-- 4. Rango de fechas
IF @FechaFin < @FechaInicio
    RAISERROR('La fecha de fin no puede ser anterior a la fecha de inicio.', 16, 1);

-- 5. Valores de enumeración
IF @TipoVinculacion NOT IN ('Directo', 'Temporal')
    RAISERROR('Tipo de vinculación inválido. Use Directo o Temporal.', 16, 1);
```

**Severidad de errores:**
- `16` → Error de lógica de negocio (validación fallida) — manejable por la aplicación.
- `17-19` → Errores de recursos — loguear y escalar.
- `20+` → Errores críticos — terminan la conexión.

---

## Transacciones — Reglas

| Situación | Usar transacción |
|-----------|-----------------|
| INSERT + INSERT relacionados | ✅ Sí |
| INSERT + UPDATE en la misma operación | ✅ Sí |
| Solo un INSERT simple | ❌ No (overhead innecesario) |
| Solo SELECT | ❌ Nunca |
| UPDATE que afecta múltiples tablas | ✅ Sí |

```sql
-- Patrón correcto de transacción con control de @@TRANCOUNT
BEGIN TRY
    BEGIN TRANSACTION;
        -- operaciones...
    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    -- siempre re-lanzar o registrar el error
    THROW;   -- alternativa moderna a RAISERROR; re-lanza el error original íntegro
END CATCH;
```

> Usar `THROW;` (sin parámetros) en lugar de `RAISERROR` en el CATCH cuando quieres preservar el error original exacto. Usar `RAISERROR` cuando quieres personalizar el mensaje.

---

## Parámetros de Salida y Códigos de Retorno

```sql
-- Parámetro OUTPUT para devolver ID generado
CREATE OR ALTER PROCEDURE dbo.usp_CrearSede
    @Nombre     NVARCHAR(200),
    @Ciudad     NVARCHAR(100),
    @Direccion  NVARCHAR(300),
    @NuevoId    INT OUTPUT          -- ← parámetro de salida
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    INSERT INTO dbo.Sedes (Nombre, Ciudad, Direccion, Estado, FechaCreacion)
    VALUES (@Nombre, @Ciudad, @Direccion, 'Activa', GETUTCDATE());

    SET @NuevoId = SCOPE_IDENTITY();  -- siempre SCOPE_IDENTITY(), nunca @@IDENTITY
END;
GO
```

**Regla:** usar `SCOPE_IDENTITY()` para obtener el ID recién insertado; nunca `@@IDENTITY` (puede devolver ID de un trigger).

---

## Seguridad — Permisos

```sql
-- Conceder ejecución solo a los SPs, nunca SELECT directo en tablas
GRANT EXECUTE ON dbo.usp_ObtenerEmpleadosPorSede TO [AppUser];
GRANT EXECUTE ON dbo.usp_CrearEmpleado           TO [AppUser];

-- Revocar acceso directo a tablas desde la aplicación
DENY SELECT ON dbo.Empleados TO [AppUser];
```

**Principio de mínimo privilegio:** la cuenta de la aplicación (connection string) debe tener `EXECUTE` en los SPs necesarios y **nada más**. Esto además previene SQL Injection a nivel de base de datos.

---

## Checklist antes de hacer COMMIT de un SP

- [ ] `SET NOCOUNT ON` y `SET XACT_ABORT ON` al inicio
- [ ] Nombre sigue el patrón `usp_{Verbo}{Entidad}`
- [ ] Todos los parámetros validados antes de la operación principal
- [ ] `BEGIN TRY / BEGIN CATCH` con `ROLLBACK` en el CATCH (solo si hay transacción)
- [ ] `SCOPE_IDENTITY()` para obtener ID insertado (nunca `@@IDENTITY`)
- [ ] Sin `SELECT *` — siempre columnas explícitas
- [ ] Permisos de ejecución concedidos al usuario de la app
- [ ] SP probado con parámetros válidos e inválidos
