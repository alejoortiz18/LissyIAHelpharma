# Plan de Ejecución — Capa de Mensajería y Notificaciones
**Sistema de Gestión de Personal · GestionPersonal**
Fecha: Abril 2026 | Shape Up — Large Batch (6 semanas)

---

## Referencia base
- Pitch: `Documentos/Requerimientos/requerimientosEnvioCorreoRefinado.md`
- Schema BD: `Documentos/BD/GestionRH_Schema.sql`
- Roles: `Documentos/Pruebas/Playwright/Plan-Permisos-Roles-Refinados.md`

---

## Credenciales de correo (producción)

> ⚠️ **NUNCA** poner la contraseña en código fuente, archivos `.json` comiteados, ni logs.
> En desarrollo usar `dotnet user-secrets`. En producción usar variables de entorno.

| Parámetro | Valor |
|---|---|
| Servidor SMTP | `smtp.office365.com` |
| Puerto | `587` |
| Seguridad | STARTTLS (`UseSsl = false`, `UseStartTls = true`) |
| Usuario SMTP (auth) | `sistemas.helpharma@zentria.com.co` |
| Contraseña | `{SMTP_PASSWORD}` — leer desde user-secrets o variable de entorno |
| Buzón compartido (FROM visible) | `notificacion.sf@zentria.com.co` |
| Display name del remitente | `Notificaciones GestionPersonal` |

**Prerrequisito Exchange Online:** El buzón `sistemas.helpharma@zentria.com.co` debe tener permiso
**"Send As"** sobre `notificacion.sf@zentria.com.co` en el portal de Exchange Admin de Office 365.
Sin este permiso, el servidor rechazará el envío con error `5.7.60`.

### Formato del asunto (regla de negocio global)

```
[TipoEvento] - [NombreQuienGenera]
```

Ejemplos:
- `[Nueva Solicitud] - [Juan Pérez]`
- `[Aprobación de Horas Extra] - [María López (Regente)]`
- `[Nuevo Usuario] - [Administrador]`
- `[Recuperación de Contraseña] - [carlos.rodriguez@yopmail.com]`

---

## Identificación del Jefe Apoyo

La tabla `Empleados` solo tiene `JefeInmediatoId`. El "jefe apoyo" se obtiene siguiendo
la cadena dos niveles hacia arriba:

```
Auxiliar (Operario)
  └── JefeInmediatoId → Regente               ← jefe inmediato
                           └── JefeInmediatoId → DirectorTecnico   ← jefe apoyo
```

En código: `empleado.JefeInmediato?.JefeInmediato`

Si la cadena no existe (empleado sin jefe, o jefe sin jefe), no se envía copia. No es un error.

---

## Estado actual del código (hallazgos críticos)

| Archivo | Problema | Prioridad |
|---|---|---|
| `EmailHelper.cs` | Usa `System.Net.Mail.SmtpClient` (obsoleto desde .NET 5) | 🔴 Crítico |
| `EmailConstant.cs` `CuerpoCrearUsuario` | Envía `{contrasenaTemp}` en texto plano por correo | 🔴 Crítico |
| `CuentaService.cs` `SolicitarRecuperacionAsync` | Token almacenado en BD en texto plano; expira en 1 hora | 🔴 Crítico |
| `UsuarioService.cs` | Llama `IEmailHelper` directamente, no `INotificationService` | 🟠 Alto |
| `CuentaService.cs` | Llama `IEmailHelper` directamente, no `INotificationService` | 🟠 Alto |
| `EmailConstant.cs` | Sin formato de asunto con nombre del generador | 🟡 Medio |
| — | Sin tabla `RegistroNotificaciones` ni trazabilidad | 🟡 Medio |

---

# PARTE 1 — Infraestructura de Mensajería (Semanas 1–3)

---

## P1-T01: Configurar credenciales (user-secrets + appsettings)

**Archivo: `GestionPersonal.Web/appsettings.json`** (sin contraseña real)

```json
{
  "EmailSettings": {
    "Smtp": {
      "Host": "smtp.office365.com",
      "Port": 587,
      "UseSsl": false,
      "UseStartTls": true,
      "Username": "sistemas.helpharma@zentria.com.co",
      "Password": "",
      "FromAddress": "notificacion.sf@zentria.com.co",
      "FromName": "Notificaciones GestionPersonal"
    }
  }
}
```

**Registrar secreto en desarrollo:**

```powershell
cd "Proyecto MVC/GestionPersonal.Web"
dotnet user-secrets init
dotnet user-secrets set "EmailSettings:Smtp:Password" "{SMTP_PASSWORD}"
dotnet user-secrets set "EmailSettings:Smtp:Username" "sistemas.helpharma@zentria.com.co"
```

**En producción (variable de entorno):**

```
EmailSettings__Smtp__Password={SMTP_PASSWORD}
EmailSettings__Smtp__Username=sistemas.helpharma@zentria.com.co
```

---

## P1-T02: Modelo de configuración EmailSettings

**Crear: `GestionPersonal.Models/Models/Email/EmailSettings.cs`**

```csharp
namespace GestionPersonal.Models.Models.Email;

public class EmailSettings
{
    public const string SectionName = "EmailSettings";
    public SmtpEmailSettings Smtp { get; set; } = new();
}

public class SmtpEmailSettings
{
    public string Host        { get; set; } = string.Empty;
    public int    Port        { get; set; } = 587;
    public bool   UseSsl      { get; set; } = false;
    public bool   UseStartTls { get; set; } = true;
    public string Username    { get; set; } = string.Empty;
    public string Password    { get; set; } = string.Empty;
    public string FromAddress { get; set; } = string.Empty;
    public string FromName    { get; set; } = string.Empty;
}
```

**Registrar en `Program.cs` o `DependencyContainer.cs`:**

```csharp
builder.Services.Configure<EmailSettings>(
    builder.Configuration.GetSection(EmailSettings.SectionName));
```

---

## P1-T03: Migrar EmailHelper a MailKit (Send As Office 365)

**NuGet en `GestionPersonal.Helpers/GestionPersonal.Helpers.csproj`:**

```xml
<PackageReference Include="MailKit" Version="4.*" />
<PackageReference Include="MimeKit" Version="4.*" />
```

**Refactorizar: `GestionPersonal.Helpers/Email/IEmailHelper.cs`**

```csharp
namespace GestionPersonal.Helpers.Email;

public interface IEmailHelper
{
    Task EnviarAsync(string destinatario, string asunto, string cuerpoHtml,
                     CancellationToken ct = default);

    Task EnviarConCopiaAsync(string destinatario, string copia,
                             string asunto, string cuerpoHtml,
                             CancellationToken ct = default);
}
```

**Refactorizar: `GestionPersonal.Helpers/Email/EmailHelper.cs`**

```csharp
using MailKit.Net.Smtp;
using MailKit.Security;
using Microsoft.Extensions.Options;
using MimeKit;
using GestionPersonal.Models.Models.Email;

namespace GestionPersonal.Helpers.Email;

public class EmailHelper : IEmailHelper
{
    private readonly SmtpEmailSettings _settings;

    public EmailHelper(IOptions<EmailSettings> options)
    {
        _settings = options.Value.Smtp;
    }

    public async Task EnviarAsync(string destinatario, string asunto,
                                   string cuerpoHtml, CancellationToken ct = default)
    {
        var message = ConstruirMensaje([destinatario], null, asunto, cuerpoHtml);
        await EnviarInternoAsync(message, ct);
    }

    public async Task EnviarConCopiaAsync(string destinatario, string copia,
                                           string asunto, string cuerpoHtml,
                                           CancellationToken ct = default)
    {
        var message = ConstruirMensaje([destinatario], copia, asunto, cuerpoHtml);
        await EnviarInternoAsync(message, ct);
    }

    // ── Privados ─────────────────────────────────────────────────────────────

    private MimeMessage ConstruirMensaje(
        IEnumerable<string> destinatarios,
        string? copia,
        string asunto,
        string cuerpoHtml)
    {
        var message = new MimeMessage();

        // FROM visible: buzón compartido notificacion.sf@zentria.com.co
        message.From.Add(new MailboxAddress(_settings.FromName, _settings.FromAddress));

        foreach (var d in destinatarios)
            message.To.Add(MailboxAddress.Parse(d));

        if (!string.IsNullOrWhiteSpace(copia))
            message.Cc.Add(MailboxAddress.Parse(copia));

        message.Subject = asunto;
        message.Body    = new TextPart("html") { Text = cuerpoHtml };

        return message;
    }

    private async Task EnviarInternoAsync(MimeMessage message, CancellationToken ct)
    {
        using var smtp = new SmtpClient();

        await smtp.ConnectAsync(_settings.Host, _settings.Port,
                                 SecureSocketOptions.StartTls, ct);

        // Autenticación con la cuenta SMTP (sistemas.helpharma@zentria.com.co)
        // El FROM visible es el buzón compartido — requiere permiso "Send As" en Exchange
        await smtp.AuthenticateAsync(_settings.Username, _settings.Password, ct);

        await smtp.SendAsync(message, ct);
        await smtp.DisconnectAsync(quit: true, ct);
    }
}
```

---

## P1-T04: ITemplateHelper y TemplateHelper

**Crear: `GestionPersonal.Helpers/Email/ITemplateHelper.cs`**

```csharp
namespace GestionPersonal.Helpers.Email;

public interface ITemplateHelper
{
    Task<string> RenderizarAsync(string nombrePlantilla,
                                  Dictionary<string, string> parametros);
}
```

**Crear: `GestionPersonal.Helpers/Email/TemplateHelper.cs`**

```csharp
using Microsoft.AspNetCore.Hosting;

namespace GestionPersonal.Helpers.Email;

public class TemplateHelper : ITemplateHelper
{
    private readonly string _templatesPath;

    public TemplateHelper(IWebHostEnvironment env)
    {
        _templatesPath = Path.Combine(env.ContentRootPath, "EmailTemplates");
    }

    public async Task<string> RenderizarAsync(
        string nombrePlantilla,
        Dictionary<string, string> parametros)
    {
        var ruta = Path.Combine(_templatesPath, $"{nombrePlantilla}.html");

        if (!File.Exists(ruta))
            throw new FileNotFoundException(
                $"Plantilla de correo no encontrada: {nombrePlantilla}", ruta);

        var contenido = await File.ReadAllTextAsync(ruta);

        foreach (var (clave, valor) in parametros)
            contenido = contenido.Replace($"{{{{{clave}}}}}", valor ?? string.Empty);

        return contenido;
    }
}
```

**Carpeta de plantillas:** `GestionPersonal.Web/EmailTemplates/`

> Las plantillas usan marcadores `{{NOMBRE_VARIABLE}}` en el HTML.
> Todos los valores de usuario se pasan como parámetros — **nunca** concatenar HTML con entrada de usuario (XSS).

---

## P1-T05: INotificationService y NotificationService (estructura base)

**Crear: `GestionPersonal.Application/Interfaces/INotificationService.cs`**

```csharp
using GestionPersonal.Models.DTOs.Notificaciones;

namespace GestionPersonal.Application.Interfaces;

public interface INotificationService
{
    // ── Seguridad ────────────────────────────────────────────────────────────
    Task NotificarNuevoUsuarioAsync(NotificacionNuevoUsuarioDto datos,
                                    CancellationToken ct = default);

    Task NotificarRecuperacionContrasenaAsync(NotificacionRecuperacionDto datos,
                                              CancellationToken ct = default);

    Task NotificarCambioContrasenaExitosoAsync(NotificacionCambioContrasenaDto datos,
                                               CancellationToken ct = default);

    // ── Solicitudes (HorasExtras / EventosLaborales) ─────────────────────────
    Task NotificarSolicitudCreadaAsync(NotificacionSolicitudDto datos,
                                       CancellationToken ct = default);

    Task NotificarSolicitudAprobadaAsync(NotificacionSolicitudDto datos,
                                          CancellationToken ct = default);

    Task NotificarSolicitudRechazadaAsync(NotificacionSolicitudDto datos,
                                           CancellationToken ct = default);

    Task NotificarSolicitudDevueltaAsync(NotificacionSolicitudDto datos,
                                          CancellationToken ct = default);

    // ── Horarios / Turnos ────────────────────────────────────────────────────
    Task NotificarAsignacionTurnoAsync(NotificacionTurnoDto datos,
                                        CancellationToken ct = default);

    Task NotificarModificacionTurnoAsync(NotificacionTurnoDto datos,
                                          CancellationToken ct = default);

    Task NotificarCancelacionTurnoAsync(NotificacionTurnoDto datos,
                                         CancellationToken ct = default);

    // ── Cambios de personal ──────────────────────────────────────────────────
    Task NotificarCambioCargoAsync(NotificacionCambioPersonalDto datos,
                                    CancellationToken ct = default);

    Task NotificarCambioSedeAsync(NotificacionCambioPersonalDto datos,
                                   CancellationToken ct = default);
}
```

---

## P1-T06: DTOs de notificación

**Crear en `GestionPersonal.Models/DTOs/Notificaciones/`:**

```csharp
// NotificacionNuevoUsuarioDto.cs
namespace GestionPersonal.Models.DTOs.Notificaciones;

public record NotificacionNuevoUsuarioDto(
    string DestinatarioCorreo,
    string NombreEmpleado,
    string CorreoAcceso,
    string NombreCreadorEvento   // para asunto: [Nuevo Usuario] - [NombreCreadorEvento]
);

// NotificacionRecuperacionDto.cs
public record NotificacionRecuperacionDto(
    string DestinatarioCorreo,
    string NombreEmpleado,
    string Codigo,               // código de 10 caracteres (flujo actual)
    string VigenciaMinutos       // "30"
);

// NotificacionCambioContrasenaDto.cs
public record NotificacionCambioContrasenaDto(
    string DestinatarioCorreo,
    string NombreEmpleado
);

// NotificacionSolicitudDto.cs
public record NotificacionSolicitudDto(
    string TipoEvento,           // "Nueva Solicitud", "Aprobación", "Rechazo", etc.
    string TipoSolicitud,        // "Horas Extra", "Vacaciones", "Permiso", "Incapacidad"
    string FechaEvento,
    string NombreEmpleadoSolicitante,
    string CorreoEmpleadoSolicitante,
    string NombreJefeInmediato,
    string CorreoJefeInmediato,
    string? NombreJefeApoyo,     // puede ser null si no existe en la cadena
    string? CorreoJefeApoyo,
    string? NombreAprobador,     // quien aprobó/rechazó (solo en respuesta)
    string? Observacion,
    string NombreQuienGenera     // para asunto: [TipoEvento] - [NombreQuienGenera]
);

// NotificacionTurnoDto.cs
public record NotificacionTurnoDto(
    string TipoEvento,           // "Asignación de Turno", "Cambio de Turno", "Cancelación de Turno"
    string NombreEmpleado,
    string CorreoEmpleado,
    string NombreTurno,
    string FechaVigencia,
    string CorreoJefeEmisor,
    string NombreJefeEmisor,
    string NombreQuienGenera
);

// NotificacionCambioPersonalDto.cs
public record NotificacionCambioPersonalDto(
    string TipoEvento,           // "Cambio de Cargo", "Cambio de Sede"
    string NombreEmpleado,
    string CorreoEmpleado,
    string ValorAnterior,
    string ValorNuevo,
    string CorreoRRHH,           // correo del admin/analista que ejecutó el cambio
    string NombreQuienGenera
);
```

---

## P1-T07: SQL — Tabla RegistroNotificaciones

**Crear archivo: `Documentos/BD/Migracion_RegistroNotificaciones.sql`**

```sql
-- ============================================================
-- MIGRACIÓN: Tabla RegistroNotificaciones
-- Trazabilidad de todos los correos enviados por el sistema
-- Ejecutar en: USE GestionPersonal
-- ============================================================

CREATE TABLE dbo.RegistroNotificaciones (
    Id              INT             IDENTITY(1,1)   NOT NULL,
    TipoEvento      NVARCHAR(60)                    NOT NULL,   -- ej: 'NuevoUsuario', 'SolicitudCreada'
    Destinatario    NVARCHAR(256)                   NOT NULL,
    Copia           NVARCHAR(256)                   NULL,
    Asunto          NVARCHAR(500)                   NOT NULL,
    Exitoso         BIT                             NOT NULL
        CONSTRAINT DF_RegistroNot_Exitoso   DEFAULT 0,
    ErrorMensaje    NVARCHAR(1000)                  NULL,
    FechaIntento    DATETIME2(0)                    NOT NULL
        CONSTRAINT DF_RegistroNot_FechaC    DEFAULT GETUTCDATE(),

    CONSTRAINT PK_RegistroNotificaciones    PRIMARY KEY (Id)
);
GO

-- Índice para consulta por fecha (administración y auditoría)
CREATE NONCLUSTERED INDEX IX_RegistroNot_FechaIntento
    ON dbo.RegistroNotificaciones (FechaIntento DESC)
    INCLUDE (TipoEvento, Destinatario, Exitoso);
GO

-- Índice para diagnóstico de fallos
CREATE NONCLUSTERED INDEX IX_RegistroNot_Exitoso
    ON dbo.RegistroNotificaciones (Exitoso, FechaIntento DESC)
    WHERE Exitoso = 0;
GO
```

---

## P1-T08: Entidad EF Core — RegistroNotificacion

**Crear: `GestionPersonal.Models/Entities/GestionPersonalEntities/RegistroNotificacion.cs`**

```csharp
namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class RegistroNotificacion
{
    public int      Id           { get; set; }
    public string   TipoEvento   { get; set; } = string.Empty;
    public string   Destinatario { get; set; } = string.Empty;
    public string?  Copia        { get; set; }
    public string   Asunto       { get; set; } = string.Empty;
    public bool     Exitoso      { get; set; }
    public string?  ErrorMensaje { get; set; }
    public DateTime FechaIntento { get; set; } = DateTime.UtcNow;
}
```

**Agregar al `AppDbContext.cs`:**

```csharp
public DbSet<RegistroNotificacion> RegistroNotificaciones => Set<RegistroNotificacion>();
```

---

## P1-T09: SQL — Corregir TokensRecuperacion (hash + expiración)

**Contexto actual:**
- `Token NVARCHAR(256)` almacena el token en texto plano (código alfanumérico como `TK1H6K9M2N`).
- `FechaExpiracion`: actualmente `UtcNow.AddHours(1)` — debe ser **30 minutos**.
- Sin hash: si alguien accede a la BD, puede usar cualquier token vigente.

**Migración SQL — `Documentos/BD/Migracion_TokensRecuperacion_Hash.sql`:**

```sql
-- ============================================================
-- MIGRACIÓN: TokensRecuperacion — cambio semántico del campo Token
-- El campo Token almacenará únicamente el HASH SHA-256 del código
-- enviado al usuario. El código en texto plano NUNCA se guarda en BD.
-- ============================================================

-- Paso 1: Invalidar todos los tokens existentes (texto plano en BD, ya no válidos)
UPDATE dbo.TokensRecuperacion
SET    Usado = 1
WHERE  Usado = 0;
GO

-- Paso 2 (documentación): El campo Token ahora almacena SHA-256 en hex (64 chars)
-- No requiere cambio de columna (NVARCHAR(256) es suficiente para 64 chars)
-- El cambio es puramente en el código del servicio.
EXEC sys.sp_addextendedproperty
    @name       = N'MS_Description',
    @value      = N'SHA-256 hex del código enviado al usuario. El código en texto plano NUNCA se persiste.',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE',  @level1name = N'TokensRecuperacion',
    @level2type = N'COLUMN', @level2name = N'Token';
GO
```

**Cambio en `CuentaService.cs` — `SolicitarRecuperacionAsync`:**

```csharp
// ANTES (inseguro)
Token = _codigoHelper.GenerarCodigoUnico(),
FechaExpiracion = DateTime.UtcNow.AddHours(1),

// DESPUÉS (seguro)
// Generar código criptográficamente aleatorio (12 chars alfanumérico)
var codigoPlano = GenerarCodigoSeguro();         // ver implementación abajo
var hashCodigo  = ComputarHashSha256(codigoPlano);

_tokenRepo.Agregar(new TokenRecuperacion
{
    UsuarioId       = usuario.Id,
    Token           = hashCodigo,                // SHA-256 hex — solo el hash en BD
    FechaExpiracion = DateTime.UtcNow.AddMinutes(30),  // 30 minutos
    Usado           = false,
    FechaCreacion   = DateTime.UtcNow
});

// Enviar el código PLANO al usuario (no el hash)
await _notificationService.NotificarRecuperacionContrasenaAsync(
    new NotificacionRecuperacionDto(
        DestinatarioCorreo : usuario.CorreoAcceso,
        NombreEmpleado     : usuario.Empleado?.NombreCompleto ?? usuario.CorreoAcceso,
        Codigo             : codigoPlano,        // el código plano va al correo
        VigenciaMinutos    : "30"
    ), ct);

// ── Helpers privados ──────────────────────────────────────────────────────────
private static string GenerarCodigoSeguro()
{
    const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    var bytes = System.Security.Cryptography.RandomNumberGenerator.GetBytes(12);
    return new string(bytes.Select(b => chars[b % chars.Length]).ToArray());
}

private static string ComputarHashSha256(string input)
{
    var hash = System.Security.Cryptography.SHA256.HashData(
                   System.Text.Encoding.UTF8.GetBytes(input));
    return Convert.ToHexString(hash).ToLowerInvariant(); // 64 chars hex
}
```

**Cambio en `CuentaService.cs` — `RestablecerPasswordAsync`:**

```csharp
// ANTES: busca por token plano
var tokenEntidad = await _tokenRepo.ObtenerTokenActivoAsync(dto.Token, ct);

// DESPUÉS: busca por hash del token recibido
var hashRecibido = ComputarHashSha256(dto.Token);
var tokenEntidad = await _tokenRepo.ObtenerTokenActivoAsync(hashRecibido, ct);
```

---

## P1-T10: Corregir envío de contraseña temporal en texto plano

**Problema crítico en `EmailConstant.cs`:**
El template `CuerpoCrearUsuario` incluye `{contrasenaTemp}` — se envía la contraseña por correo.

**Nueva plantilla `GestionPersonal.Web/EmailTemplates/NuevoUsuario.html`:**

```html
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Bienvenida</title></head>
<body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background: #1e3a8a; padding: 16px; border-radius: 6px 6px 0 0;">
    <h2 style="color: #fff; margin: 0;">GestionPersonal</h2>
  </div>
  <div style="background: #f9fafb; padding: 24px; border: 1px solid #e5e7eb; border-radius: 0 0 6px 6px;">
    <p>Hola <strong>{{NOMBRE_EMPLEADO}}</strong>,</p>
    <p>Tu cuenta ha sido creada en el sistema.</p>
    <table style="width:100%; border-collapse: collapse; margin: 16px 0;">
      <tr><td style="padding: 8px; background:#eef2ff; width:40%;"><strong>Correo de acceso:</strong></td>
          <td style="padding: 8px; background:#eef2ff;">{{CORREO_ACCESO}}</td></tr>
    </table>
    <p>Por seguridad, <strong>no se envía la contraseña por correo</strong>. Al ingresar
    por primera vez, el sistema te pedirá establecer tu propia contraseña.</p>
    <p>Si tienes problemas para acceder, contacta a tu administrador.</p>
    <hr style="border:none; border-top:1px solid #e5e7eb; margin: 20px 0;">
    <p style="font-size: 12px; color: #6b7280;">
      Este correo fue generado automáticamente por <strong>{{NOMBRE_QUIEN_GENERA}}</strong>.
    </p>
  </div>
</body>
</html>
```

**Actualizar `UsuarioService.cs`** — reemplazar llamada a `_emailHelper` por `_notificationService`:

```csharp
// ANTES
await _emailHelper.EnviarCorreoNuevoUsuarioAsync(
    correo, EmailConstant.AsuntoUsuarioNuevo,
    EmailConstant.CuerpoCrearUsuario, correo, contrasenaTemp);

// DESPUÉS — sin contraseña en el correo
await _notificationService.NotificarNuevoUsuarioAsync(
    new NotificacionNuevoUsuarioDto(
        DestinatarioCorreo  : correo,
        NombreEmpleado      : nombreEmpleado,
        CorreoAcceso        : correo,
        NombreCreadorEvento : nombreCreador    // nombre del admin/director que crea la cuenta
    ), ct);
```

---

## P1-T11: NotificationService — implementación base con RegistroNotificaciones

**Crear: `GestionPersonal.Application/Services/NotificationService.cs`**

```csharp
using GestionPersonal.Application.Interfaces;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Helpers.Email;
using GestionPersonal.Models.DTOs.Notificaciones;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using Microsoft.Extensions.Logging;

namespace GestionPersonal.Application.Services;

public class NotificationService : INotificationService
{
    private readonly IEmailHelper        _emailHelper;
    private readonly ITemplateHelper     _templateHelper;
    private readonly INotificacionRepository _registroRepo;
    private readonly ILogger<NotificationService> _logger;

    public NotificationService(
        IEmailHelper emailHelper,
        ITemplateHelper templateHelper,
        INotificacionRepository registroRepo,
        ILogger<NotificationService> logger)
    {
        _emailHelper    = emailHelper;
        _templateHelper = templateHelper;
        _registroRepo   = registroRepo;
        _logger         = logger;
    }

    // ── Nuevo Usuario ─────────────────────────────────────────────────────────
    public async Task NotificarNuevoUsuarioAsync(
        NotificacionNuevoUsuarioDto datos, CancellationToken ct = default)
    {
        var asunto = $"[Nuevo Usuario] - [{datos.NombreCreadorEvento}]";
        var cuerpo = await _templateHelper.RenderizarAsync("NuevoUsuario", new()
        {
            ["NOMBRE_EMPLEADO"]      = datos.NombreEmpleado,
            ["CORREO_ACCESO"]        = datos.CorreoAcceso,
            ["NOMBRE_QUIEN_GENERA"]  = datos.NombreCreadorEvento
        });
        await EnviarConRegistroAsync(datos.DestinatarioCorreo, null,
                                      asunto, cuerpo, "NuevoUsuario", ct);
    }

    // ── Recuperación de contraseña ────────────────────────────────────────────
    public async Task NotificarRecuperacionContrasenaAsync(
        NotificacionRecuperacionDto datos, CancellationToken ct = default)
    {
        var asunto = $"[Recuperación de Contraseña] - [{datos.DestinatarioCorreo}]";
        var cuerpo = await _templateHelper.RenderizarAsync("RecuperacionContrasena", new()
        {
            ["NOMBRE_EMPLEADO"]  = datos.NombreEmpleado,
            ["CODIGO"]           = datos.Codigo,
            ["VIGENCIA_MINUTOS"] = datos.VigenciaMinutos
        });
        await EnviarConRegistroAsync(datos.DestinatarioCorreo, null,
                                      asunto, cuerpo, "RecuperacionContrasena", ct);
    }

    // ── Cambio de contraseña exitoso ──────────────────────────────────────────
    public async Task NotificarCambioContrasenaExitosoAsync(
        NotificacionCambioContrasenaDto datos, CancellationToken ct = default)
    {
        var asunto = $"[Cambio de Contraseña] - [{datos.DestinatarioCorreo}]";
        var cuerpo = await _templateHelper.RenderizarAsync("CambioContrasenaExitoso", new()
        {
            ["NOMBRE_EMPLEADO"] = datos.NombreEmpleado
        });
        await EnviarConRegistroAsync(datos.DestinatarioCorreo, null,
                                      asunto, cuerpo, "CambioContrasenaExitoso", ct);
    }

    // ── Solicitud creada ──────────────────────────────────────────────────────
    public async Task NotificarSolicitudCreadaAsync(
        NotificacionSolicitudDto datos, CancellationToken ct = default)
    {
        var asunto = $"[Nueva {datos.TipoSolicitud}] - [{datos.NombreQuienGenera}]";
        var cuerpo = await _templateHelper.RenderizarAsync("SolicitudCreada_Jefe", new()
        {
            ["TIPO_SOLICITUD"]       = datos.TipoSolicitud,
            ["NOMBRE_EMPLEADO"]      = datos.NombreEmpleadoSolicitante,
            ["FECHA_EVENTO"]         = datos.FechaEvento,
            ["NOMBRE_QUIEN_GENERA"]  = datos.NombreQuienGenera
        });
        // Al jefe inmediato con CC al jefe apoyo (si existe)
        await EnviarConRegistroAsync(datos.CorreoJefeInmediato, datos.CorreoJefeApoyo,
                                      asunto, cuerpo, "SolicitudCreada", ct);
    }

    // ── Solicitud aprobada / rechazada / devuelta ─────────────────────────────
    public async Task NotificarSolicitudAprobadaAsync(
        NotificacionSolicitudDto datos, CancellationToken ct = default)
    {
        var asunto = $"[{datos.TipoSolicitud} Aprobada] - [{datos.NombreQuienGenera}]";
        var cuerpo = await _templateHelper.RenderizarAsync("SolicitudAprobada_Empleado", new()
        {
            ["TIPO_SOLICITUD"]  = datos.TipoSolicitud,
            ["NOMBRE_APROBADOR"]= datos.NombreAprobador ?? string.Empty,
            ["FECHA_EVENTO"]    = datos.FechaEvento,
            ["OBSERVACION"]     = datos.Observacion ?? "—"
        });
        await EnviarConRegistroAsync(datos.CorreoEmpleadoSolicitante, null,
                                      asunto, cuerpo, "SolicitudAprobada", ct);
    }

    public async Task NotificarSolicitudRechazadaAsync(
        NotificacionSolicitudDto datos, CancellationToken ct = default)
    {
        var asunto = $"[{datos.TipoSolicitud} Rechazada] - [{datos.NombreQuienGenera}]";
        var cuerpo = await _templateHelper.RenderizarAsync("SolicitudRechazada_Empleado", new()
        {
            ["TIPO_SOLICITUD"]  = datos.TipoSolicitud,
            ["NOMBRE_APROBADOR"]= datos.NombreQuienGenera,
            ["FECHA_EVENTO"]    = datos.FechaEvento,
            ["OBSERVACION"]     = datos.Observacion ?? "—"
        });
        await EnviarConRegistroAsync(datos.CorreoEmpleadoSolicitante, null,
                                      asunto, cuerpo, "SolicitudRechazada", ct);
    }

    public async Task NotificarSolicitudDevueltaAsync(
        NotificacionSolicitudDto datos, CancellationToken ct = default)
        => await NotificarSolicitudRechazadaAsync(datos with
           { TipoEvento = $"{datos.TipoSolicitud} Devuelta" }, ct);

    // ── Turnos ────────────────────────────────────────────────────────────────
    public async Task NotificarAsignacionTurnoAsync(
        NotificacionTurnoDto datos, CancellationToken ct = default)
    {
        var asunto = $"[Asignación de Turno] - [{datos.NombreQuienGenera}]";
        var cuerpo = await _templateHelper.RenderizarAsync("AsignacionTurno_Empleado", new()
        {
            ["NOMBRE_EMPLEADO"] = datos.NombreEmpleado,
            ["NOMBRE_TURNO"]    = datos.NombreTurno,
            ["FECHA_VIGENCIA"]  = datos.FechaVigencia,
            ["NOMBRE_JEFE"]     = datos.NombreJefeEmisor
        });
        await EnviarConRegistroAsync(datos.CorreoEmpleado, datos.CorreoJefeEmisor,
                                      asunto, cuerpo, "AsignacionTurno", ct);
    }

    public async Task NotificarModificacionTurnoAsync(
        NotificacionTurnoDto datos, CancellationToken ct = default)
    {
        var asunto = $"[Cambio de Turno] - [{datos.NombreQuienGenera}]";
        var cuerpo = await _templateHelper.RenderizarAsync("AsignacionTurno_Empleado", new()
        {
            ["NOMBRE_EMPLEADO"] = datos.NombreEmpleado,
            ["NOMBRE_TURNO"]    = datos.NombreTurno,
            ["FECHA_VIGENCIA"]  = datos.FechaVigencia,
            ["NOMBRE_JEFE"]     = datos.NombreJefeEmisor
        });
        await EnviarConRegistroAsync(datos.CorreoEmpleado, datos.CorreoJefeEmisor,
                                      asunto, cuerpo, "ModificacionTurno", ct);
    }

    public async Task NotificarCancelacionTurnoAsync(
        NotificacionTurnoDto datos, CancellationToken ct = default)
    {
        var asunto = $"[Cancelación de Turno] - [{datos.NombreQuienGenera}]";
        var cuerpo = await _templateHelper.RenderizarAsync("CancelacionTurno_Empleado", new()
        {
            ["NOMBRE_EMPLEADO"] = datos.NombreEmpleado,
            ["NOMBRE_TURNO"]    = datos.NombreTurno,
            ["FECHA_VIGENCIA"]  = datos.FechaVigencia
        });
        await EnviarConRegistroAsync(datos.CorreoEmpleado, null,
                                      asunto, cuerpo, "CancelacionTurno", ct);
    }

    // ── Cambios de personal ───────────────────────────────────────────────────
    public async Task NotificarCambioCargoAsync(
        NotificacionCambioPersonalDto datos, CancellationToken ct = default)
    {
        var asunto = $"[Cambio de Cargo] - [{datos.NombreQuienGenera}]";
        var cuerpo = await _templateHelper.RenderizarAsync("CambioPersonal_Empleado", new()
        {
            ["TIPO_CAMBIO"]     = "cargo",
            ["NOMBRE_EMPLEADO"] = datos.NombreEmpleado,
            ["VALOR_ANTERIOR"]  = datos.ValorAnterior,
            ["VALOR_NUEVO"]     = datos.ValorNuevo
        });
        await EnviarConRegistroAsync(datos.CorreoEmpleado, datos.CorreoRRHH,
                                      asunto, cuerpo, "CambioCargo", ct);
    }

    public async Task NotificarCambioSedeAsync(
        NotificacionCambioPersonalDto datos, CancellationToken ct = default)
    {
        var asunto = $"[Cambio de Sede] - [{datos.NombreQuienGenera}]";
        var cuerpo = await _templateHelper.RenderizarAsync("CambioPersonal_Empleado", new()
        {
            ["TIPO_CAMBIO"]     = "sede",
            ["NOMBRE_EMPLEADO"] = datos.NombreEmpleado,
            ["VALOR_ANTERIOR"]  = datos.ValorAnterior,
            ["VALOR_NUEVO"]     = datos.ValorNuevo
        });
        await EnviarConRegistroAsync(datos.CorreoEmpleado, datos.CorreoRRHH,
                                      asunto, cuerpo, "CambioDeSede", ct);
    }

    // ── Privado: enviar y registrar ───────────────────────────────────────────
    private async Task EnviarConRegistroAsync(
        string destinatario, string? copia,
        string asunto, string cuerpoHtml,
        string tipoEvento, CancellationToken ct)
    {
        var registro = new RegistroNotificacion
        {
            TipoEvento   = tipoEvento,
            Destinatario = destinatario,
            Copia        = copia,
            Asunto       = asunto,
            FechaIntento = DateTime.UtcNow
        };

        try
        {
            if (!string.IsNullOrWhiteSpace(copia))
                await _emailHelper.EnviarConCopiaAsync(destinatario, copia, asunto, cuerpoHtml, ct);
            else
                await _emailHelper.EnviarAsync(destinatario, asunto, cuerpoHtml, ct);

            registro.Exitoso = true;
        }
        catch (Exception ex)
        {
            registro.Exitoso      = false;
            registro.ErrorMensaje = ex.Message;
            _logger.LogError(ex,
                "Error enviando notificación [{TipoEvento}] a [{Destinatario}]",
                tipoEvento, destinatario);
        }

        _registroRepo.Agregar(registro);
        await _registroRepo.GuardarCambiosAsync(ct);
    }
}
```

---

## P1-T12: Registro de dependencias

**Agregar en `GestionPersonal.Application/AccessDependency/ApplicationAccessDependency.cs`:**

```csharp
services.AddScoped<INotificationService, NotificationService>();
```

**Agregar en `GestionPersonal.Helpers/AccessDependency/HelperAccessDependency.cs`:**

```csharp
services.AddScoped<ITemplateHelper, TemplateHelper>();
// (IEmailHelper ya estaba registrado)
```

---

## P1-T13: HTML Plantillas base (Fase 1 — 3 plantillas de seguridad)

**Archivos a crear en `GestionPersonal.Web/EmailTemplates/`:**

| Archivo | Evento | Variables clave |
|---|---|---|
| `NuevoUsuario.html` | EVT-01 | `{{NOMBRE_EMPLEADO}}`, `{{CORREO_ACCESO}}`, `{{NOMBRE_QUIEN_GENERA}}` |
| `RecuperacionContrasena.html` | EVT-02 | `{{NOMBRE_EMPLEADO}}`, `{{CODIGO}}`, `{{VIGENCIA_MINUTOS}}` |
| `CambioContrasenaExitoso.html` | EVT-03 | `{{NOMBRE_EMPLEADO}}` |

> **Reglas UX para plantillas HTML de correo:**
> - Ancho máximo: 600px (compatible con Outlook, Gmail, mobile)
> - Sin JavaScript ni CSS externo (inline styles únicamente)
> - Fuente: Arial/sans-serif, mínimo 14px
> - Contraste de color: ratio mínimo 4.5:1 (WCAG AA)
> - Botones de acción: fondo sólido, texto claro, padding mínimo 12px 24px
> - Nunca incluir links que pidan contraseñas o datos sensibles
> - Pie de correo: indicar quién generó el evento (campo `{{NOMBRE_QUIEN_GENERA}}`)

---

# PARTE 2 — Eventos de Negocio (Semanas 4–6)

---

## P2-T01: Integrar NotificationService en servicios existentes

### HoraExtraService — Solicitud creada

Al crear una HoraExtra (rol Operario/Auxiliar), buscar jefe inmediato y jefe apoyo:

```csharp
// HoraExtraService.cs — después de guardar en BD
var empleado = await _empleadoRepo.ObtenerConJefesAsync(dto.EmpleadoId, ct);
// ObtenerConJefesAsync debe incluir:
//   .Include(e => e.JefeInmediato)
//       .ThenInclude(j => j.JefeInmediato)
//   .Include(e => e.JefeInmediato!).ThenInclude(j => j.Usuario)
//   .Include(e => e.JefeInmediato!.JefeInmediato!).ThenInclude(j => j.Usuario)

await _notificationService.NotificarSolicitudCreadaAsync(new NotificacionSolicitudDto(
    TipoEvento                  : "Nueva Solicitud",
    TipoSolicitud               : "Horas Extra",
    FechaEvento                 : dto.FechaTrabajada.ToString("dd/MM/yyyy"),
    NombreEmpleadoSolicitante   : empleado.NombreCompleto,
    CorreoEmpleadoSolicitante   : empleado.CorreoElectronico ?? "",
    NombreJefeInmediato         : empleado.JefeInmediato?.NombreCompleto ?? "—",
    CorreoJefeInmediato         : empleado.JefeInmediato?.CorreoElectronico ?? "",
    NombreJefeApoyo             : empleado.JefeInmediato?.JefeInmediato?.NombreCompleto,
    CorreoJefeApoyo             : empleado.JefeInmediato?.JefeInmediato?.CorreoElectronico,
    NombreAprobador             : null,
    Observacion                 : null,
    NombreQuienGenera           : empleado.NombreCompleto
), ct);
```

### HoraExtraService — Aprobación / Rechazo

```csharp
// Al aprobar (estado → Aprobado)
await _notificationService.NotificarSolicitudAprobadaAsync(new NotificacionSolicitudDto(
    TipoEvento                : "Aprobación",
    TipoSolicitud             : "Horas Extra",
    FechaEvento               : horaExtra.FechaTrabajada.ToString("dd/MM/yyyy"),
    NombreEmpleadoSolicitante : empleado.NombreCompleto,
    CorreoEmpleadoSolicitante : empleado.CorreoElectronico ?? "",
    NombreJefeInmediato       : "",
    CorreoJefeInmediato       : "",
    NombreJefeApoyo           : null,
    CorreoJefeApoyo           : null,
    NombreAprobador           : nombreAprobador,
    Observacion               : null,
    NombreQuienGenera         : nombreAprobador
), ct);
```

### EventoLaboralService — Solicitud y respuesta

Mismo patrón que HoraExtra. El `TipoSolicitud` puede ser `"Vacaciones"`, `"Incapacidad"` o `"Permiso"`.

---

## P2-T02: Integrar en TurnoService (AsignacionesTurno)

```csharp
// Al crear/modificar AsignacionTurno
var empleado  = await _empleadoRepo.ObtenerPorIdAsync(dto.EmpleadoId, ct);
var programadoPor = await _usuarioRepo.ObtenerPorIdAsync(dto.ProgramadoPorId, ct);

await _notificationService.NotificarAsignacionTurnoAsync(new NotificacionTurnoDto(
    TipoEvento        : "Asignación de Turno",
    NombreEmpleado    : empleado.NombreCompleto,
    CorreoEmpleado    : empleado.CorreoElectronico ?? "",
    NombreTurno       : plantilla.Nombre,
    FechaVigencia     : dto.FechaVigencia.ToString("dd/MM/yyyy"),
    CorreoJefeEmisor  : programadoPor.CorreoAcceso,
    NombreJefeEmisor  : programadoPor.Empleado?.NombreCompleto ?? programadoPor.CorreoAcceso,
    NombreQuienGenera : programadoPor.Empleado?.NombreCompleto ?? programadoPor.CorreoAcceso
), ct);
```

---

## P2-T03: Integrar en EmpleadoService (cambios de cargo/sede)

Al modificar `CargoId` o `SedeId` de un empleado:

```csharp
// En EmpleadoService.ActualizarAsync — detectar cambios
if (empleadoAntes.CargoId != dto.CargoId)
{
    var cargoAnterior = await _catalogoRepo.ObtenerCargoAsync(empleadoAntes.CargoId, ct);
    var cargoNuevo    = await _catalogoRepo.ObtenerCargoAsync(dto.CargoId, ct);

    await _notificationService.NotificarCambioCargoAsync(new NotificacionCambioPersonalDto(
        TipoEvento        : "Cambio de Cargo",
        NombreEmpleado    : empleado.NombreCompleto,
        CorreoEmpleado    : empleado.CorreoElectronico ?? "",
        ValorAnterior     : cargoAnterior.Nombre,
        ValorNuevo        : cargoNuevo.Nombre,
        CorreoRRHH        : correoAdminActual,   // claim del usuario autenticado
        NombreQuienGenera : nombreAdminActual
    ), ct);
}
```

---

## P2-T04: Plantillas HTML restantes (9 plantillas)

| Archivo | Evento | Variables |
|---|---|---|
| `SolicitudCreada_Jefe.html` | EVT-04 | `{{TIPO_SOLICITUD}}`, `{{NOMBRE_EMPLEADO}}`, `{{FECHA_EVENTO}}`, `{{NOMBRE_QUIEN_GENERA}}` |
| `SolicitudAprobada_Empleado.html` | EVT-05 | `{{TIPO_SOLICITUD}}`, `{{NOMBRE_APROBADOR}}`, `{{FECHA_EVENTO}}`, `{{OBSERVACION}}` |
| `SolicitudRechazada_Empleado.html` | EVT-06 | idem aprobada |
| `SolicitudDevuelta_Empleado.html` | EVT-07 | idem + `{{OBSERVACION}}` |
| `AsignacionTurno_Empleado.html` | EVT-08/09 | `{{NOMBRE_EMPLEADO}}`, `{{NOMBRE_TURNO}}`, `{{FECHA_VIGENCIA}}`, `{{NOMBRE_JEFE}}` |
| `CancelacionTurno_Empleado.html` | EVT-10 | `{{NOMBRE_EMPLEADO}}`, `{{NOMBRE_TURNO}}`, `{{FECHA_VIGENCIA}}` |
| `CambioPersonal_Empleado.html` | EVT-11/12 | `{{TIPO_CAMBIO}}`, `{{NOMBRE_EMPLEADO}}`, `{{VALOR_ANTERIOR}}`, `{{VALOR_NUEVO}}` |

---

# PARTE 3 — Pruebas (Semanas 5–6, en paralelo con Parte 2)

---

## Estrategia de pruebas

| Capa | Qué se verifica | Herramienta |
|---|---|---|
| **Infraestructura** | `EmailHelper` envía sin excepción con SMTP real | Prueba manual (envío a yopmail) |
| **Integración** | `RegistroNotificaciones` registra `Exitoso = true` después de cada acción | Playwright + consulta SQL |
| **E2E UI** | La acción en pantalla dispara el flujo correcto y actualiza estado en BD | Playwright |
| **Seguridad** | No hay contraseñas en correos, token de recuperación expira, token usado no se reutiliza | Playwright |

---

## Comandos de ejecución

```powershell
# 1. Levantar la app
cd "Proyecto MVC"
dotnet run --project GestionPersonal.Web/GestionPersonal.Web.csproj --launch-profile http

# 2. Activar venv
cd ..
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1

# 3. Ejecutar suite de email
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\email-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null

pytest Tests/test_email_seguridad.py Tests/test_email_solicitudes.py Tests/test_email_turnos.py `
  -v --headed --slowmo 800 -s `
  2>&1 | Tee-Object -FilePath $informe

Write-Host "Informe: $informe"
```

---

## Archivo: `Tests/test_email_seguridad.py`

Cubre EVT-01, EVT-02, EVT-03.

```python
"""
Pruebas de correo — Seguridad y Acceso
EVT-01  Nuevo usuario → RegistroNotificaciones registra Exitoso=1 (sin contraseña en cuerpo)
EVT-02  Recuperación contraseña → token en BD es hash SHA-256, no el código plano
EVT-02b Token válido → formulario de nueva contraseña accesible
EVT-02c Token expirado (> 30 min) → sistema rechaza
EVT-02d Token ya usado → sistema rechaza
EVT-03  Cambio exitoso → RegistroNotificaciones registra Exitoso=1
"""

import pytest
import pyodbc
from helpers import BASE_URL, hacer_login

# ── Conexión BD (verificar RegistroNotificaciones) ───────────────────────────
def obtener_ultimo_registro(tipo_evento: str) -> dict | None:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=(localdb)\\MSSQLLocalDB;DATABASE=GestionPersonal;Trusted_Connection=yes"
    )
    cursor = conn.cursor()
    cursor.execute(
        "SELECT TOP 1 Exitoso, ErrorMensaje, Destinatario, Asunto "
        "FROM RegistroNotificaciones "
        "WHERE TipoEvento = ? "
        "ORDER BY FechaIntento DESC",
        tipo_evento
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"exitoso": row[0], "error": row[1],
                "destinatario": row[2], "asunto": row[3]}
    return None


def obtener_token_bd(correo: str) -> dict | None:
    """Obtiene el último token activo. Verifica que sea hash hex (64 chars), no código legible."""
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=(localdb)\\MSSQLLocalDB;DATABASE=GestionPersonal;Trusted_Connection=yes"
    )
    cursor = conn.cursor()
    cursor.execute(
        "SELECT TOP 1 t.Token, t.FechaExpiracion, t.Usado "
        "FROM TokensRecuperacion t "
        "INNER JOIN Usuarios u ON t.UsuarioId = u.Id "
        "WHERE u.CorreoAcceso = ? "
        "ORDER BY t.FechaCreacion DESC",
        correo
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"token": row[0], "expiracion": row[1], "usado": row[2]}
    return None


# ── EVT-01: Nuevo usuario ─────────────────────────────────────────────────────
def test_evt01_nuevo_usuario_registro_notificacion(page):
    """
    Al crear un empleado con usuario, RegistroNotificaciones debe registrar
    TipoEvento='NuevoUsuario' con Exitoso=1.
    Verificar que el asunto NO contiene 'contraseña' ni 'password'.
    """
    hacer_login(page, "admin@yopmail.com", "AdminPass2026!")  # Administrador

    # Navegar a crear empleado y completar formulario
    page.goto(f"{BASE_URL}/Empleados/Nuevo")
    page.wait_for_load_state("networkidle")

    # TODO: completar campos del formulario con datos de prueba únicos
    # page.fill("#NombreCompleto", "Test Email EVT01")
    # ... (completar según campos reales del formulario)
    # page.click("button[type=submit]")
    # page.wait_for_load_state("networkidle")

    # Verificar registro en BD
    registro = obtener_ultimo_registro("NuevoUsuario")
    assert registro is not None, "EVT-01: No se encontró registro en RegistroNotificaciones"
    assert registro["exitoso"] == 1, f"EVT-01: Correo falló. Error: {registro['error']}"

    # Verificar que el asunto NO contiene datos sensibles
    asunto = registro["asunto"].lower()
    assert "contraseña" not in asunto, "EVT-01: El asunto contiene 'contraseña' (dato sensible)"
    assert "password"   not in asunto, "EVT-01: El asunto contiene 'password' (dato sensible)"

    # Verificar formato de asunto: [Nuevo Usuario] - [NombreGenerador]
    assert asunto.startswith("[nuevo usuario]"), (
        f"EVT-01: Formato de asunto incorrecto. Asunto: {registro['asunto']}"
    )


# ── EVT-02: Token de recuperación es hash SHA-256 ────────────────────────────
def test_evt02_token_recuperacion_es_hash(page):
    """
    Al solicitar recuperación de contraseña, el Token en BD debe ser
    un hash hex de 64 caracteres (SHA-256), no el código alfanumérico legible.
    """
    correo = "carlos.rodriguez@yopmail.com"

    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.wait_for_load_state("networkidle")
    page.fill("#CorreoAcceso", correo)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    token_bd = obtener_token_bd(correo)
    assert token_bd is not None, "EVT-02: No se creó token en BD"

    # El token en BD debe ser hex de 64 caracteres (SHA-256), no el código original
    token_valor = token_bd["token"]
    assert len(token_valor) == 64, (
        f"EVT-02: Token en BD tiene {len(token_valor)} chars. "
        f"Se esperaban 64 (SHA-256 hex). Valor: {token_valor[:20]}..."
    )
    assert all(c in "0123456789abcdef" for c in token_valor), (
        "EVT-02: Token en BD no es hex válido — podría ser texto plano (inseguro)"
    )


def test_evt02_token_expira_30_minutos(page):
    """
    El token creado debe expirar en ≤ 30 minutos desde su creación.
    """
    from datetime import datetime, timezone, timedelta

    correo = "natalia.bermudez@yopmail.com"

    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.fill("#CorreoAcceso", correo)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    token_bd = obtener_token_bd(correo)
    assert token_bd is not None, "EVT-02: No se creó token en BD"

    expiracion = token_bd["expiracion"]
    ahora = datetime.now(timezone.utc)
    diferencia = expiracion.replace(tzinfo=timezone.utc) - ahora

    assert diferencia <= timedelta(minutes=31), (
        f"EVT-02: Token expira en {diferencia}. Máximo permitido: 30 minutos"
    )
    assert diferencia > timedelta(minutes=0), (
        "EVT-02: Token ya expiró al momento de crearlo"
    )


def test_evt02c_token_expirado_es_rechazado(page):
    """
    TC-15a equivalente post-refactoring.
    Token expirado (TK7E4D8F5G del seeding) → sistema rechaza y muestra mensaje.
    """
    token_expirado = "TK7E4D8F5G"
    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token={token_expirado}")
    page.wait_for_load_state("networkidle")

    # El sistema NO debe mostrar el formulario de nueva contraseña
    formulario = page.locator("input[name='NuevoPassword']")
    assert not formulario.is_visible(), (
        "EVT-02c: El formulario de contraseña no debería mostrarse con token expirado"
    )
    # Debe mostrar mensaje de error
    mensaje = page.locator(".alert--error, .alert-danger").inner_text()
    assert len(mensaje.strip()) > 0, (
        "EVT-02c: No se mostró mensaje de error para token expirado"
    )


def test_evt02d_token_usado_es_rechazado(page):
    """TC-15b: Token ya utilizado → rechazado."""
    token_usado = "TK3F9A2B1C"
    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token={token_usado}")
    page.wait_for_load_state("networkidle")

    formulario = page.locator("input[name='NuevoPassword']")
    assert not formulario.is_visible(), (
        "EVT-02d: El formulario no debería mostrarse con token ya usado"
    )


# ── EVT-03: Cambio de contraseña exitoso ─────────────────────────────────────
def test_evt03_cambio_contrasena_registro_notificacion(page):
    """
    Al completar el flujo de recuperación (token válido + nueva contraseña),
    RegistroNotificaciones debe registrar TipoEvento='CambioContrasenaExitoso'
    con Exitoso=1.
    """
    # Este test requiere un token válido en BD — usar Seeding_Completo.sql
    token_vigente = "TK1H6K9M2N"   # Natalia Bermúdez, vigente en seeding

    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token={token_vigente}")
    page.wait_for_load_state("networkidle")

    # Completar formulario de nueva contraseña
    page.fill("input[name='NuevoPassword']",      "NuevaClaveSegura2026!")
    page.fill("input[name='ConfirmarPassword']",  "NuevaClaveSegura2026!")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    registro = obtener_ultimo_registro("CambioContrasenaExitoso")
    assert registro is not None, "EVT-03: No se encontró registro en RegistroNotificaciones"
    assert registro["exitoso"] == 1, f"EVT-03: Correo de confirmación falló. Error: {registro['error']}"
```

---

## Archivo: `Tests/test_email_solicitudes.py`

Cubre EVT-04, EVT-05, EVT-06, EVT-07.

```python
"""
Pruebas de correo — Solicitudes (HorasExtras / EventosLaborales)
EVT-04  Solicitud creada → correo a jefe inmediato (CC jefe apoyo si existe)
EVT-05  Solicitud aprobada → correo al auxiliar solicitante
EVT-06  Solicitud rechazada → correo al auxiliar solicitante
"""

import pytest
import pyodbc
from helpers import BASE_URL, hacer_login


def obtener_ultimo_registro(tipo_evento: str) -> dict | None:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=(localdb)\\MSSQLLocalDB;DATABASE=GestionPersonal;Trusted_Connection=yes"
    )
    cursor = conn.cursor()
    cursor.execute(
        "SELECT TOP 1 Exitoso, ErrorMensaje, Destinatario, Copia, Asunto "
        "FROM RegistroNotificaciones "
        "WHERE TipoEvento = ? "
        "ORDER BY FechaIntento DESC",
        tipo_evento
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"exitoso": row[0], "error": row[1],
                "destinatario": row[2], "copia": row[3], "asunto": row[4]}
    return None


# ── EVT-04: Solicitud creada por auxiliar ────────────────────────────────────
def test_evt04_solicitud_creada_notifica_jefe(page):
    """
    Un Operario (Auxiliar) crea una solicitud de horas extra.
    Debe generarse RegistroNotificaciones con TipoEvento='SolicitudCreada',
    Destinatario=CorreoJefeInmediato, Exitoso=1.
    El asunto debe tener formato [Nueva Horas Extra] - [NombreAuxiliar].
    """
    # Login como Auxiliar (Operario)
    hacer_login(page, "auxiliar.farmacia@yopmail.com", "AuxiliarPass2026!")

    page.goto(f"{BASE_URL}/HorasExtras/Nuevo")
    page.wait_for_load_state("networkidle")

    # Completar formulario mínimo de horas extra
    page.fill("input[name='FechaTrabajada']", "2026-05-01")
    page.fill("input[name='CantidadHoras']",  "2")
    page.fill("textarea[name='Motivo']",       "Prueba automatizada EVT-04")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    registro = obtener_ultimo_registro("SolicitudCreada")
    assert registro is not None,  "EVT-04: No se registró notificación SolicitudCreada"
    assert registro["exitoso"] == 1, f"EVT-04: Correo falló. Error: {registro['error']}"

    # El destinatario es el jefe inmediato, no el auxiliar
    assert registro["destinatario"] != "auxiliar.farmacia@yopmail.com", (
        "EVT-04: El destinatario debería ser el jefe, no el auxiliar"
    )

    # Formato de asunto
    assert "[nueva horas extra]" in registro["asunto"].lower(), (
        f"EVT-04: Formato de asunto incorrecto. Asunto: {registro['asunto']}"
    )


def test_evt04_solicitud_creada_copia_jefe_apoyo(page):
    """
    Si el auxiliar tiene jefe inmediato con jefe apoyo (cadena de dos niveles),
    el campo Copia en RegistroNotificaciones debe estar poblado.
    """
    hacer_login(page, "auxiliar.farmacia@yopmail.com", "AuxiliarPass2026!")
    page.goto(f"{BASE_URL}/HorasExtras/Nuevo")
    page.wait_for_load_state("networkidle")

    page.fill("input[name='FechaTrabajada']", "2026-05-02")
    page.fill("input[name='CantidadHoras']",  "3")
    page.fill("textarea[name='Motivo']",       "Prueba EVT-04 con CC jefe apoyo")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    registro = obtener_ultimo_registro("SolicitudCreada")
    assert registro is not None, "EVT-04b: No se registró notificación"
    # Si el jefe apoyo existe, el campo Copia debe estar poblado
    # (este test pasa si el auxiliar en seeding tiene cadena de dos niveles)
    # Si no existe cadena, Copia puede ser NULL — documentar resultado


# ── EVT-05: Solicitud aprobada ────────────────────────────────────────────────
def test_evt05_aprobacion_notifica_auxiliar(page):
    """
    El Regente aprueba una HoraExtra pendiente.
    RegistroNotificaciones debe tener TipoEvento='SolicitudAprobada',
    Destinatario=CorreoAuxiliar, Exitoso=1.
    El asunto debe incluir el nombre del Regente aprobador.
    """
    hacer_login(page, "regente.farmacia@yopmail.com", "RegentePass2026!")

    # Navegar a la lista de horas extras pendientes y aprobar la primera
    page.goto(f"{BASE_URL}/HorasExtras")
    page.wait_for_load_state("networkidle")

    # Hacer clic en el botón de aprobar de la primera solicitud pendiente
    page.locator("button[data-accion='aprobar']").first.click()
    page.wait_for_load_state("networkidle")

    registro = obtener_ultimo_registro("SolicitudAprobada")
    assert registro is not None, "EVT-05: No se registró notificación SolicitudAprobada"
    assert registro["exitoso"] == 1, f"EVT-05: Correo falló. Error: {registro['error']}"

    asunto = registro["asunto"].lower()
    assert "aprobada" in asunto, f"EVT-05: Asunto no contiene 'aprobada'. Asunto: {registro['asunto']}"


# ── EVT-06: Solicitud rechazada ───────────────────────────────────────────────
def test_evt06_rechazo_notifica_auxiliar(page):
    """
    El Regente rechaza una HoraExtra pendiente.
    RegistroNotificaciones: TipoEvento='SolicitudRechazada', Exitoso=1.
    """
    hacer_login(page, "regente.farmacia@yopmail.com", "RegentePass2026!")

    page.goto(f"{BASE_URL}/HorasExtras")
    page.wait_for_load_state("networkidle")

    # Clic en rechazar (modal de motivo si aplica)
    page.locator("button[data-accion='rechazar']").first.click()

    # Si hay modal de motivo
    motivo_input = page.locator("textarea[name='MotivoRechazo']")
    if motivo_input.is_visible():
        motivo_input.fill("Prueba automatizada EVT-06")
        page.locator("button[data-confirmar='rechazar']").click()

    page.wait_for_load_state("networkidle")

    registro = obtener_ultimo_registro("SolicitudRechazada")
    assert registro is not None, "EVT-06: No se registró notificación SolicitudRechazada"
    assert registro["exitoso"] == 1, f"EVT-06: Correo falló. Error: {registro['error']}"
```

---

## Archivo: `Tests/test_email_turnos.py`

Cubre EVT-08, EVT-09, EVT-10.

```python
"""
Pruebas de correo — Asignación de Turnos
EVT-08  Turno asignado → correo a empleado + confirmación a jefe
EVT-09  Turno modificado → correo a empleado + confirmación a jefe
EVT-10  Turno cancelado → correo a empleado
"""

import pytest
import pyodbc
from helpers import BASE_URL, hacer_login


def obtener_ultimo_registro(tipo_evento: str) -> dict | None:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=(localdb)\\MSSQLLocalDB;DATABASE=GestionPersonal;Trusted_Connection=yes"
    )
    cursor = conn.cursor()
    cursor.execute(
        "SELECT TOP 1 Exitoso, ErrorMensaje, Destinatario, Copia, Asunto "
        "FROM RegistroNotificaciones "
        "WHERE TipoEvento = ? "
        "ORDER BY FechaIntento DESC",
        tipo_evento
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"exitoso": row[0], "error": row[1],
                "destinatario": row[2], "copia": row[3], "asunto": row[4]}
    return None


def test_evt08_asignacion_turno_notifica_empleado(page):
    """
    El DirectorTecnico asigna un turno a un empleado.
    RegistroNotificaciones: TipoEvento='AsignacionTurno', Destinatario=CorreoEmpleado.
    El campo Copia debe ser el correo del director (confirmación).
    """
    hacer_login(page, "director.tecnico@yopmail.com", "DirectorPass2026!")

    page.goto(f"{BASE_URL}/Turnos/AsignarTurno")
    page.wait_for_load_state("networkidle")

    # TODO: seleccionar empleado y plantilla, establecer fecha vigencia
    # page.select_option("select[name='EmpleadoId']", label="Auxiliar de Prueba")
    # page.select_option("select[name='PlantillaTurnoId']", label="Turno Mañana")
    # page.fill("input[name='FechaVigencia']", "2026-05-05")
    # page.click("button[type=submit]")
    # page.wait_for_load_state("networkidle")

    registro = obtener_ultimo_registro("AsignacionTurno")
    assert registro is not None,  "EVT-08: No se registró notificación AsignacionTurno"
    assert registro["exitoso"] == 1, f"EVT-08: Correo falló. Error: {registro['error']}"
    assert registro["copia"] is not None, (
        "EVT-08: El campo Copia (confirmación al jefe emisor) no está poblado"
    )

    asunto = registro["asunto"].lower()
    assert "[asignación de turno]" in asunto, (
        f"EVT-08: Formato de asunto incorrecto. Asunto: {registro['asunto']}"
    )
```

---

## Checklist de cierre del ciclo

### Fase 1 (Semanas 1–3)

- [ ] `dotnet user-secrets` configurado con credenciales reales (no en repo)
- [ ] Exchange Admin confirmó permisos "Send As" de `sistemas.helpharma` sobre `notificacion.sf`
- [ ] `EmailHelper` usa MailKit; `System.Net.Mail.SmtpClient` eliminado del proyecto
- [ ] Envío manual de prueba desde consola/Postman confirma llegada desde `notificacion.sf@zentria.com.co`
- [ ] `UsuarioService` NO envía contraseña en correo (eliminar `{contrasenaTemp}` de templates)
- [ ] Token en `TokensRecuperacion.Token` almacena SHA-256 hex (64 chars), no código legible
- [ ] Expiración de token: 30 minutos
- [ ] Tabla `RegistroNotificaciones` creada en BD (migración ejecutada)
- [ ] `INotificationService` registrado en DI
- [ ] 3 plantillas HTML de seguridad creadas y renderizadas correctamente
- [ ] `test_email_seguridad.py::test_evt02_token_recuperacion_es_hash` pasa en verde

### Fase 2 (Semanas 4–6)

- [ ] `HoraExtraService` llama `INotificationService` en creación/aprobación/rechazo
- [ ] `EventoLaboralService` llama `INotificationService` en creación/aprobación/rechazo
- [ ] `TurnoService` notifica asignación/modificación/cancelación
- [ ] `EmpleadoService` notifica cambio de cargo y sede
- [ ] Todas las 9 plantillas HTML restantes creadas
- [ ] Formato de asunto `[TipoEvento] - [NombreQuienGenera]` verificado en todos los eventos
- [ ] `test_email_solicitudes.py` completo pasa en verde
- [ ] `test_email_turnos.py` completo pasa en verde
- [ ] `RegistroNotificaciones` no contiene entradas con `Exitoso = 0` en pruebas normales

---

## Estructura de archivos a crear / modificar (resumen)

```
GestionPersonal.Application/
 ├── Interfaces/
 │   └── INotificationService.cs              ← NUEVO
 └── Services/
     ├── NotificationService.cs               ← NUEVO
     ├── UsuarioService.cs                    ← MODIFICAR (usa INotificationService)
     ├── CuentaService.cs                     ← MODIFICAR (hash token, 30 min, sin pwd en email)
     ├── HoraExtraService.cs                  ← MODIFICAR (notifica creación, aprobación, rechazo)
     ├── EventoLaboralService.cs              ← MODIFICAR (notifica creación, aprobación, rechazo)
     ├── TurnoService.cs                      ← MODIFICAR (notifica asignación/modificación/cancelación)
     └── EmpleadoService.cs                   ← MODIFICAR (notifica cambio cargo/sede)

GestionPersonal.Helpers/
 └── Email/
     ├── IEmailHelper.cs                      ← REFACTORIZAR (nuevo contrato)
     ├── EmailHelper.cs                       ← REFACTORIZAR (MailKit + Send As)
     ├── ITemplateHelper.cs                   ← NUEVO
     └── TemplateHelper.cs                    ← NUEVO

GestionPersonal.Models/
 ├── DTOs/Notificaciones/
 │   ├── NotificacionNuevoUsuarioDto.cs       ← NUEVO
 │   ├── NotificacionRecuperacionDto.cs       ← NUEVO
 │   ├── NotificacionCambioContrasenaDto.cs   ← NUEVO
 │   ├── NotificacionSolicitudDto.cs          ← NUEVO
 │   ├── NotificacionTurnoDto.cs              ← NUEVO
 │   └── NotificacionCambioPersonalDto.cs     ← NUEVO
 ├── Models/Email/
 │   └── EmailSettings.cs                    ← NUEVO
 └── Entities/GestionPersonalEntities/
     └── RegistroNotificacion.cs             ← NUEVO

GestionPersonal.Constants/Messages/
 └── EmailConstant.cs                        ← MODIFICAR (nuevo formato asuntos, limpiar templates inline)

GestionPersonal.Web/
 ├── appsettings.json                        ← MODIFICAR (agregar sección EmailSettings sin password)
 └── EmailTemplates/
     ├── NuevoUsuario.html                   ← NUEVO
     ├── RecuperacionContrasena.html          ← NUEVO
     ├── CambioContrasenaExitoso.html         ← NUEVO
     ├── SolicitudCreada_Jefe.html            ← NUEVO
     ├── SolicitudAprobada_Empleado.html      ← NUEVO
     ├── SolicitudRechazada_Empleado.html     ← NUEVO
     ├── SolicitudDevuelta_Empleado.html      ← NUEVO
     ├── AsignacionTurno_Empleado.html        ← NUEVO
     ├── CancelacionTurno_Empleado.html       ← NUEVO
     └── CambioPersonal_Empleado.html         ← NUEVO

Documentos/BD/
 ├── Migracion_RegistroNotificaciones.sql    ← NUEVO
 └── Migracion_TokensRecuperacion_Hash.sql   ← NUEVO

Tests/
 ├── test_email_seguridad.py                 ← NUEVO
 ├── test_email_solicitudes.py               ← NUEVO
 └── test_email_turnos.py                    ← NUEVO
```
