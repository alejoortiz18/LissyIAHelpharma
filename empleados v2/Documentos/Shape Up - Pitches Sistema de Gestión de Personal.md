# Shape Up Pitches — Sistema de Administración de Empleados

> Refinamiento del requerimiento original aplicando la metodología **Shape Up** de Basecamp.
> Cada módulo funcional se convierte en un **Pitch** independiente con los cinco ingredientes obligatorios.
> El sistema está diseñado para ser operado directamente por **coordinadores y supervisores** de cada área, sin depender de un departamento de Gestión Humana centralizado.

---

## Visión General del Producto

Centralizar la administración de empleados y el control operativo de sus actividades diarias, permitiendo un seguimiento riguroso de su ciclo de vida dentro de la organización. El sistema está compuesto por **cuatro pitches** que pueden apostarse de forma independiente en ciclos de seis semanas.

---

---

# Pitch 1 — Gestión de Empleados

## 1. Problema

Los coordinadores y supervisores de cada área no tienen un único lugar donde consultar la información completa de un empleado: sus datos personales, a qué sede pertenece, qué cargo ocupa, bajo qué tipo de contrato y quién es su jefe inmediato. Hoy esa información está dispersa en hojas de cálculo o sistemas no integrados. Cuando un empleado se desvincula, no queda registro estructurado del motivo ni de la fecha exacta, lo que genera problemas de auditoría.

**Historia representativa:** Un coordinador de área necesita contactar al jefe inmediato de un empleado que tuvo un incidente. Debe buscar en tres archivos distintos antes de encontrar el dato. En el proceso descubre que el empleado ya está inactivo pero nadie actualizó el registro.

## 2. Appetite

**Big Batch — 6 semanas** (1 diseñador + 2 programadores)

El registro de empleados es el núcleo del sistema. Sin él ningún otro módulo funciona. Justifica una inversión completa de un ciclo.

## 3. Solución

**Pantalla principal:** Lista de empleados con filtros rápidos por sede, cargo, estado (Activo / Inactivo) y tipo de contrato.

**Formulario de registro / edición** con las siguientes secciones:

| Sección | Campos clave |
|---|---|
| Datos personales | Nombre completo, tipo y número de identificación, fecha de nacimiento, teléfono, correo |
| Vinculación | Sede, Cargo, Tipo de vinculación (`Directo` / `Temporal`), Empresa Temporal *(si aplica)*, Jefe inmediato |
| Estado | Activo / Inactivo, Motivo de retiro, Fecha de desvinculación |
| Credenciales | Correo de acceso + contraseña cifrada (hash bcrypt) |

> **Regla de vinculación:** si se selecciona `Temporal`, el campo **Empresa Temporal** se vuelve obligatorio. Si se selecciona `Directo`, ese campo se oculta. Esto se gestiona desde el catálogo de Empresas Temporales (ABM simple).

**Flujo de desvinculación:** Al marcar un empleado como Inactivo, el sistema obliga a ingresar Motivo de retiro y Fecha de desvinculación antes de guardar. El registro queda en modo solo-lectura; no se elimina.

**Catálogos de soporte** (pantallas simples de ABM):
- Sedes
- Cargos
- Tipos de contrato
- Empresas Temporales

**Historial del empleado (pestaña dentro del perfil):**
Vista de solo-lectura que consolida cronológicamente todos los registros vinculados al empleado, independientemente del tipo de vinculación:

| Tipo de registro | Origen |
|---|---|
| Eventos laborales | Vacaciones, incapacidades, permisos |
| Horas extras | Solicitudes aprobadas, rechazadas y pendientes |
| Cambios de turno | Historial de asignaciones de jornada |
| Desvinculación | Motivo y fecha si aplica |

Este historial no desaparece si el empleado pasa a Inactivo. Permite consultar toda la trazabilidad de su estadía en la empresa.

```
[Lista de empleados]
  → Filtrar: Sede | Cargo | Estado | Tipo de vinculación
  → Botón "Nuevo empleado"
  → Click en fila → [Detalle / Edición]
                        → Si tipo = Temporal → campo Empresa Temporal (obligatorio)
                        → Si estado = Inactivo → Formulario de retiro
                        → Pestaña "Historial" → línea de tiempo de todos sus registros
```

### Validaciones de integridad (servicio: `EmpleadoService`)

- **Unicidad de identificación:** No pueden existir dos empleados con el mismo `TipoIdentificacion` + `NumeroIdentificacion`. Validado con índice único compuesto en base de datos **y** en el Service antes de guardar. Mensaje: *"Ya existe un empleado con esta identificación."*
- **Correo electrónico único y obligatorio:** Todo empleado debe tener correo. Se valida formato y unicidad en el sistema. Mensaje en duplicado: *"Ya existe un usuario con este correo electrónico."*
- **Auto-referencia de jefe:** `EmpleadoId` ≠ `JefeId`. Un empleado no puede ser su propio jefe inmediato.
- **Jefe obligatorio para no-Jefes:** Si el rol es `Empleado` o `Regente`, el campo `JefeId` es obligatorio.
- **Sede obligatoria para Regente:** Si el rol es `Regente`, la `SedeId` es obligatoria y debe existir en el catálogo activo.
- **Coherencia de fechas del empleado:**
  - `FechaNacimiento` ≤ `FechaActual`
  - `FechaDesvinculacion` ≥ `FechaIngreso` *(si aplica)*

## 4. Rabbit Holes

- **Jerarquía de jefes:** El campo "Jefe inmediato" es simplemente una referencia a otro empleado del sistema. No construir un árbol organizacional visual en este ciclo; eso es un proyecto aparte.
- **Empresa Temporal:** El sistema registra el nombre de la empresa temporal como dato informativo. No hay integración con el sistema interno de la temporal ni sincronización de contratos externos.
- **Contraseñas:** Se almacenan en dos columnas independientes en la base de datos: `password_hash` (resultado del algoritmo bcrypt) y `password_salt` (salt aleatorio generado por empleado). Nunca en texto plano. No construir un flujo de "recuperar contraseña" en este ciclo.
- **Historial:** La pestaña de historial lee datos que ya existen en el sistema (eventos, horas extras, turnos). No requiere lógica adicional; es una vista agrupada por empleado.

## 5. No-Gos

- No hay importación masiva de empleados desde Excel/CSV en este ciclo.
- No hay árbol organizacional visual ni organigramas.
- No hay roles ni permisos diferenciados por usuario (eso es seguridad avanzada para un ciclo posterior).
- No hay auditoría de cambios a nivel de campo (quién modificó qué valor específico en el formulario). El historial de **actividades y novedades** sí se guarda; la auditoría de ediciones del formulario base queda para un ciclo posterior.
- No hay integración con sistemas externos de empresas temporales.

---

---

# Pitch 2 — Control de Eventos Laborales

## 1. Problema

Los eventos de ausentismo (vacaciones, incapacidades, permisos) se aprueban verbalmente o por correo y luego nadie tiene visibilidad centralizada de quién está disponible hoy. Si dos managers autorizan eventos solapados al mismo empleado, nadie se da cuenta hasta que el empleado no aparece. Tampoco existe registro del documento de soporte que justifica el evento.

**Historia representativa:** El gerente de operaciones quiere saber cuántos empleados de la sede Norte estarán en vacaciones la próxima semana. Tiene que llamar a tres supervisores y consolidar la información a mano.

## 2. Appetite

**Big Batch — 6 semanas** (1 diseñador + 2 programadores)

Es el módulo con mayor impacto en la operación diaria. Requiere la lógica de validación de solapamiento y la gestión de archivos adjuntos, lo que lo hace suficientemente complejo para un ciclo completo.

## 3. Solución

**Vista de calendario semanal/mensual** que muestra los eventos activos por empleado y sede. El objetivo es "ver espacios libres y ocupados" — no reemplazar un sistema de calendario completo.

**Registro de evento** con:
- Empleado (selector)
- Tipo de evento: Vacaciones | Incapacidad | Permiso
- Fecha inicio / Fecha fin
- Descripción o justificación
- Documento de soporte (adjunto PDF/imagen — máx. 5 MB, formatos PDF/JPG/PNG): **no se almacena en base de datos ni en disco**; se adjunta en memoria al correo de notificación y se descarta después del envío
- Autorizado por (campo obligatorio: nombre del autorizante)

**Regla de evento único activo:** Al guardar, el sistema verifica que el empleado no tenga otro evento activo en el mismo rango de fechas. Si hay solapamiento, muestra un error claro antes de guardar.

**Estados del evento:** `Activo` → `Finalizado` (automático al pasar la fecha fin) | `Anulado` (manual, requiere motivo).

```
[Vista calendario]  ←→  [Lista de eventos]
  → Click en día  →  [Nuevo evento]
                        → Validar solapamiento (EventoService)
                        → Adjuntar soporte en memoria (máx. 5 MB, PDF/JPG/PNG)
                        → Enviar correo SMTP (EmailService)
                             → Destinatario primario: Regente de la sede
                             → Si no existe Regente → Jefe general
                        → Si envío exitoso → Guardar evento + registrar EmailLog
                        → Si envío falla   → Rollback completo (NO se guarda el evento)
```

### Definición de evento activo

Un evento se considera **activo** cuando se cumplen simultáneamente:

```
FechaInicio <= FechaActual <= FechaFin
Y Estado != Anulado
```

Esta definición es compartida por `EventoService` y `HoraExtraService` al validar disponibilidad del empleado.

## 4. Rabbit Holes

- **Archivos en memoria únicamente:** El archivo viaja adjunto en el correo. No construir gestor de documentos, visor ni descarga desde el sistema. Si el correo falla, el evento no se guarda (rollback completo de la transacción).
- **Fallo de SMTP:** Si el servidor SMTP no responde, el sistema registra el intento en `EmailLog` con estado `Fallido` y muestra un error al usuario. No hay reintento automático en este ciclo.
- **Cálculo de días hábiles:** Para vacaciones, el sistema registra las fechas; el cálculo de días hábiles descontando festivos queda fuera del alcance de este ciclo.
- **Destinatario del correo:** La lógica usa `ObtenerResponsable(empleado)` para determinar el destinatario: Regente de la sede → si no existe, Jefe general.

## 5. No-Gos

- No hay flujo de solicitud/aprobación (workflow) — el autorizante se registra manualmente. Un workflow completo es un proyecto separado.
- No hay integración con nómina ni cálculo de descuentos por ausentismo.
- No hay almacenamiento de archivos adjuntos en base de datos ni en disco del servidor.
- No hay portal de descarga de adjuntos desde el sistema; el archivo solo existe en el correo enviado.
- No hay reintentos automáticos de envío de correo fallido.
- No hay subtipos de permiso (permiso remunerado vs. no remunerado) en este ciclo.

---

---

# Pitch 3 — Administración de Jornadas y Horarios

## 1. Problema

No existe un registro formal de los turnos asignados a cada empleado. Los supervisores saben de memoria a qué hora entra y sale cada persona, pero cuando alguien falta o hay un cambio, no hay documento de referencia. Tampoco se registra quién programó el horario ni si aplica para fines de semana o festivos.

**Historia representativa:** Un supervisor nuevo necesita cubrir un turno del fin de semana. No sabe quiénes tienen jornada configurada para sábados porque esa información no está en ningún sistema, solo en la memoria del supervisor anterior.

## 2. Appetite

**Small Batch — 2 semanas** (1 diseñador + 1 programador)

El módulo es conceptualmente simple: una tabla de turnos con hora de entrada, hora de salida y configuración de días. No requiere lógica de negocio compleja.

## 3. Solución

**Catálogo de Turnos** (ABM simple):
- Nombre del turno (ej. "Turno mañana")
- Hora de entrada / Hora de salida
- Aplica fines de semana: Sí / No
- Aplica festivos: Sí / No

**Asignación de turno a empleado:**
- Desde el perfil del empleado se selecciona el turno activo.
- Campo "Programado por": referencia al empleado que asignó el turno.
- Fecha de vigencia (desde cuándo aplica).

> **Regla de turno único activo:** Un empleado solo puede tener **un turno activo** a la vez (`IsActive = true`). Al asignar un nuevo turno, el anterior queda con `IsActive = false` conservando su fecha de vigencia. El historial completo de asignaciones es visible en la pestaña de historial del empleado. El cambio se registra con el usuario responsable y la fecha.

```
[Catálogo de Turnos]
  → Nuevo turno → Nombre | Entrada | Salida | Fines de semana | Festivos

[Perfil de empleado]
  → Sección "Horario" → Seleccionar turno | Programado por | Vigente desde
```

## 4. Rabbit Holes

- **Múltiples turnos por empleado:** Un empleado tiene un único turno activo a la vez. Si cambia de turno, el registro anterior queda como historial (solo guardar la nueva asignación con nueva fecha de vigencia, no sobrescribir).
- **Festivos:** El campo "Aplica festivos" es una bandera booleana. No construir un calendario de festivos en este ciclo.

## 5. No-Gos

- No hay control de asistencia ni marcación de entrada/salida.
- No hay generación automática de cuadrantes o grillas de turnos rotativos.
- No hay alertas por incumplimiento de horario.
- No hay integración con biométrico o reloj de fichaje.

---

---

# Pitch 4 — Gestión de Horas Extras

## 1. Problema

Las horas extras se registran en papel o en correo y luego alguien las transcribe a una hoja de cálculo al final del mes. No hay trazabilidad de quién aprobó cada solicitud ni existe un estado formal que indique si fueron aprobadas, rechazadas o están pendientes. Esto genera disputas a la hora de pagar.

**Historia representativa:** Un empleado alega que trabajó 8 horas extras en el último mes pero el área de nómina solo tiene registro de 5. No hay forma de saber qué pasó con las otras 3 horas porque el correo de aprobación no se encontró.

## 2. Appetite

**Small Batch — 2 semanas** (1 diseñador + 1 programador)

Es un formulario de registro con estados. La lógica es acotada: registrar, aprobar/rechazar y consultar.

## 3. Solución

**Formulario de solicitud de horas extras:**
- Empleado
- Fecha en que se trabajaron las horas
- Cantidad de horas *(> 0 y ≤ 24)*
- Motivo / justificación (texto obligatorio)
- Estado inicial: `Pendiente`

**Reglas de validación (servicio: `HoraExtraService`):**

**1. Unicidad por día:** No puede existir más de una solicitud activa para el mismo empleado en la misma fecha. Si ya existe, el sistema bloquea con: *"Ya existe una solicitud de horas extras para este empleado en la fecha indicada."*

**2. Disponibilidad del empleado:** Antes de guardar, el sistema verifica que el empleado no tenga un evento activo (`FechaInicio` ≤ fecha ≤ `FechaFin` y estado ≠ `Anulado`) de tipo Vacaciones, Incapacidad o Permiso. Mensaje: *"El empleado no está disponible en la fecha seleccionada."*

**3. Validación de horas:** Solo se aceptan valores entre 1 y 24 (entero o decimal). No se permiten valores iguales a 0 ni superiores a 24.

**Flujo de estados:**
```
Pendiente → Aprobado   (solo Regente, sobre empleados de su sede)
          → Rechazado  (solo Regente, sobre empleados de su sede — requiere motivo)

Aprobado  → Anulado    (solo Jefe — requiere motivo obligatorio)
```

**Control de concurrencia:** Antes de aprobar o rechazar, el Service valida que el estado actual en base de datos siga siendo `Pendiente`. Si fue modificado por otro usuario: *"El registro ya fue procesado por otro usuario."*

**Registro de aprobación / anulación:** Toda acción de cambio de estado guarda: usuario responsable, fecha/hora y motivo *(si aplica)*.

**Vistas por rol:**
- **Regente:** ve solo solicitudes de empleados de su sede; puede aprobar o rechazar `Pendiente`.
- **Jefe:** ve todas las solicitudes de todas las sedes; puede anular solicitudes `Aprobado`.

```
[Lista de horas extras]
  → Filtrar: Empleado | Fecha | Estado
  → Nueva solicitud → Empleado | Fecha | Horas | Motivo
        → Validar: unicidad por día (HoraExtraService)
        → Validar: disponibilidad del empleado (EventoService)
        → Validar: horas en rango [1–24]
  → Solicitud Pendiente (Regente) → [Aprobar] | [Rechazar + motivo]
        → Validar concurrencia antes de actualizar
  → Solicitud Aprobada (Jefe)     → [Anular + motivo obligatorio]
```

## 4. Rabbit Holes

- **Tipos de hora extra:** En Colombia existen horas extras diurnas, nocturnas, en festivo, etc., con diferentes recargos. El sistema solo registra la cantidad y fecha; el cálculo del recargo monetario queda fuera de este ciclo para no abrir una caja de Pandora con la normativa laboral.
- **Control de concurrencia:** La validación del estado `Pendiente` antes de aprobar previene doble procesamiento. No construir bloqueo optimista completo con `RowVersion` en este ciclo; basta con validar el estado en el Service antes de actualizar.
- **Anulación vs. rechazo:** Rechazar aplica sobre solicitudes `Pendiente`; anular aplica sobre solicitudes `Aprobado`. Son dos acciones distintas con actores distintos (Regente rechaza, Jefe anula).

## 5. No-Gos

- No hay cálculo de valor monetario de las horas extras.
- No hay límite automático de horas extras por empleado o por ley.
- No hay integración con nómina.
- No hay notificaciones automáticas al empleado cuando su solicitud cambia de estado.

**Restricciones por rol:**

| Rol | Puede registrar | Puede aprobar / rechazar | Puede anular |
|---|---|---|---|
| `Empleado` | ✅ (para sí mismo) | ❌ | ❌ |
| `Regente` | ✅ (para su equipo) | ✅ solo su equipo | ❌ |
| `Jefe` | ✅ | ❌ | ✅ cualquier aprobada |

---

---

## Resumen de Apuestas (Betting Table)

| Pitch | Tipo | Ciclo sugerido | Dependencias |
|---|---|---|---|
| Pitch 1 — Gestión de Empleados | Big Batch | Ciclo 1 | Ninguna — es la base |
| Pitch 2 — Control de Eventos Laborales | Big Batch | Ciclo 2 | Requiere Pitch 1 |
| Pitch 3 — Jornadas y Horarios | Small Batch | Ciclo 2 (en paralelo con Pitch 2) | Requiere Pitch 1 |
| Pitch 4 — Gestión de Horas Extras | Small Batch | Ciclo 2 (en paralelo con Pitch 2) | Requiere Pitch 1 |

> **Principio Shape Up aplicado:** tiempo fijo, alcance variable. Si durante la construcción algo resulta más complejo de lo esperado, se recorta el alcance — no se extiende el ciclo.

---

## Reglas de Negocio Transversales (aplican a todos los pitches)

### Reglas originales

1. **Integridad referencial:** Todo empleado debe tener Sede y Cargo antes de poder ser guardado.
2. **Tipo de vinculación obligatorio:** Todo empleado debe indicar si su contrato es `Directo` o `Temporal`. Si es `Temporal`, la Empresa Temporal es obligatoria.
3. **Historial perpetuo:** Todos los registros de actividades y novedades (eventos laborales, horas extras, cambios de turno) quedan vinculados al empleado de forma permanente, incluso si el empleado pasa a estado Inactivo. No se eliminan al desvincular.
4. **Seguridad:** Las contraseñas creadas por el usuario se almacenan en la base de datos usando **hash bcrypt** y un **salt aleatorio**, guardados en columnas **independientes** (`password_hash` y `password_salt`). Nunca se almacena la contraseña en texto plano. El acceso al sistema requiere credenciales válidas en cada sesión.
5. **Soft delete:** Los registros (empleados, eventos, turnos, horas extras) no se eliminan físicamente; se marcan con `IsActive = false` y opcionalmente `FechaInactivacion`. Todo modelo de datos debe incluir estos dos campos.
6. **Auditoría mínima:** Toda acción de aprobación o cambio de estado registra quién la realizó y cuándo.

### Reglas adicionales

7. **Unicidad de empleados:** No pueden existir dos empleados con el mismo `TipoIdentificacion` + `NumeroIdentificacion`. Validado con índice único compuesto en base de datos **y** en el Service antes de guardar. Mensaje: *"Ya existe un empleado con esta identificación."*

8. **Correo electrónico único y obligatorio:** Todo empleado debe tener correo. Se valida formato (regex estándar) y unicidad en el sistema. Mensaje en duplicado: *"Ya existe un usuario con este correo electrónico."*

9. **Coherencia de fechas:**
   - `FechaNacimiento` ≤ `FechaActual`
   - `FechaDesvinculacion` ≥ `FechaIngreso` *(si aplica)*
   - En eventos laborales: `FechaFin` ≥ `FechaInicio`

10. **Restricciones por estado del empleado:** Si el empleado tiene estado `Inactivo`, el sistema **bloquea** el registro de eventos laborales, horas extras y cambios de turno asociados a ese empleado. Solo permite consultar su perfil e historial.

11. **Modelo de usuarios y roles:** Todos los empleados son usuarios del sistema. Los roles son: `Empleado`, `Regente` y `Jefe`. Un empleado tiene exactamente un rol activo.

12. **Control de acceso por rol:**
    - `Empleado` → accede únicamente a su propia información.
    - `Regente` → gestiona empleados de su sede.
    - `Jefe` → accede a toda la información del sistema.

13. **Regente único por sede:** Cada sede puede tener como máximo un `Regente` activo. El sistema no permite asignar un segundo Regente a la misma sede mientras el primero esté activo.

14. **Jerarquía obligatoria:** Todo empleado con rol `Empleado` o `Regente` debe tener un `JefeId` asignado. La excepción es el rol `Jefe`, que no tiene jefe superior en el sistema.

15. **Arquitectura en capas:** Los Controllers solo orquestan llamadas; toda la lógica de negocio reside en los Services; el acceso a datos es exclusivo de los Repositories. No se permite lógica de negocio en Controllers ni queries directas fuera de los Repositories.

16. **Transacciones:** Cuando una operación implica múltiples escrituras (ej: guardar evento + registrar EmailLog + enviar correo), se usa una transacción de base de datos. Si cualquier paso falla, se hace rollback completo.

---

---

## Jerarquía y Responsable — Método `ObtenerResponsable`

El sistema debe garantizar que **siempre** haya un responsable identificado para cualquier empleado. La lógica es:

```
ObtenerResponsable(empleado):
  1. Si el empleado tiene JefeId asignado y activo  → devolver ese Jefe
  2. Si no tiene JefeId (o está inactivo):
       → Buscar el Regente activo de la sede del empleado
  3. Si la sede no tiene Regente activo:
       → Devolver el Jefe general (usuario con rol Jefe activo en el sistema)
  4. Si no hay ningún Jefe en el sistema → lanzar excepción controlada
```

Este método reside en `EmpleadoService` y es consumido por `EventoService`, `HoraExtraService` y `EmailService`.

---

---

## Configuración SMTP (`appsettings.json`)

```json
"Smtp": {
  "Host": "smtp.empresa.com",
  "Puerto": 587,
  "Usuario": "notificaciones@empresa.com",
  "Password": "...",
  "UsarSSL": true
}
```

- La configuración SMTP **nunca** se hardcodea en el código; siempre se lee desde `appsettings` o variables de entorno.
- Las credenciales de producción se gestionan fuera del repositorio (variables de entorno o secret manager).

---

---

## Modelo: `EmailLog`

Registra todos los intentos de envío de correo del sistema.

| Campo | Tipo | Descripción |
|---|---|---|
| `Id` | int | PK |
| `FechaEnvio` | datetime | Fecha y hora del intento |
| `EmpleadoId` | int | Empleado relacionado con el evento |
| `Tipo` | string | Tipo de notificación (ej. `EventoLaboral`) |
| `Destinatarios` | string | Correos destinatarios (separados por coma) |
| `Estado` | enum | `Enviado` / `Fallido` |
| `Error` | string | Mensaje de error si `Estado = Fallido`; null si exitoso |
| `NombreArchivo` | string | Nombre del adjunto; null si no hubo adjunto |
| `UsuarioAccion` | string | Usuario del sistema que disparó la acción |

- El `EmailLog` se registra **siempre**, independientemente del resultado del envío.
- Si el envío falla → `Estado = Fallido` + se registra el error, pero el evento **no** se guarda (rollback).

---

---

## Servicios Requeridos

| Servicio | Responsabilidad |
|---|---|
| `EmpleadoService` | CRUD de empleados, validaciones de unicidad, coherencia de fechas, jerarquía |
| `EventoService` | Registro de eventos laborales, validación de solapamiento, definición de evento activo |
| `HoraExtraService` | Solicitudes, validaciones de unicidad/disponibilidad/horas, flujo de aprobación/anulación |
| `EmailService` | Envío SMTP, adjuntos en memoria, integración con `EmailLogService` |
| `EmailLogService` | Registro de todos los intentos de envío (éxito y fallo) |

> **Regla de oro:** Ningún Controller llama directamente a un Repository. Toda operación pasa por el Service correspondiente.
