# Pitch — Notificaciones por Cambio de Estado de Solicitud
## Sistema GestionPersonal · Módulo EventoLaboral + Correos

> **Metodología:** Shape Up (Basecamp) — https://basecamp.com/shapeup  
> **Ciclo:** Small Batch — 2 semanas  
> **Stack:** C# ASP.NET Core MVC / .NET 10 · `INotificationService` · `ISolicitudService` · `IEventoLaboralService`  
> **Fecha:** 26 de abril de 2026  
> **Depende de:** `Plan-AprobacionSolicitudes.md` (el flujo de aprobación debe estar implementado)  
> **Versión:** 1.1

---

## 1. Problema

El sistema tiene dos brechas de comunicación en el ciclo de vida de una solicitud:

**Brecha 1 — Creación de solicitud:** cuando un empleado genera una nueva solicitud, su jefe inmediato no recibe ningún aviso. Tiene que ingresar manualmente a `/EventoLaboral` para descubrir que existe trabajo pendiente de gestión. El empleado tampoco sabe si su jefe ya se enteró.

**Brecha 2 — Cambio de estado:** cuando el jefe aprueba, rechaza o revierte una solicitud, el empleado solicitante no recibe ningún aviso. Tiene que entrar manualmente a `/Solicitud` para ver si ya hubo una decisión. El jefe del jefe tampoco sabe cuándo un subordinado aprobó algo bajo su línea. Todo el seguimiento ocurre por WhatsApp o de forma verbal, fuera del sistema.

**Historia representativa — Brecha 1:** Diana Vargas (Operario) crea una solicitud de permiso. Laura Sánchez (Regente, jefa de Diana) no recibe ningún correo. La solicitud queda en `/EventoLaboral` sin que Laura sepa que existe. Diana asume que Laura ya revisó; Laura nunca se enteró.

**Historia representativa — Brecha 2:** Laura Sánchez (Regente) aprueba la solicitud de Diana. Diana sigue esperando — nunca recibió ningún aviso. El Analista tampoco sabe que Laura acaba de comprometer disponibilidad en su sede para esa fecha. El sistema registró el cambio; nadie lo vio.

Este pitch cierra ambas brechas. La segunda cierra exactamente el gap declarado en `Plan-AprobacionSolicitudes.md` sección No-Gos: *"No se construye notificación por correo al empleado cuando el jefe actúa."*

---

## 2. Appetite

**Small Batch — 2 semanas** (1 programador + 1 QA)

El sistema ya tiene `INotificationService`, `EmailTemplates` y `RegistroNotificaciones` de la capa de mensajería centralizada. El modelo de datos expone `AutorizadoPor`, `JefeInmediatoId` y `EstadoEvento`. Lo que falta es un único punto de disparo después de `CambiarEstadoAsync` que construya y envíe los correos correctos a los destinatarios correctos.

No se construyen nuevas tablas, nuevos flujos de UI ni paneles de reenvío. Se conectan dos puntos de disparo con la capa de mensajería ya existente: la creación de solicitud (nuevo) y el cambio de estado (original).

---

## 3. Solución

### Idea central

El sistema tiene **dos puntos de disparo** de notificación:

**Flujo 1 — Creación de solicitud (nuevo)**

Después de que `CrearSolicitudAsync` (o el Controller equivalente) persiste la nueva solicitud en BD, se invoca `INotificationService.NotificarNuevaSolicitudAsync(contexto)`. Ese método obtiene el jefe inmediato del solicitante y le envía un correo informativo con todos los datos de la solicitud.

```
[Empleado crea solicitud en /Solicitud]
       ↓
ISolicitudService.CrearSolicitudAsync(...)
       ↓ persiste en BD
       ↓ llama a
INotificationService.NotificarNuevaSolicitudAsync(contexto)
       ↓ destinatario = JefeInmediatoId del solicitante
       ↓ genera HTML via EmailTemplates.NuevaSolicitud(...)
       ↓ envía via IEmailHelper
       ↓ registra en RegistroNotificaciones
```

**Flujo 2 — Cambio de estado (original)**

Después de que `CambiarEstadoAsync` persiste el cambio, el servicio invoca a `INotificationService.NotificarCambioEstadoSolicitudAsync(contexto)`. Ese método determina la lista de destinatarios según la lógica de jerarquía y delega el envío a `IEmailHelper`.

```
[Jefe ejecuta acción en /EventoLaboral]
       ↓
IEventoLaboralService.CambiarEstadoAsync(...)
       ↓ persiste en BD
       ↓ llama a
INotificationService.NotificarCambioEstadoSolicitudAsync(contexto)
       ↓ construye destinatarios
       ↓ genera HTML via EmailTemplates.CambioEstadoSolicitud(...)
       ↓ envía via IEmailHelper
       ↓ registra en RegistroNotificaciones
```

---

### Lógica de destinatarios (regla de negocio central)

La regla varía según si la acción fue una **aprobación** o un **rechazo/reversión**:

| Condición | Destinatarios |
|---|---|
| El jefe aprueba Y tiene jefe por encima | Empleado solicitante + jefe(s) por encima del aprobador |
| El jefe aprueba Y NO tiene jefe por encima (Analista) | Solo el empleado solicitante |
| El jefe rechaza (sin importar jerarquía) | Solo el empleado solicitante |
| El jefe revierte a Pendiente | Solo el empleado solicitante |

> **Jerarquía del sistema (de menor a mayor autoridad):**  
> `Operario / Direccionador` → `Regente` → `AuxiliarRegente` → `DirectorTecnico` → `Analista`

**Ejemplo concreto — Regente aprueba:**

```
Diana Vargas (Operario)  solicita permiso
Laura Sánchez (Regente)  aprueba
Carlos Méndez (Analista) es el jefe de Laura

→ Correo 1: Diana Vargas  ← "Tu solicitud fue aprobada por Laura Sánchez"
→ Correo 2: Carlos Méndez ← "Laura Sánchez aprobó una solicitud de Diana Vargas"
```

**Ejemplo concreto — Regente rechaza:**

```
Diana Vargas (Operario)  solicita permiso
Laura Sánchez (Regente)  rechaza

→ Correo 1: Diana Vargas  ← "Tu solicitud fue rechazada por Laura Sánchez"
→ (sin correo al Analista)
```

---

### Scope A — Lógica de construcción de destinatarios

Dos métodos nuevos en `INotificationService`:

```csharp
// Flujo 1: empleado crea solicitud → notifica al jefe inmediato
Task NotificarNuevaSolicitudAsync(NuevaSolicitudDto contexto);

// Flujo 2: jefe cambia estado → notifica al solicitante (y al jefe del jefe si aprueba)
Task NotificarCambioEstadoSolicitudAsync(CambioEstadoSolicitudDto contexto);
```

**DTO para Flujo 1:**

```csharp
public class NuevaSolicitudDto
{
    public int EventoLaboralId   { get; set; }
    public string TipoEvento     { get; set; }  // "Permiso", "Vacaciones", etc.
    public DateTime? FechaInicio { get; set; }
    public DateTime? FechaFin    { get; set; }
    public string Descripcion    { get; set; }

    // Quién creó la solicitud
    public int    SolicitanteId     { get; set; }
    public string SolicitanteNombre { get; set; }
    public string SolicitanteCorreo { get; set; }

    // Jefe inmediato del solicitante (destinatario del correo)
    public int?   JefeId     { get; set; }
    public string JefeNombre { get; set; }
    public string JefeCorreo { get; set; }
}
```

**Algoritmo de destinatarios — Flujo 1 (pseudocódigo):**

```
if JefeId != null:
    enviar correo a Jefe con datos de la solicitud     // siempre informativo
else:
    omitir y registrar en RegistroNotificaciones       // solicitante sin jefe (Analista)
```

**DTO para Flujo 2:**

```csharp
Task NotificarCambioEstadoSolicitudAsync(CambioEstadoSolicitudDto contexto);
```

Donde `CambioEstadoSolicitudDto` contiene (sin cambios respecto a v1.0):

```csharp
public class CambioEstadoSolicitudDto
{
    public int EventoLaboralId     { get; set; }
    public string TipoEvento       { get; set; }  // "Permiso", "Vacaciones", etc.
    public DateTime? FechaInicio   { get; set; }
    public DateTime? FechaFin      { get; set; }
    public string Descripcion      { get; set; }

    public EstadoEvento NuevoEstado    { get; set; }
    public EstadoEvento EstadoAnterior { get; set; }

    // Quién ejecutó la acción
    public int    AprobadorId     { get; set; }
    public string AprobadorNombre { get; set; }
    public string AprobadorCorreo { get; set; }
    public int?   JefeDelAprobadorId     { get; set; }  // JefeInmediatoId del aprobador
    public string JefeDelAprobadorNombre { get; set; }
    public string JefeDelAprobadorCorreo { get; set; }

    // Quién creó la solicitud
    public int    SolicitanteId     { get; set; }
    public string SolicitanteNombre { get; set; }
    public string SolicitanteCorreo { get; set; }

    // Observación del jefe (obligatoria en rechazo)
    public string Observacion { get; set; }
}
```

**Algoritmo de destinatarios — Flujo 2 (pseudocódigo):**

```
destinatarios = []
destinatarios.Add(solicitante)                         // siempre

if NuevoEstado == Aprobado AND JefeDelAprobadorId != null:
    destinatarios.Add(jefeDelAprobador)                // solo en aprobación con jerarquía
```

---

### Scope B — Plantillas de correo

Dos métodos nuevos en `GestionPersonal.Constants/Messages/EmailTemplates/`:

```
// Flujo 1 — Correo al jefe cuando se crea una solicitud
EmailTemplates.NuevaSolicitud(
    jefeNombre,
    solicitanteNombre,
    tipoEvento,
    fechaInicio,
    fechaFin,
    descripcion
)

// Flujo 2 — Correo al solicitante / jefe del aprobador cuando cambia el estado
EmailTemplates.CambioEstadoSolicitud(
    destinatarioNombre,
    solicitanteNombre,
    aprobadorNombre,
    tipoEvento,
    fechaInicio,
    fechaFin,
    descripcion,
    nuevoEstado,
    observacion,
    esSolicitante   // true: correo para el empleado | false: correo para el jefe del aprobador
)
```

**Contenido del correo al jefe cuando se crea una solicitud (Flujo 1):**

```
Asunto: Nueva solicitud de [Permiso] — [Diana Vargas]

Hola [Laura Sánchez],

Te informamos que un empleado a tu cargo ha creado una nueva solicitud.

────────────────────────────────
  Empleado:     Diana Vargas
  Tipo:         Permiso
  Fecha inicio: 30 de abril de 2026
  Fecha fin:    2 de mayo de 2026
  Descripción:  "Cita médica"
  Estado:       Pendiente
────────────────────────────────

Puedes gestionar esta solicitud en /EventoLaboral.
Este correo es solo informativo.
```

**Contenido del correo al solicitante:**

```
Asunto: Tu solicitud de [Permiso] fue [Aprobada / Rechazada]

Hola [Diana Vargas],

Te informamos que tu solicitud ha sido [aprobada / rechazada].

────────────────────────────────
  Tipo:        Permiso
  Fecha inicio: 30 de abril de 2026
  Fecha fin:    2 de mayo de 2026
  Descripción: "Cita médica"
  Estado:       Aprobada
  Gestionada por: Laura Sánchez
  Observación:  (si aplica)
────────────────────────────────

Puedes consultar el estado de todas tus solicitudes en /Solicitud.
```

**Contenido del correo al jefe del aprobador (solo en aprobación):**

```
Asunto: [Regente Laura Sánchez] aprobó una solicitud de [Diana Vargas]

Hola [Carlos Méndez],

Te informamos que una solicitud fue aprobada bajo tu línea de autoridad.

────────────────────────────────
  Aprobado por:  Laura Sánchez
  Empleado:      Diana Vargas
  Tipo:          Permiso
  Fecha inicio:  30 de abril de 2026
  Fecha fin:     2 de mayo de 2026
  Descripción:   "Cita médica"
  Observación:   (si aplica)
────────────────────────────────

No se requiere acción de tu parte. Este correo es solo informativo.
```

---

### Scope C — Puntos de disparo en los servicios

**Flujo 1 — En `ISolicitudService.CrearSolicitudAsync`** (o en el Controller equivalente), después del `SaveChanges`:

```csharp
// Construir DTO con datos del nuevo evento y del jefe del solicitante
var contextoNueva = new NuevaSolicitudDto
{
    EventoLaboralId   = eventoGuardado.Id,
    TipoEvento        = eventoGuardado.TipoEvento,
    FechaInicio       = eventoGuardado.FechaInicio,
    FechaFin          = eventoGuardado.FechaFin,
    Descripcion       = eventoGuardado.Descripcion,
    SolicitanteId     = solicitante.Id,
    SolicitanteNombre = solicitante.NombreCompleto,
    SolicitanteCorreo = solicitante.Correo,
    JefeId            = solicitante.JefeInmediatoId,
    JefeNombre        = jefe?.NombreCompleto,
    JefeCorreo        = jefe?.Correo
};

// Fire-and-forget: un fallo SMTP no cancela la creación de la solicitud
_ = _notificationService
        .NotificarNuevaSolicitudAsync(contextoNueva)
        .ContinueWith(t => _logger.LogError(t.Exception, "Error al notificar nueva solicitud"),
                      TaskContinuationOptions.OnlyOnFaulted);
```

**Flujo 2 — En `IEventoLaboralService.CambiarEstadoAsync`** (o en el Controller, si el servicio no tiene acceso al contexto del usuario autenticado), después del `SaveChanges`:

```csharp
// Construir DTO con datos del evento, solicitante y aprobador
var contextoNotificacion = new CambioEstadoSolicitudDto { ... };

// Disparar de forma fire-and-forget con logging de errores
_ = _notificationService
        .NotificarCambioEstadoSolicitudAsync(contextoNotificacion)
        .ContinueWith(t => _logger.LogError(t.Exception, "Error al notificar cambio de estado"),
                      TaskContinuationOptions.OnlyOnFaulted);
```

> El envío de correo es **fire-and-forget** en ambos flujos. Un fallo en el SMTP no debe revertir ni bloquear la operación de BD. Los errores quedan en `RegistroNotificaciones` y en los logs.

---

### Scope D — Pruebas Playwright

Casos de prueba cubiertos:

**Flujo 1 — Notificación al jefe en creación de solicitud:**

| ID | Escenario | Actor | Correo jefe inmediato |
|---|---|---|---|
| TC-NS-01 | Operario crea solicitud de permiso | Operario | ✅ Regente recibe correo informativo |
| TC-NS-02 | El correo al jefe incluye tipo, fechas y descripción | Operario | ✅ Info completa |
| TC-NS-03 | El correo al jefe menciona el nombre del solicitante | Operario | ✅ Nombre correcto |
| TC-NS-04 | El correo al jefe contiene enlace / referencia a /EventoLaboral | Operario | ✅ Referencia presente |

**Flujo 2 — Notificación en cambio de estado:**

| ID | Escenario | Actor | Estado final | Correo solicitante | Correo jefe del aprobador |
|---|---|---|---|---|---|
| TC-CE-01 | Regente aprueba solicitud de Operario | Regente | Aprobado | ✅ Recibe | ✅ Analista recibe |
| TC-CE-02 | Regente rechaza solicitud de Operario | Regente | Rechazado | ✅ Recibe | ❌ No recibe |
| TC-CE-03 | Analista aprueba solicitud (sin jefe por encima) | Analista | Aprobado | ✅ Recibe | ❌ No aplica |
| TC-CE-04 | Analista rechaza solicitud | Analista | Rechazado | ✅ Recibe | ❌ No aplica |
| TC-CE-05 | Regente revierte a Pendiente | Regente | Pendiente | ✅ Recibe | ❌ No recibe |
| TC-CE-06 | El correo del solicitante menciona al aprobador | Regente | Aprobado | ✅ Nombre correcto | — |
| TC-CE-07 | El correo incluye tipo, fechas y descripción del evento | Regente | Rechazado | ✅ Info completa | — |
| TC-CE-08 | El correo del jefe incluye nombre del aprobador y del empleado | Regente | Aprobado | — | ✅ Info completa |

**Verificación en yopmail.com:** todos los correos de prueba usan dominio `@yopmail.com` (regla del proyecto).

**Breadboard de la prueba TC-NS-01:**

```
1. Login como Diana Vargas (Operario) → /Solicitud
2. Crear nueva solicitud de Permiso
   → Fecha inicio: 30 de abril de 2026
   → Fecha fin: 2 de mayo de 2026
   → Descripción: "Cita médica"
3. Verificar que la solicitud aparece en la lista con estado "Pendiente"
4. Abrir yopmail.com → laura.sanchez@yopmail.com (Regente, jefe de Diana)
   → Validar asunto: "Nueva solicitud de Permiso — Diana Vargas"
   → Validar cuerpo: menciona "Diana Vargas", tipo "Permiso", fechas, descripción
   → Validar cuerpo: contiene referencia a /EventoLaboral
   → Validar cuerpo: dice "Este correo es solo informativo"
```

**Breadboard de la prueba TC-CE-01:**

```
1. Login como Laura Sánchez (Regente) → /EventoLaboral
2. Localizar solicitud Pendiente de Diana Vargas
3. Gestionar → Aprobar (observación opcional)
4. Verificar estado en tabla: "Aprobado"
5. Abrir yopmail.com → diana.vargas@yopmail.com
   → Validar asunto: "Tu solicitud de Permiso fue Aprobada"
   → Validar cuerpo: menciona "Laura Sánchez", tipo, fechas, descripción
6. Abrir yopmail.com → carlos.mendez@yopmail.com (Analista)
   → Validar asunto: "Laura Sánchez aprobó una solicitud de Diana Vargas"
   → Validar cuerpo: menciona tipo, fechas, nombre del empleado
```

---

## 4. Rabbit Holes

- **`JefeInmediatoId` del solicitante puede ser null (Flujo 1):** si el solicitante es Analista (sin jefe) y de algún modo crea una solicitud, no se envía correo. Omitir silenciosamente y registrar en `RegistroNotificaciones`.
- **`JefeInmediatoId` del aprobador puede ser null (Flujo 2):** si el Analista (sin jefe) aprueba, no se busca destinatario adicional. La lógica es `if (JefeDelAprobadorId != null && NuevoEstado == Aprobado)` — no hay excepción, simplemente no hay destinatario adicional.
- **Cadena de jerarquía multinivel:** en este ciclo se notifica **un solo nivel** en ambos flujos. Notificar toda la cadena hasta el Analista es un pitch separado.
- **Correo del empleado vs correo de acceso:** si `Empleados.CorreoElectronico` es null, usar `Usuarios.CorreoAcceso` como fallback. Si ambos son null, omitir silenciosamente y registrar en `RegistroNotificaciones.Error`.
- **Doble correo si el aprobador ES el Analista del solicitante (Flujo 2):** deduplicar destinatarios por correo antes de enviar.
- **El jefe recibe dos correos si actúa rápido:** en Flujo 1 recibe el aviso de creación; si luego aprueba, el solicitante recibe el aviso de cambio de estado. Son eventos distintos, no se considera redundancia.
- **Fire-and-forget vs transaccional:** el envío de correo no forma parte de la transacción de BD en ningún flujo. Un fallo SMTP no debe exponer al usuario ningún error. Solo se registra internamente.
- **Reversión a Pendiente:** cuando se revierte a `Pendiente`, el sistema notifica al solicitante (para que sepa que su solicitud volvió a revisión), pero **no** al jefe del aprobador — una reversión no es una aprobación.

---

## 5. No-Gos

- No se notifica a toda la cadena jerárquica en cascada (solo un nivel en cada flujo).
- No se construye vista de "correos enviados" en la UI.
- No se implementa reenvío manual de correos desde la interfaz.
- No se envía correo al propio solicitante como confirmación de que su solicitud fue creada (ya lo ve en pantalla al momento de crearla).
- No se gestionan notificaciones para los estados `Cancelado` ni `EnRevision`.
- No se envía correo al propio aprobador como confirmación de su acción.
- El correo al jefe en la creación de solicitud es **solo informativo** — no incluye acciones de aprobación/rechazo directas desde el correo.
