# Arquitectura — Sistema de Administración de Empleados

> **Stack:** ASP.NET Core MVC (.NET 10) · Entity Framework Core · SQL Server (`GestionPersonal`)  
> **Patrón:** Arquitectura en capas · Sin APIs REST · Cookie Authentication  
> **Metodología:** Shape Up — 6 pitches definidos  
> **Fecha:** Abril 2026

---

## 1. Estructura de la Solución

```
GestionPersonal.sln
├── GestionPersonal.Web/                  ← Presentación (MVC, Views, ViewModels)
│   ├── Controllers/
│   │   ├── CuentaController.cs           → Login, Logout, CambiarPassword, RecuperarPassword
│   │   ├── DashboardController.cs        → Vista consolidada del Jefe (Pitch 6)
│   │   ├── EmpleadoController.cs         → CRUD empleados activos (Pitch 1)
│   │   ├── EmpleadoDesvinculadoController.cs → Vista solo-lectura desvinculados (Pitch 1)
│   │   ├── EventoLaboralController.cs    → Vacaciones, Incapacidades, Permisos (Pitch 2)
│   │   ├── HoraExtraController.cs        → Solicitudes y aprobación HE (Pitch 4)
│   │   ├── TurnoController.cs            → Plantillas y asignación de turnos (Pitch 3)
│   │   └── Catalogos/
│   │       ├── SedeController.cs         → ABM Sedes (solo Jefe)
│   │       ├── CargoController.cs        → ABM Cargos (solo Jefe)
│   │       └── EmpresaTemporalController.cs → ABM Empresas Temporales (solo Jefe)
│   ├── Views/
│   │   ├── Shared/
│   │   │   ├── _Layout.cshtml
│   │   │   ├── _LayoutLogin.cshtml
│   │   │   └── _ValidationScripts.cshtml
│   │   ├── Cuenta/
│   │   │   ├── Login.cshtml
│   │   │   ├── CambiarPassword.cshtml
│   │   │   └── RecuperarPassword.cshtml
│   │   ├── Dashboard/
│   │   │   └── Index.cshtml              → Tarjetas + acordeones
│   │   ├── Empleado/
│   │   │   ├── Index.cshtml              → Lista activos con paginación
│   │   │   ├── Desvinculados.cshtml      → Lista inactivos solo-lectura
│   │   │   ├── Crear.cshtml
│   │   │   ├── Editar.cshtml
│   │   │   └── Perfil.cshtml             → Perfil + historial + horario
│   │   ├── EventoLaboral/
│   │   │   ├── Index.cshtml              → Calendario semanal/mensual
│   │   │   ├── Crear.cshtml
│   │   │   └── Detalle.cshtml
│   │   ├── HoraExtra/
│   │   │   ├── Index.cshtml              → Lista filtrada por estado
│   │   │   └── Crear.cshtml
│   │   ├── Turno/
│   │   │   ├── Index.cshtml              → Catálogo de plantillas
│   │   │   ├── Crear.cshtml
│   │   │   └── Editar.cshtml
│   │   └── Catalogos/
│   │       ├── Sedes/
│   │       ├── Cargos/
│   │       └── EmpresasTemporales/
│   ├── ViewModels/
│   │   ├── Cuenta/
│   │   ├── Dashboard/
│   │   ├── Empleado/
│   │   ├── EventoLaboral/
│   │   ├── HoraExtra/
│   │   ├── Turno/
│   │   └── Catalogos/
│   ├── AutoMapper/
│   │   └── AutoMapperURT.cs              → Perfil único de AutoMapper (entidades ↔ DTOs ↔ ViewModels)
│   ├── DependencyContainer/
│   │   └── DependencyContainer.cs        → Centraliza todo el registro de dependencias
│   ├── Filters/
│   │   └── SedeAuthorizationFilter.cs    → Valida acceso de usuario a sede del recurso
│   └── wwwroot/
│       ├── css/
│       ├── js/
│       └── lib/
│
├── GestionPersonal.Application/          ← Lógica de negocio (services e interfaces)
│   ├── Services/
│   │   ├── EmpleadoService.cs            → Pitch 1 (validaciones negocio)
│   │   ├── EventoLaboralService.cs       → Pitch 2 (saldo vacaciones, solapamiento)
│   │   ├── TurnoService.cs               → Pitch 3
│   │   ├── HoraExtraService.cs           → Pitch 4 (disponibilidad, concurrencia)
│   │   ├── UsuarioService.cs             → Pitch 5 (autenticación, tokens)
│   │   ├── DashboardService.cs           → Pitch 6 (consultas consolidadas)
│   │   └── Catalogos/
│   │       ├── SedeService.cs
│   │       ├── CargoService.cs
│   │       └── EmpresaTemporalService.cs
│   ├── Interfaces/
│   │   ├── IEmpleadoService.cs
│   │   ├── IEventoLaboralService.cs
│   │   ├── ITurnoService.cs
│   │   ├── IHoraExtraService.cs
│   │   ├── IUsuarioService.cs
│   │   ├── IDashboardService.cs
│   │   └── Catalogos/
│   │       ├── ISedeService.cs
│   │       ├── ICargoService.cs
│   │       └── IEmpresaTemporalService.cs
│   └── AccessDependency/
│       └── ApplicationAccessDependency.cs
│
├── GestionPersonal.Models/               ← Capa central de modelos (DTOs, entidades, enums, resultados)
│   ├── DTOs/                             ← Data Transfer Objects por módulo
│   │   ├── Empleado/
│   │   │   ├── EmpleadoDto.cs
│   │   │   ├── EmpleadoListaDto.cs
│   │   │   ├── CrearEmpleadoDto.cs
│   │   │   ├── EditarEmpleadoDto.cs
│   │   │   └── EmpleadoDesvinculadoDto.cs
│   │   ├── EventoLaboral/
│   │   │   ├── EventoLaboralDto.cs
│   │   │   └── CrearEventoLaboralDto.cs
│   │   ├── HoraExtra/
│   │   │   ├── HoraExtraDto.cs
│   │   │   └── CrearHoraExtraDto.cs
│   │   ├── Turno/
│   │   │   ├── PlantillaTurnoDto.cs
│   │   │   └── AsignacionTurnoDto.cs
│   │   ├── Dashboard/
│   │   │   └── DashboardResumenDto.cs
│   │   └── Cuenta/
│   │       ├── UsuarioSesionDto.cs
│   │       └── LoginDto.cs
│   ├── Entities/                         ← Generadas con EF Core scaffold
│   │   └── GestionPersonalEntities/      ← Carpeta nombrada: {NombreProyecto}Entities
│   │       ├── AppDbContext.cs           ← DbContext de la base de datos
│   │       ├── Configurations/           ← IEntityTypeConfiguration<T> por entidad
│   │       │   ├── SedeConfiguration.cs
│   │       │   ├── CargoConfiguration.cs
│   │       │   ├── EmpresaTemporalConfiguration.cs
│   │       │   ├── PlantillaTurnoConfiguration.cs
│   │       │   ├── PlantillaTurnoDetalleConfiguration.cs
│   │       │   ├── UsuarioConfiguration.cs
│   │       │   ├── TokenRecuperacionConfiguration.cs
│   │       │   ├── EmpleadoConfiguration.cs
│   │       │   ├── ContactoEmergenciaConfiguration.cs
│   │       │   ├── HistorialDesvinculacionConfiguration.cs
│   │       │   ├── AsignacionTurnoConfiguration.cs
│   │       │   ├── EventoLaboralConfiguration.cs
│   │       │   └── HoraExtraConfiguration.cs
│   │       ├── Sede.cs
│   │       ├── Cargo.cs
│   │       ├── EmpresaTemporal.cs
│   │       ├── PlantillaTurno.cs
│   │       ├── PlantillaTurnoDetalle.cs
│   │       ├── Usuario.cs
│   │       ├── TokenRecuperacion.cs
│   │       ├── Empleado.cs
│   │       ├── ContactoEmergencia.cs
│   │       ├── HistorialDesvinculacion.cs
│   │       ├── AsignacionTurno.cs
│   │       ├── EventoLaboral.cs
│   │       └── HoraExtra.cs
│   ├── Models/                           ← Modelos de resultado, paginación y respuesta
│   │   ├── ResultadoOperacion.cs
│   │   └── PaginacionModel.cs
│   └── Enums/                            ← Enums del dominio (accesibles por todas las capas)
│       ├── EstadoEmpleado.cs
│       ├── RolUsuario.cs
│       ├── TipoVinculacion.cs
│       ├── TipoEvento.cs
│       ├── TipoIncapacidad.cs
│       ├── EstadoEvento.cs
│       ├── EstadoHoraExtra.cs
│       └── NivelEscolaridad.cs
│
├── GestionPersonal.Domain/               ← Contratos de repositorios (solo interfaces)
│   └── Interfaces/
│       ├── IEmpleadoRepository.cs
│       ├── IEventoLaboralRepository.cs
│       ├── IHoraExtraRepository.cs
│       ├── ITurnoRepository.cs
│       ├── IUsuarioRepository.cs
│       └── Catalogos/
│           ├── ISedeRepository.cs
│           ├── ICargoRepository.cs
│           └── IEmpresaTemporalRepository.cs
│
├── GestionPersonal.Infrastructure/       ← Repositorios y migraciones EF Core
│   ├── Repositories/
│   │   ├── EmpleadoRepository.cs
│   │   ├── EventoLaboralRepository.cs
│   │   ├── HoraExtraRepository.cs
│   │   ├── TurnoRepository.cs
│   │   ├── UsuarioRepository.cs
│   │   └── Catalogos/
│   │       ├── SedeRepository.cs
│   │       ├── CargoRepository.cs
│   │       └── EmpresaTemporalRepository.cs
│   ├── Migrations/                       ← Migraciones EF Core (DbContext vive en Models)
│   └── AccessDependency/
│       └── InfrastructureAccessDependency.cs
│
├── GestionPersonal.Helpers/              ← Utilidades transversales
│   ├── Email/
│   │   ├── IEmailHelper.cs
│   │   └── EmailHelper.cs
│   ├── Security/
│   │   ├── PasswordHelper.cs             → HMACSHA512 + salt
│   │   ├── ICodigoHelper.cs
│   │   └── CodigoGeneradorHelper.cs      → Tokens recuperación (Base36, 8 chars)
│   ├── Archivos/
│   │   ├── IArchivoHelper.cs
│   │   └── ArchivoHelper.cs              → Validación y guardado de adjuntos (PDF/JPG/PNG ≤5MB)
│   ├── Excel/
│   │   ├── IExcelHelper.cs
│   │   └── ExcelHelper.cs                → Exportar historial empleado (.xlsx)
│   └── AccessDependency/
│       └── HelperAccessDependency.cs
│
└── GestionPersonal.Constants/            ← Mensajes y enums globales sin dependencias
    ├── Messages/
    │   ├── InicioSesionConstant.cs
    │   ├── EmpleadoConstant.cs
    │   ├── EventoLaboralConstant.cs
    │   ├── HoraExtraConstant.cs
    │   ├── TurnoConstant.cs
    │   ├── CatalogoConstant.cs
    │   └── EmailConstant.cs
    └── Paginacion/
        └── PaginacionConstant.cs         → Opciones: 10 / 25 / 50 / 100
```

---

## 2. Flujo de Dependencias entre Capas

```
Web  ──────────→  Application  ──────────→  Domain
 ↓                    ↓                       ↓
 ↓                 Helpers                Infrastructure
 ↓                    ↓                       ↓
 └────────────────────────────────────────────┘
            ↓                     ↓
          Models  ←──────────  Constants
```

**Reglas:**
- `Constants` no referencia ninguna otra capa del proyecto. Solo `string const`.
- `Models` referencia únicamente `Constants` (si aplica). Tiene `Microsoft.EntityFrameworkCore.SqlServer` para `AppDbContext` y las configuraciones.
- `Helpers` referencia `Constants`.
- `Domain` referencia `Models` (tipos de entidad en interfaces de repositorio). Solo interfaces, sin implementaciones.
- `Application` referencia `Domain` (interfaces), `Models` (DTOs, entidades, enums, modelos de resultado), `Helpers` y `Constants`.
- `Infrastructure` referencia `Domain` (interfaces) y `Models` (entidades, DbContext, enums).
- `Web` referencia `Application`, `Models`, `Constants` y `Helpers` (solo vía interfaces).
- **Nunca** `Infrastructure` referencia `Web`.
- **Nunca** `Application` referencia `Infrastructure` directamente (solo vía interfaces de `Domain`).
- **Nunca** ninguna capa referencia `Web`.

---

## 3. Capa de Models

`GestionPersonal.Models` es la **capa central de modelos**: la única fuente de verdad para entidades, DTOs, enums y modelos de resultado. Es referenciada por todas las demás capas.

### 3.1 Entidades (13 tablas del schema `GestionPersonal`)

Las entidades se generan con **scaffold de EF Core** sobre la base de datos ya creada. El destino es **`GestionPersonal.Models`**, carpeta `Entities/GestionPersonalEntities`:

```bash
dotnet ef dbcontext scaffold \
  "Server=.\SQLEXPRESS;Database=GestionPersonal;Trusted_Connection=True;TrustServerCertificate=True;" \
  Microsoft.EntityFrameworkCore.SqlServer \
  -o Entities/GestionPersonalEntities \
  --context AppDbContext \
  --force \
  --project "GestionPersonal.Models\GestionPersonal.Models.csproj" \
  --startup-project "GestionPersonal.Web\GestionPersonal.Web.csproj"
```

> **Flags importantes:**
> - `-o Entities/GestionPersonalEntities` → subcarpeta nombrada `{Proyecto}Entities` dentro de `Entities/`.
> - `--project` → **`GestionPersonal.Models`** (no Domain); aquí vivirán entidades y DbContext.
> - `--force` → sobreescribe si ya existen.
>
> Después del scaffold, crear `Entities/GestionPersonalEntities/Configurations/` y añadir los `IEntityTypeConfiguration<T>` allí. El namespace de `AppDbContext.cs` debe quedar `GestionPersonal.Models.Entities.GestionPersonalEntities`.

| Entidad | Tabla BD | Depende de |
|---|---|---|
| `Sede` | `Sedes` | — |
| `Cargo` | `Cargos` | — |
| `EmpresaTemporal` | `EmpresasTemporales` | — |
| `PlantillaTurno` | `PlantillasTurno` | — |
| `PlantillaTurnoDetalle` | `PlantillasTurnoDetalle` | `PlantillaTurno` |
| `Usuario` | `Usuarios` | `Sede` |
| `TokenRecuperacion` | `TokensRecuperacion` | `Usuario` |
| `Empleado` | `Empleados` | `Sede`, `Cargo`, `Usuario`, `EmpresaTemporal`, `Empleado` (auto-ref) |
| `ContactoEmergencia` | `ContactosEmergencia` | `Empleado` |
| `HistorialDesvinculacion` | `HistorialDesvinculaciones` | `Empleado`, `Usuario` |
| `AsignacionTurno` | `AsignacionesTurno` | `Empleado`, `PlantillaTurno`, `Usuario` |
| `EventoLaboral` | `EventosLaborales` | `Empleado`, `Usuario` |
| `HoraExtra` | `HorasExtras` | `Empleado`, `Usuario` |

### 3.2 AppDbContext

`AppDbContext.cs` vive en `Models/Entities/GestionPersonalEntities/`. Usa `ApplyConfigurationsFromAssembly` para registrar automáticamente todas las `IEntityTypeConfiguration<T>` del mismo ensamblado:

```csharp
// Models/Entities/GestionPersonalEntities/AppDbContext.cs
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Sede>                    Sedes                    => Set<Sede>();
    public DbSet<Cargo>                   Cargos                   => Set<Cargo>();
    public DbSet<EmpresaTemporal>         EmpresasTemporales       => Set<EmpresaTemporal>();
    public DbSet<PlantillaTurno>          PlantillasTurno          => Set<PlantillaTurno>();
    public DbSet<PlantillaTurnoDetalle>   PlantillasTurnoDetalle   => Set<PlantillaTurnoDetalle>();
    public DbSet<Usuario>                 Usuarios                 => Set<Usuario>();
    public DbSet<TokenRecuperacion>       TokensRecuperacion       => Set<TokenRecuperacion>();
    public DbSet<Empleado>                Empleados                => Set<Empleado>();
    public DbSet<ContactoEmergencia>      ContactosEmergencia      => Set<ContactoEmergencia>();
    public DbSet<HistorialDesvinculacion> HistorialDesvinculaciones => Set<HistorialDesvinculacion>();
    public DbSet<AsignacionTurno>         AsignacionesTurno        => Set<AsignacionTurno>();
    public DbSet<EventoLaboral>           EventosLaborales         => Set<EventoLaboral>();
    public DbSet<HoraExtra>              HorasExtras              => Set<HoraExtra>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
        => modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
}
```

### 3.3 Enums de Dominio

Todos los enums viven en `Models/Enums/` y son accesibles por todas las capas:

```csharp
// Models/Enums/EstadoEmpleado.cs
public enum EstadoEmpleado { Activo, Inactivo }

// Models/Enums/RolUsuario.cs
public enum RolUsuario { Jefe, Regente, AuxiliarRegente, Operario, Administrador }

// Models/Enums/TipoVinculacion.cs
public enum TipoVinculacion { Directo, Temporal }

// Models/Enums/TipoEvento.cs
public enum TipoEvento { Vacaciones, Incapacidad, Permiso }

// Models/Enums/TipoIncapacidad.cs
public enum TipoIncapacidad
{
    EnfermedadGeneral,
    AccidenteTrabajo,
    EnfermedadLaboral,
    MaternidadPaternidad
}

// Models/Enums/EstadoEvento.cs
public enum EstadoEvento { Activo, Finalizado, Anulado }

// Models/Enums/EstadoHoraExtra.cs
public enum EstadoHoraExtra { Pendiente, Aprobado, Rechazado, Anulado }

// Models/Enums/NivelEscolaridad.cs
public enum NivelEscolaridad
{
    Primaria, Bachillerato, Tecnico, Tecnologico, Profesional, Posgrado
}
```

### 3.4 Modelos de resultado

`ResultadoOperacion<T>` es el contrato de retorno entre services y controllers:

```csharp
// Models/Models/ResultadoOperacion.cs
public class ResultadoOperacion
{
    public bool   Exito   { get; init; }
    public string Mensaje { get; init; } = string.Empty;
    public static ResultadoOperacion Ok(string mensaje = "")  => new() { Exito = true,  Mensaje = mensaje };
    public static ResultadoOperacion Fail(string mensaje)     => new() { Exito = false, Mensaje = mensaje };
}

public class ResultadoOperacion<T> : ResultadoOperacion
{
    public T? Datos { get; init; }
    public static ResultadoOperacion<T> Ok(T datos, string mensaje = "")
        => new() { Exito = true, Datos = datos, Mensaje = mensaje };
}

// Models/Models/PaginacionModel.cs
public class PaginacionModel
{
    public int Pagina        { get; set; } = 1;
    public int TamanioPagina { get; set; } = 10;
    public static readonly int[] OpcionesTamanio = [10, 25, 50, 100];
}
```

---

## 4. Capa de Dominio

Contiene **únicamente interfaces de repositorio**. Las entidades, enums y DTOs viven en `GestionPersonal.Models`. Referencia `GestionPersonal.Models` para usar los tipos de entidad en las firmas de sus interfaces.

### 4.1 Interfaces de Repositorios

```csharp
// Domain/Interfaces/IEmpleadoRepository.cs
public interface IEmpleadoRepository
{
    Task<Empleado?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<Empleado>> ObtenerActivosPorSedeAsync(int sedeId, CancellationToken ct = default);
    Task<IReadOnlyList<Empleado>> ObtenerTodosActivosAsync(CancellationToken ct = default);   // solo Jefe
    Task<IReadOnlyList<Empleado>> ObtenerDesvinculadosAsync(CancellationToken ct = default);
    Task<bool> ExisteCedulaAsync(string cedula, int? excluirId = null, CancellationToken ct = default);
    Task<bool> ExisteCorreoAsync(string correo, int? excluirId = null, CancellationToken ct = default);
    Task<bool> ExisteRegenteActivoEnSedeAsync(int sedeId, int? excluirId = null, CancellationToken ct = default);
    void Agregar(Empleado empleado);
    void Actualizar(Empleado empleado);
    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}

// Domain/Interfaces/IEventoLaboralRepository.cs
public interface IEventoLaboralRepository
{
    Task<EventoLaboral?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<EventoLaboral>> ObtenerPorSedeYRangoAsync(int sedeId, DateOnly desde, DateOnly hasta, CancellationToken ct = default);
    Task<bool> TieneSolapamientoAsync(int empleadoId, DateOnly inicio, DateOnly fin, int? excluirId = null, CancellationToken ct = default);
    Task<bool> TieneEventoActivoEnFechaAsync(int empleadoId, DateOnly fecha, CancellationToken ct = default);
    Task<decimal> ObtenerDiasVacacionesTomadosAsync(int empleadoId, CancellationToken ct = default);
    void Agregar(EventoLaboral evento);
    void Actualizar(EventoLaboral evento);
    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}

// Domain/Interfaces/IHoraExtraRepository.cs
public interface IHoraExtraRepository
{
    Task<HoraExtra?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<HoraExtra>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default);
    Task<IReadOnlyList<HoraExtra>> ObtenerPorEmpleadoAsync(int empleadoId, CancellationToken ct = default);
    Task<bool> ExisteSolicitudActivaEnFechaAsync(int empleadoId, DateOnly fecha, int? excluirId = null, CancellationToken ct = default);
    void Agregar(HoraExtra horaExtra);
    void Actualizar(HoraExtra horaExtra);
    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}

// Domain/Interfaces/IUsuarioRepository.cs
public interface IUsuarioRepository
{
    Task<Usuario?> ObtenerPorCorreoAsync(string correo, CancellationToken ct = default);
    Task<Usuario?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<TokenRecuperacion?> ObtenerTokenValidoAsync(string token, CancellationToken ct = default);
    void Agregar(Usuario usuario);
    void AgregarToken(TokenRecuperacion token);
    void Actualizar(Usuario usuario);
    void ActualizarToken(TokenRecuperacion token);
    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}
```

---

## 5. Capa de Constants

```csharp
// Constants/Messages/InicioSesionConstant.cs
public static class InicioSesionConstant
{
    public const string CredencialesInvalidas   = "Correo o contraseña incorrectos.";
    public const string UsuarioInactivo         = "La cuenta está desactivada. Contacte al administrador.";
    public const string SesionExpirada          = "Tu sesión ha expirado. Por favor inicia sesión nuevamente.";
    public const string AccesoDenegado          = "No tienes permisos para acceder a esta sección.";
    public const string DebeCambiarPassword     = "Por seguridad, debes cambiar tu contraseña antes de continuar.";
    public const string TokenInvalido           = "El enlace de recuperación es inválido o ha expirado.";
}

// Constants/Messages/EmpleadoConstant.cs
public static class EmpleadoConstant
{
    public const string CedulaDuplicada             = "Ya existe un empleado con esta identificación.";
    public const string CorreoDuplicado             = "Ya existe un usuario con este correo electrónico.";
    public const string AutorefereciaJefe           = "Un empleado no puede ser su propio jefe inmediato.";
    public const string JefeInmediatoObligatorio    = "El campo Jefe inmediato es obligatorio para este rol.";
    public const string RegenteDuplicadoEnSede      = "La sede ya tiene un Regente activo asignado.";
    public const string FechaInvalida               = "La fecha ingresada no es válida.";
    public const string EmpleadoNoEncontrado        = "El empleado no fue encontrado.";
    public const string EmpleadoDesvinculado        = "El empleado fue desvinculado exitosamente.";
    public const string MotivoRetiroObligatorio     = "El motivo de retiro es obligatorio para desvincular.";
    public const string EmpleadoGuardado            = "Los datos del empleado fueron guardados exitosamente.";
}

// Constants/Messages/EventoLaboralConstant.cs
public static class EventoLaboralConstant
{
    public const string SolapamientoFechas          = "El empleado ya tiene un evento registrado en ese rango de fechas.";
    public const string SaldoInsuficiente           = "El empleado no tiene suficientes días de vacaciones disponibles.";
    public const string DocumentoRequerido          = "El documento de soporte es obligatorio para incapacidades.";
    public const string EventoGuardado              = "El evento laboral fue registrado exitosamente.";
    public const string EventoAnulado               = "El evento laboral fue anulado exitosamente.";
    public const string MotivoAnulacionObligatorio  = "El motivo de anulación es obligatorio.";
}

// Constants/Messages/HoraExtraConstant.cs
public static class HoraExtraConstant
{
    public const string SolicitudDuplicadaEnFecha   = "Ya existe una solicitud de horas extras para este empleado en la fecha indicada.";
    public const string EmpleadoNoDisponible        = "El empleado no está disponible en la fecha seleccionada.";
    public const string CantidadInvalida            = "La cantidad de horas debe estar entre 1 y 24.";
    public const string RegistroProcesado           = "El registro ya fue procesado por otro usuario. Refresca la página.";
    public const string MotivoRechazoObligatorio    = "El motivo de rechazo es obligatorio.";
    public const string MotivoAnulacionObligatorio  = "El motivo de anulación es obligatorio.";
    public const string JefeNoPuedeAprobarse        = "El Jefe no puede aprobar sus propias horas extras.";
    public const string SolicitudAprobada           = "La solicitud fue aprobada exitosamente.";
    public const string SolicitudRechazada          = "La solicitud fue rechazada.";
}

// Constants/Messages/TurnoConstant.cs
public static class TurnoConstant
{
    public const string PlantillaSinDiasLaborales   = "La plantilla debe tener al menos un día con horario configurado.";
    public const string FechaVigenciaAnteriorIngreso = "La fecha de vigencia no puede ser anterior a la fecha de ingreso del empleado.";
    public const string PlantillaGuardada           = "La plantilla de turno fue guardada exitosamente.";
    public const string TurnoAsignado               = "El turno fue asignado exitosamente.";
}

// Constants/Messages/EmailConstant.cs
public static class EmailConstant
{
    public const string AsuntoRecuperarPassword = "Recuperación de contraseña — GestiónPersonal";
    public const string CuerpoRecuperarPassword = @"
        <p>Estimado usuario,</p>
        <p>Recibimos una solicitud para restablecer la contraseña de su cuenta en <strong>GestiónPersonal</strong>.</p>
        <p>Use el siguiente enlace (válido por 1 hora):</p>
        <p><a href='{enlace}'>Restablecer contraseña</a></p>
        <p>Si no solicitó este cambio, ignore este mensaje.</p>
        <p>Atentamente,<br/><strong>Equipo GestiónPersonal</strong></p>";

    public const string AsuntoNuevoUsuario = "Bienvenid@ a GestiónPersonal";
    public const string CuerpoNuevoUsuario = @"
        <p>Estimado usuario,</p>
        <p>Tu cuenta en <strong>GestiónPersonal</strong> ha sido creada exitosamente.</p>
        <ul>
          <li><strong>Correo:</strong> {correo}</li>
          <li><strong>Contraseña temporal:</strong> {contrasenaTemp}</li>
        </ul>
        <p>Deberás cambiar tu contraseña al iniciar sesión por primera vez.</p>
        <p>Atentamente,<br/><strong>Equipo GestiónPersonal</strong></p>";
}

// Constants/Paginacion/PaginacionConstant.cs
public static class PaginacionConstant
{
    public const int TamanioDefecto        = 10;
    public static readonly int[] Opciones  = [10, 25, 50, 100];
}
```

---

## 6. Capa de Helpers

### 5.1 PasswordHelper (HMACSHA512)

```csharp
// Helpers/Security/PasswordHelper.cs
// Clase estática — sin inyección de dependencias
public static class PasswordHelper
{
    /// <summary>Genera PasswordHash (64 bytes) y PasswordSalt (128 bytes) con HMACSHA512.</summary>
    public static (byte[] Hash, byte[] Salt) CrearHash(string password)
    {
        using var hmac = new HMACSHA512();              // Key aleatoria = salt
        byte[] salt = hmac.Key;                         // 128 bytes
        byte[] hash = hmac.ComputeHash(
            Encoding.UTF8.GetBytes(password));          // 64 bytes
        return (hash, salt);
    }

    /// <summary>Verifica contraseña contra hash y salt almacenados. Comparación en tiempo constante.</summary>
    public static bool VerificarPassword(string password, byte[] hashGuardado, byte[] saltGuardado)
    {
        using var hmac = new HMACSHA512(saltGuardado);
        byte[] hashComparar = hmac.ComputeHash(
            Encoding.UTF8.GetBytes(password));
        return CryptographicOperations.FixedTimeEquals(hashComparar, hashGuardado);
    }

    /// <summary>Genera contraseña temporal aleatoria.</summary>
    public static string GenerarContrasenaTemp(int longitud = 10)
    {
        const string chars = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#";
        var bytes = RandomNumberGenerator.GetBytes(longitud);
        return new string(bytes.Select(b => chars[b % chars.Length]).ToArray());
    }
}
```

### 5.2 ArchivoHelper (adjuntos eventos laborales)

```csharp
// Helpers/Archivos/IArchivoHelper.cs
public interface IArchivoHelper
{
    /// <summary>
    /// Valida y guarda el archivo. Retorna la ruta relativa guardada.
    /// Lanza ArgumentException si el archivo es inválido.
    /// </summary>
    Task<(string Ruta, string NombreOriginal)> GuardarAdjuntoAsync(IFormFile archivo, string subcarpeta);
    void EliminarAdjunto(string rutaRelativa);
}
```

> **Restricciones de adjuntos** (Pitch 2): 1 archivo por evento, máximo 5 MB, formatos PDF / JPG / PNG.  
> Almacenar archivos en `wwwroot/uploads/eventos/{eventoId}/`.

### 5.3 ExcelHelper (exportar historial)

```csharp
// Helpers/Excel/IExcelHelper.cs
public interface IExcelHelper
{
    /// <summary>Genera un archivo .xlsx con el historial del empleado.</summary>
    byte[] GenerarHistorialEmpleado(HistorialEmpleadoDto historial);
}
```

> Usar la librería **ClosedXML** o **EPPlus** para la generación del Excel.

---

## 7. Capa de Infraestructura

### 7.1 AppDbContext y Configuraciones

`GestionPersonal.Infrastructure` **no** contiene `AppDbContext.cs` ni configuraciones de entidad — esos archivos viven en `GestionPersonal.Models/Entities/GestionPersonalEntities/`. Solo contiene repositorios, migraciones y su `AccessDependency`.

Referencia: `GestionPersonal.Domain` (interfaces) + `GestionPersonal.Models` (entidades, DbContext, enums).

> Ver §3.2 para el código completo de `AppDbContext.cs` y §3.1 para las `Configurations/`.

### 7.2 Reglas de Configuración EF Core

Cada entidad tiene su clase `IEntityTypeConfiguration<T>` en `Models/Entities/GestionPersonalEntities/Configurations/`:

- Usar `.HasConversion<string>()` para todas las propiedades de tipo enum → se persisten como `NVARCHAR` legible.
- Usar `.OnDelete(DeleteBehavior.Restrict)` en todas las FK (sin cascadas).
- Usar `.AsNoTracking()` en **todas** las queries de solo lectura.
- Siempre pasar `CancellationToken` a los métodos async.
- Usar projections (`.Select(...)`) en listados; usar `.Include()` solo para el perfil completo.

**Ejemplo para `EmpleadoConfiguration`:**

```csharp
// Models/Entities/GestionPersonalEntities/Configurations/EmpleadoConfiguration.cs
public class EmpleadoConfiguration : IEntityTypeConfiguration<Empleado>
{
    public void Configure(EntityTypeBuilder<Empleado> builder)
    {
        builder.ToTable("Empleados");
        builder.HasKey(e => e.Id);

        builder.Property(e => e.NombreCompleto).IsRequired().HasMaxLength(200);
        builder.Property(e => e.Cedula).IsRequired().HasMaxLength(20);
        builder.HasIndex(e => e.Cedula).IsUnique().HasDatabaseName("UX_Empleados_Cedula");
        builder.HasIndex(e => e.CorreoElectronico).IsUnique().HasDatabaseName("UX_Empleados_Correo");

        builder.Property(e => e.Estado)
            .HasConversion<string>().HasMaxLength(20).IsRequired();
        builder.Property(e => e.TipoVinculacion)
            .HasConversion<string>().HasMaxLength(20).IsRequired();
        builder.Property(e => e.NivelEscolaridad)
            .HasConversion<string>().HasMaxLength(30);

        // Relaciones
        builder.HasOne(e => e.Sede).WithMany(s => s.Empleados)
            .HasForeignKey(e => e.SedeId).OnDelete(DeleteBehavior.Restrict);
        builder.HasOne(e => e.Cargo).WithMany(c => c.Empleados)
            .HasForeignKey(e => e.CargoId).OnDelete(DeleteBehavior.Restrict);
        builder.HasOne(e => e.JefeInmediato).WithMany()
            .HasForeignKey(e => e.JefeInmediatoId).OnDelete(DeleteBehavior.Restrict);
        builder.HasOne(e => e.EmpresaTemporal).WithMany()
            .HasForeignKey(e => e.EmpresaTemporalId).OnDelete(DeleteBehavior.Restrict);
        builder.HasOne(e => e.Usuario).WithMany()
            .HasForeignKey(e => e.UsuarioId).OnDelete(DeleteBehavior.Restrict);
    }
}
```

### 7.3 Patrón Repository

```csharp
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

    public async Task<IReadOnlyList<Empleado>> ObtenerActivosPorSedeAsync(int sedeId, CancellationToken ct = default)
        => await _context.Empleados
            .Where(e => e.SedeId == sedeId && e.Estado == EstadoEmpleado.Activo)
            .Select(e => new Empleado { Id = e.Id, NombreCompleto = e.NombreCompleto, Cedula = e.Cedula, Estado = e.Estado })
            .AsNoTracking()
            .ToListAsync(ct);

    public void Agregar(Empleado empleado) => _context.Empleados.Add(empleado);
    public void Actualizar(Empleado empleado) => _context.Empleados.Update(empleado);
    public Task<int> GuardarCambiosAsync(CancellationToken ct = default) => _context.SaveChangesAsync(ct);
}
```

### 7.4 InfrastructureAccessDependency

```csharp
// Infrastructure/AccessDependency/InfrastructureAccessDependency.cs
// AppDbContext vive en GestionPersonal.Models; las Migrations se almacenan en este proyecto
public static class InfrastructureAccessDependency
{
    public static IServiceCollection AddInfrastructure(
        this IServiceCollection services, IConfiguration configuration)
    {
        services.AddDbContext<AppDbContext>(options =>
            options.UseSqlServer(
                configuration.GetConnectionString("Default"),
                sql => sql.MigrationsAssembly("GestionPersonal.Infrastructure")));

        // Repositorios
        services.AddScoped<IEmpleadoRepository,       EmpleadoRepository>();
        services.AddScoped<IEventoLaboralRepository,  EventoLaboralRepository>();
        services.AddScoped<IHoraExtraRepository,      HoraExtraRepository>();
        services.AddScoped<ITurnoRepository,          TurnoRepository>();
        services.AddScoped<IUsuarioRepository,        UsuarioRepository>();
        services.AddScoped<ISedeRepository,           SedeRepository>();
        services.AddScoped<ICargoRepository,          CargoRepository>();
        services.AddScoped<IEmpresaTemporalRepository, EmpresaTemporalRepository>();
        return services;
    }
}
```

---

## 8. Capa de Aplicación (Services)

### 8.1 Responsabilidades por servicio — módulo a módulo

#### `EmpleadoService` (Pitch 1)

| Operación | Validaciones de negocio |
|---|---|
| `CrearAsync` | Unicidad CC · Unicidad correo · Auto-referencia jefe · Jefe obligatorio para no-Jefes · Regente único por sede · Coherencia fechas |
| `EditarAsync` | Mismas validaciones excluyendo el empleado editado (`excluirId`) |
| `DesvincularAsync` | Solo rol Jefe · Motivo y fecha obligatorios · Empleado pasa a `Inactivo` · Crea registro en `HistorialDesvinculaciones` |
| `ObtenerHistorialAsync` | Consolida: eventos laborales, horas extras, asignaciones de turno, desvinculación |
| `ExportarHistorialAsync` | Delega a `IExcelHelper` para generar `.xlsx` |
| `ObtenerJefesPorSedeAsync` | Para el selector dependiente de sede en el formulario |

**Lógica de saldo de vacaciones** (colaboración con `EventoLaboralService`):

```
DiasAcumulados = (15 / 12) × mesesTrabajados + DiasVacacionesPrevios − DiasYaTomados
```

#### `EventoLaboralService` (Pitch 2)

| Operación | Validaciones de negocio |
|---|---|
| `RegistrarAsync` | Sin solapamiento con eventos del mismo empleado · Saldo disponible suficiente (solo Vacaciones) · Documento obligatorio (solo Incapacidad) |
| `AnularAsync` | Requiere motivo · Registra `AnuladoPor` y `FechaModificacion` |
| `ObtenerCalendarioAsync` | Filtrado por sede, empleado, tipo, rango de fechas |
| `TieneEventoActivoEnFechaAsync` | Usada por `HoraExtraService`; definición: `FechaInicio ≤ fecha ≤ FechaFin AND Estado ≠ Anulado` |

#### `HoraExtraService` (Pitch 4)

| Operación | Validaciones de negocio |
|---|---|
| `SolicitarAsync` | Unicidad por empleado+fecha (activas) · Sin evento activo en la fecha · Horas entre 1 y 24 |
| `AprobarAsync` | Solo rol Jefe · El Jefe no puede aprobar sus propias horas (`EmpleadoId` del solicitante ≠ Jefe autenticado) · Control de concurrencia: verificar estado actual en BD antes de aprobar |
| `RechazarAsync` | Solo rol Jefe · Motivo obligatorio · Control de concurrencia |
| `AnularAsync` | Solo sobre `Aprobado` · Solo rol Jefe · Motivo obligatorio |

#### `UsuarioService` (Pitch 5)

| Operación | Descripción |
|---|---|
| `ValidarCredencialesAsync` | Busca por correo → verifica `PasswordHelper.VerificarPassword` → retorna `UsuarioSesionDto` o `null` |
| `CrearAsync` | Genera contraseña temporal · `PasswordHelper.CrearHash` · Persiste `PasswordHash` + `PasswordSalt` · Envía correo de bienvenida |
| `CambiarPasswordAsync` | Verifica contraseña actual · Genera nuevo hash · Limpia flag `DebeCambiarPassword` |
| `SolicitarRecuperacionAsync` | Genera token con `ICodigoHelper` · Persiste en `TokensRecuperacion` con expiración 1 hora · Envía correo |
| `RestablecerPasswordAsync` | Valida token (no usado, no expirado) · Cambia hash · Marca token como `Usado = true` |

#### `DashboardService` (Pitch 6)

```csharp
// Models/DTOs/Dashboard/DashboardResumenDto.cs
public class DashboardResumenDto
{
    public int TotalEmpleadosActivos { get; set; }
    public int TotalJefes            { get; set; }
    public int NoDisponiblesHoy      { get; set; }

    // Detalle para acordeones (cargado bajo demanda)
    public IReadOnlyList<EmpleadoListaDto> EmpleadosActivos     { get; set; } = [];
    public IReadOnlyList<UsuarioJefeDto>   Jefes                { get; set; } = [];
    public IReadOnlyList<NoDisponibleDto>  EmpleadosNoDisponibles { get; set; } = [];
}
```

> Las consultas del dashboard usan proyecciones con `.AsNoTracking()`. Nunca cargan entidades completas — solo las columnas necesarias para cada tarjeta.

### 8.2 Patrón de retorno desde Services

Los services devuelven `ResultadoOperacion<T>` (definido en `Models/Models/`) para comunicar al controller si la operación fue exitosa o falló con un mensaje que siempre viene de una clase `Constant`:

```csharp
// Models/Models/ResultadoOperacion.cs
public class ResultadoOperacion
{
    public bool   Exito   { get; init; }
    public string Mensaje { get; init; } = string.Empty;
    public static ResultadoOperacion Ok(string mensaje = "")  => new() { Exito = true,  Mensaje = mensaje };
    public static ResultadoOperacion Fail(string mensaje)     => new() { Exito = false, Mensaje = mensaje };
}

public class ResultadoOperacion<T> : ResultadoOperacion
{
    public T? Datos { get; init; }
    public static ResultadoOperacion<T> Ok(T datos, string mensaje = "")
        => new() { Exito = true, Datos = datos, Mensaje = mensaje };
}
```

---

## 9. Capa de Presentación

### 9.1 Controllers — responsabilidades

**Regla:** los controllers son delgados. Solo validan `ModelState`, llaman al service y redirigen. Nunca contienen lógica de negocio.

```csharp
// Web/Controllers/EmpleadoController.cs
[Authorize]
public class EmpleadoController : Controller
{
    [HttpGet]
    public async Task<IActionResult> Index(int sedeId = 0, int cargoId = 0, string tipo = "")
    { /* obtiene lista con filtros, paginación */ }

    [HttpGet]
    [Authorize(Roles = "Jefe")]
    public IActionResult Crear() { /* carga selectores */ }

    [HttpPost]
    [ValidateAntiForgeryToken]
    [Authorize(Roles = "Jefe")]
    public async Task<IActionResult> Crear(CrearEmpleadoViewModel vm) { /* llama al service */ }

    [HttpPost]
    [ValidateAntiForgeryToken]
    [Authorize(Roles = "Jefe")]
    public async Task<IActionResult> Desvincular(DesvincularEmpleadoViewModel vm) { /* modal */ }

    [HttpGet]
    public async Task<IActionResult> ExportarHistorial(int id) { /* retorna FileResult */ }
}
```

**Tabla de controllers por módulo:**

| Controller | Acciones principales | Roles permitidos |
|---|---|---|
| `CuentaController` | `Login`, `Logout`, `CambiarPassword`, `RecuperarPassword`, `RestablecerPassword` | Todos (sin auth en login/recuperar) |
| `DashboardController` | `Index` | `Jefe` |
| `EmpleadoController` | `Index`, `Crear`, `Editar`, `Perfil`, `Desvincular`, `ExportarHistorial` | `Jefe`, `Regente`, `AuxiliarRegente` (crear solo Jefe) |
| `EmpleadoDesvinculadoController` | `Index`, `Perfil` | `Jefe`, `Regente`, `AuxiliarRegente` |
| `EventoLaboralController` | `Index`, `Crear`, `Detalle`, `Anular` | `Jefe`, `Regente`, `AuxiliarRegente` |
| `HoraExtraController` | `Index`, `Crear`, `Aprobar`, `Rechazar`, `Anular` | Según rol (ver matriz Pitch 4) |
| `TurnoController` | `Index`, `Crear`, `Editar`, `AsignarTurno` | `Jefe`, `Regente`, `AuxiliarRegente` |
| `SedeController` | `Index`, `Crear`, `Editar` | `Jefe` |
| `CargoController` | `Index`, `Crear`, `Editar` | `Jefe` |
| `EmpresaTemporalController` | `Index`, `Crear`, `Editar` | `Jefe` |

### 9.2 ViewModels clave

```csharp
// Web/ViewModels/Empleado/CrearEmpleadoViewModel.cs
public class CrearEmpleadoViewModel : IValidatableObject
{
    // Datos personales
    [Required(ErrorMessage = "El nombre completo es obligatorio.")]
    [MaxLength(200)] public string NombreCompleto { get; set; } = string.Empty;

    [Required(ErrorMessage = "La cédula es obligatoria.")]
    [RegularExpression(@"^\d{6,12}$")] public string Cedula { get; set; } = string.Empty;

    [DataType(DataType.Date)] public DateOnly? FechaNacimiento { get; set; }

    [Required] [EmailAddress] public string CorreoElectronico { get; set; } = string.Empty;

    // Vinculación
    [Required] public int SedeId        { get; set; }
    [Required] public int CargoId       { get; set; }
    [Required] public RolUsuario Rol    { get; set; }
    public int? JefeInmediatoId         { get; set; }

    [Required] public TipoVinculacion TipoVinculacion { get; set; }
    [Required] [DataType(DataType.Date)] public DateOnly FechaIngreso { get; set; }

    // Contrato temporal (condicional)
    public int?      EmpresaTemporalId    { get; set; }
    [DataType(DataType.Date)] public DateOnly? FechaInicioContrato { get; set; }
    [DataType(DataType.Date)] public DateOnly? FechaFinContrato    { get; set; }

    // Selectores para la vista
    public List<SelectListItem> Sedes             { get; set; } = [];
    public List<SelectListItem> Cargos            { get; set; } = [];
    public List<SelectListItem> EmpresasTemporales { get; set; } = [];
    public List<SelectListItem> JefesDisponibles  { get; set; } = [];

    public IEnumerable<ValidationResult> Validate(ValidationContext ctx)
    {
        if (TipoVinculacion == TipoVinculacion.Temporal)
        {
            if (EmpresaTemporalId is null)
                yield return new ValidationResult("La empresa temporal es obligatoria.", [nameof(EmpresaTemporalId)]);
            if (FechaInicioContrato is null)
                yield return new ValidationResult("La fecha de inicio del contrato es obligatoria.", [nameof(FechaInicioContrato)]);
            if (FechaFinContrato is null)
                yield return new ValidationResult("La fecha de fin del contrato es obligatoria.", [nameof(FechaFinContrato)]);
            if (FechaInicioContrato.HasValue && FechaFinContrato.HasValue && FechaFinContrato < FechaInicioContrato)
                yield return new ValidationResult("La fecha fin no puede ser anterior a la fecha inicio.", [nameof(FechaFinContrato)]);
        }
        // Jefe inmediato obligatorio si rol ≠ Jefe
        if (Rol != RolUsuario.Jefe && JefeInmediatoId is null)
            yield return new ValidationResult("El jefe inmediato es obligatorio para este rol.", [nameof(JefeInmediatoId)]);
    }
}
```

```csharp
// Web/ViewModels/HoraExtra/CrearHoraExtraViewModel.cs
public class CrearHoraExtraViewModel
{
    [Required] public int EmpleadoId { get; set; }
    [Required] [DataType(DataType.Date)] public DateOnly FechaTrabajada { get; set; }

    [Required]
    [Range(1, 24, ErrorMessage = "La cantidad de horas debe estar entre 1 y 24.")]
    public decimal CantidadHoras { get; set; }

    [Required(ErrorMessage = "El motivo es obligatorio.")]
    [MaxLength(500)] public string Motivo { get; set; } = string.Empty;

    public List<SelectListItem> Empleados { get; set; } = [];
}
```

```csharp
// Web/ViewModels/Dashboard/DashboardViewModel.cs
public class DashboardViewModel
{
    public int TotalEmpleadosActivos  { get; set; }
    public int TotalJefes             { get; set; }
    public int NoDisponiblesHoy       { get; set; }
    // Acordeones — cargados al montar la página; el JS toggle muestra/oculta
    public IReadOnlyList<EmpleadoListaDto>  EmpleadosActivos      { get; set; } = [];
    public IReadOnlyList<UsuarioJefeDto>    Jefes                 { get; set; } = [];
    public IReadOnlyList<NoDisponibleDto>   EmpleadosNoDisponibles { get; set; } = [];
}
```

### 9.3 Autorización por rol en el servidor

**Nunca** confiar solo en la UI para ocultar botones. El servidor valida en cada request:

```csharp
// Atributo en actions
[Authorize(Roles = "Jefe")]

// Para validar sede del recurso (no solo rol):
// Web/Filters/SedeAuthorizationFilter.cs — IAsyncAuthorizationFilter
// Verifica que el empleado/evento solicitado pertenezca a la sede del usuario autenticado
// (excepto Jefe, que ve todas las sedes)
```

Claims almacenados en la cookie:
- `ClaimTypes.NameIdentifier` → `UsuarioId`
- `ClaimTypes.Email` → `CorreoAcceso`
- `ClaimTypes.Role` → `Rol` (ej: `"Jefe"`)
- `"SedeId"` → `SedeId` del usuario

---

## 10. Autenticación y Seguridad (Pitch 5)

### 10.1 Configuración de Cookies en Program.cs

```csharp
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.LoginPath         = "/Cuenta/Login";
        options.LogoutPath        = "/Cuenta/Logout";
        options.AccessDeniedPath  = "/Cuenta/Acceso-Denegado";
        options.ExpireTimeSpan    = TimeSpan.FromMinutes(30);  // inactividad configurable
        options.SlidingExpiration = true;                       // renueva en cada request
        options.Cookie.HttpOnly   = true;                       // no accesible desde JS
        options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
        options.Cookie.SameSite   = SameSiteMode.Strict;
    });

// Prevenir caché de páginas protegidas (botón Atrás no funciona tras logout)
builder.Services.AddControllersWithViews(options =>
    options.Filters.Add(new ResponseCacheAttribute
    {
        NoStore  = true,
        Location = ResponseCacheLocation.None
    }));
```

### 10.2 Flujo de autenticación

```
[GET /Cuenta/Login]
       ↓
[POST /Cuenta/Login]  →  UsuarioService.ValidarCredencialesAsync()
       ↓
  DebeCambiarPassword = true?
       ├── Sí → Redirect /Cuenta/CambiarPassword
       └── No → Emite cookie → Redirect /Dashboard (Jefe) | /Empleados (otros roles)
```

### 10.3 Flujo de recuperación de contraseña

```
[POST /Cuenta/RecuperarPassword]
       ↓
  UsuarioService.SolicitarRecuperacionAsync()
       ↓
  Genera token (Base36, 8 chars) + expira en 1 hora
       ↓
  Persiste en TokensRecuperacion (Usado = false)
       ↓
  EmailHelper.EnviarCorreoConCodigoAsync()
       ↓
[GET /Cuenta/RestablecerPassword?token=XXX]
       ↓
  UsuarioService.RestablecerPasswordAsync()
       ↓
  Valida: token existe, Usado = false, FechaExpiracion > ahora
       ↓
  Nuevo hash con PasswordHelper · Marca Usado = true
```

### 10.4 Contraseña temporal en creación de usuario

```
Jefe crea empleado → PasswordHelper.GenerarContrasenaTemp()
        ↓
PasswordHelper.CrearHash(contrasenaTemp) → { Hash, Salt }
        ↓
Persiste en Usuarios: PasswordHash, PasswordSalt, DebeCambiarPassword = 1
        ↓
EmailHelper.EnviarCorreoNuevoUsuarioAsync(correo, contrasenaTemp)
        ↓
En primer login → DebeCambiarPassword = true → redirect CambiarPassword
```

---

## 11. DependencyContainer — Centralización de Dependencias

Todas las capas mantienen sus propias clases `AccessDependency` (ver secciones anteriores), pero el punto de entrada único en la capa Web es `DependencyContainer`. Este es el **único lugar** al que `Program.cs` llama para registrar todo.

```csharp
// Web/DependencyContainer/DependencyContainer.cs
public static class DependencyContainer
{
    public static IServiceCollection DependencyInjection(
        this IServiceCollection services, IConfiguration configuration)
    {
        // Infraestructura: EF Core + Repositorios
        services.AddInfrastructure(configuration);

        // Aplicación: Services de negocio
        services.AddApplication();

        // Helpers: Email, Password, Excel, Archivos
        services.AddHelpers();

        // AutoMapper: perfil único centralizado en Web
        services.AddAutoMapper(typeof(AutoMapperURT));

        // Autenticación con cookies
        services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
            .AddCookie(options =>
            {
                options.LoginPath         = "/Cuenta/Login";
                options.LogoutPath        = "/Cuenta/Logout";
                options.AccessDeniedPath  = "/Cuenta/Acceso-Denegado";
                options.ExpireTimeSpan    = TimeSpan.FromMinutes(30);
                options.SlidingExpiration = true;
                options.Cookie.HttpOnly   = true;
                options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
                options.Cookie.SameSite   = SameSiteMode.Strict;
            });

        services.AddAuthorization();

        // Prevenir caché de páginas protegidas
        services.AddControllersWithViews(options =>
            options.Filters.Add(new ResponseCacheAttribute
            {
                NoStore  = true,
                Location = ResponseCacheLocation.None
            }));

        return services;
    }
}
```

**`ApplicationAccessDependency`** (sigue existiendo; es llamado internamente por `DependencyContainer`):

```csharp
// Application/AccessDependency/ApplicationAccessDependency.cs
public static class ApplicationAccessDependency
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        services.AddScoped<IEmpleadoService,        EmpleadoService>();
        services.AddScoped<IEventoLaboralService,   EventoLaboralService>();
        services.AddScoped<ITurnoService,           TurnoService>();
        services.AddScoped<IHoraExtraService,       HoraExtraService>();
        services.AddScoped<IUsuarioService,         UsuarioService>();
        services.AddScoped<IDashboardService,       DashboardService>();
        services.AddScoped<ISedeService,            SedeService>();
        services.AddScoped<ICargoService,           CargoService>();
        services.AddScoped<IEmpresaTemporalService, EmpresaTemporalService>();
        return services;
    }
}
```

## 12. AutoMapper — Perfil Único

Todo el mapeo entidad ↔ DTO ↔ ViewModel se centraliza en un único perfil ubicado en la raíz de la capa Web:

```csharp
// Web/AutoMapper/AutoMapperURT.cs
public class AutoMapperURT : Profile
{
    public AutoMapperURT()
    {
        // ── Empleados ──────────────────────────────────────────
        CreateMap<Empleado, EmpleadoListaDto>()
            .ForMember(d => d.Cargo, o => o.MapFrom(s => s.Cargo.Nombre))
            .ForMember(d => d.Sede,  o => o.MapFrom(s => s.Sede.Nombre));

        CreateMap<Empleado, EmpleadoDto>()
            .ForMember(d => d.Cargo,          o => o.MapFrom(s => s.Cargo.Nombre))
            .ForMember(d => d.Sede,           o => o.MapFrom(s => s.Sede.Nombre))
            .ForMember(d => d.EmpresaTemporal, o => o.MapFrom(s => s.EmpresaTemporal != null ? s.EmpresaTemporal.Nombre : null));

        CreateMap<CrearEmpleadoViewModel, CrearEmpleadoDto>();
        CreateMap<EditarEmpleadoViewModel, EditarEmpleadoDto>();

        // ── Eventos Laborales ──────────────────────────────────
        CreateMap<EventoLaboral, EventoLaboralDto>()
            .ForMember(d => d.NombreEmpleado, o => o.MapFrom(s => s.Empleado.NombreCompleto));

        CreateMap<CrearEventoLaboralViewModel, CrearEventoLaboralDto>();

        // ── Horas Extras ───────────────────────────────────────
        CreateMap<HoraExtra, HoraExtraDto>()
            .ForMember(d => d.NombreEmpleado, o => o.MapFrom(s => s.Empleado.NombreCompleto));

        CreateMap<CrearHoraExtraViewModel, CrearHoraExtraDto>();

        // ── Turnos ─────────────────────────────────────────────
        CreateMap<PlantillaTurno, PlantillaTurnoDto>();
        CreateMap<AsignacionTurno, AsignacionTurnoDto>()
            .ForMember(d => d.NombrePlantilla, o => o.MapFrom(s => s.PlantillaTurno.Nombre));

        // ── Catálogos ──────────────────────────────────────────
        CreateMap<Sede, SedeDto>();
        CreateMap<Cargo, CargoDto>();
        CreateMap<EmpresaTemporal, EmpresaTemporalDto>();
    }
}
```

> **Regla:** los `Mapper` estáticos de `Application/Mappers/` se eliminan cuando se adopta AutoMapper. El perfil `AutoMapperURT` es el único punto de configuración de mapeos del sistema. Se inyecta `IMapper` en los services que lo necesiten.

## 13. Registro de Dependencias en Program.cs

Con `DependencyContainer`, `Program.cs` queda mínimo — una sola llamada centraliza todo:

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// Una sola línea registra infraestructura, servicios, helpers, AutoMapper,
// autenticación, autorización y configuración de controllers.
builder.Services.DependencyInjection(builder.Configuration);

var app = builder.Build();

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();
app.UseAuthentication();   // ← ANTES de UseAuthorization
app.UseAuthorization();
app.MapDefaultControllerRoute();
app.Run();
```

---

## 14. Configuración de la Base de Datos

```json
// appsettings.json
{
  "ConnectionStrings": {
    "Default": "Server=.\\SQLEXPRESS;Database=GestionPersonal;Trusted_Connection=True;TrustServerCertificate=True;MultipleActiveResultSets=true;Connect Timeout=30"
  },
  "Email": {
    "Host":      "smtp.tuproveedor.com",
    "Port":      "587",
    "Remitente": "noreply@gestionpersonal.com",
    "Contrasena": ""
  }
}
```

> `TrustServerCertificate=True` solo para desarrollo local. En producción configurar certificado válido.  
> Las credenciales SMTP van en variables de entorno o secretos de usuario (`dotnet user-secrets`), **nunca** en el repositorio.

---

## 15. Comandos de Migraciones y Scaffold

```bash
# Scaffolding inicial desde BD ya existente
# El destino es GestionPersonal.Models, carpeta Entities/GestionPersonalEntities
dotnet ef dbcontext scaffold \\
  "Server=.\\SQLEXPRESS;Database=GestionPersonal;Trusted_Connection=True;TrustServerCertificate=True;" \\
  Microsoft.EntityFrameworkCore.SqlServer \\
  -o Entities/GestionPersonalEntities \\
  --context AppDbContext \\
  --force \\
  --project "GestionPersonal.Models" \\
  --startup-project "GestionPersonal.Web"

# Migraciones code-first (si se necesitan en el futuro)
# Las migraciones viven en Infrastructure; el DbContext en Models
dotnet ef migrations add NombreMigracion \\
  --project GestionPersonal.Infrastructure \\
  --startup-project GestionPersonal.Web

dotnet ef database update \\
  --project GestionPersonal.Infrastructure \\
  --startup-project GestionPersonal.Web
```

---

## 16. Decisiones de Diseño Clave

| Decisión | Justificación |
|---|---|
| **`GestionPersonal.Models` como capa central** | Centraliza entidades (AppDbContext + Configurations), DTOs, enums y modelos de resultado. Elimina referencias circulares entre Application e Infrastructure. Todas las capas referencian Models. |
| **`DependencyContainer` como punto único** | `Program.cs` solo llama `builder.Services.DependencyInjection(builder.Configuration)`. Las capas internas mantienen sus `AccessDependency` para organización, pero el exterior solo conoce una entrada. |
| **AutoMapper con perfil único `AutoMapperURT`** | Un solo `Profile` en `Web/AutoMapper/` centraliza todos los mapeos. Elimina la necesidad de mappers estáticos manuales en `Application/Mappers/`. Se inyecta `IMapper` en los services que lo requieren. |
| **Sin APIs REST** | App intranet MVC pura. Las Views consumen datos del servidor directamente vía Controller → Service. |
| **Scaffold desde BD existente** | El schema SQL (`GestionPersonal`) ya está definido y validado. El scaffold evita inconsistencias entre el modelo C# y la BD. |
| **Soft delete en todas las entidades principales** | Empleados pasan a `Inactivo`, eventos se `Anulan`. Nunca `DELETE` físico en producción. |
| **Validación en dos niveles** | `DataAnnotations` + `IValidatableObject` en ViewModels para validaciones de formato y cruzadas; la lógica de negocio (unicidad, reglas de sede, concurrencia) en los Services. |
| **Cookie auth con `SlidingExpiration`** | 30 minutos de inactividad. La sesión se renueva en cada request activo. No hay JWT ni bearer tokens — es innecesario para una intranet MVC. |
| **`PasswordHelper` con HMACSHA512** | Algoritmo requerido en el schema: `PasswordHash VARBINARY(64)` + `PasswordSalt VARBINARY(128)`. Comparación con `CryptographicOperations.FixedTimeEquals` para resistir timing attacks. |
| **Control de concurrencia en HorasExtras** | Antes de aprobar/rechazar, el service verifica el estado actual en BD. Evita condiciones de carrera si dos supervisores actúan simultáneamente. |
| **Paginación editable** | Opciones 10/25/50/100 en `PaginacionConstant`. Persiste en sesión del usuario durante la navegación. |
| **Proyecciones en queries de listado** | Usar `.Select(...)` + `.AsNoTracking()` en listados. Solo `.Include()` en el perfil completo del empleado. Previene el problema N+1 y reduce datos transferidos. |
| **Acordeones del Dashboard cargados en el render** | El dashboard carga todos los datos en el `GET /Dashboard/Index`. Los acordeones se muestran/ocultan con JS en el cliente. No hay llamadas AJAX adicionales — datos al momento de cargar la página (Pitch 6, Rabbit Hole "datos en tiempo real"). |

---

## 17. Matriz de Módulos vs. Pitches

| Pitch | Módulo | Semanas | Servicios | Controllers |
|---|---|---|---|---|
| Pitch 1 | Gestión de Empleados | Big Batch (6 sem) | `EmpleadoService`, `SedeService`, `CargoService`, `EmpresaTemporalService` | `EmpleadoController`, `EmpleadoDesvinculadoController`, `SedeController`, `CargoController`, `EmpresaTemporalController` |
| Pitch 2 | Control de Eventos Laborales | Big Batch (6 sem) | `EventoLaboralService` | `EventoLaboralController` |
| Pitch 3 | Administración de Jornadas | Small Batch (2 sem) | `TurnoService` | `TurnoController` |
| Pitch 4 | Gestión de Horas Extras | Small Batch (2 sem) | `HoraExtraService` | `HoraExtraController` |
| Pitch 5 | Autenticación y Seguridad | Small Batch (1 sem) | `UsuarioService` | `CuentaController` |
| Pitch 6 | Dashboard del Jefe | Small Batch (1 sem) | `DashboardService` | `DashboardController` |
