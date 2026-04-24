# Pitch — Capa de Mensajería y Notificaciones
**Sistema de Gestión de Personal · Shape Up Pitch**
Autor: Equipo backend · Fecha: Abril 2026

---

## 1. Problema

### Contexto actual

El sistema ya tiene una implementación inicial de correos (`IEmailHelper`) que cubre dos casos de uso puntuales: envío de contraseña temporal al crear un usuario y envío de un código de recuperación de contraseña.

Sin embargo, a medida que el sistema crece, se detecta una brecha estructural importante:

> **Ningún evento de negocio — solicitudes, cambios de horario, aprobaciones, novedades de personal — genera notificación al usuario afectado ni al responsable de aprobarlo.**

Esto produce fricciones concretas:

- Un auxiliar registra una solicitud y no sabe si alguien la recibió.
- Un jefe aprueba un evento y el empleado no se entera hasta que lo consulta manualmente.
- El equipo de RRHH asigna un horario y el empleado lo descubre el mismo día del turno.
- Un token de recuperación de contraseña no expira, ni se invalida al usarse: cualquier enlace es válido indefinidamente.

### Deuda técnica detectada

| Problema | Archivo afectado |
|---|---|
| `System.Net.Mail.SmtpClient` está obsoleto desde .NET 5 | `EmailHelper.cs` |
| Contraseña temporal enviada en texto plano por correo | `UsuarioService.cs`, `EmailHelper.cs` |
| Token de recuperación sin expiración ni uso único controlado | `CuentaService.cs` |
| Sin `INotificationService`: cada servicio llama email directamente | `UsuarioService.cs`, `CuentaService.cs` |
| Sin plantillas parametrizadas ni versionadas | — |
| Sin registro de correos enviados ni trazabilidad de notificaciones | — |

---

## 2. Apetito

**6 semanas — Ciclo completo (Large Batch)**

El trabajo se divide en dos fases internas de 3 semanas cada una. Si alguna parte excede su bloque de tiempo, se recorta el alcance, **no se extiende el tiempo**.

| Fase | Alcance | Semanas |
|---|---|---|
| **Fase 1** — Infraestructura + Seguridad | Migrar a MailKit, diseñar `INotificationService`, corregir token de recuperación, plantillas en HTML, envío asíncrono | 1–3 |
| **Fase 2** — Eventos de negocio | Notificaciones de solicitudes, horarios y aprobaciones. Auditoría de envíos | 4–6 |

### Lo que NO entra en este ciclo (ver §5 No-Gos)

- SMS, WhatsApp, notificaciones push
- Panel de administración de plantillas
- Preferencias de notificación por usuario
- Correos de cumpleaños o contratos próximos a vencer

---

## 3. Solución

### 3.1 Arquitectura propuesta

La solución introduce una capa de abstracción limpia entre los servicios de negocio y el canal de entrega. Ningún servicio de aplicación llama directamente a `IEmailHelper`.

```
Application Layer
  ├── EventoLaboralService  ──┐
  ├── TurnoService           ├──► INotificationService (Application/Interfaces)
  ├── CuentaService          ┘        │
                                       ▼
                              NotificationService (Application/Services)
                                 ├── IEmailHelper (Helpers)
                                 ├── ITemplateHelper (Helpers)
                                 └── IAuditService (Application/Interfaces)
```

### 3.2 Contratos de interfaz

**`INotificationService`** — punto único de entrada para toda notificación del sistema:

```csharp
// GestionPersonal.Application/Interfaces/INotificationService.cs
public interface INotificationService
{
    // Seguridad
    Task NotificarNuevoUsuarioAsync(string destinatario, string nombreCompleto, string correoAcceso);
    Task NotificarRecuperacionContrasenaAsync(string destinatario, string nombreCompleto, string urlToken);
    Task NotificarCambioContrasenaExitosoAsync(string destinatario, string nombreCompleto);

    // Solicitudes
    Task NotificarSolicitudCreadaAsync(NotificacionSolicitudDto datos);
    Task NotificarSolicitudAprobadaAsync(NotificacionSolicitudDto datos);
    Task NotificarSolicitudRechazadaAsync(NotificacionSolicitudDto datos);
    Task NotificarSolicitudDevueltaAsync(NotificacionSolicitudDto datos);

    // Horarios / Turnos
    Task NotificarAsignacionTurnoAsync(NotificacionTurnoDto datos);
    Task NotificarModificacionTurnoAsync(NotificacionTurnoDto datos);
    Task NotificarCancelacionTurnoAsync(NotificacionTurnoDto datos);

    // Personal
    Task NotificarCambioCargoAsync(NotificacionCambioPersonalDto datos);
    Task NotificarCambioSedeAsync(NotificacionCambioPersonalDto datos);
}
```

**`IEmailHelper`** — refactorizado para usar MailKit, sin detalles de negocio:

```csharp
// GestionPersonal.Helpers/Email/IEmailHelper.cs
public interface IEmailHelper
{
    Task EnviarAsync(string destinatario, string asunto, string cuerpoHtml);
    Task EnviarConCopiaAsync(string destinatario, string copia, string asunto, string cuerpoHtml);
}
```

**`ITemplateHelper`** — renderiza plantillas HTML con parámetros nombrados:

```csharp
// GestionPersonal.Helpers/Email/ITemplateHelper.cs
public interface ITemplateHelper
{
    string Renderizar(string nombrePlantilla, Dictionary<string, string> parametros);
}
```

### 3.3 DTOs de notificación

```csharp
// GestionPersonal.Models/DTOs/Notificaciones/
public record NotificacionSolicitudDto(
    string NombreEmpleado,
    string TipoSolicitud,
    string FechaSolicitud,
    string NombreJefeInmediato,
    string CorreoJefeInmediato,
    string? CorreoJefeApoyo,
    string? NombreAprobador,
    string? Observacion
);

public record NotificacionTurnoDto(
    string NombreEmpleado,
    string CorreoEmpleado,
    string FechaTurno,
    string NombreTurno,
    string CorreoJefeEmisor
);

public record NotificacionCambioPersonalDto(
    string NombreEmpleado,
    string CorreoEmpleado,
    string ValorAnterior,
    string ValorNuevo,
    string CorreoRRHH
);
```

### 3.4 Flujo de recuperación de contraseña (corregido)

El flujo actual no invalida tokens usados y no tiene expiración controlada. El flujo corregido es:

```
[1] POST /Cuenta/RecuperarContrasena
        │
        ▼
[2] Generar token = RandomNumberGenerator.GetHexString(64)
    Hash del token = SHA-256(token)
    Guardar en BD: HashToken, FechaExpiracion = UtcNow + 30min, Usado = false
        │
        ▼
[3] INotificationService.NotificarRecuperacionContrasenaAsync(
        correo, nombre, $"{baseUrl}/Cuenta/RestablecerContrasena?token={token}")
        │
        ▼
[4] GET /Cuenta/RestablecerContrasena?token={token}
    - Buscar por SHA-256(token)
    - Validar: existe && !Usado && FechaExpiracion > UtcNow
    - Si válido → formulario nueva contraseña
    - Si inválido → mensaje específico (vencido / usado / inválido)
        │
        ▼
[5] POST /Cuenta/RestablecerContrasena
    - Actualizar PasswordHash + Salt
    - Marcar token como Usado = true
    - INotificationService.NotificarCambioContrasenaExitosoAsync(...)
```

**Reglas de seguridad:**
- El token en texto plano **nunca** se guarda en base de datos.
- La URL contiene el token en plano; en BD solo existe su hash SHA-256.
- Expiración máxima: **30 minutos** desde generación.
- Uso único estricto: el campo `Usado` se marca `true` al validar el formulario, antes de actualizar la contraseña.

### 3.5 Plantillas HTML

Las plantillas se almacenan como archivos `.html` en `GestionPersonal.Web/EmailTemplates/`. `ITemplateHelper` las lee por nombre y reemplaza marcadores `{{VARIABLE}}`.

```
GestionPersonal.Web/
└── EmailTemplates/
    ├── NuevoUsuario.html
    ├── RecuperacionContrasena.html
    ├── CambioContrasenaExitoso.html
    ├── SolicitudCreada_Jefe.html
    ├── SolicitudAprobada_Empleado.html
    ├── SolicitudRechazada_Empleado.html
    ├── AsignacionTurno_Empleado.html
    └── CambioPersonal_Empleado.html
```

Variables disponibles: `{{NOMBRE_EMPLEADO}}`, `{{TIPO_SOLICITUD}}`, `{{FECHA}}`, `{{APROBADOR}}`, `{{OBSERVACION}}`, `{{URL_TOKEN}}`, `{{VIGENCIA_TOKEN}}`.

### 3.6 Envío asíncrono (sin cola externa)

Para este ciclo se usa `Task.Run` con manejo de errores y log estructurado. No se introduce Hangfire ni Worker Service (ver §4 Agujeros del conejo). El servicio registra cada intento en una tabla `RegistroNotificaciones`.

```csharp
// NotificationService.cs
private async Task EnviarConRegistroAsync(
    string destinatario, string asunto, string cuerpoHtml, string tipoEvento)
{
    var registro = new RegistroNotificacion
    {
        Destinatario = destinatario,
        Asunto       = asunto,
        TipoEvento   = tipoEvento,
        FechaIntento = DateTime.UtcNow
    };
    try
    {
        await _emailHelper.EnviarAsync(destinatario, asunto, cuerpoHtml);
        registro.Exitoso = true;
    }
    catch (Exception ex)
    {
        registro.Exitoso = false;
        registro.ErrorMensaje = ex.Message;
        _logger.LogError(ex, "Error al enviar notificación {TipoEvento} a {Destinatario}", tipoEvento, destinatario);
    }
    await _auditService.RegistrarNotificacionAsync(registro);
}
```

### 3.7 Tabla de destinatarios por evento

| Evento | Destinatario principal | Copia / CC |
|---|---|---|
| Nueva solicitud (auxiliar) | Jefe inmediato | Jefe apoyo (si existe) |
| Solicitud aprobada | Empleado solicitante | — |
| Solicitud rechazada | Empleado solicitante | — |
| Solicitud devuelta | Empleado solicitante | — |
| Turno asignado | Empleado | Jefe emisor (confirmación) |
| Turno modificado | Empleado | Jefe emisor (confirmación) |
| Turno cancelado | Empleado | — |
| Cambio de cargo | Empleado | Correo RRHH configurado |
| Cambio de sede | Empleado | Correo RRHH configurado |
| Nuevo usuario creado | Usuario nuevo | — |
| Recuperación de contraseña | Usuario solicitante | — |
| Cambio de contraseña exitoso | Usuario | — |

### 3.8 Migración de `EmailHelper` a MailKit

`System.Net.Mail.SmtpClient` se reemplaza por MailKit como parte de la Fase 1. La interfaz `IEmailHelper` no cambia para los consumidores. Solo la implementación interna en `EmailHelper.cs` se actualiza.

```xml
<!-- GestionPersonal.Helpers/GestionPersonal.Helpers.csproj -->
<PackageReference Include="MailKit" Version="4.*" />
<PackageReference Include="MimeKit" Version="4.*" />
```

**Nunca** se usa `new NetworkCredential(usuario, password)` hardcodeado. Las credenciales se leen desde `appsettings.json` con `dotnet user-secrets` en desarrollo y variables de entorno en producción.

---

## 4. Agujeros del conejo

Estas son las áreas donde el equipo puede perderse fácilmente. Se documentan para que no haya exploración abierta durante la ejecución.

### 4.1 Cola de mensajes (Hangfire / RabbitMQ / Azure Service Bus)
**No entra en este ciclo.** El envío asíncrono con `Task.Run` + log estructurado es suficiente para el volumen actual. Agregar una cola de mensajes distribuida triplica la complejidad de infraestructura sin beneficio real para el número de usuarios proyectado.

**Decisión fija:** Si un correo falla, queda registrado en `RegistroNotificaciones` con `Exitoso = false`. El administrador puede revisar y reenviar manualmente. No hay reintentos automáticos en v1.

### 4.2 Renderizado de plantillas con motor externo (Razor Engine, Fluid, Handlebars)
**No entra en este ciclo.** Las plantillas son archivos HTML estáticos con sustitución de `{{VARIABLE}}` por `string.Replace`. Un motor de templates agrega dependencias y complejidad de caché innecesaria para 8–10 plantillas estáticas.

**Decisión fija:** `ITemplateHelper` lee el archivo `.html` con `File.ReadAllTextAsync` y hace `Replace` secuencial. Si una plantilla necesita lógica condicional en el futuro, se evalúa en ese momento.

### 4.3 Múltiples proveedores de correo (Graph API, SendGrid, etc.)
**No entra en este ciclo.** La implementación SMTP con MailKit cubre los requisitos actuales. El contrato `IEmailHelper` permite cambiar el proveedor en el futuro sin modificar la capa de negocio.

**Decisión fija:** Proveedor SMTP (Office 365 / Gmail). No hay `IEmailProviderFactory` ni registro de múltiples providers.

### 4.4 Preferencias de notificación por usuario
**No entra en este ciclo.** Todos los eventos notifican siempre. No hay tabla `PreferenciasNotificacion` ni lógica de opt-in/opt-out.

### 4.5 Notificaciones en tiempo real (SignalR / WebSockets)
**No entra en este ciclo.** Las notificaciones internas in-app (badge de campana) son un feature independiente que requiere su propio pitch.

---

## 5. No-Goes

Los siguientes ítems están **explícitamente excluidos** de este ciclo. No se diseñan, no se codifican, no se discuten como parte de esta entrega.

| Excluido | Razón |
|---|---|
| SMS / WhatsApp | Requiere integración con terceros (Twilio / Meta). Pitch separado. |
| Notificaciones push (PWA / móvil) | No existe app móvil en el roadmap actual. |
| Panel WYSIWYG de edición de plantillas | Complejidad desproporcionada para el ciclo. |
| Preferencias de notificación por usuario | No hay demanda validada. Deja al equipo libre de enfocar. |
| Correos de cumpleaños, contratos por vencer | Nice-to-have. Requiere background jobs y lógica de calendario. |
| i18n / correos en múltiples idiomas | El sistema opera en español únicamente. |
| Confirmación de lectura de correo | Tracking de apertura es complejo y tiene implicaciones de privacidad. |
| Sistema de reintentos automáticos | El volumen no lo justifica. Se registra el error; reenvío manual. |
| Notificaciones de mantenimiento programado | Operación de infraestructura. No es responsabilidad de la capa de negocio. |

---

## 6. Checklist de validación antes de cerrar el ciclo

Antes de considerar la entrega completa, el equipo valida:

- [ ] `EmailHelper` usa MailKit; `System.Net.Mail.SmtpClient` eliminado del proyecto.
- [ ] Contraseñas temporales **no** se envían por correo en ningún flujo.
- [ ] Token de recuperación expira en ≤ 30 minutos y se invalida al usarse.
- [ ] Solo el hash SHA-256 del token se guarda en base de datos.
- [ ] `INotificationService` es el único punto de entrada a correos desde servicios de aplicación.
- [ ] `UsuarioService` y `CuentaService` usan `INotificationService`, no `IEmailHelper` directamente.
- [ ] Todos los correos enviados quedan en `RegistroNotificaciones` con estado y timestamp.
- [ ] Credenciales de SMTP no están en el código fuente ni en archivos comiteados.
- [ ] Las 8 plantillas HTML base están creadas y probadas manualmente.
- [ ] Regla "Solicitud auxiliar → Jefe inmediato + Jefe apoyo" está implementada y probada.

---

## Apéndice A — Mapa de eventos de negocio en scope

```
SEGURIDAD (Fase 1)
 ├── [EVT-01] Nuevo usuario creado           → Empleado
 ├── [EVT-02] Recuperación de contraseña     → Empleado
 └── [EVT-03] Cambio de contraseña exitoso   → Empleado

SOLICITUDES (Fase 2)
 ├── [EVT-04] Solicitud creada (auxiliar)    → Jefe inmediato + Jefe apoyo (CC)
 ├── [EVT-05] Solicitud aprobada             → Empleado solicitante
 ├── [EVT-06] Solicitud rechazada            → Empleado solicitante
 └── [EVT-07] Solicitud devuelta             → Empleado solicitante

HORARIOS / TURNOS (Fase 2)
 ├── [EVT-08] Turno asignado                 → Empleado + Jefe (confirmación)
 ├── [EVT-09] Turno modificado               → Empleado + Jefe (confirmación)
 └── [EVT-10] Turno cancelado                → Empleado

PERSONAL (Fase 2)
 ├── [EVT-11] Cambio de cargo                → Empleado + RRHH (CC)
 └── [EVT-12] Cambio de sede                 → Empleado + RRHH (CC)
```

**Total: 12 eventos en scope para este ciclo.**
Los eventos fuera de scope (incapacidades, vacaciones, cumpleaños, auditorías del sistema) se priorizan en el próximo ciclo o en un pitch independiente.

---

## Apéndice B — Estructura de archivos a crear o modificar

```
GestionPersonal.Application/
 ├── Interfaces/
 │   ├── INotificationService.cs              ← NUEVO
 │   └── IAuditService.cs (ampliar)           ← MODIFICAR
 └── Services/
     ├── NotificationService.cs               ← NUEVO
     ├── UsuarioService.cs                    ← MODIFICAR (usa INotificationService)
     └── CuentaService.cs                     ← MODIFICAR (flujo token corregido)

GestionPersonal.Helpers/
 └── Email/
     ├── IEmailHelper.cs                      ← REFACTORIZAR (simplificar contrato)
     ├── EmailHelper.cs                       ← REFACTORIZAR (MailKit)
     ├── ITemplateHelper.cs                   ← NUEVO
     └── TemplateHelper.cs                    ← NUEVO

GestionPersonal.Models/
 ├── DTOs/
 │   └── Notificaciones/
 │       ├── NotificacionSolicitudDto.cs      ← NUEVO
 │       ├── NotificacionTurnoDto.cs          ← NUEVO
 │       └── NotificacionCambioPersonalDto.cs ← NUEVO
 └── Entities/GestionPersonalEntities/
     └── RegistroNotificacion.cs              ← NUEVO

GestionPersonal.Web/
 └── EmailTemplates/
     ├── NuevoUsuario.html                    ← NUEVO
     ├── RecuperacionContrasena.html          ← NUEVO
     ├── CambioContrasenaExitoso.html         ← NUEVO
     ├── SolicitudCreada_Jefe.html            ← NUEVO
     ├── SolicitudAprobada_Empleado.html      ← NUEVO
     ├── SolicitudRechazada_Empleado.html     ← NUEVO
     ├── AsignacionTurno_Empleado.html        ← NUEVO
     └── CambioPersonal_Empleado.html         ← NUEVO
```
