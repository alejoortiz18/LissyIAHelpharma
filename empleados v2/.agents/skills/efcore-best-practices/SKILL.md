---
name: efcore-best-practices
description: Aplica mejores prácticas de Entity Framework Core en proyectos .NET. Úsalo cuando configures DbContext, escribas queries LINQ, crees migraciones, relaciones entre entidades o manejes transacciones.
metadata:
  author: custom
  version: "1.0.0"
---

# Entity Framework Core — Mejores Prácticas

Guía de patrones y convenciones para EF Core en proyectos ASP.NET Core MVC con SQL Server.

## Configuración del DbContext

Usa `IEntityTypeConfiguration<T>` para cada entidad en lugar de configurar en `OnModelCreating`:

```csharp
// Infrastructure/Data/AppDbContext.cs
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Empleado> Empleados => Set<Empleado>();
    public DbSet<Sede> Sedes => Set<Sede>();
    public DbSet<Cargo> Cargos => Set<Cargo>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
    }
}
```

## Configuración de Entidades

```csharp
// Infrastructure/Data/Configurations/EmpleadoConfiguration.cs
public class EmpleadoConfiguration : IEntityTypeConfiguration<Empleado>
{
    public void Configure(EntityTypeBuilder<Empleado> builder)
    {
        builder.ToTable("Empleados");
        builder.HasKey(e => e.Id);

        builder.Property(e => e.NombreCompleto)
            .IsRequired()
            .HasMaxLength(200);

        builder.Property(e => e.Cedula)
            .IsRequired()
            .HasMaxLength(20);

        builder.HasIndex(e => e.Cedula)
            .IsUnique()
            .HasDatabaseName("IX_Empleados_Cedula");

        builder.Property(e => e.Estado)
            .HasConversion<string>()   // guarda el enum como string legible
            .HasMaxLength(20)
            .IsRequired();

        // Relaciones
        builder.HasOne(e => e.Sede)
            .WithMany(s => s.Empleados)
            .HasForeignKey(e => e.SedeId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasOne(e => e.Cargo)
            .WithMany(c => c.Empleados)
            .HasForeignKey(e => e.CargoId)
            .OnDelete(DeleteBehavior.Restrict);
    }
}
```

## Patrones de Query

### Carga explícita (preferida para listas)
```csharp
// Projection → evita cargar columnas innecesarias
var empleados = await _context.Empleados
    .Where(e => e.SedeId == sedeId && e.Estado == EstadoEmpleado.Activo)
    .Select(e => new EmpleadoDto
    {
        Id        = e.Id,
        Nombre    = e.NombreCompleto,
        Cargo     = e.Cargo.Nombre,
        Estado    = e.Estado.ToString()
    })
    .AsNoTracking()          // solo lectura → más rápido
    .ToListAsync(cancellationToken);
```

### Carga por Id con includes
```csharp
var empleado = await _context.Empleados
    .Include(e => e.Sede)
    .Include(e => e.Cargo)
    .FirstOrDefaultAsync(e => e.Id == id, cancellationToken);
```

### Reglas de querying
- Usar `.AsNoTracking()` en todas las queries de **solo lectura**.
- Siempre pasar `CancellationToken` a los métodos async.
- Preferir **projections** (`.Select(...)`) en lugar de `.Include()` para listados.
- Evitar `.ToList()` antes de filtrar; los filtros deben ejecutarse en SQL.
- **No** usar `.Find()` en queries complejas; usar `.FirstOrDefaultAsync()`.

## Migraciones

```bash
# Agregar nueva migración (desde la raíz de la solución)
dotnet ef migrations add NombreMigracion --project NombreProyecto.Infrastructure --startup-project NombreProyecto.Web

# Aplicar migraciones a la base de datos
dotnet ef database update --project NombreProyecto.Infrastructure --startup-project NombreProyecto.Web

# Revertir última migración
dotnet ef migrations remove --project NombreProyecto.Infrastructure --startup-project NombreProyecto.Web
```

### Convenciones para migraciones
- Nombres descriptivos en PascalCase: `AgregarTablaTurnos`, `AgregarCampoFechaRetiro`.
- Una migración por feature o cambio cohesivo; no acumular cambios no relacionados.
- **Nunca** modificar migraciones ya aplicadas en producción; crear una nueva.
- Revisar el SQL generado con `dotnet ef migrations script` antes de aplicar en producción.

## Transacciones

Usa transacciones explícitas solo cuando necesitas atomicidad entre múltiples operaciones:

```csharp
await using var transaction = await _context.Database.BeginTransactionAsync(cancellationToken);
try
{
    _context.Empleados.Add(nuevoEmpleado);
    await _context.SaveChangesAsync(cancellationToken);

    historial.EmpleadoId = nuevoEmpleado.Id;
    _context.Historiales.Add(historial);
    await _context.SaveChangesAsync(cancellationToken);

    await transaction.CommitAsync(cancellationToken);
}
catch
{
    await transaction.RollbackAsync(cancellationToken);
    throw;
}
```

## Patrón Repository

```csharp
// Domain/Interfaces/IEmpleadoRepository.cs
public interface IEmpleadoRepository
{
    Task<Empleado?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<Empleado>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default);
    void Agregar(Empleado empleado);
    void Actualizar(Empleado empleado);
    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}

// Infrastructure/Repositories/EmpleadoRepository.cs
public class EmpleadoRepository : IEmpleadoRepository
{
    private readonly AppDbContext _context;
    public EmpleadoRepository(AppDbContext context) => _context = context;

    public async Task<Empleado?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => await _context.Empleados
            .Include(e => e.Sede)
            .Include(e => e.Cargo)
            .FirstOrDefaultAsync(e => e.Id == id, ct);

    public async Task<IReadOnlyList<Empleado>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default)
        => await _context.Empleados
            .Where(e => e.SedeId == sedeId && e.Estado == EstadoEmpleado.Activo)
            .AsNoTracking()
            .ToListAsync(ct);

    public void Agregar(Empleado empleado) => _context.Empleados.Add(empleado);
    public void Actualizar(Empleado empleado) => _context.Empleados.Update(empleado);

    public Task<int> GuardarCambiosAsync(CancellationToken ct = default)
        => _context.SaveChangesAsync(ct);
}
```

## Errores Comunes a Evitar

| Error | Problema | Solución |
|-------|----------|----------|
| `N+1 queries` | Loop con `.Find()` o navegación lazy dentro de un foreach | Proyectar con `.Select()` o usar `.Include()` antes del loop |
| `DbContext` singleton | Conflictos de concurrencia en multi-request | Registrar siempre como `Scoped` |
| `SaveChanges` en el repositorio por cada operación | Pérdida de atomicidad | Llamar `SaveChangesAsync` una sola vez al final de la operación |
| `Include` en cadena profunda | Queries lentos y datos innecesarios | Usar projections (`.Select`) para datos de solo lectura |
| Lazy loading habilitado | Queries inesperados y difíciles de detectar | Mantener lazy loading **deshabilitado** (por defecto en EF Core) |

## Connection String en appsettings.json

```json
{
  "ConnectionStrings": {
    "Default": "Server=localhost;Database=GestionRH;Trusted_Connection=True;MultipleActiveResultSets=true;TrustServerCertificate=True"
  }
}
```

Registro en `Program.cs`:
```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(
        builder.Configuration.GetConnectionString("Default"),
        sql => sql.MigrationsAssembly("NombreProyecto.Infrastructure")));
```
