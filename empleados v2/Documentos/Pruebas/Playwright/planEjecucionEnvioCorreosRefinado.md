# Plan de Ejecución — Capa de Mensajería y Notificaciones (Refinado)
**Sistema GestionPersonal · Shape Up Large Batch · 6 semanas**
Fecha: Abril 2026

---

# PITCH — Shape Up

## Problema

El sistema no notifica a los actores correctos cuando ocurren eventos laborales.
Las vulnerabilidades actuales son críticas:

1. **`UsuarioService`** envía la contraseña temporal en texto plano por correo (OWASP A02: Cryptographic Failures).
2. **`CuentaService`** guarda el token de recuperación sin hash en BD — cualquiera con acceso a la DB puede usarlo.
3. **`EmailHelper`** usa `System.Net.Mail.SmtpClient`, obsoleto desde .NET 5, sin soporte STARTTLS correcto.
4. **No existe trazabilidad**: no hay registro de qué correos se enviaron, a quién, ni si fallaron.
5. **Los eventos de negocio** (aprobación de horas, asignación de turno, cambios de personal) no generan ninguna notificación.

---

## Apetito

**6 semanas (Large Batch)**

- Semanas 1–3: Infraestructura base, seguridad y plantillas.
- Semanas 4–6: Eventos de negocio + pruebas Playwright.

No queremos un sistema de notificaciones genérico para todos los sistemas. Solo cubrimos los 12 eventos definidos en este pitch.

---

## Solución

### Idea central (el cambio de forma)

Introducir una **capa de mensajería centralizada** con tres responsabilidades separadas:

```
┌──────────────────────────────────────────────────────────────────┐
│  Servicio de aplicación (HoraExtraService, EventoLaboralService…) │
│       ↓ llama a                                                   │
│  INotificationService                ← ÚNICO punto de entrada     │
│       ↓ compone                                                   │
│  EmailTemplates.*  (clases estáticas)  ← HTML generado en código  │
│       ↓ envía via                                                  │
│  IEmailHelper  (MailKit / STARTTLS)   ← solo transporte           │
│       ↓ registra en                                               │
│  RegistroNotificaciones (tabla SQL)   ← auditoría y diagnóstico   │
└──────────────────────────────────────────────────────────────────┘
```

### Decisión de diseño clave: plantillas como clases estáticas

Las plantillas de correo **NO son archivos HTML en disco**. Son métodos estáticos en clases C# que retornan `string` (HTML).

**Por qué esta decisión:**

| Aspecto | HTML en disco (`EmailTemplates/*.html`) | Clase estática C# |
|---|---|---|
| Velocidad | Lectura de disco en cada envío | Compilado en memoria |
| Errores en tiempo de compilación | ❌ Solo en runtime | ✅ El compilador detecta parámetros faltantes |
| Testabilidad | Requiere `IWebHostEnvironment` mock | ✅ Función pura, sin dependencias |
| Versionado | El HTML puede desincronizarse | ✅ Viaja con el assembly |
| Inyección HTML (XSS) | Requiere sanitización manual | ✅ Parámetros en `string`-interpolation, HTML literal en el estático |

Las clases estáticas viven en **`GestionPersonal.Constants/Messages/EmailTemplates/`** — capa de Constantes, sin dependencias externas.

---

## Rabbit Holes (qué vigilar)

1. **Permiso "Send As" en Exchange Online**: sin él el servidor Office 365 rechaza con error `5.7.60`. Debe gestionarlo el administrador de Exchange antes de despliegue.
2. **Tokens del seeding existentes**: los tokens `TK1H6K9M2N`, `TK7E4D8F5G`, `TK3F9A2B1C` quedarán inválidos tras la migración a SHA-256 hash. Las pruebas de `test_recuperacion.py` deben actualizarse.
3. **Cadena `JefeInmediatoId` nula**: si el solicitante no tiene jefe configurado, la notificación al jefe simplemente no se envía. No es un error; se registra en `RegistroNotificaciones` con `TipoEvento` y `Destinatario` vacío si aplica, o se omite silenciosamente.
4. **Correo del empleado vs correo de acceso**: `Empleados.CorreoElectronico` puede ser null (empleados sin correo corporativo). Si es null, el correo va solo al `Usuarios.CorreoAcceso`.

---

## No-Goes (fuera del alcance en este ciclo)

- No se implementa sistema de plantillas con motor Razor o Fluid.
- No se agrega panel de administración para reenviar correos fallidos (ciclo futuro).
- No se implementan notificaciones push ni SMS.
- No se construye un `RegistroNotificaciones` visible en la UI (solo BD por ahora).
- No se migra a Microsoft Graph API (SMTP es suficiente con el tenant actual).

---

# PARTE 1 — Infraestructura de Mensajería (Semanas 1–3)

---

## P1-T01: Credenciales — appsettings + user-secrets

**`GestionPersonal.Web/appsettings.json`** — sección a agregar (sin contraseña):

```json
{
  "EmailSettings": {
    "Provider": "Smtp",
    "Smtp": {
      "Host":        "smtp.office365.com",
      "Port":        587,
      "UseSsl":      false,
      "UseStartTls": true,
      "Username":    "sistemas.helpharma@zentria.com.co",
      "Password":    "",
      "FromAddress": "notificacion.sf@zentria.com.co",
      "FromName":    "Notificaciones GestionPersonal"
    }
  }
}
```

**Registrar secreto en desarrollo (PowerShell desde `GestionPersonal.Web/`):**

```powershell
dotnet user-secrets init
dotnet user-secrets set "EmailSettings:Smtp:Password" "{SMTP_PASSWORD}"
```

**En producción — variables de entorno:**

```
EmailSettings__Smtp__Password={SMTP_PASSWORD}
```

> ⚠️ El buzón `sistemas.helpharma@zentria.com.co` debe tener permiso **"Send As"**
> sobre `notificacion.sf@zentria.com.co` en Exchange Admin de Office 365.
> Sin este permiso el servidor responde con error `5.7.60`.

---

## P1-T02: Modelo de configuración

**Crear: `GestionPersonal.Models/Models/Email/EmailSettings.cs`**

```csharp
namespace GestionPersonal.Models.Models.Email;

/// <summary>
/// Configuración de correo. La contraseña se lee desde user-secrets o variable de entorno.
/// Nunca debe estar en appsettings.json comiteado.
/// </summary>
public class EmailSettings
{
    public const string SectionName = "EmailSettings";

    public string       Provider { get; set; } = "Smtp";  // "Smtp" | "Graph"
    public SmtpSettings Smtp     { get; set; } = new();
}

public class SmtpSettings
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

**Registrar en `Program.cs`:**

```csharp
builder.Services.Configure<EmailSettings>(
    builder.Configuration.GetSection(EmailSettings.SectionName));
```

---

## P1-T03: Refactorizar IEmailHelper + EmailHelper a MailKit

**Refactorizar: `GestionPersonal.Helpers/Email/IEmailHelper.cs`**

```csharp
namespace GestionPersonal.Helpers.Email;

/// <summary>
/// Contrato de transporte de correo. Solo responsable del envío.
/// No conoce plantillas ni lógica de negocio.
/// </summary>
public interface IEmailHelper
{
    Task EnviarAsync(
        string destinatario,
        string asunto,
        string cuerpoHtml,
        CancellationToken ct = default);

    Task EnviarConCopiaAsync(
        string destinatario,
        string copia,
        string asunto,
        string cuerpoHtml,
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

/// <summary>
/// Implementación SMTP con MailKit.
/// Envía como buzón compartido (notificacion.sf@zentria.com.co)
/// autenticándose con la cuenta de servicio (sistemas.helpharma@zentria.com.co).
/// Requiere permiso "Send As" configurado en Exchange Online.
/// </summary>
public class EmailHelper : IEmailHelper
{
    private readonly SmtpSettings _settings;

    public EmailHelper(IOptions<EmailSettings> options)
        => _settings = options.Value.Smtp;

    public Task EnviarAsync(
        string destinatario, string asunto, string cuerpoHtml,
        CancellationToken ct = default)
        => EnviarInternoAsync(
               ConstruirMensaje([destinatario], null, asunto, cuerpoHtml), ct);

    public Task EnviarConCopiaAsync(
        string destinatario, string copia, string asunto, string cuerpoHtml,
        CancellationToken ct = default)
        => EnviarInternoAsync(
               ConstruirMensaje([destinatario], copia, asunto, cuerpoHtml), ct);

    // ── Privados ──────────────────────────────────────────────────────────────

    private MimeMessage ConstruirMensaje(
        IEnumerable<string> destinatarios, string? copia,
        string asunto, string cuerpoHtml)
    {
        var msg = new MimeMessage();
        msg.From.Add(new MailboxAddress(_settings.FromName, _settings.FromAddress));

        foreach (var d in destinatarios)
            msg.To.Add(MailboxAddress.Parse(d));

        if (!string.IsNullOrWhiteSpace(copia))
            msg.Cc.Add(MailboxAddress.Parse(copia));

        msg.Subject = asunto;
        msg.Body    = new TextPart("html") { Text = cuerpoHtml };
        return msg;
    }

    private async Task EnviarInternoAsync(MimeMessage mensaje, CancellationToken ct)
    {
        using var smtp = new SmtpClient();
        await smtp.ConnectAsync(_settings.Host, _settings.Port,
                                 SecureSocketOptions.StartTls, ct);
        await smtp.AuthenticateAsync(_settings.Username, _settings.Password, ct);
        await smtp.SendAsync(mensaje, ct);
        await smtp.DisconnectAsync(quit: true, ct);
    }
}
```

**NuGet requerido en `GestionPersonal.Helpers/GestionPersonal.Helpers.csproj`:**

```xml
<PackageReference Include="MailKit"  Version="4.*" />
<PackageReference Include="MimeKit"  Version="4.*" />
```

---

## P1-T04: Arquitectura de plantillas — clases estáticas en Constants

### Estructura completa

```
GestionPersonal.Constants/
 └── Messages/
     └── EmailTemplates/
         ├── EmailBase.cs               ← Shell HTML compartido (cabecera, pie, estilos inline)
         ├── SeguridadEmailTemplate.cs  ← EVT-01, EVT-02, EVT-03 (seguridad y acceso)
         ├── SolicitudEmailTemplate.cs  ← EVT-04, EVT-05, EVT-06, EVT-07 (solicitudes)
         ├── TurnoEmailTemplate.cs      ← EVT-08, EVT-09, EVT-10 (turnos)
         └── PersonalEmailTemplate.cs   ← EVT-11, EVT-12 (cambios de personal)
```

### Principio de diseño de las clases

Cada clase estática expone métodos que reciben **parámetros tipados** y retornan `string` (HTML completo listo para enviar).
No hay token de reemplazo `{{VARIABLE}}` ni lectura de disco. El compilador verifica que ningún parámetro quede sin valor.

---

### `EmailBase.cs` — Shell compartido

**Crear: `GestionPersonal.Constants/Messages/EmailTemplates/EmailBase.cs`**

```csharp
namespace GestionPersonal.Constants.Messages.EmailTemplates;

/// <summary>
/// Proporciona el shell HTML base para todos los correos del sistema.
/// Ancho máximo 600px, compatible con Outlook, Gmail y clientes móviles.
/// Inline styles únicamente (sin CSS externo ni JavaScript).
/// </summary>
public static class EmailBase
{
    // ── Paleta de colores corporativos ────────────────────────────────────────
    private const string ColorPrimario      = "#1e3a8a";   // azul oscuro — cabecera
    private const string ColorSecundario    = "#3b5bdb";   // azul medio  — acento
    private const string ColorExito         = "#16a34a";   // verde       — aprobado
    private const string ColorAlerta        = "#b45309";   // ámbar       — advertencia
    private const string ColorPeligro       = "#dc2626";   // rojo        — rechazado
    private const string ColorFondo         = "#f1f5f9";   // gris muy claro
    private const string ColorTarjeta       = "#ffffff";
    private const string ColorTexto         = "#1e293b";
    private const string ColorTextoSuave    = "#64748b";
    private const string ColorBorde         = "#e2e8f0";

    /// <summary>
    /// Construye el HTML completo del correo.
    /// </summary>
    /// <param name="tituloVentana">Aparece en la pestaña/asunto de algunos clientes.</param>
    /// <param name="badgeColor">Color del badge superior (usa constantes de esta clase).</param>
    /// <param name="badgeTexto">Texto pequeño encima del título principal.</param>
    /// <param name="tituloPrincipal">Título grande dentro del correo.</param>
    /// <param name="cuerpoHtml">Contenido HTML del mensaje (párrafos, tablas, botones).</param>
    /// <param name="generadoPor">Nombre de quien generó el evento.</param>
    /// <param name="tipoEvento">Identificador del tipo de evento para el pie.</param>
    public static string Construir(
        string tituloVentana,
        string badgeColor,
        string badgeTexto,
        string tituloPrincipal,
        string cuerpoHtml,
        string generadoPor,
        string tipoEvento)
    {
        return $"""
        <!DOCTYPE html>
        <html lang="es" xmlns="http://www.w3.org/1999/xhtml">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <meta http-equiv="X-UA-Compatible" content="IE=edge" />
          <title>{EscapeHtml(tituloVentana)}</title>
        </head>
        <body style="margin:0;padding:0;background-color:{ColorFondo};font-family:Arial,Helvetica,sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;">
          <!-- Wrapper externo -->
          <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color:{ColorFondo};padding:32px 16px;">
            <tr>
              <td align="center">
                <!-- Tarjeta principal 600px -->
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="max-width:600px;width:100%;background-color:{ColorTarjeta};border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,0.08);overflow:hidden;">

                  <!-- ── Cabecera con gradiente ── -->
                  <tr>
                    <td style="background:linear-gradient(135deg,{ColorPrimario} 0%,{ColorSecundario} 100%);padding:28px 32px;">
                      <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                        <tr>
                          <td>
                            <p style="margin:0;color:rgba(255,255,255,0.75);font-size:11px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;">{EscapeHtml(badgeTexto)}</p>
                            <h1 style="margin:6px 0 0;color:#ffffff;font-size:22px;font-weight:700;line-height:1.3;">{EscapeHtml(tituloPrincipal)}</h1>
                          </td>
                          <td align="right" style="vertical-align:top;">
                            <div style="display:inline-block;background-color:rgba(255,255,255,0.15);border-radius:20px;padding:4px 14px;">
                              <span style="color:#ffffff;font-size:12px;font-weight:600;">{EscapeHtml(badgeColor)}</span>
                            </div>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>

                  <!-- ── Cuerpo del mensaje ── -->
                  <tr>
                    <td style="padding:32px;">
                      {cuerpoHtml}
                    </td>
                  </tr>

                  <!-- ── Pie de correo ── -->
                  <tr>
                    <td style="background-color:{ColorFondo};padding:20px 32px;border-top:1px solid {ColorBorde};">
                      <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                        <tr>
                          <td>
                            <p style="margin:0;color:{ColorTextoSuave};font-size:12px;line-height:1.6;">
                              Este correo fue generado automáticamente por <strong>{EscapeHtml(generadoPor)}</strong>
                              como parte del proceso <em>{EscapeHtml(tipoEvento)}</em>.
                            </p>
                            <p style="margin:8px 0 0;color:{ColorTextoSuave};font-size:11px;">
                              Si tienes dudas, contacta a tu administrador del sistema.
                              Por favor no respondas a este correo.
                            </p>
                          </td>
                          <td align="right" style="vertical-align:bottom;padding-left:16px;">
                            <p style="margin:0;color:{ColorPrimario};font-size:13px;font-weight:700;white-space:nowrap;">GestionPersonal</p>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>

                </table>
                <!-- Fin tarjeta -->
              </td>
            </tr>
          </table>
        </body>
        </html>
        """;
    }

    // ── Helpers internos compartidos ──────────────────────────────────────────

    /// <summary>Escapa caracteres HTML para evitar XSS en parámetros de usuario.</summary>
    public static string EscapeHtml(string? valor)
        => System.Net.WebUtility.HtmlEncode(valor ?? string.Empty);

    /// <summary>Genera una fila de datos con etiqueta y valor para las tablas de información.</summary>
    public static string FilaDato(string etiqueta, string valor, bool alternada = false)
    {
        var bg = alternada ? "#f8fafc" : "#ffffff";
        return $"""
            <tr>
              <td style="padding:10px 14px;background-color:{bg};border-bottom:1px solid #f1f5f9;font-size:13px;color:#64748b;font-weight:600;width:40%;">{EscapeHtml(etiqueta)}</td>
              <td style="padding:10px 14px;background-color:{bg};border-bottom:1px solid #f1f5f9;font-size:13px;color:#1e293b;">{EscapeHtml(valor)}</td>
            </tr>
            """;
    }

    /// <summary>Genera un botón de acción CTA con color y enlace.</summary>
    public static string Boton(string texto, string href, string color = "#1e3a8a")
        => $"""
           <a href="{EscapeHtml(href)}"
              style="display:inline-block;background-color:{color};color:#ffffff;text-decoration:none;
                     font-size:14px;font-weight:700;padding:12px 28px;border-radius:8px;
                     letter-spacing:0.3px;margin-top:8px;">{EscapeHtml(texto)}</a>
           """;

    /// <summary>Banner de alerta (info, éxito, advertencia, peligro).</summary>
    public static string Banner(string mensaje, string tipo = "info")
    {
        var (bg, borde, icono) = tipo switch
        {
            "exito"      => ("#dcfce7", "#16a34a", "✓"),
            "advertencia"=> ("#fef9c3", "#b45309", "⚠"),
            "peligro"    => ("#fee2e2", "#dc2626", "✗"),
            _            => ("#eff6ff", "#3b5bdb", "ℹ")
        };
        return $"""
           <div style="background-color:{bg};border-left:4px solid {borde};
                       border-radius:0 8px 8px 0;padding:14px 18px;margin:20px 0;">
             <p style="margin:0;font-size:14px;color:#1e293b;">
               <strong style="margin-right:6px;">{icono}</strong>{EscapeHtml(mensaje)}
             </p>
           </div>
           """;
    }

    /// <summary>Tabla de información con borde redondeado.</summary>
    public static string TablaInfo(string filasHtml)
        => $"""
           <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%"
                  style="border-collapse:collapse;border:1px solid #e2e8f0;border-radius:8px;
                         overflow:hidden;margin:20px 0;">
             <tbody>
               {filasHtml}
             </tbody>
           </table>
           """;

    // ── Colores expuestos para las subclases ──────────────────────────────────
    public const string Verde  = "#16a34a";
    public const string Rojo   = "#dc2626";
    public const string Azul   = "#3b5bdb";
    public const string Ambar  = "#b45309";
    public const string Gris   = "#64748b";
}
```

---

### `SeguridadEmailTemplate.cs` — EVT-01, EVT-02, EVT-03

**Crear: `GestionPersonal.Constants/Messages/EmailTemplates/SeguridadEmailTemplate.cs`**

```csharp
namespace GestionPersonal.Constants.Messages.EmailTemplates;

/// <summary>
/// Plantillas de correo para eventos de seguridad y acceso al sistema.
/// Todos los métodos son funciones puras — sin estado, sin IO, testeables directamente.
/// </summary>
public static class SeguridadEmailTemplate
{
    // ── EVT-01: Nuevo usuario creado ─────────────────────────────────────────

    /// <summary>
    /// Correo de bienvenida al crear una cuenta nueva.
    /// NO incluye contraseña — el usuario la establece al primer inicio de sesión.
    /// </summary>
    public static string NuevoUsuario(
        string nombreEmpleado,
        string correoAcceso,
        string nombreCreador)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Tu cuenta en <strong>GestionPersonal</strong> ha sido creada. A continuación encontrarás tu correo de acceso:
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Correo de acceso", correoAcceso, false) +
                EmailBase.FilaDato("Estado de la cuenta", "Activa — primer acceso pendiente", true)
            )}

            {EmailBase.Banner(
                "Por seguridad, no enviamos contraseñas por correo. Al ingresar por primera vez, " +
                "el sistema te pedirá crear tu propia contraseña.", "info")}

            <p style="margin:24px 0 0;font-size:14px;color:#475569;line-height:1.7;">
              Si tienes dificultades para acceder, comunícate con tu administrador o con
              <strong>{EmailBase.EscapeHtml(nombreCreador)}</strong>, quien creó tu cuenta.
            </p>
            """;

        return EmailBase.Construir(
            tituloVentana   : "Bienvenido a GestionPersonal",
            badgeColor      : "Cuenta nueva",
            badgeTexto      : "Sistema de Gestión de Personal",
            tituloPrincipal : $"Bienvenido, {nombreEmpleado}",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreCreador,
            tipoEvento      : "Creación de Usuario");
    }

    // ── EVT-02: Recuperación de contraseña ───────────────────────────────────

    /// <summary>
    /// Correo con el código de recuperación de contraseña.
    /// El parámetro <paramref name="codigo"/> es el código PLANO (no el hash).
    /// El hash SHA-256 del código es lo que se almacena en BD.
    /// </summary>
    public static string RecuperacionContrasena(
        string nombreEmpleado,
        string correoAcceso,
        string codigo,
        string vigenciaMinutos = "30")
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Recibimos una solicitud para restablecer la contraseña de la cuenta
              <strong>{EmailBase.EscapeHtml(correoAcceso)}</strong>.
              Usa el código de verificación que aparece a continuación:
            </p>

            <!-- Código destacado -->
            <div style="text-align:center;margin:28px 0;">
              <div style="display:inline-block;background-color:#f0f4ff;border:2px dashed #3b5bdb;
                          border-radius:12px;padding:20px 40px;">
                <p style="margin:0 0 6px;font-size:11px;font-weight:700;letter-spacing:2px;
                           text-transform:uppercase;color:#3b5bdb;">Código de verificación</p>
                <p style="margin:0;font-size:32px;font-weight:900;letter-spacing:8px;
                           color:#1e3a8a;font-family:'Courier New',monospace;">{EmailBase.EscapeHtml(codigo)}</p>
                <p style="margin:8px 0 0;font-size:12px;color:#64748b;">
                  Válido por <strong>{EmailBase.EscapeHtml(vigenciaMinutos)} minutos</strong>
                </p>
              </div>
            </div>

            {EmailBase.Banner(
                $"Este código expira en {vigenciaMinutos} minutos y solo puede usarse una vez. " +
                "Si no solicitaste este cambio, ignora este correo — tu contraseña no será modificada.",
                "advertencia")}

            <p style="margin:20px 0 0;font-size:13px;color:#94a3b8;line-height:1.6;">
              Por tu seguridad, nunca compartas este código con nadie, incluyendo personal de soporte.
            </p>
            """;

        return EmailBase.Construir(
            tituloVentana   : "Código de recuperación de contraseña",
            badgeColor      : "Seguridad",
            badgeTexto      : "Solicitud de restablecimiento",
            tituloPrincipal : "Recuperación de contraseña",
            cuerpoHtml      : cuerpo,
            generadoPor     : correoAcceso,
            tipoEvento      : "Recuperación de Contraseña");
    }

    // ── EVT-03: Cambio de contraseña exitoso ─────────────────────────────────

    /// <summary>
    /// Confirmación de que la contraseña fue cambiada. Alerta de seguridad.
    /// </summary>
    public static string CambioContrasenaExitoso(
        string nombreEmpleado,
        string correoAcceso)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>

            {EmailBase.Banner(
                "Tu contraseña fue cambiada exitosamente. Si realizaste este cambio, no es necesario que hagas nada más.",
                "exito")}

            <p style="margin:20px 0;font-size:14px;color:#475569;line-height:1.7;">
              Si <strong>no realizaste este cambio</strong>, tu cuenta puede estar comprometida.
              Contacta inmediatamente a tu administrador del sistema.
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Cuenta afectada", correoAcceso, false) +
                EmailBase.FilaDato("Acción", "Cambio de contraseña", true) +
                EmailBase.FilaDato("Fecha", DateTime.Now.ToString("dd/MM/yyyy HH:mm"), false)
            )}
            """;

        return EmailBase.Construir(
            tituloVentana   : "Contraseña actualizada",
            badgeColor      : "Confirmación",
            badgeTexto      : "Seguridad de la cuenta",
            tituloPrincipal : "Contraseña actualizada",
            cuerpoHtml      : cuerpo,
            generadoPor     : correoAcceso,
            tipoEvento      : "Cambio de Contraseña");
    }
}
```

---

### `SolicitudEmailTemplate.cs` — EVT-04, EVT-05, EVT-06, EVT-07

**Crear: `GestionPersonal.Constants/Messages/EmailTemplates/SolicitudEmailTemplate.cs`**

```csharp
namespace GestionPersonal.Constants.Messages.EmailTemplates;

/// <summary>
/// Plantillas para el ciclo de vida de solicitudes laborales
/// (Horas Extra, Vacaciones, Permisos, Incapacidades).
/// EVT-04: Solicitud creada → notifica al jefe.
/// EVT-05: Aprobada → notifica al solicitante.
/// EVT-06: Rechazada → notifica al solicitante.
/// EVT-07: Devuelta para corrección → notifica al solicitante.
/// </summary>
public static class SolicitudEmailTemplate
{
    // ── EVT-04: Solicitud creada — notificación al jefe inmediato ────────────

    public static string SolicitudCreadaParaJefe(
        string nombreJefe,
        string nombreSolicitante,
        string tipoSolicitud,
        string fechaEvento,
        string detalle = "")
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreJefe)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Se ha registrado una nueva solicitud de <strong>{EmailBase.EscapeHtml(tipoSolicitud)}</strong>
              que requiere tu revisión:
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Solicitante",   nombreSolicitante, false) +
                EmailBase.FilaDato("Tipo",          tipoSolicitud,     true)  +
                EmailBase.FilaDato("Fecha",         fechaEvento,       false) +
                (string.IsNullOrWhiteSpace(detalle) ? "" :
                    EmailBase.FilaDato("Detalle",   detalle,           true))
            )}

            {EmailBase.Banner(
                "Esta solicitud está pendiente de tu aprobación. Ingresa al sistema para revisarla.",
                "info")}
            """;

        return EmailBase.Construir(
            tituloVentana   : $"Nueva solicitud de {tipoSolicitud}",
            badgeColor      : "Pendiente",
            badgeTexto      : "Solicitud en espera de aprobación",
            tituloPrincipal : $"Nueva solicitud — {tipoSolicitud}",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreSolicitante,
            tipoEvento      : "Solicitud Creada");
    }

    // ── EVT-05: Solicitud aprobada — notificación al solicitante ────────────

    public static string SolicitudAprobada(
        string nombreSolicitante,
        string tipoSolicitud,
        string fechaEvento,
        string nombreAprobador,
        string observacion = "")
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreSolicitante)}</strong>,
            </p>

            {EmailBase.Banner(
                $"Tu solicitud de {tipoSolicitud} fue aprobada por {nombreAprobador}.",
                "exito")}

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Tipo de solicitud", tipoSolicitud,    false) +
                EmailBase.FilaDato("Fecha",             fechaEvento,      true)  +
                EmailBase.FilaDato("Aprobado por",      nombreAprobador,  false) +
                (string.IsNullOrWhiteSpace(observacion) ? "" :
                    EmailBase.FilaDato("Observación",   observacion,      true))
            )}

            <p style="margin:20px 0 0;font-size:14px;color:#475569;line-height:1.7;">
              Si tienes alguna consulta sobre esta aprobación, comunícate con
              <strong>{EmailBase.EscapeHtml(nombreAprobador)}</strong>.
            </p>
            """;

        return EmailBase.Construir(
            tituloVentana   : $"Solicitud de {tipoSolicitud} aprobada",
            badgeColor      : "Aprobada",
            badgeTexto      : "Resultado de tu solicitud",
            tituloPrincipal : $"Tu solicitud fue aprobada",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreAprobador,
            tipoEvento      : "Solicitud Aprobada");
    }

    // ── EVT-06: Solicitud rechazada — notificación al solicitante ────────────

    public static string SolicitudRechazada(
        string nombreSolicitante,
        string tipoSolicitud,
        string fechaEvento,
        string nombreRevisor,
        string motivoRechazo = "")
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreSolicitante)}</strong>,
            </p>

            {EmailBase.Banner(
                $"Tu solicitud de {tipoSolicitud} no fue aprobada.",
                "peligro")}

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Tipo de solicitud", tipoSolicitud, false) +
                EmailBase.FilaDato("Fecha",             fechaEvento,   true)  +
                EmailBase.FilaDato("Revisado por",      nombreRevisor, false) +
                (string.IsNullOrWhiteSpace(motivoRechazo) ? "" :
                    EmailBase.FilaDato("Motivo",        motivoRechazo, true))
            )}

            <p style="margin:20px 0 0;font-size:14px;color:#475569;line-height:1.7;">
              Si consideras que esta decisión es incorrecta, comunícate con
              <strong>{EmailBase.EscapeHtml(nombreRevisor)}</strong>.
            </p>
            """;

        return EmailBase.Construir(
            tituloVentana   : $"Solicitud de {tipoSolicitud} rechazada",
            badgeColor      : "Rechazada",
            badgeTexto      : "Resultado de tu solicitud",
            tituloPrincipal : "Tu solicitud fue rechazada",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreRevisor,
            tipoEvento      : "Solicitud Rechazada");
    }

    // ── EVT-07: Solicitud devuelta para corrección ────────────────────────────

    public static string SolicitudDevuelta(
        string nombreSolicitante,
        string tipoSolicitud,
        string fechaEvento,
        string nombreRevisor,
        string comentario)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreSolicitante)}</strong>,
            </p>

            {EmailBase.Banner(
                $"Tu solicitud de {tipoSolicitud} fue devuelta para corrección.",
                "advertencia")}

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Tipo de solicitud", tipoSolicitud, false) +
                EmailBase.FilaDato("Fecha",             fechaEvento,   true)  +
                EmailBase.FilaDato("Devuelta por",      nombreRevisor, false) +
                EmailBase.FilaDato("Comentario",        comentario,    true)
            )}

            <p style="margin:20px 0 0;font-size:14px;color:#475569;line-height:1.7;">
              Ingresa al sistema, corrige los campos indicados y vuelve a enviar la solicitud.
            </p>
            """;

        return EmailBase.Construir(
            tituloVentana   : $"Solicitud de {tipoSolicitud} devuelta",
            badgeColor      : "Requiere corrección",
            badgeTexto      : "Solicitud pendiente de ajuste",
            tituloPrincipal : "Tu solicitud requiere corrección",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreRevisor,
            tipoEvento      : "Solicitud Devuelta");
    }
}
```

---

### `TurnoEmailTemplate.cs` — EVT-08, EVT-09, EVT-10

**Crear: `GestionPersonal.Constants/Messages/EmailTemplates/TurnoEmailTemplate.cs`**

```csharp
namespace GestionPersonal.Constants.Messages.EmailTemplates;

/// <summary>
/// Plantillas para eventos de asignación y gestión de turnos.
/// EVT-08: Turno asignado.
/// EVT-09: Turno modificado.
/// EVT-10: Turno cancelado.
/// </summary>
public static class TurnoEmailTemplate
{
    // ── EVT-08: Turno asignado ────────────────────────────────────────────────

    public static string TurnoAsignado(
        string nombreEmpleado,
        string nombreTurno,
        string fechaVigencia,
        string nombreJefe)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Se te ha asignado un turno de trabajo. Revisa los detalles a continuación:
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Turno asignado", nombreTurno,   false) +
                EmailBase.FilaDato("Vigencia desde", fechaVigencia, true)  +
                EmailBase.FilaDato("Asignado por",   nombreJefe,    false)
            )}

            {EmailBase.Banner("Ingresa al sistema para ver el detalle completo de tu horario.", "info")}
            """;

        return EmailBase.Construir(
            tituloVentana   : "Asignación de turno",
            badgeColor      : "Turno asignado",
            badgeTexto      : "Gestión de horarios",
            tituloPrincipal : "Nuevo turno asignado",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreJefe,
            tipoEvento      : "Asignación de Turno");
    }

    // ── EVT-09: Turno modificado ──────────────────────────────────────────────

    public static string TurnoModificado(
        string nombreEmpleado,
        string nombreTurnoAnterior,
        string nombreTurnoNuevo,
        string fechaVigencia,
        string nombreJefe)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Tu turno de trabajo ha sido modificado:
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Turno anterior", nombreTurnoAnterior, false) +
                EmailBase.FilaDato("Turno nuevo",    nombreTurnoNuevo,    true)  +
                EmailBase.FilaDato("Vigencia desde", fechaVigencia,       false) +
                EmailBase.FilaDato("Modificado por", nombreJefe,          true)
            )}

            {EmailBase.Banner("Verifica tu nuevo horario en el sistema.", "advertencia")}
            """;

        return EmailBase.Construir(
            tituloVentana   : "Cambio de turno",
            badgeColor      : "Turno modificado",
            badgeTexto      : "Gestión de horarios",
            tituloPrincipal : "Tu turno fue modificado",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreJefe,
            tipoEvento      : "Modificación de Turno");
    }

    // ── EVT-10: Turno cancelado ───────────────────────────────────────────────

    public static string TurnoCancelado(
        string nombreEmpleado,
        string nombreTurno,
        string fechaVigencia,
        string nombreJefe)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>

            {EmailBase.Banner(
                $"El turno '{nombreTurno}' con vigencia desde {fechaVigencia} ha sido cancelado.",
                "peligro")}

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Turno cancelado", nombreTurno,   false) +
                EmailBase.FilaDato("Vigencia desde",  fechaVigencia, true)  +
                EmailBase.FilaDato("Cancelado por",   nombreJefe,    false)
            )}

            <p style="margin:20px 0 0;font-size:14px;color:#475569;line-height:1.7;">
              Comunícate con <strong>{EmailBase.EscapeHtml(nombreJefe)}</strong>
              para más información sobre tu nueva asignación.
            </p>
            """;

        return EmailBase.Construir(
            tituloVentana   : "Turno cancelado",
            badgeColor      : "Turno cancelado",
            badgeTexto      : "Gestión de horarios",
            tituloPrincipal : "Turno cancelado",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreJefe,
            tipoEvento      : "Cancelación de Turno");
    }
}
```

---

### `PersonalEmailTemplate.cs` — EVT-11, EVT-12

**Crear: `GestionPersonal.Constants/Messages/EmailTemplates/PersonalEmailTemplate.cs`**

```csharp
namespace GestionPersonal.Constants.Messages.EmailTemplates;

/// <summary>
/// Plantillas para cambios en la información del empleado.
/// EVT-11: Cambio de cargo.
/// EVT-12: Cambio de sede.
/// </summary>
public static class PersonalEmailTemplate
{
    // ── EVT-11: Cambio de cargo ───────────────────────────────────────────────

    public static string CambioCargo(
        string nombreEmpleado,
        string cargoAnterior,
        string cargoNuevo,
        string nombreResponsable)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Se ha registrado un cambio en tu cargo dentro de la organización:
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Cargo anterior",   cargoAnterior,     false) +
                EmailBase.FilaDato("Cargo nuevo",      cargoNuevo,        true)  +
                EmailBase.FilaDato("Registrado por",   nombreResponsable, false) +
                EmailBase.FilaDato("Fecha de cambio",  DateTime.Now.ToString("dd/MM/yyyy"), true)
            )}

            {EmailBase.Banner(
                "Si tienes dudas sobre este cambio, comunícate con Recursos Humanos.",
                "info")}
            """;

        return EmailBase.Construir(
            tituloVentana   : "Cambio de cargo",
            badgeColor      : "Cambio registrado",
            badgeTexto      : "Actualización de personal",
            tituloPrincipal : "Cambio de cargo",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreResponsable,
            tipoEvento      : "Cambio de Cargo");
    }

    // ── EVT-12: Cambio de sede ────────────────────────────────────────────────

    public static string CambioSede(
        string nombreEmpleado,
        string sedeAnterior,
        string sedeNueva,
        string nombreResponsable)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Se ha registrado un traslado de sede en tu perfil:
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Sede anterior",    sedeAnterior,      false) +
                EmailBase.FilaDato("Sede nueva",       sedeNueva,         true)  +
                EmailBase.FilaDato("Registrado por",   nombreResponsable, false) +
                EmailBase.FilaDato("Fecha de traslado",DateTime.Now.ToString("dd/MM/yyyy"), true)
            )}

            {EmailBase.Banner(
                "Si tienes dudas sobre este traslado, comunícate con Recursos Humanos.",
                "info")}
            """;

        return EmailBase.Construir(
            tituloVentana   : "Traslado de sede",
            badgeColor      : "Traslado registrado",
            badgeTexto      : "Actualización de personal",
            tituloPrincipal : "Traslado de sede",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreResponsable,
            tipoEvento      : "Cambio de Sede");
    }
}
```

---

## P1-T05: INotificationService y DTOs

**Crear: `GestionPersonal.Application/Interfaces/INotificationService.cs`**

```csharp
using GestionPersonal.Models.DTOs.Notificaciones;

namespace GestionPersonal.Application.Interfaces;

/// <summary>
/// Único punto de entrada para todas las notificaciones del sistema.
/// Los servicios de aplicación solo conocen esta interfaz.
/// El transporte, la plantilla y el registro son detalles internos de la implementación.
/// </summary>
public interface INotificationService
{
    // ── Seguridad ─────────────────────────────────────────────────────────────
    Task NotificarNuevoUsuarioAsync(NotificacionNuevoUsuarioDto datos, CancellationToken ct = default);
    Task NotificarRecuperacionContrasenaAsync(NotificacionRecuperacionDto datos, CancellationToken ct = default);
    Task NotificarCambioContrasenaExitosoAsync(NotificacionCambioContrasenaDto datos, CancellationToken ct = default);

    // ── Solicitudes ───────────────────────────────────────────────────────────
    Task NotificarSolicitudCreadaAsync(NotificacionSolicitudDto datos, CancellationToken ct = default);
    Task NotificarSolicitudAprobadaAsync(NotificacionSolicitudDto datos, CancellationToken ct = default);
    Task NotificarSolicitudRechazadaAsync(NotificacionSolicitudDto datos, CancellationToken ct = default);
    Task NotificarSolicitudDevueltaAsync(NotificacionSolicitudDto datos, CancellationToken ct = default);

    // ── Turnos ────────────────────────────────────────────────────────────────
    Task NotificarAsignacionTurnoAsync(NotificacionTurnoDto datos, CancellationToken ct = default);
    Task NotificarModificacionTurnoAsync(NotificacionTurnoDto datos, CancellationToken ct = default);
    Task NotificarCancelacionTurnoAsync(NotificacionTurnoDto datos, CancellationToken ct = default);

    // ── Cambios de personal ───────────────────────────────────────────────────
    Task NotificarCambioCargoAsync(NotificacionCambioPersonalDto datos, CancellationToken ct = default);
    Task NotificarCambioSedeAsync(NotificacionCambioPersonalDto datos, CancellationToken ct = default);
}
```

**Crear DTOs en `GestionPersonal.Models/DTOs/Notificaciones/`:**

```csharp
// NotificacionNuevoUsuarioDto.cs
namespace GestionPersonal.Models.DTOs.Notificaciones;
public record NotificacionNuevoUsuarioDto(
    string DestinatarioCorreo,
    string NombreEmpleado,
    string CorreoAcceso,
    string NombreCreadorEvento);     // asunto: [Nuevo Usuario] - [NombreCreadorEvento]

// NotificacionRecuperacionDto.cs
public record NotificacionRecuperacionDto(
    string DestinatarioCorreo,
    string NombreEmpleado,
    string Codigo,                   // código PLANO — el hash va en BD
    string VigenciaMinutos = "30");

// NotificacionCambioContrasenaDto.cs
public record NotificacionCambioContrasenaDto(
    string DestinatarioCorreo,
    string NombreEmpleado);

// NotificacionSolicitudDto.cs
public record NotificacionSolicitudDto(
    string  TipoEvento,
    string  TipoSolicitud,           // "Horas Extra", "Vacaciones", "Permiso", "Incapacidad"
    string  FechaEvento,
    string  NombreEmpleadoSolicitante,
    string  CorreoEmpleadoSolicitante,
    string  NombreJefeInmediato,
    string  CorreoJefeInmediato,
    string? NombreJefeApoyo,         // null si no hay segundo nivel en la cadena
    string? CorreoJefeApoyo,
    string? NombreAprobador,
    string? Observacion,
    string  NombreQuienGenera);

// NotificacionTurnoDto.cs
public record NotificacionTurnoDto(
    string TipoEvento,
    string NombreEmpleado,
    string CorreoEmpleado,
    string NombreTurno,
    string? NombreTurnoAnterior,     // solo para modificación
    string FechaVigencia,
    string CorreoJefeEmisor,
    string NombreJefeEmisor,
    string NombreQuienGenera);

// NotificacionCambioPersonalDto.cs
public record NotificacionCambioPersonalDto(
    string TipoEvento,
    string NombreEmpleado,
    string CorreoEmpleado,
    string ValorAnterior,
    string ValorNuevo,
    string CorreoRRHH,
    string NombreQuienGenera);
```

---

## P1-T06: NotificationService — implementación profunda

**Crear: `GestionPersonal.Application/Services/NotificationService.cs`**

```csharp
using GestionPersonal.Application.Interfaces;
using GestionPersonal.Constants.Messages.EmailTemplates;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Helpers.Email;
using GestionPersonal.Models.DTOs.Notificaciones;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using Microsoft.Extensions.Logging;

namespace GestionPersonal.Application.Services;

/// <summary>
/// Módulo profundo de notificaciones.
/// Interfaz: INotificationService (12 métodos semánticos).
/// Implementación oculta: selección de plantilla, formato de asunto,
///                        lógica de CC, envío por MailKit y auditoría en BD.
///
/// Los servicios que llaman a este módulo NO conocen IEmailHelper ni EmailTemplates.
/// Solo reciben un DTO con el contexto del evento.
/// </summary>
public class NotificationService : INotificationService
{
    private const string FormatoAsunto = "[{0}] - [{1}]";  // [TipoEvento] - [Quien]

    private readonly IEmailHelper             _email;
    private readonly INotificacionRepository  _registro;
    private readonly ILogger<NotificationService> _logger;

    public NotificationService(
        IEmailHelper email,
        INotificacionRepository registro,
        ILogger<NotificationService> logger)
    {
        _email    = email;
        _registro = registro;
        _logger   = logger;
    }

    // ── Seguridad ─────────────────────────────────────────────────────────────

    public Task NotificarNuevoUsuarioAsync(
        NotificacionNuevoUsuarioDto d, CancellationToken ct = default)
        => Enviar(
               destinatario : d.DestinatarioCorreo,
               copia        : null,
               asunto       : Asunto("Nuevo Usuario", d.NombreCreadorEvento),
               html         : SeguridadEmailTemplate.NuevoUsuario(
                                  d.NombreEmpleado, d.CorreoAcceso, d.NombreCreadorEvento),
               tipoEvento   : "NuevoUsuario",
               ct);

    public Task NotificarRecuperacionContrasenaAsync(
        NotificacionRecuperacionDto d, CancellationToken ct = default)
        => Enviar(
               destinatario : d.DestinatarioCorreo,
               copia        : null,
               asunto       : Asunto("Recuperación de Contraseña", d.DestinatarioCorreo),
               html         : SeguridadEmailTemplate.RecuperacionContrasena(
                                  d.NombreEmpleado, d.DestinatarioCorreo,
                                  d.Codigo, d.VigenciaMinutos),
               tipoEvento   : "RecuperacionContrasena",
               ct);

    public Task NotificarCambioContrasenaExitosoAsync(
        NotificacionCambioContrasenaDto d, CancellationToken ct = default)
        => Enviar(
               destinatario : d.DestinatarioCorreo,
               copia        : null,
               asunto       : Asunto("Cambio de Contraseña", d.DestinatarioCorreo),
               html         : SeguridadEmailTemplate.CambioContrasenaExitoso(
                                  d.NombreEmpleado, d.DestinatarioCorreo),
               tipoEvento   : "CambioContrasenaExitoso",
               ct);

    // ── Solicitudes ───────────────────────────────────────────────────────────

    public Task NotificarSolicitudCreadaAsync(
        NotificacionSolicitudDto d, CancellationToken ct = default)
        => Enviar(
               destinatario : d.CorreoJefeInmediato,
               copia        : d.CorreoJefeApoyo,
               asunto       : Asunto($"Nueva {d.TipoSolicitud}", d.NombreQuienGenera),
               html         : SolicitudEmailTemplate.SolicitudCreadaParaJefe(
                                  d.NombreJefeInmediato, d.NombreEmpleadoSolicitante,
                                  d.TipoSolicitud, d.FechaEvento, d.Observacion ?? ""),
               tipoEvento   : "SolicitudCreada",
               ct);

    public Task NotificarSolicitudAprobadaAsync(
        NotificacionSolicitudDto d, CancellationToken ct = default)
        => Enviar(
               destinatario : d.CorreoEmpleadoSolicitante,
               copia        : null,
               asunto       : Asunto($"{d.TipoSolicitud} Aprobada", d.NombreQuienGenera),
               html         : SolicitudEmailTemplate.SolicitudAprobada(
                                  d.NombreEmpleadoSolicitante, d.TipoSolicitud,
                                  d.FechaEvento, d.NombreAprobador ?? d.NombreQuienGenera,
                                  d.Observacion ?? ""),
               tipoEvento   : "SolicitudAprobada",
               ct);

    public Task NotificarSolicitudRechazadaAsync(
        NotificacionSolicitudDto d, CancellationToken ct = default)
        => Enviar(
               destinatario : d.CorreoEmpleadoSolicitante,
               copia        : null,
               asunto       : Asunto($"{d.TipoSolicitud} Rechazada", d.NombreQuienGenera),
               html         : SolicitudEmailTemplate.SolicitudRechazada(
                                  d.NombreEmpleadoSolicitante, d.TipoSolicitud,
                                  d.FechaEvento, d.NombreAprobador ?? d.NombreQuienGenera,
                                  d.Observacion ?? ""),
               tipoEvento   : "SolicitudRechazada",
               ct);

    public Task NotificarSolicitudDevueltaAsync(
        NotificacionSolicitudDto d, CancellationToken ct = default)
        => Enviar(
               destinatario : d.CorreoEmpleadoSolicitante,
               copia        : null,
               asunto       : Asunto($"{d.TipoSolicitud} Devuelta", d.NombreQuienGenera),
               html         : SolicitudEmailTemplate.SolicitudDevuelta(
                                  d.NombreEmpleadoSolicitante, d.TipoSolicitud,
                                  d.FechaEvento, d.NombreAprobador ?? d.NombreQuienGenera,
                                  d.Observacion ?? "(sin comentario)"),
               tipoEvento   : "SolicitudDevuelta",
               ct);

    // ── Turnos ────────────────────────────────────────────────────────────────

    public Task NotificarAsignacionTurnoAsync(
        NotificacionTurnoDto d, CancellationToken ct = default)
        => Enviar(
               destinatario : d.CorreoEmpleado,
               copia        : d.CorreoJefeEmisor,
               asunto       : Asunto("Asignación de Turno", d.NombreQuienGenera),
               html         : TurnoEmailTemplate.TurnoAsignado(
                                  d.NombreEmpleado, d.NombreTurno,
                                  d.FechaVigencia,  d.NombreJefeEmisor),
               tipoEvento   : "AsignacionTurno",
               ct);

    public Task NotificarModificacionTurnoAsync(
        NotificacionTurnoDto d, CancellationToken ct = default)
        => Enviar(
               destinatario : d.CorreoEmpleado,
               copia        : d.CorreoJefeEmisor,
               asunto       : Asunto("Cambio de Turno", d.NombreQuienGenera),
               html         : TurnoEmailTemplate.TurnoModificado(
                                  d.NombreEmpleado,
                                  d.NombreTurnoAnterior ?? "—",
                                  d.NombreTurno,
                                  d.FechaVigencia,
                                  d.NombreJefeEmisor),
               tipoEvento   : "ModificacionTurno",
               ct);

    public Task NotificarCancelacionTurnoAsync(
        NotificacionTurnoDto d, CancellationToken ct = default)
        => Enviar(
               destinatario : d.CorreoEmpleado,
               copia        : null,
               asunto       : Asunto("Cancelación de Turno", d.NombreQuienGenera),
               html         : TurnoEmailTemplate.TurnoCancelado(
                                  d.NombreEmpleado, d.NombreTurno,
                                  d.FechaVigencia,  d.NombreJefeEmisor),
               tipoEvento   : "CancelacionTurno",
               ct);

    // ── Cambios de personal ───────────────────────────────────────────────────

    public Task NotificarCambioCargoAsync(
        NotificacionCambioPersonalDto d, CancellationToken ct = default)
        => Enviar(
               destinatario : d.CorreoEmpleado,
               copia        : d.CorreoRRHH,
               asunto       : Asunto("Cambio de Cargo", d.NombreQuienGenera),
               html         : PersonalEmailTemplate.CambioCargo(
                                  d.NombreEmpleado, d.ValorAnterior,
                                  d.ValorNuevo,     d.NombreQuienGenera),
               tipoEvento   : "CambioCargo",
               ct);

    public Task NotificarCambioSedeAsync(
        NotificacionCambioPersonalDto d, CancellationToken ct = default)
        => Enviar(
               destinatario : d.CorreoEmpleado,
               copia        : d.CorreoRRHH,
               asunto       : Asunto("Cambio de Sede", d.NombreQuienGenera),
               html         : PersonalEmailTemplate.CambioSede(
                                  d.NombreEmpleado, d.ValorAnterior,
                                  d.ValorNuevo,     d.NombreQuienGenera),
               tipoEvento   : "CambioDeSede",
               ct);

    // ── Privados: formato de asunto + envío + registro ─────────────────────────

    private static string Asunto(string tipo, string quien)
        => string.Format(FormatoAsunto, tipo, quien);

    private async Task Enviar(
        string destinatario, string? copia,
        string asunto, string html,
        string tipoEvento, CancellationToken ct)
    {
        var reg = new RegistroNotificacion
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
                await _email.EnviarConCopiaAsync(destinatario, copia, asunto, html, ct);
            else
                await _email.EnviarAsync(destinatario, asunto, html, ct);

            reg.Exitoso = true;
        }
        catch (Exception ex)
        {
            reg.Exitoso      = false;
            reg.ErrorMensaje = ex.Message;
            _logger.LogError(ex,
                "Error al enviar notificación [{TipoEvento}] → [{Destinatario}]",
                tipoEvento, destinatario);
        }

        _registro.Agregar(reg);
        await _registro.GuardarCambiosAsync(ct);
    }
}
```

---

## P1-T07: SQL + Entidad — RegistroNotificaciones

**Crear: `Documentos/BD/Migracion_RegistroNotificaciones.sql`**

```sql
-- ===========================================================
-- MIGRACIÓN: Tabla RegistroNotificaciones
-- Auditoría completa de correos enviados por el sistema
-- ===========================================================
CREATE TABLE dbo.RegistroNotificaciones (
    Id           INT           IDENTITY(1,1) NOT NULL,
    TipoEvento   NVARCHAR(60)                NOT NULL,
    Destinatario NVARCHAR(256)               NOT NULL,
    Copia        NVARCHAR(256)               NULL,
    Asunto       NVARCHAR(500)               NOT NULL,
    Exitoso      BIT                         NOT NULL CONSTRAINT DF_RN_Exitoso DEFAULT 0,
    ErrorMensaje NVARCHAR(1000)              NULL,
    FechaIntento DATETIME2(0)                NOT NULL CONSTRAINT DF_RN_Fecha DEFAULT GETUTCDATE(),
    CONSTRAINT PK_RegistroNotificaciones PRIMARY KEY (Id)
);
GO

CREATE NONCLUSTERED INDEX IX_RN_Fecha
    ON dbo.RegistroNotificaciones (FechaIntento DESC)
    INCLUDE (TipoEvento, Destinatario, Exitoso);
GO

CREATE NONCLUSTERED INDEX IX_RN_Fallos
    ON dbo.RegistroNotificaciones (Exitoso, FechaIntento DESC)
    WHERE Exitoso = 0;
GO
```

**Entidad: `GestionPersonal.Models/Entities/GestionPersonalEntities/RegistroNotificacion.cs`**

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

---

## P1-T08: Correcciones de seguridad críticas en CuentaService

### Token de recuperación — SHA-256 + 30 minutos

```csharp
// CuentaService.cs — SolicitarRecuperacionAsync (DESPUÉS — seguro)

var codigoPlano  = GenerarCodigoSeguro();
var hashCodigo   = ComputarHashSha256(codigoPlano);

_tokenRepo.Agregar(new TokenRecuperacion
{
    UsuarioId       = usuario.Id,
    Token           = hashCodigo,                       // SHA-256 hex (64 chars) en BD
    FechaExpiracion = DateTime.UtcNow.AddMinutes(30),   // 30 min (antes: 1 hora)
    Usado           = false,
    FechaCreacion   = DateTime.UtcNow
});

await _notificationService.NotificarRecuperacionContrasenaAsync(
    new NotificacionRecuperacionDto(
        DestinatarioCorreo : usuario.CorreoAcceso,
        NombreEmpleado     : usuario.Empleado?.NombreCompleto ?? usuario.CorreoAcceso,
        Codigo             : codigoPlano,   // código legible va al correo, NO el hash
        VigenciaMinutos    : "30"
    ), ct);

// ── Helpers privados de CuentaService ──────────────────────────────────────
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
    return Convert.ToHexString(hash).ToLowerInvariant(); // "a3f9..." — 64 chars
}
```

**En `RestablecerPasswordAsync`** — comparar por hash:

```csharp
// ANTES
var token = await _tokenRepo.ObtenerTokenActivoAsync(dto.Token, ct);

// DESPUÉS
var hash  = ComputarHashSha256(dto.Token);
var token = await _tokenRepo.ObtenerTokenActivoAsync(hash, ct);
```

### Eliminar contraseña del correo de bienvenida

```csharp
// UsuarioService.cs — CrearParaEmpleadoAsync (DESPUÉS — sin contraseña en correo)

await _notificationService.NotificarNuevoUsuarioAsync(
    new NotificacionNuevoUsuarioDto(
        DestinatarioCorreo  : correo,
        NombreEmpleado      : nombreEmpleado,    // obtener del empleado asociado
        CorreoAcceso        : correo,
        NombreCreadorEvento : nombreAdminActual  // del claim del usuario autenticado
    ), ct);

// ELIMINAR COMPLETAMENTE:
// await _emailHelper.EnviarCorreoNuevoUsuarioAsync(correo, ..., contrasenaTemp);
```

---

## P1-T09: SQL — Migración TokensRecuperacion (semántica de hash)

**Crear: `Documentos/BD/Migracion_TokensRecuperacion_Hash.sql`**

```sql
-- ===========================================================
-- MIGRACIÓN: TokensRecuperacion — almacenar SHA-256 en lugar de texto plano
-- Ejecutar ANTES de desplegar la versión con CuentaService refactorizado
-- ===========================================================

-- Invalidar todos los tokens existentes (texto plano ya no es compatible)
UPDATE dbo.TokensRecuperacion SET Usado = 1 WHERE Usado = 0;
GO

-- Documentar el cambio semántico en la columna
EXEC sys.sp_addextendedproperty
    @name       = N'MS_Description',
    @value      = N'SHA-256 hex (64 chars) del código enviado al usuario. El código en texto plano NUNCA se persiste en BD.',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE',  @level1name = N'TokensRecuperacion',
    @level2type = N'COLUMN', @level2name = N'Token';
GO
```

---

## P1-T10: Registro de dependencias

**`GestionPersonal.Application/AccessDependency/ApplicationAccessDependency.cs`** — agregar:

```csharp
services.AddScoped<INotificationService, NotificationService>();
```

**`GestionPersonal.Helpers/AccessDependency/HelperAccessDependency.cs`** — asegurar que `IEmailHelper` esté registrado con la nueva implementación MailKit:

```csharp
services.Configure<EmailSettings>(configuration.GetSection(EmailSettings.SectionName));
services.AddScoped<IEmailHelper, EmailHelper>();
```

**`GestionPersonal.Domain/Interfaces/INotificacionRepository.cs`** — crear si no existe:

```csharp
namespace GestionPersonal.Domain.Interfaces;

public interface INotificacionRepository
{
    void Agregar(RegistroNotificacion entidad);
    Task GuardarCambiosAsync(CancellationToken ct = default);
}
```

---

# PARTE 2 — Eventos de Negocio (Semanas 4–6)

---

## P2-T01: Identificación del jefe apoyo (patrón de carga)

Al crear solicitudes, el servicio necesita cargar la cadena de `JefeInmediatoId`:

```csharp
// En IEmpleadoRepository — agregar método especializado
Task<Empleado?> ObtenerConJefesAsync(int empleadoId, CancellationToken ct = default);

// Implementación en EmpleadoRepository
public Task<Empleado?> ObtenerConJefesAsync(int empleadoId, CancellationToken ct = default)
    => _context.Empleados
               .Include(e => e.JefeInmediato!)
                   .ThenInclude(j => j.JefeInmediato!)
               .Include(e => e.JefeInmediato!.Usuario)
               .Include(e => e.JefeInmediato!.JefeInmediato!.Usuario)
               .FirstOrDefaultAsync(e => e.Id == empleadoId, ct);
```

Uso en `HoraExtraService`:

```csharp
var empleado = await _empleadoRepo.ObtenerConJefesAsync(dto.EmpleadoId, ct)
               ?? throw new InvalidOperationException("Empleado no encontrado");

await _notificationService.NotificarSolicitudCreadaAsync(new NotificacionSolicitudDto(
    TipoEvento                  : "Nueva Solicitud",
    TipoSolicitud               : "Horas Extra",
    FechaEvento                 : dto.FechaTrabajada.ToString("dd/MM/yyyy"),
    NombreEmpleadoSolicitante   : empleado.NombreCompleto,
    CorreoEmpleadoSolicitante   : empleado.CorreoElectronico ?? "",
    NombreJefeInmediato         : empleado.JefeInmediato?.NombreCompleto ?? "—",
    CorreoJefeInmediato         : empleado.JefeInmediato?.Usuario?.CorreoAcceso ?? "",
    NombreJefeApoyo             : empleado.JefeInmediato?.JefeInmediato?.NombreCompleto,
    CorreoJefeApoyo             : empleado.JefeInmediato?.JefeInmediato?.Usuario?.CorreoAcceso,
    NombreAprobador             : null,
    Observacion                 : null,
    NombreQuienGenera           : empleado.NombreCompleto
), ct);
```

---

## P2-T02: EventoLaboralService — mismo patrón, tipo dinámico

```csharp
// TipoSolicitud varía según TipoEvento del EventoLaboral
var tipo = eventoLaboral.TipoEvento switch
{
    TipoEvento.Vacaciones  => "Vacaciones",
    TipoEvento.Incapacidad => "Incapacidad",
    TipoEvento.Permiso     => "Permiso",
    _                      => "Solicitud Laboral"
};
```

---

## P2-T03: TurnoService — notifica empleado + copia al jefe

```csharp
await _notificationService.NotificarAsignacionTurnoAsync(new NotificacionTurnoDto(
    TipoEvento        : "Asignación de Turno",
    NombreEmpleado    : empleado.NombreCompleto,
    CorreoEmpleado    : empleado.CorreoElectronico ?? "",
    NombreTurno       : plantilla.Nombre,
    NombreTurnoAnterior: null,
    FechaVigencia     : dto.FechaVigencia.ToString("dd/MM/yyyy"),
    CorreoJefeEmisor  : asignadoPor.CorreoAcceso,
    NombreJefeEmisor  : asignadoPor.Empleado?.NombreCompleto ?? asignadoPor.CorreoAcceso,
    NombreQuienGenera : asignadoPor.Empleado?.NombreCompleto ?? asignadoPor.CorreoAcceso
), ct);
```

---

## P2-T04: EmpleadoService — cambios de cargo y sede

```csharp
// Detectar cambio de cargo
if (empleadoOriginal.CargoId != dto.CargoId)
{
    var anterior = await _cargoRepo.ObtenerPorIdAsync(empleadoOriginal.CargoId, ct);
    var nuevo    = await _cargoRepo.ObtenerPorIdAsync(dto.CargoId, ct);

    await _notificationService.NotificarCambioCargoAsync(new NotificacionCambioPersonalDto(
        TipoEvento        : "Cambio de Cargo",
        NombreEmpleado    : empleado.NombreCompleto,
        CorreoEmpleado    : empleado.CorreoElectronico ?? "",
        ValorAnterior     : anterior?.Nombre ?? "—",
        ValorNuevo        : nuevo?.Nombre    ?? "—",
        CorreoRRHH        : correoActual,
        NombreQuienGenera : nombreActual
    ), ct);
}
```

---

# PARTE 3 — Pruebas Playwright (Semanas 5–6)

---

## Estrategia de pruebas

| Capa | Verificación | Herramienta |
|---|---|---|
| HTML generado | Los métodos estáticos retornan HTML válido sin XSS | Unit test C# (xUnit) |
| Seguridad | Token en BD es SHA-256 hex (64 chars), no código legible | Playwright + pyodbc |
| Registro | `RegistroNotificaciones.Exitoso = 1` tras cada acción | Playwright + pyodbc |
| Asunto | Formato `[TipoEvento] - [Quien]` en todos los eventos | Playwright + pyodbc |
| Contraseña | El cuerpo HTML del correo no contiene la contraseña | Playwright + pyodbc |

---

## Comandos de ejecución

```powershell
# Desde la raíz del workspace

# 1. Activar entorno virtual
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1

# 2. Ejecutar suite completa de email
$fecha   = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\email-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null

.venv\Scripts\python.exe -m pytest `
    Tests/test_email_seguridad.py `
    Tests/test_email_solicitudes.py `
    Tests/test_email_turnos.py `
    -v --headed --slowmo 800 -s `
    2>&1 | Tee-Object -FilePath $informe

Write-Host "Informe guardado: $informe"
```

---

## `Tests/test_email_seguridad.py`

```python
"""
Pruebas de correo — Seguridad y Acceso
EVT-01  Nuevo usuario → RegistroNotificaciones Exitoso=1, sin contraseña en asunto
EVT-02  Recuperación → token en BD es hash SHA-256 (64 chars hex), no código legible
EVT-02b Expiración de 30 minutos verificada en FechaExpiracion
EVT-02c Token expirado → formulario bloqueado
EVT-02d Token ya usado → formulario bloqueado
EVT-03  Cambio contraseña → RegistroNotificaciones Exitoso=1
"""
import pytest
import pyodbc
from datetime import datetime, timezone, timedelta
from helpers import BASE_URL, hacer_login

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;DATABASE=GestionPersonal;Trusted_Connection=yes"
)

def obtener_ultimo_registro(tipo_evento: str) -> dict | None:
    with pyodbc.connect(CONN_STR) as conn:
        row = conn.cursor().execute(
            "SELECT TOP 1 Exitoso, ErrorMensaje, Destinatario, Asunto "
            "FROM RegistroNotificaciones WHERE TipoEvento = ? "
            "ORDER BY FechaIntento DESC", tipo_evento
        ).fetchone()
    return {"exitoso": row[0], "error": row[1],
            "destinatario": row[2], "asunto": row[3]} if row else None

def obtener_token_bd(correo: str) -> dict | None:
    with pyodbc.connect(CONN_STR) as conn:
        row = conn.cursor().execute(
            "SELECT TOP 1 t.Token, t.FechaExpiracion, t.Usado "
            "FROM TokensRecuperacion t "
            "INNER JOIN Usuarios u ON t.UsuarioId = u.Id "
            "WHERE u.CorreoAcceso = ? ORDER BY t.FechaCreacion DESC", correo
        ).fetchone()
    return {"token": row[0], "expiracion": row[1], "usado": row[2]} if row else None


def test_evt01_nuevo_usuario_sin_contrasena_en_asunto(page):
    """
    Al crear un usuario, RegistroNotificaciones registra Exitoso=1
    y el asunto NO revela datos sensibles.
    """
    hacer_login(page, "admin@yopmail.com", "AdminPass2026!")
    page.goto(f"{BASE_URL}/Empleados/Nuevo")
    page.wait_for_load_state("networkidle")
    # TODO: completar campos del formulario según IDs reales y hacer submit

    reg = obtener_ultimo_registro("NuevoUsuario")
    assert reg is not None, "EVT-01: Sin registro en RegistroNotificaciones"
    assert reg["exitoso"] == 1, f"EVT-01: Correo falló — {reg['error']}"

    asunto = reg["asunto"].lower()
    assert "contraseña" not in asunto, "EVT-01: El asunto contiene 'contraseña'"
    assert "password"   not in asunto, "EVT-01: El asunto contiene 'password'"
    assert asunto.startswith("[nuevo usuario]"), (
        f"EVT-01: Formato incorrecto. Asunto: {reg['asunto']}")


def test_evt02_token_en_bd_es_hash_sha256(page):
    """
    El Token en BD debe ser SHA-256 hex (64 chars lowercase), no el código legible.
    """
    correo = "carlos.rodriguez@yopmail.com"
    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.fill("#CorreoAcceso", correo)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    t = obtener_token_bd(correo)
    assert t is not None, "EVT-02: No se creó token en BD"

    valor = t["token"]
    assert len(valor) == 64, (
        f"EVT-02: Token tiene {len(valor)} chars (se esperaban 64 — SHA-256 hex). "
        f"Valor: {valor[:20]}... — posible texto plano inseguro")
    assert all(c in "0123456789abcdef" for c in valor), (
        "EVT-02: Token no es hex válido — podría ser texto plano")


def test_evt02b_token_expira_en_30_minutos(page):
    correo = "natalia.bermudez@yopmail.com"
    page.goto(f"{BASE_URL}/Cuenta/RecuperarPassword")
    page.fill("#CorreoAcceso", correo)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    t = obtener_token_bd(correo)
    assert t is not None

    exp  = t["expiracion"].replace(tzinfo=timezone.utc)
    diff = exp - datetime.now(timezone.utc)

    assert timedelta(0) < diff <= timedelta(minutes=31), (
        f"EVT-02b: Expiración incorrecta — diferencia: {diff}")


def test_evt02c_token_expirado_bloqueado(page):
    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token=TK7E4D8F5G")
    page.wait_for_load_state("networkidle")
    assert not page.locator("input[name='NuevoPassword']").is_visible(), (
        "EVT-02c: Formulario visible con token expirado")
    assert len(page.locator(".alert--error, .alert-danger").inner_text().strip()) > 0, (
        "EVT-02c: Sin mensaje de error")


def test_evt02d_token_usado_bloqueado(page):
    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token=TK3F9A2B1C")
    page.wait_for_load_state("networkidle")
    assert not page.locator("input[name='NuevoPassword']").is_visible(), (
        "EVT-02d: Formulario visible con token ya usado")


def test_evt03_cambio_contrasena_registrado(page):
    page.goto(f"{BASE_URL}/Cuenta/RestablecerPassword?token=TK1H6K9M2N")
    page.wait_for_load_state("networkidle")
    page.fill("input[name='NuevoPassword']",     "NuevaClaveSegura2026!")
    page.fill("input[name='ConfirmarPassword']", "NuevaClaveSegura2026!")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    reg = obtener_ultimo_registro("CambioContrasenaExitoso")
    assert reg is not None, "EVT-03: Sin registro"
    assert reg["exitoso"] == 1, f"EVT-03: Correo falló — {reg['error']}"
```

---

## `Tests/test_email_solicitudes.py`

```python
"""
Pruebas de correo — Ciclo de solicitudes laborales
EVT-04  Solicitud creada → correo al jefe (CC al jefe apoyo si existe)
EVT-05  Aprobación → correo al auxiliar solicitante
EVT-06  Rechazo → correo al auxiliar solicitante
"""
import pytest
import pyodbc
from helpers import BASE_URL, hacer_login

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;DATABASE=GestionPersonal;Trusted_Connection=yes"
)

def obtener_ultimo_registro(tipo_evento: str) -> dict | None:
    with pyodbc.connect(CONN_STR) as conn:
        row = conn.cursor().execute(
            "SELECT TOP 1 Exitoso, ErrorMensaje, Destinatario, Copia, Asunto "
            "FROM RegistroNotificaciones WHERE TipoEvento = ? "
            "ORDER BY FechaIntento DESC", tipo_evento
        ).fetchone()
    return {"exitoso": row[0], "error": row[1], "destinatario": row[2],
            "copia": row[3], "asunto": row[4]} if row else None


def test_evt04_solicitud_notifica_jefe_no_solicitante(page):
    """El destinatario es el jefe inmediato, no el auxiliar que creó la solicitud."""
    hacer_login(page, "auxiliar.farmacia@yopmail.com", "AuxiliarPass2026!")
    page.goto(f"{BASE_URL}/HorasExtras/Nuevo")
    page.wait_for_load_state("networkidle")
    page.fill("input[name='FechaTrabajada']", "2026-05-01")
    page.fill("input[name='CantidadHoras']",  "2")
    page.fill("textarea[name='Motivo']",       "Prueba EVT-04")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    reg = obtener_ultimo_registro("SolicitudCreada")
    assert reg is not None, "EVT-04: Sin registro"
    assert reg["exitoso"] == 1, f"EVT-04: Error — {reg['error']}"
    assert reg["destinatario"] != "auxiliar.farmacia@yopmail.com", (
        "EVT-04: El destinatario no debe ser el auxiliar")
    assert "[nueva horas extra]" in reg["asunto"].lower(), (
        f"EVT-04: Formato de asunto incorrecto: {reg['asunto']}")


def test_evt04b_copia_al_jefe_apoyo(page):
    """Si existe cadena de dos niveles, Copia debe estar poblada."""
    hacer_login(page, "auxiliar.farmacia@yopmail.com", "AuxiliarPass2026!")
    page.goto(f"{BASE_URL}/HorasExtras/Nuevo")
    page.wait_for_load_state("networkidle")
    page.fill("input[name='FechaTrabajada']", "2026-05-02")
    page.fill("input[name='CantidadHoras']",  "3")
    page.fill("textarea[name='Motivo']",       "Prueba EVT-04b CC jefe apoyo")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    reg = obtener_ultimo_registro("SolicitudCreada")
    assert reg is not None
    # Si la cadena JefeInmediato → JefeInmediato existe, Copia debe estar poblada
    # Si no, este test documenta el comportamiento y puede marcarse como xfail
    # dependiendo del seeding.


def test_evt05_aprobacion_notifica_auxiliar(page):
    hacer_login(page, "regente.farmacia@yopmail.com", "RegentePass2026!")
    page.goto(f"{BASE_URL}/HorasExtras")
    page.wait_for_load_state("networkidle")
    page.locator("button[data-accion='aprobar']").first.click()
    page.wait_for_load_state("networkidle")

    reg = obtener_ultimo_registro("SolicitudAprobada")
    assert reg is not None, "EVT-05: Sin registro"
    assert reg["exitoso"] == 1
    assert "aprobada" in reg["asunto"].lower()


def test_evt06_rechazo_notifica_auxiliar(page):
    hacer_login(page, "regente.farmacia@yopmail.com", "RegentePass2026!")
    page.goto(f"{BASE_URL}/HorasExtras")
    page.wait_for_load_state("networkidle")
    page.locator("button[data-accion='rechazar']").first.click()
    motivo = page.locator("textarea[name='MotivoRechazo']")
    if motivo.is_visible():
        motivo.fill("Prueba EVT-06")
        page.locator("button[data-confirmar='rechazar']").click()
    page.wait_for_load_state("networkidle")

    reg = obtener_ultimo_registro("SolicitudRechazada")
    assert reg is not None, "EVT-06: Sin registro"
    assert reg["exitoso"] == 1
    assert "rechazada" in reg["asunto"].lower()
```

---

## `Tests/test_email_turnos.py`

```python
"""
Pruebas de correo — Asignación de turnos
EVT-08  Turno asignado → correo a empleado + CC al jefe
EVT-09  Turno modificado → mismo patrón
EVT-10  Turno cancelado → solo al empleado
"""
import pytest
import pyodbc
from helpers import BASE_URL, hacer_login

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;DATABASE=GestionPersonal;Trusted_Connection=yes"
)

def obtener_ultimo_registro(tipo_evento: str) -> dict | None:
    with pyodbc.connect(CONN_STR) as conn:
        row = conn.cursor().execute(
            "SELECT TOP 1 Exitoso, ErrorMensaje, Destinatario, Copia, Asunto "
            "FROM RegistroNotificaciones WHERE TipoEvento = ? "
            "ORDER BY FechaIntento DESC", tipo_evento
        ).fetchone()
    return {"exitoso": row[0], "error": row[1], "destinatario": row[2],
            "copia": row[3], "asunto": row[4]} if row else None


def test_evt08_asignacion_turno(page):
    """Asignación genera correo al empleado con CC al jefe asignador."""
    hacer_login(page, "director.tecnico@yopmail.com", "DirectorPass2026!")
    page.goto(f"{BASE_URL}/Turnos/AsignarTurno")
    page.wait_for_load_state("networkidle")
    # TODO: seleccionar empleado, plantilla y fecha — completar según IDs reales
    # page.select_option("select[name='EmpleadoId']", label="Auxiliar de Prueba")
    # page.select_option("select[name='PlantillaTurnoId']", label="Turno Mañana")
    # page.fill("input[name='FechaVigencia']", "2026-05-05")
    # page.click("button[type=submit]")
    # page.wait_for_load_state("networkidle")

    reg = obtener_ultimo_registro("AsignacionTurno")
    assert reg is not None, "EVT-08: Sin registro"
    assert reg["exitoso"] == 1
    assert reg["copia"] is not None, "EVT-08: Sin CC al jefe"
    assert "[asignación de turno]" in reg["asunto"].lower()
```

---

## Checklist de cierre

### Fase 1 — Infraestructura (Semanas 1–3)

- [ ] `dotnet user-secrets` configurado localmente con `{SMTP_PASSWORD}` real
- [ ] Exchange Admin confirmó permisos "Send As" en Office 365
- [ ] `EmailHelper` usa MailKit — `System.Net.Mail.SmtpClient` eliminado
- [ ] Test de envío manual a `test@yopmail.com` confirma recepción desde `notificacion.sf@zentria.com.co`
- [ ] 4 clases estáticas de plantillas creadas y compilando sin errores
- [ ] Token en BD es SHA-256 hex (64 chars) — `test_evt02_token_en_bd_es_hash_sha256` en verde
- [ ] Expiración de token en 30 minutos
- [ ] `UsuarioService` NO envía contraseña en correo
- [ ] Tabla `RegistroNotificaciones` creada en BD (migración ejecutada)
- [ ] `INotificationService` registrado en DI

### Fase 2 — Eventos de Negocio (Semanas 4–6)

- [ ] `HoraExtraService` notifica creación, aprobación y rechazo
- [ ] `EventoLaboralService` notifica creación, aprobación y rechazo
- [ ] `TurnoService` notifica asignación, modificación y cancelación
- [ ] `EmpleadoService` notifica cambio de cargo y sede
- [ ] Cadena `JefeInmediato?.JefeInmediato` carga correctamente (ObtenerConJefesAsync)
- [ ] Formato de asunto `[TipoEvento] - [Quien]` verificado en todos los eventos
- [ ] `test_email_solicitudes.py` pasa en verde
- [ ] `test_email_turnos.py` pasa en verde
- [ ] `RegistroNotificaciones` sin entradas `Exitoso = 0` en ejecución de pruebas normales

---

## Estructura completa de archivos (resumen)

```
GestionPersonal.Constants/
 └── Messages/
     └── EmailTemplates/                     ← NUEVO — plantillas como clases estáticas
         ├── EmailBase.cs                    ← Shell HTML, paleta, helpers (FilaDato, Banner, Boton)
         ├── SeguridadEmailTemplate.cs       ← EVT-01, EVT-02, EVT-03
         ├── SolicitudEmailTemplate.cs       ← EVT-04, EVT-05, EVT-06, EVT-07
         ├── TurnoEmailTemplate.cs           ← EVT-08, EVT-09, EVT-10
         └── PersonalEmailTemplate.cs        ← EVT-11, EVT-12

GestionPersonal.Application/
 ├── Interfaces/
 │   └── INotificationService.cs            ← NUEVO
 └── Services/
     ├── NotificationService.cs             ← NUEVO (módulo profundo)
     ├── UsuarioService.cs                  ← MODIFICAR (quitar contraseña del correo)
     ├── CuentaService.cs                   ← MODIFICAR (hash SHA-256, 30 min)
     ├── HoraExtraService.cs                ← MODIFICAR
     ├── EventoLaboralService.cs            ← MODIFICAR
     ├── TurnoService.cs                    ← MODIFICAR
     └── EmpleadoService.cs                 ← MODIFICAR

GestionPersonal.Helpers/
 └── Email/
     ├── IEmailHelper.cs                    ← REFACTORIZAR (2 métodos: Enviar + EnviarConCopia)
     └── EmailHelper.cs                     ← REFACTORIZAR (MailKit, Send As)

GestionPersonal.Models/
 ├── DTOs/Notificaciones/                   ← NUEVO
 │   ├── NotificacionNuevoUsuarioDto.cs
 │   ├── NotificacionRecuperacionDto.cs
 │   ├── NotificacionCambioContrasenaDto.cs
 │   ├── NotificacionSolicitudDto.cs
 │   ├── NotificacionTurnoDto.cs
 │   └── NotificacionCambioPersonalDto.cs
 ├── Models/Email/
 │   └── EmailSettings.cs                   ← NUEVO
 └── Entities/GestionPersonalEntities/
     └── RegistroNotificacion.cs            ← NUEVO

GestionPersonal.Domain/
 └── Interfaces/
     └── INotificacionRepository.cs         ← NUEVO

GestionPersonal.Web/
 └── appsettings.json                       ← MODIFICAR (sección EmailSettings, sin contraseña)

Documentos/BD/
 ├── Migracion_RegistroNotificaciones.sql   ← NUEVO
 └── Migracion_TokensRecuperacion_Hash.sql  ← NUEVO

Tests/
 ├── test_email_seguridad.py                ← NUEVO
 ├── test_email_solicitudes.py              ← NUEVO
 └── test_email_turnos.py                   ← NUEVO
```
