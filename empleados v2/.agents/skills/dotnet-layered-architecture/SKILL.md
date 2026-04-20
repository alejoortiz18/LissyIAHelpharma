---
name: dotnet-layered-architecture
description: Aplica convenciones de arquitectura en capas para proyectos ASP.NET Core MVC con C#. Úsalo cuando diseñes la estructura del proyecto, crees controllers, services, repositories, helpers, constants, mappers, cookies de sesión o cualquier clase del backend.
metadata:
  author: custom
  version: "2.0.0"
---

# Arquitectura en Capas – ASP.NET Core MVC (.NET 10)

Guía de convenciones y patrones para proyectos C# con arquitectura en capas sobre ASP.NET Core MVC.

## Estructura de Proyectos (Solución)

```
GestionPersonal.sln
├── GestionPersonal.Web/                   ← Capa de Presentación (MVC)
│   ├── Controllers/
│   ├── Views/
│   ├── ViewModels/
│   ├── AutoMapper/
│   │   └── AutoMapperURT.cs         ← Perfil único de AutoMapper
│   ├── DependencyContainer/
│   │   └── DependencyContainer.cs   ← Punto único de registro de dependencias
│   └── wwwroot/
├── GestionPersonal.Application/           ← Capa de Aplicación (lógica de negocio)
│   ├── Services/
│   ├── Interfaces/
│   └── AccessDependency/
│       └── ApplicationAccessDependency.cs
├── GestionPersonal.Models/                ← Capa de Modelos (centraliza DTOs, entidades y enums)
│   ├── DTOs/                        ← Data Transfer Objects por módulo
│   │   ├── Empleado/
│   │   │   ├── EmpleadoDto.cs
│   │   │   ├── EmpleadoListaDto.cs
│   │   │   ├── CrearEmpleadoDto.cs
│   │   │   └── EditarEmpleadoDto.cs
│   │   ├── EventoLaboral/
│   │   │   ├── EventoLaboralDto.cs
│   │   │   └── CrearEventoLaboralDto.cs
│   │   ├── HoraExtra/
│   │   ├── Turno/
│   │   ├── Dashboard/
│   │   └── Cuenta/
│   │       ├── UsuarioSesionDto.cs
│   │       └── LoginDto.cs
│   ├── Entities/                    ← Generadas con EF Core scaffold
│   │   └── GestionPersonalEntities/       ← Carpeta nombrada: {NombreProyecto}Entities
│   │       ├── AppDbContext.cs      ← DbContext de la base de datos
│   │       ├── Configurations/      ← IEntityTypeConfiguration<T> por entidad
│   │       │   ├── EmpleadoConfiguration.cs
│   │       │   ├── SedeConfiguration.cs
│   │       │   └── ...
│   │       ├── Empleado.cs
│   │       ├── Sede.cs
│   │       ├── Cargo.cs
│   │       └── ...
│   ├── Models/                      ← Modelos de resultado, paginación y respuesta
│   │   ├── ResultadoOperacion.cs
│   │   └── PaginacionModel.cs
│   └── Enums/                       ← Enums del dominio (accesibles por todas las capas)
│       ├── EstadoEmpleado.cs
│       ├── RolUsuario.cs
│       ├── TipoVinculacion.cs
│       ├── TipoEvento.cs
│       └── ...
├── GestionPersonal.Domain/                ← Capa de Dominio (contratos de repositorios)
│   └── Interfaces/                  ← Solo interfaces; las entidades viven en Models
│       ├── IEmpleadoRepository.cs
│       ├── IEventoLaboralRepository.cs
│       └── ...
├── GestionPersonal.Infrastructure/        ← Capa de Infraestructura (repositorios, migraciones)
│   ├── Repositories/
│   ├── Migrations/                  ← Migraciones EF Core (DbContext vive en Models)
│   └── AccessDependency/
│       └── InfrastructureAccessDependency.cs
├── GestionPersonal.Helpers/               ← Capa de Helpers (utilidades reutilizables)
│   ├── Email/
│   │   ├── IEmailHelper.cs
│   │   └── EmailHelper.cs
│   ├── Security/
│   │   ├── ICodigoHelper.cs
│   │   ├── CodigoGeneradorHelper.cs
│   │   └── PasswordHelper.cs
│   └── AccessDependency/
│       └── HelperAccessDependency.cs
└── GestionPersonal.Constants/             ← Capa de Constantes (mensajes de texto sin dependencias)
    └── Messages/
        ├── InicioSesionConstant.cs
        ├── EmpleadoConstant.cs
        └── EmailConstant.cs
```

## Convenciones por Capa

### Capa de Models (`Models`) ← **capa central de modelos**
- Proyecto de clase referenciado por **todas** las capas. Es la única fuente de verdad para entidades, DTOs, enums y modelos de resultado.
- Tiene **package reference** a `Microsoft.EntityFrameworkCore.SqlServer` (necesario para `AppDbContext` y las configuraciones).
- **No** referencia `Application`, `Infrastructure`, `Web` ni `Domain`.

#### Subcarpetas

| Carpeta | Contenido |
|---|---|
| `DTOs/` | Data Transfer Objects agrupados por módulo |
| `Entities/{Proyecto}Entities/` | POCOs generados por scaffold + `AppDbContext.cs` + `Configurations/` |
| `Models/` | Modelos de resultado, respuesta y paginación |
| `Enums/` | Todos los enums del dominio |

#### Convención de nombre para la carpeta de entidades

La carpeta dentro de `Entities/` se nombra **`{NombreProyecto}Entities`** (sin punto ni espacio):
- Proyecto `GestionPersonal` → carpeta `GestionPersonalEntities`

Esta carpeta contiene exactamente lo que genera el scaffold de EF Core más las clases de configuración:

```
Entities/
└── GestionPersonalEntities/
    ├── AppDbContext.cs          ← DbContext (generado por scaffold, ajustar namespace)
    ├── Configurations/          ← IEntityTypeConfiguration<T> por entidad
    │   ├── EmpleadoConfiguration.cs
    │   ├── SedeConfiguration.cs
    │   └── ...
    ├── Empleado.cs
    ├── Sede.cs
    ├── Cargo.cs
    └── ...
```

#### Enums en `Models/Enums/`

Todos los enums del dominio viven en `Models/Enums/` y son accesibles por todas las capas:

```csharp
// Models/Enums/EstadoEmpleado.cs
public enum EstadoEmpleado { Activo, Inactivo }

// Models/Enums/RolUsuario.cs
public enum RolUsuario { Jefe, Regente, AuxiliarRegente, Operario, Administrador }

// Models/Enums/TipoVinculacion.cs
public enum TipoVinculacion { Directo, Temporal }

// Models/Enums/TipoEvento.cs
public enum TipoEvento { Vacaciones, Incapacidad, Permiso }
```

#### Modelos de resultado en `Models/Models/`

```csharp
// Models/Models/ResultadoOperacion.cs
public class ResultadoOperacion
{
    public bool   Exito   { get; init; }
    public string Mensaje { get; init; } = string.Empty;
    public static ResultadoOperacion Ok(string mensaje = "")   => new() { Exito = true,  Mensaje = mensaje };
    public static ResultadoOperacion Fail(string mensaje)      => new() { Exito = false, Mensaje = mensaje };
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

### Capa de Dominio (`Domain`)
- Contiene **únicamente interfaces de repositorio**. Las entidades, enums y DTOs se trasladaron a `Models`.
- Referencia `GestionPersonal.Models` para usar los tipos de entidad en las firmas de sus interfaces.
- **No** contiene lógica ni implementaciones.

```csharp
// Domain/Interfaces/IEmpleadoRepository.cs
// Los tipos Empleado, EstadoEmpleado, etc. vienen de GestionPersonal.Models
public interface IEmpleadoRepository
{
    Task<Empleado?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<Empleado>> ObtenerActivosPorSedeAsync(int sedeId, CancellationToken ct = default);
    void Agregar(Empleado empleado);
    void Actualizar(Empleado empleado);
    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}
```

---

### Capa de Constants (`Constants`)
- Proyecto de clase sin dependencias externas. Solo `string const` y enums.
- **No** referencia ninguna otra capa del proyecto.
- Organizar en clases estáticas agrupadas por contexto funcional.
- Los mensajes de correo usan `{placeholder}` (llaves simples) para los valores dinámicos que se reemplazan en runtime.
- **Regla:** todo mensaje visible al usuario (errores, éxito, correos) debe venir de una clase `Constant`. Nunca strings hardcodeados en controllers o services.
- **Ejemplo:**

```csharp
// Constants/Messages/InicioSesionConstant.cs
public static class InicioSesionConstant
{
    public const string UsuarioIncorrecto  = "Datos incorrectos";
    public const string UsuarioInactivo    = "La cuenta no se ha activado";
    public const string UsuarioSuspendido  = "La cuenta está suspendida temporalmente";
    public const string UsuarioBienvenido  = "Bienvenid@.";
    public const string SesionExpirada     = "Tu sesión ha expirado. Por favor inicia sesión nuevamente.";
    public const string AccesoDenegado     = "No tienes permisos para acceder a esta sección.";
}

// Constants/Messages/EmpleadoConstant.cs
public static class EmpleadoConstant
{
    public const string CedulaDuplicada          = "Ya existe un empleado registrado con esa cédula.";
    public const string EmpleadoNoEncontrado     = "El empleado no fue encontrado.";
    public const string EmpleadoDesactivado      = "El empleado fue desvinculado exitosamente.";
    public const string MotivoRetiroObligatorio  = "El motivo de retiro es obligatorio.";
}

// Constants/Messages/EmailConstant.cs
public static class EmailConstant
{
    #region RESTABLECER CONTRASEÑA

    public const string AsuntoRestablecerContrasena = "Restablecer Contraseña";

    public const string CuerpoRestablecerContrasena = @"
        <p>Estimado usuario,</p>
        <p>Hemos recibido una solicitud para restablecer la contraseña de su cuenta en <strong>GestiónPersonal</strong>.</p>
        <p>Para completar el proceso, utilice el siguiente código:</p>
        <h2 style='color: #1e3a8a;'>{codigo}</h2>
        <p><strong>Este código es de un solo uso y tiene una vigencia de 1 hora.</strong></p>
        <p>Si no solicitó este cambio, ignore este mensaje.</p>
        <p>Atentamente,<br/><strong>Equipo GestiónPersonal</strong></p>";

    #endregion

    #region CREAR USUARIO

    public const string AsuntoUsuarioNuevo = "Bienvenid@ a GestiónPersonal";

    public const string CuerpoCrearUsuario = @"
        <p>Estimado usuario,</p>
        <p>Tu cuenta en <strong>GestiónPersonal</strong> ha sido creada exitosamente.</p>
        <p>Tus credenciales de acceso son:</p>
        <ul>
          <li><strong>Correo:</strong> {correo}</li>
          <li><strong>Contraseña temporal:</strong> {contrasenaTemp}</li>
        </ul>
        <p>Deberás cambiar tu contraseña al iniciar sesión por primera vez.</p>
        <p>Atentamente,<br/><strong>Equipo GestiónPersonal</strong></p>";

    #endregion
}
```

> **Regla:** todo mensaje visible al usuario (errores, éxito, correos) debe venir de una clase `Constant`. Nunca strings hardcodeados en controllers o services.

---

### Capa de Helpers (`Helpers`)
- Clases de utilidad reutilizables sin lógica de negocio.
- Cada helper tiene su interfaz correspondiente para permitir inyección de dependencias y testing.
- Registrar todas las implementaciones en `HelperAccessDependency`.
- **Ejemplos de helpers comunes:**
  - `EmailHelper` → envío de correos con plantillas.
  - `PasswordHelper` → generación y verificación de hashes de contraseña.
  - `CodigoGeneradorHelper` → generación de códigos únicos para verificación o recuperación.

#### EmailHelper

```csharp
// Helpers/Email/IEmailHelper.cs
public interface IEmailHelper
{
    Task EnviarCorreoAsync(string destinatario, string asunto, string cuerpo);
    Task EnviarCorreoConCodigoAsync(string destinatario, string asunto, string plantilla, string codigo);
    Task EnviarCorreoNuevoUsuarioAsync(string destinatario, string asunto, string plantilla, string correo, string contrasenaTemp);
}

// Helpers/Email/EmailHelper.cs
public class EmailHelper : IEmailHelper
{
    private readonly IConfiguration _config;

    public EmailHelper(IConfiguration config)
    {
        _config = config;
    }

    private SmtpClient CrearCliente()
    {
        return new SmtpClient
        {
            Host                  = _config["Email:Host"]!,
            Port                  = int.Parse(_config["Email:Port"]!),
            EnableSsl             = true,
            UseDefaultCredentials = false,
            Credentials           = new NetworkCredential(
                _config["Email:Remitente"],
                _config["Email:Contrasena"])
        };
    }

    public async Task EnviarCorreoAsync(string destinatario, string asunto, string cuerpo)
    {
        using var smtp    = CrearCliente();
        using var mensaje = new MailMessage(_config["Email:Remitente"]!, destinatario)
        {
            Subject    = asunto,
            Body       = cuerpo,
            IsBodyHtml = true
        };
        await smtp.SendMailAsync(mensaje);
    }

    public async Task EnviarCorreoConCodigoAsync(
        string destinatario, string asunto, string plantilla, string codigo)
    {
        string cuerpo = plantilla.Replace("{codigo}", codigo);
        await EnviarCorreoAsync(destinatario, asunto, cuerpo);
    }

    public async Task EnviarCorreoNuevoUsuarioAsync(
        string destinatario, string asunto, string plantilla, string correo, string contrasenaTemp)
    {
        string cuerpo = plantilla
            .Replace("{correo}", correo)
            .Replace("{contrasenaTemp}", contrasenaTemp);
        await EnviarCorreoAsync(destinatario, asunto, cuerpo);
    }
}
```

> **Regla de seguridad:** las credenciales SMTP siempre desde `appsettings.json` / variables de entorno. Nunca `new SmtpClient` con strings hardcodeados. Configurar en `appsettings.json`:
> ```json
> "Email": {
>   "Host": "smtp.tuproveedor.com",
>   "Port": "587",
>   "Remitente": "noreply@gestionpersonal.com",
>   "Contrasena": ""
> }
> ```

#### PasswordHelper

```csharp
// Helpers/Security/PasswordHelper.cs
// Clase estática → no requiere interfaz ni inyección de dependencias
public static class PasswordHelper
{
    private const int Iteraciones = 10000;
    private const int TamanioHash = 32;  // 256 bits

    /// <summary>Genera hash + salt usando PBKDF2/SHA-256. Almacenar ambos en la BD.</summary>
    public static (byte[] Hash, byte[] Salt) CrearHash(string password)
    {
        byte[] salt = new byte[16];
        using (var rng = RandomNumberGenerator.Create())
            rng.GetBytes(salt);

        using var pbkdf2 = new Rfc2898DeriveBytes(
            password, salt, Iteraciones, HashAlgorithmName.SHA256);

        return (pbkdf2.GetBytes(TamanioHash), salt);
    }

    /// <summary>Verifica una contraseña contra el hash y salt almacenados.</summary>
    public static bool VerificarPassword(string password, byte[] hashGuardado, byte[] saltGuardado)
    {
        using var pbkdf2 = new Rfc2898DeriveBytes(
            password, saltGuardado, Iteraciones, HashAlgorithmName.SHA256);

        byte[] hashComparar = pbkdf2.GetBytes(TamanioHash);
        return hashComparar.SequenceEqual(hashGuardado);
    }

    /// <summary>Genera una contraseña temporal aleatoria de longitud configurable.</summary>
    public static string GenerarContrasenaTemp(int longitud = 10)
    {
        const string chars = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#";
        var random = RandomNumberGenerator.GetBytes(longitud);
        return new string(random.Select(b => chars[b % chars.Length]).ToArray());
    }
}
```

> **Notas de seguridad:**
> - Usar `PBKDF2` con `SHA-256` y 10 000 iteraciones (mínimo recomendado NIST).
> - **Nunca** `MD5` ni `SHA1` para contraseñas.
> - Almacenar `Hash` y `Salt` en columnas separadas tipo `VARBINARY(64)` en la BD.
> - `SequenceEqual` hace comparación constante y evita timing attacks en comparación básica; para producción crítica considerar `CryptographicOperations.FixedTimeEquals`.

#### CodigoGeneradorHelper

```csharp
// Helpers/Security/ICodigoHelper.cs
public interface ICodigoHelper
{
    string GenerarCodigoUnico();
}

// Helpers/Security/CodigoGeneradorHelper.cs
public class CodigoGeneradorHelper : ICodigoHelper
{
    /// <summary>
    /// Genera un código único de 8 caracteres alfanuméricos (base 36, A-Z 0-9).
    /// Útil para tokens de verificación, recuperación de contraseña, etc.
    /// </summary>
    public string GenerarCodigoUnico()
    {
        BigInteger bigInt = new BigInteger(Guid.NewGuid().ToByteArray());
        if (bigInt < 0) bigInt = -bigInt;
        return Base36Encode(bigInt)[..8].ToUpper();
    }

    private static string Base36Encode(BigInteger value)
    {
        const string Caracteres = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        var resultado = new System.Text.StringBuilder();

        do
        {
            resultado.Insert(0, Caracteres[(int)(value % 36)]);
            value /= 36;
        }
        while (value > 0);

        return resultado.ToString();
    }
}
```

#### AccessDependency de Helpers

```csharp
// Helpers/AccessDependency/HelperAccessDependency.cs
public static class HelperAccessDependency
{
    public static IServiceCollection AddHelpers(this IServiceCollection services)
    {
        services.AddScoped<IEmailHelper, EmailHelper>();
        services.AddScoped<ICodigoHelper, CodigoGeneradorHelper>();
        return services;
    }
}
```

---

### Capa de Aplicación (`Application`)
- Los **Services** orquestan la lógica de negocio, coordinan repositorios y usan helpers.
- Reciben y devuelven **DTOs** que viven en `GestionPersonal.Models/DTOs/`; **nunca** exponen entidades hacia la capa Web.
- **No** contiene DTOs propios; los importa directamente de `GestionPersonal.Models`.
- Referencia: `GestionPersonal.Domain` (interfaces de repositorio) + `GestionPersonal.Models` (DTOs, entidades, enums, modelos de resultado) + `GestionPersonal.Helpers` + `GestionPersonal.Constants`.

#### AccessDependency de Application

```csharp
// Application/AccessDependency/ApplicationAccessDependency.cs
public static class ApplicationAccessDependency
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        services.AddScoped<IEmpleadoService, EmpleadoService>();
        services.AddScoped<IUsuarioService, UsuarioService>();
        services.AddScoped<IEventoLaboralService, EventoLaboralService>();
        services.AddScoped<IHoraExtraService, HoraExtraService>();
        services.AddScoped<ITurnoService, TurnoService>();
        // AutoMapper (si se usa):
        // services.AddAutoMapper(typeof(ApplicationAccessDependency).Assembly);
        return services;
    }
}
```

---

### Capa de Infraestructura (`Infrastructure`)
- **No** contiene `AppDbContext.cs` ni configuraciones de entidad → esos archivos viven en `GestionPersonal.Models/Entities/{Proyecto}Entities/`.
- Solo contiene repositorios, migraciones y su `AccessDependency`.
- Referencia: `GestionPersonal.Domain` (interfaces) + `GestionPersonal.Models` (entidades, DbContext, enums).
- Las **Migrations** se generan en este proyecto usando `MigrationsAssembly`.

```csharp
// Infrastructure/AccessDependency/InfrastructureAccessDependency.cs
public static class InfrastructureAccessDependency
{
    public static IServiceCollection AddInfrastructure(
        this IServiceCollection services, IConfiguration configuration)
    {
        // AppDbContext vive en GestionPersonal.Models; las Migrations se almacenan aquí
        services.AddDbContext<AppDbContext>(options =>
            options.UseSqlServer(
                configuration.GetConnectionString("Default"),
                sql => sql.MigrationsAssembly("GestionPersonal.Infrastructure")));

        services.AddScoped<IEmpleadoRepository, EmpleadoRepository>();
        services.AddScoped<IUsuarioRepository, UsuarioRepository>();
        services.AddScoped<IEventoLaboralRepository, EventoLaboralRepository>();
        services.AddScoped<IHoraExtraRepository, HoraExtraRepository>();
        return services;
    }
}
```

#### Scaffold de Entidades desde BD existente

Ejecutar **después** de crear la base de datos. El destino es **`GestionPersonal.Models`**, carpeta `Entities/{Proyecto}Entities`:

```bash
dotnet ef dbcontext scaffold \
  "Server=SERVIDOR\SQLEXPRESS;Database=GestionPersonal;Trusted_Connection=True;TrustServerCertificate=True;" \
  Microsoft.EntityFrameworkCore.SqlServer \
  -o Entities/GestionPersonalEntities \
  --context AppDbContext \
  --force \
  --project "ruta\GestionPersonal.Models\GestionPersonal.Models.csproj" \
  --startup-project "ruta\GestionPersonal.Web\GestionPersonal.Web.csproj"
```

> **Flags importantes:**
> - `-o Entities/GestionPersonalEntities` → subcarpeta nombrada `{Proyecto}Entities` dentro de `Entities/`.
> - `--context AppDbContext` → nombre de la clase DbContext generada.
> - `--force` → sobreescribe archivos si ya existen.
> - `--project` → **`GestionPersonal.Models`** (no Domain); aquí vivirán entidades y DbContext.
> - `--startup-project` → proyecto con `appsettings.json` (generalmente `Web`).

> Después del scaffold, crear la carpeta `Entities/GestionPersonalEntities/Configurations/` y mover o crear los archivos `IEntityTypeConfiguration<T>` allí. El namespace de `AppDbContext.cs` debe quedar `GestionPersonal.Models.Entities.GestionPersonalEntities`.

---

### Capa de Presentación (`Web`)

#### Controllers (delgados)

```csharp
// Web/Controllers/EmpleadoController.cs
[Authorize]
public class EmpleadoController : Controller
{
    private readonly IEmpleadoService _empleadoService;

    public EmpleadoController(IEmpleadoService empleadoService)
        => _empleadoService = empleadoService;

    public async Task<IActionResult> Index()
    {
        var empleados = await _empleadoService.ObtenerTodosAsync();
        return View(empleados);
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Crear(CrearEmpleadoViewModel vm)
    {
        if (!ModelState.IsValid)
            return View(vm);

        await _empleadoService.CrearAsync(vm.ToDto());
        TempData["Exito"] = EmpleadoConstant.EmpleadoCreado;
        return RedirectToAction(nameof(Index));
    }
}
```

#### ViewModels con DataAnnotations e IValidatableObject

```csharp
// Web/ViewModels/Empleado/CrearEmpleadoViewModel.cs
public class CrearEmpleadoViewModel : IValidatableObject
{
    [Required(ErrorMessage = "El nombre completo es obligatorio.")]
    [MaxLength(200, ErrorMessage = "El nombre no puede superar los 200 caracteres.")]
    public string NombreCompleto { get; set; } = string.Empty;

    [Required(ErrorMessage = "La cédula es obligatoria.")]
    [RegularExpression(@"^\d{6,12}$", ErrorMessage = "La cédula debe contener entre 6 y 12 dígitos.")]
    public string Cedula { get; set; } = string.Empty;

    [Required(ErrorMessage = "La fecha de ingreso es obligatoria.")]
    [DataType(DataType.Date)]
    public DateOnly FechaIngreso { get; set; }

    [Required(ErrorMessage = "El tipo de vinculación es obligatorio.")]
    public TipoVinculacion TipoVinculacion { get; set; }

    // Campos condicionales → solo obligatorios si TipoVinculacion = Temporal
    public int? EmpresaTemporalId { get; set; }

    [DataType(DataType.Date)]
    public DateOnly? FechaInicioContrato { get; set; }

    [DataType(DataType.Date)]
    public DateOnly? FechaFinContrato { get; set; }

    /// <summary>Validaciones cruzadas que DataAnnotations no puede expresar.</summary>
    public IEnumerable<ValidationResult> Validate(ValidationContext validationContext)
    {
        if (TipoVinculacion == TipoVinculacion.Temporal)
        {
            if (EmpresaTemporalId is null)
                yield return new ValidationResult(
                    "La empresa temporal es obligatoria para contratos temporales.",
                    [nameof(EmpresaTemporalId)]);

            if (FechaInicioContrato is null)
                yield return new ValidationResult(
                    "La fecha de inicio del contrato es obligatoria.",
                    [nameof(FechaInicioContrato)]);

            if (FechaFinContrato is null)
                yield return new ValidationResult(
                    "La fecha de fin del contrato es obligatoria.",
                    [nameof(FechaFinContrato)]);

            if (FechaInicioContrato.HasValue && FechaFinContrato.HasValue
                && FechaFinContrato < FechaInicioContrato)
                yield return new ValidationResult(
                    "La fecha de fin no puede ser anterior a la fecha de inicio.",
                    [nameof(FechaFinContrato)]);
        }

        if (FechaIngreso > DateOnly.FromDateTime(DateTime.Today))
            yield return new ValidationResult(
                "La fecha de ingreso no puede ser futura.",
                [nameof(FechaIngreso)]);
    }
}
```

#### Cookies de Sesión (Autenticación)

Configurar en `Program.cs` para que la sesión sea segura y el usuario no pueda volver al login al retroceder con el botón Atrás, ni acceder a rutas protegidas tras cerrar sesión:

```csharp
// Program.cs
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.LoginPath        = "/Cuenta/Login";
        options.LogoutPath       = "/Cuenta/Logout";
        options.AccessDeniedPath = "/Cuenta/Acceso-Denegado";
        options.ExpireTimeSpan   = TimeSpan.FromMinutes(30);     // inactividad → logout
        options.SlidingExpiration = true;                         // renueva el tiempo en cada request
        options.Cookie.HttpOnly  = true;                          // no accesible desde JS
        options.Cookie.SecurePolicy = CookieSecurePolicy.Always; // solo HTTPS
        options.Cookie.SameSite  = SameSiteMode.Strict;
    });

// Evitar cache de páginas protegidas (botón Atrás no muestra contenido tras logout)
builder.Services.AddControllersWithViews(options =>
{
    options.Filters.Add(new ResponseCacheAttribute
    {
        NoStore = true,
        Location = ResponseCacheLocation.None
    });
});
```

```csharp
// Web/Controllers/CuentaController.cs
public class CuentaController : Controller
{
    private readonly IUsuarioService _usuarioService;

    public CuentaController(IUsuarioService usuarioService)
        => _usuarioService = usuarioService;

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Login(LoginViewModel vm)
    {
        if (!ModelState.IsValid)
            return View(vm);

        var usuario = await _usuarioService.ValidarCredencialesAsync(vm.Correo, vm.Password);

        if (usuario is null)
        {
            ModelState.AddModelError(string.Empty, InicioSesionConstant.UsuarioIncorrecto);
            return View(vm);
        }

        var claims = new List<Claim>
        {
            new(ClaimTypes.NameIdentifier, usuario.Id.ToString()),
            new(ClaimTypes.Email,          usuario.Correo),
            new(ClaimTypes.Role,           usuario.Rol.ToString()),
            new("SedeId",                  usuario.SedeId.ToString())
        };

        var identity  = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
        var principal = new ClaimsPrincipal(identity);

        await HttpContext.SignInAsync(
            CookieAuthenticationDefaults.AuthenticationScheme,
            principal,
            new AuthenticationProperties
            {
                IsPersistent = false,   // no recordar sesión entre reinicios del navegador
                ExpiresUtc   = DateTimeOffset.UtcNow.AddMinutes(30)
            });

        return RedirectToAction("Index", "Dashboard");
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Logout()
    {
        await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);

        // Forzar headers anti-caché para que el botón Atrás no muestre páginas protegidas
        Response.Headers.CacheControl = "no-cache, no-store, must-revalidate";
        Response.Headers.Pragma       = "no-cache";
        Response.Headers.Expires      = "0";

        return RedirectToAction("Login");
    }
}
```

> **Reglas de seguridad de cookies:**
> - `HttpOnly = true` → previene acceso desde JavaScript (mitigación XSS).
> - `SecurePolicy = Always` → la cookie solo viaja por HTTPS.
> - `SameSite = Strict` → protección contra CSRF en requests cross-site.
> - `IsPersistent = false` → la sesión muere al cerrar el navegador.
> - `NoStore = true` en `ResponseCache` → el navegador no cachea páginas protegidas (al dar Atrás tras logout se solicita de nuevo al servidor, que redirige al login).

---

## Registro de Dependencias en Program.cs

El único punto de entrada es `DependencyContainer`, ubicado en `Web/DependencyContainer/DependencyContainer.cs`. Centraliza el registro de todas las capas e internamente llama a cada `AccessDependency`.

```csharp
// Web/DependencyContainer/DependencyContainer.cs
public static class DependencyContainer
{
    public static IServiceCollection DependencyInjection(
        this IServiceCollection services, IConfiguration configuration)
    {
        services.AddInfrastructure(configuration);   // EF Core + repositorios
        services.AddApplication();                   // services de negocio
        services.AddHelpers();                       // Email, Password, Excel, etc.
        services.AddAutoMapper(typeof(AutoMapperURT)); // perfil único en Web/AutoMapper/

        services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
            .AddCookie(options => { /* ver sección Cookies de Sesión */ });

        services.AddAuthorization();
        services.AddControllersWithViews(options =>
            options.Filters.Add(new ResponseCacheAttribute
            {
                NoStore = true, Location = ResponseCacheLocation.None
            }));

        return services;
    }
}

// Program.cs → una sola línea
var builder = WebApplication.CreateBuilder(args);

builder.Services.DependencyInjection(builder.Configuration);

var app = builder.Build();

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();
app.UseAuthentication();   // debe ir ANTES de UseAuthorization
app.UseAuthorization();
app.MapDefaultControllerRoute();
app.Run();
```

---

## Convenciones de Nomenclatura

| Elemento                    | Convención                               | Ejemplo                                    |
|-----------------------------|------------------------------------------|--------------------------------------------|
| Clases                      | PascalCase                               | `EmpleadoService`                          |
| Interfaces                  | PascalCase con `I` prefijo               | `IEmpleadoRepository`                      |
| Métodos async               | PascalCase + sufijo `Async`              | `ObtenerPorIdAsync`                        |
| Variables locales           | camelCase                                | `empleadoDto`                              |
| Constantes                  | PascalCase                               | `UsuarioIncorrecto`                        |
| Parámetros                  | camelCase                                | `sedeId`, `motivoRetiro`                   |
| DTOs                        | Nombre + sufijo `Dto`                    | `EmpleadoDto`, `CrearEmpleadoDto`          |
| ViewModels                  | Nombre + sufijo `ViewModel`              | `CrearEmpleadoViewModel`                   |
| AutoMapper perfil           | `AutoMapper` + nombre del proyecto       | `AutoMapperURT`                            |
| Carpeta de entidades        | `{NombreProyecto}Entities`               | `GestionPersonalEntities`                  |
| Modelos de resultado        | Nombre + sufijo `Model` o `Operacion`    | `ResultadoOperacion`, `PaginacionModel`    |
| AccessDependency            | Capa + `AccessDependency`                | `HelperAccessDependency`                   |
| DependencyContainer         | Siempre `DependencyContainer`            | `DependencyContainer.cs`                   |
| Constants                   | Contexto + `Constant`                    | `InicioSesionConstant`                     |
| Helpers                     | Función + `Helper`                       | `PasswordHelper`, `EmailHelper`            |

---

## Flujo de Referencias entre Capas

```
Web  ----------→  Application  ----------→  Domain
 ↓                    ↓                       ↓
 ↓                    ↓                       ↓
 ↓                 Helpers                Infrastructure
 ↓                    ↓                       ↓
 ↓                    ↓                       ↓
 +--------------------------------------------+
            ↓                     ↓
          Models  ←----------  Constants
```

- `Constants` no referencia a nadie. Solo `string const` y sin dependencias externas.
- `Models` referencia únicamente `Constants` (para mensajes en modelos, si aplica). Tiene `Microsoft.EntityFrameworkCore.SqlServer`.
- `Helpers` referencia `Constants`.
- `Domain` referencia `Models` (tipos de entidad en interfaces de repositorio).
- `Application` referencia `Domain`, `Models`, `Helpers` y `Constants`.
- `Infrastructure` referencia `Domain` y `Models` (entidades, DbContext, enums).
- `Web` referencia `Application`, `Models`, `Constants` y `Helpers` (solo a través de interfaces).
- **Nunca** `Infrastructure` referencia `Web`.
- **Nunca** `Application` referencia `Infrastructure` directamente (solo vía interfaces de `Domain`).
- **Nunca** ninguna capa referencia `Web`.

---

## Reglas Generales

- `SET NOCOUNT ON` en todos los SPs (ver skill `sqlserver-stored-procedures`).
- Todos los métodos que tocan base de datos deben ser `async/await` con `CancellationToken`.
- Los strings de conexión siempre desde `appsettings.json` o variables de entorno, **nunca** hardcodeados.
- Habilitar `Nullable reference types` en todos los proyectos: `<Nullable>enable</Nullable>`.
- Validar `ModelState.IsValid` en cada `[HttpPost]` antes de llamar al servicio.
- Usar `[ValidateAntiForgeryToken]` en todos los formularios POST (prevención CSRF).
- Los mensajes al usuario siempre desde clases `Constant`; nunca strings literales en controllers.
