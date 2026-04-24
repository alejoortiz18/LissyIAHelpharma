---
name: email-dotnet-aspnetcore
description: Implementa envío de correos en ASP.NET Core MVC con C#. Cubre SMTP via MailKit/MimeKit y Microsoft 365 via Microsoft Graph API. Úsalo cuando necesites enviar correos de recuperación de contraseña, notificaciones, confirmaciones, o cualquier funcionalidad de email en el proyecto.
metadata:
  author: custom
  version: "1.0.0"
---

# Envío de Correos — ASP.NET Core MVC (.NET 10)

Guía de implementación para envío de correos electrónicos con dos estrategias:
- **SMTP clásico** (Office 365, Gmail, cualquier servidor SMTP) mediante **MailKit**
- **Microsoft 365 / Graph API** (recomendado para tenants M365 con autenticación OAuth2)

> `System.Net.Mail.SmtpClient` está **obsoleto** desde .NET 5. Usar siempre MailKit.

---

## 1. Cuándo Usar Cada Estrategia

| Escenario | Estrategia recomendada |
|-----------|----------------------|
| SMTP con usuario/contraseña (Office 365, Gmail) | MailKit + SMTP |
| Microsoft 365 con OAuth2 / App Registration | Microsoft Graph API |
| Servidor SMTP propio (on-premise) | MailKit + SMTP |
| Sin acceso a Exchange / solo Graph API | Microsoft Graph API |
| Correos simples de notificación sin tenant M365 | MailKit + SMTP |

---

## 2. SMTP via MailKit

### 2.1 Instalación del paquete

```xml
<!-- GestionPersonal.Helpers/GestionPersonal.Helpers.csproj -->
<PackageReference Include="MailKit" Version="4.*" />
<PackageReference Include="MimeKit" Version="4.*" />
```

### 2.2 Configuración (`appsettings.json`)

```json
{
  "EmailSettings": {
    "Provider": "Smtp",
    "Smtp": {
      "Host": "smtp.office365.com",
      "Port": 587,
      "UseSsl": false,
      "UseStartTls": true,
      "Username": "no-reply@tuempresa.com",
      "Password": "tu_password_aqui",
      "FromName": "GestionPersonal",
      "FromAddress": "no-reply@tuempresa.com"
    }
  }
}
```

> **Seguridad:** Nunca hardcodear credenciales. En desarrollo usar `dotnet user-secrets`, en producción usar variables de entorno o Azure Key Vault.

```powershell
# Registrar secretos en desarrollo
dotnet user-secrets set "EmailSettings:Smtp:Password" "tu_password_real"
```

### 2.3 Modelo de configuración

```csharp
// GestionPersonal.Models/Models/Email/EmailSettings.cs
namespace GestionPersonal.Models.Models.Email;

public class EmailSettings
{
    public const string SectionName = "EmailSettings";

    public string Provider { get; set; } = "Smtp"; // "Smtp" | "Graph"

    public SmtpSettings Smtp { get; set; } = new();
    public GraphSettings Graph { get; set; } = new();
}

public class SmtpSettings
{
    public string Host        { get; set; } = string.Empty;
    public int    Port        { get; set; } = 587;
    public bool   UseSsl      { get; set; } = false;
    public bool   UseStartTls { get; set; } = true;
    public string Username    { get; set; } = string.Empty;
    public string Password    { get; set; } = string.Empty;
    public string FromName    { get; set; } = string.Empty;
    public string FromAddress { get; set; } = string.Empty;
}

public class GraphSettings
{
    public string TenantId     { get; set; } = string.Empty;
    public string ClientId     { get; set; } = string.Empty;
    public string ClientSecret { get; set; } = string.Empty;
    public string FromAddress  { get; set; } = string.Empty;
    public string FromName     { get; set; } = string.Empty;
}
```

### 2.4 Interfaz del servicio de correo

```csharp
// GestionPersonal.Domain/Interfaces/IEmailService.cs
namespace GestionPersonal.Domain.Interfaces;

public interface IEmailService
{
    Task EnviarAsync(string destinatario, string asunto, string cuerpoHtml,
                     CancellationToken cancellationToken = default);

    Task EnviarAsync(IEnumerable<string> destinatarios, string asunto, string cuerpoHtml,
                     CancellationToken cancellationToken = default);
}
```

### 2.5 Helper SMTP con MailKit

```csharp
// GestionPersonal.Helpers/Email/SmtpEmailHelper.cs
using MailKit.Net.Smtp;
using MailKit.Security;
using Microsoft.Extensions.Options;
using MimeKit;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Models.Email;

namespace GestionPersonal.Helpers.Email;

public class SmtpEmailHelper : IEmailService
{
    private readonly SmtpSettings _settings;

    public SmtpEmailHelper(IOptions<EmailSettings> options)
    {
        _settings = options.Value.Smtp;
    }

    public Task EnviarAsync(string destinatario, string asunto, string cuerpoHtml,
                            CancellationToken cancellationToken = default)
        => EnviarAsync(new[] { destinatario }, asunto, cuerpoHtml, cancellationToken);

    public async Task EnviarAsync(IEnumerable<string> destinatarios, string asunto, string cuerpoHtml,
                                  CancellationToken cancellationToken = default)
    {
        var mensaje = new MimeMessage();
        mensaje.From.Add(new MailboxAddress(_settings.FromName, _settings.FromAddress));

        foreach (var dest in destinatarios)
            mensaje.To.Add(MailboxAddress.Parse(dest));

        mensaje.Subject = asunto;
        mensaje.Body = new TextPart("html") { Text = cuerpoHtml };

        using var client = new SmtpClient();

        var secureOption = _settings.UseStartTls
            ? SecureSocketOptions.StartTls
            : (_settings.UseSsl ? SecureSocketOptions.SslOnConnect : SecureSocketOptions.None);

        await client.ConnectAsync(_settings.Host, _settings.Port, secureOption, cancellationToken);
        await client.AuthenticateAsync(_settings.Username, _settings.Password, cancellationToken);
        await client.SendAsync(mensaje, cancellationToken);
        await client.DisconnectAsync(quit: true, cancellationToken);
    }
}
```

---

## 3. Microsoft 365 via Microsoft Graph API

### 3.1 Instalación del paquete

```xml
<!-- GestionPersonal.Helpers/GestionPersonal.Helpers.csproj -->
<PackageReference Include="Microsoft.Graph" Version="5.*" />
<PackageReference Include="Azure.Identity" Version="1.*" />
```

### 3.2 Configuración (`appsettings.json`)

```json
{
  "EmailSettings": {
    "Provider": "Graph",
    "Graph": {
      "TenantId":     "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "ClientId":     "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "ClientSecret": "tu_client_secret",
      "FromAddress":  "no-reply@tuempresa.onmicrosoft.com",
      "FromName":     "GestionPersonal"
    }
  }
}
```

### 3.3 Registrar App Registration en Azure AD

En el portal de Azure (portal.azure.com):
1. **Azure Active Directory → App registrations → New registration**
2. Nombre: `GestionPersonal-Email`
3. En **API permissions** agregar: `Mail.Send` (Application permission, no delegada)
4. Crear un **Client secret** en *Certificates & secrets*
5. Copiar **Tenant ID**, **Client ID** y el secret al `appsettings.json`
6. El admin del tenant debe dar **Grant admin consent**

### 3.4 Helper Microsoft Graph

```csharp
// GestionPersonal.Helpers/Email/GraphEmailHelper.cs
using Azure.Identity;
using Microsoft.Extensions.Options;
using Microsoft.Graph;
using Microsoft.Graph.Models;
using Microsoft.Graph.Users.Item.SendMail;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Models.Email;

namespace GestionPersonal.Helpers.Email;

public class GraphEmailHelper : IEmailService
{
    private readonly GraphSettings _settings;
    private readonly GraphServiceClient _graphClient;

    public GraphEmailHelper(IOptions<EmailSettings> options)
    {
        _settings = options.Value.Graph;

        var credential = new ClientSecretCredential(
            _settings.TenantId,
            _settings.ClientId,
            _settings.ClientSecret);

        _graphClient = new GraphServiceClient(credential,
            new[] { "https://graph.microsoft.com/.default" });
    }

    public Task EnviarAsync(string destinatario, string asunto, string cuerpoHtml,
                            CancellationToken cancellationToken = default)
        => EnviarAsync(new[] { destinatario }, asunto, cuerpoHtml, cancellationToken);

    public async Task EnviarAsync(IEnumerable<string> destinatarios, string asunto, string cuerpoHtml,
                                  CancellationToken cancellationToken = default)
    {
        var mensaje = new Message
        {
            Subject = asunto,
            Body = new ItemBody { ContentType = BodyType.Html, Content = cuerpoHtml },
            From = new Recipient
            {
                EmailAddress = new EmailAddress
                {
                    Address = _settings.FromAddress,
                    Name    = _settings.FromName
                }
            },
            ToRecipients = destinatarios.Select(d => new Recipient
            {
                EmailAddress = new EmailAddress { Address = d }
            }).ToList()
        };

        var body = new SendMailPostRequestBody { Message = mensaje, SaveToSentItems = false };

        // Usar el userId del remitente (email address o GUID de objeto)
        await _graphClient.Users[_settings.FromAddress]
            .SendMail
            .PostAsync(body, cancellationToken: cancellationToken);
    }
}
```

---

## 4. Registro de Dependencias

```csharp
// GestionPersonal.Helpers/AccessDependency/HelpersAccessDependency.cs
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Helpers.Email;
using GestionPersonal.Models.Models.Email;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace GestionPersonal.Helpers.AccessDependency;

public static class HelpersAccessDependency
{
    public static IServiceCollection AddHelpers(this IServiceCollection services,
                                                IConfiguration configuration)
    {
        // Vincular configuración de correo
        services.Configure<EmailSettings>(
            configuration.GetSection(EmailSettings.SectionName));

        // Registrar el proveedor correcto según configuración
        var provider = configuration
            .GetSection(EmailSettings.SectionName)
            .GetValue<string>("Provider") ?? "Smtp";

        if (provider.Equals("Graph", StringComparison.OrdinalIgnoreCase))
            services.AddTransient<IEmailService, GraphEmailHelper>();
        else
            services.AddTransient<IEmailService, SmtpEmailHelper>();

        return services;
    }
}
```

---

## 5. Uso desde un Service / Controller

```csharp
// En cualquier Application Service que necesite enviar correo
public class CuentaService : ICuentaService
{
    private readonly IEmailService _emailService;

    public CuentaService(IEmailService emailService)
    {
        _emailService = emailService;
    }

    public async Task EnviarRecuperacionPasswordAsync(string correo, string token)
    {
        var enlace = $"https://tu-app.com/Cuenta/ResetPassword?token={Uri.EscapeDataString(token)}";

        var cuerpo = $"""
            <h2>Recuperación de contraseña</h2>
            <p>Haz clic en el enlace para restablecer tu contraseña:</p>
            <p><a href="{enlace}">Restablecer contraseña</a></p>
            <p>Este enlace expira en 24 horas.</p>
            """;

        await _emailService.EnviarAsync(correo, "Recuperación de contraseña", cuerpo);
    }
}
```

---

## 6. Plantillas HTML de Correo (Patrón Recomendado)

Crear las plantillas como archivos `.html` embebidos o como strings en una clase de constantes:

```csharp
// GestionPersonal.Constants/Messages/EmailTemplates.cs
namespace GestionPersonal.Constants.Messages;

public static class EmailTemplates
{
    public static string RecuperacionPassword(string nombreUsuario, string enlace) => $"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family:Arial,sans-serif;max-width:600px;margin:auto">
          <div style="background:#0078d4;padding:20px;text-align:center">
            <h1 style="color:white;margin:0">GestionPersonal</h1>
          </div>
          <div style="padding:30px">
            <h2>Hola, {nombreUsuario}</h2>
            <p>Recibimos una solicitud para restablecer tu contraseña.</p>
            <p>
              <a href="{enlace}"
                 style="background:#0078d4;color:white;padding:12px 24px;
                        text-decoration:none;border-radius:4px;display:inline-block">
                Restablecer contraseña
              </a>
            </p>
            <p>Si no solicitaste este cambio, ignora este mensaje.</p>
            <p style="color:#666;font-size:12px">Este enlace expira en 24 horas.</p>
          </div>
        </body>
        </html>
        """;

    public static string BienvenidaNuevoEmpleado(string nombreCompleto, string correo) => $"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family:Arial,sans-serif;max-width:600px;margin:auto">
          <div style="background:#107c10;padding:20px;text-align:center">
            <h1 style="color:white;margin:0">Bienvenido/a</h1>
          </div>
          <div style="padding:30px">
            <h2>¡Hola, {nombreCompleto}!</h2>
            <p>Tu cuenta ha sido creada en el sistema de gestión de personal.</p>
            <p><strong>Usuario:</strong> {correo}</p>
            <p>Al ingresar por primera vez deberás cambiar tu contraseña.</p>
          </div>
        </body>
        </html>
        """;
}
```

---

## 7. Pruebas con Mailtrap (Desarrollo)

Para desarrollo local sin enviar correos reales, usar **Mailtrap**:

```json
// appsettings.Development.json
{
  "EmailSettings": {
    "Provider": "Smtp",
    "Smtp": {
      "Host": "sandbox.smtp.mailtrap.io",
      "Port": 587,
      "UseSsl": false,
      "UseStartTls": true,
      "Username": "tu_mailtrap_user",
      "Password": "tu_mailtrap_password",
      "FromName": "GestionPersonal DEV",
      "FromAddress": "dev@gestionpersonal.local"
    }
  }
}
```

---

## 8. Seguridad — Checklist

- [ ] **Nunca** almacenar passwords de SMTP en el repositorio (usar `user-secrets` o variables de entorno)
- [ ] Para M365 con Graph API: usar **Application permissions** (`Mail.Send`), no delegadas
- [ ] El Client Secret de Azure AD debe rotar periódicamente (máx. 24 meses)
- [ ] Validar que el destinatario sea un correo legítimo antes de enviar (evitar open relay)
- [ ] Implementar **rate limiting** en endpoints que disparen envío de correos (recuperación de contraseña, etc.)
- [ ] Usar tokens de un solo uso con expiración para flujos de recuperación de contraseña
- [ ] Registrar en logs el envío (sin incluir el contenido del correo ni datos sensibles)

---

## 9. Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `AuthenticationException: The SMTP server requires a secure connection` | Puerto/TLS mal configurado | Usar puerto 587 con `UseStartTls = true` |
| `535 5.7.139 Authentication unsuccessful` | MFA habilitado en cuenta | Crear App Password en M365 o migrar a Graph API |
| `Graph: Forbidden (403)` | Permiso `Mail.Send` no otorgado | Dar admin consent en Azure Portal |
| `Graph: BadRequest (400)` | `FromAddress` no pertenece al tenant | Verificar que el remitente exista en el tenant M365 |
| `CERTIFICATE_VERIFY_FAILED` | Certificado SSL inválido | Solo en dev: `client.CheckCertificateRevocation = false` |

---

## 10. Referencias

- [MailKit — documentación oficial](https://github.com/jstedfast/MailKit)
- [Microsoft Graph — Send mail](https://learn.microsoft.com/en-us/graph/api/user-sendmail)
- [Azure AD App Registration](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [dotnet user-secrets](https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets)
- [Mailtrap — email sandbox](https://mailtrap.io/)
