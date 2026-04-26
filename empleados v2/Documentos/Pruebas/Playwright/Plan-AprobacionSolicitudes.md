# Pitch — Flujo de Aprobación de Solicitudes Laborales
## Sistema GestionPersonal · Módulo EventoLaboral + Mis Solicitudes

> **Metodología:** Shape Up (Basecamp) — https://basecamp.com/shapeup  
> **Ciclo:** Small Batch — 2 semanas  
> **Stack:** C# ASP.NET Core MVC / .NET 10 · `EstadoEvento` enum · `ISolicitudService` / `IEventoLaboralService`  
> **Fecha:** 25 de abril de 2026  
> **Versión:** 1.0

---

## 1. Problema

Hoy el flujo de solicitudes laborales está roto en la mitad del camino. Un `Operario` o `Direccionador` puede crear una solicitud de permiso desde `/Solicitud`, la cual queda en estado `Pendiente`—pero ahí termina todo. El jefe inmediato del empleado **no tiene una bandeja** donde ver esa solicitud, no puede aprobarla ni rechazarla, y no existe ningún camino de vuelta al empleado para informarle la decisión. La solicitud queda congelada en `Pendiente` indefinidamente.

Al mismo tiempo, el `Analista` (cargo de mayor autoridad operativa) tiene visibilidad en `/EventoLaboral` de todos los eventos de todas las sedes, pero no hay trazabilidad formal de quién tomó cada decisión, cuándo ni por qué. Cuando una aprobación fue incorrecta y hay que revertirla, el sistema no registra el estado anterior ni la observación obligatoria del responsable.

**Historia representativa:** Diana Vargas (Operario, Medellín) crea una solicitud de permiso para el próximo viernes. Laura Sánchez (Regente, su jefa inmediata) no recibe ningún aviso y no encuentra la solicitud en ningún lugar del sistema. Diana tampoco sabe si fue aprobada. El viernes llega, nadie sabe qué procede y el conflicto se resuelve por WhatsApp—fuera del sistema.

---

## 2. Appetite

**Small Batch — 2 semanas** (1 programador + 1 QA)

El modelo de datos ya tiene todo lo necesario: `EstadoEvento` tiene `Pendiente`, `Aprobado`, `Rechazado`, `EnRevision`; `EventosLaborales` tiene `AutorizadoPor`, `MotivoAnulacion`, `FechaModificacion`. El `IEventoLaboralService` ya expone `CambiarEstadoAsync`. Lo que falta es conectar el flujo desde el punto de vista del jefe:

1. Una bandeja filtrada que le muestre las solicitudes de sus subordinados.
2. Botones de acción (`Aprobar`, `Rechazar`, `Reversar`) con validación de rol.
3. Auditoría registrada en los campos existentes (sin tabla nueva).

> **Tiempo fijo, alcance variable:** si durante la construcción resulta complejo implementar la jerarquía multinivel (jefe del jefe), la bandeja puede limitarse al jefe inmediato directo. El acceso del `Analista` a todas las sedes ya está implementado en `/EventoLaboral` — no se reconstruye.

---

## 3. Solución

### Scopes identificados

La solución se organiza en **cuatro scopes** que pueden construirse en secuencia. Cada scope es una pieza completa (frontend + backend + validación) que puede verificarse de forma independiente.

---

### Scope A — Bandeja del jefe inmediato

El jefe ve las solicitudes de sus subordinados directos filtradas desde `/EventoLaboral`.

**Quién la usa:** `Regente`, `AuxiliarRegente`, `DirectorTecnico`, `Analista`.

**Elementos:**
- En `/EventoLaboral`, cuando el usuario autenticado tiene subordinados activos (`JefeInmediatoId` referenciado), la tabla muestra por defecto las solicitudes de sus subordinados directos.
- El `Analista` ve solicitudes de **todas las sedes** sin restricción.
- Filtros disponibles: Estado (`Pendiente` / `Aprobado` / `Rechazado` / `EnRevision`) · Empleado · Sede (solo Analista) · Rango de fechas.
- La columna **"Gestionar"** muestra el dropdown de acciones solo si el usuario tiene permiso de aprobar/rechazar sobre ese evento.

```
[GET /EventoLaboral]
  → Tabla solicitudes de subordinados
      → Filtrar: Estado | Empleado | Sede (Analista only) | Fecha
      → Por fila: [Ver detalle] [Gestionar ▼]
                               ├── Aprobar
                               ├── Rechazar
                               └── Reversar (si está Aprobado o Rechazado)
```

---

### Scope B — Aprobar y rechazar solicitudes

El jefe puede aprobar (`Pendiente → Aprobado`) o rechazar (`Pendiente → Rechazado`) con observación.

**Validaciones:**
- Solo `Regente`, `AuxiliarRegente`, `DirectorTecnico` y `Analista` pueden ejecutar estas acciones.
- Solo sobre solicitudes de empleados que reportan directamente a ellos (o cualquier sede para el `Analista`).
- Al rechazar, la observación es **obligatoria**.
- Al aprobar, la observación es **opcional**.
- Se registra en campos existentes: `AutorizadoPor` = nombre del usuario autenticado · `FechaModificacion` = DateTime.Now · `MotivoAnulacion` = observación.

```
[Modal Gestión]
  Estado actual: Pendiente
  Nuevo estado: [Aprobado ▼]   (u otro estado válido)
  Observación: [textarea]  ← obligatorio si rechaza
  [Confirmar]  →  POST /EventoLaboral/GestionarEstado
```

---

### Scope C — Reversión de decisiones

Los roles autorizados pueden revertir una decisión ya tomada.

**Matriz de reversiones permitidas:**

| Estado actual | Puede cambiar a |
|---|---|
| `Aprobado` | `Pendiente` · `Rechazado` |
| `Rechazado` | `Aprobado` · `Pendiente` |
| `Pendiente` | `Aprobado` · `Rechazado` |

**Quién puede reversar:** `DirectorTecnico`, `AuxiliarRegente`, `Analista` (igual que aprobar/rechazar, ya que el flujo es el mismo modal).

**Regla de auditoría:** al reversar, la observación es **siempre obligatoria**. Se registra en `MotivoAnulacion`.

---

### Scope D — Visibilidad del empleado sobre su solicitud

El empleado creador de la solicitud puede ver el estado actualizado y la observación desde `/Solicitud`.

**Elementos:**
- En la tabla de `/Solicitud`, la columna `Estado` refleja el valor actual (incluyendo `Aprobado`, `Rechazado`).
- La columna `Observación del jefe` muestra el valor de `MotivoAnulacion` si existe.
- **No hay acción de edición** sobre solicitudes ya procesadas. Solo lectura.

```
[GET /Solicitud — vista empleado]
  Tipo | Fechas | Estado | Observación del jefe | Fecha modificación
  Permiso | 30 abr – 2 may | Aprobado | — | 28 abr 10:15
  Permiso | 10 may – 11 may | Rechazado | "Sin cobertura esa semana" | 29 abr 09:00
```

---

### Breadboard completo

```
[Operario/Direccionador]
  /Solicitud
  → [Nueva solicitud] → TipoEvento | Fechas | Descripción → POST → Estado: Pendiente
  → Tabla propia: Estado | Observación del jefe

[Regente / AuxiliarRegente / DirectorTecnico]
  /EventoLaboral  (filtrado a subordinados directos)
  → Fila Pendiente → [Gestionar] → Modal → Aprobar / Rechazar + Observación
  → Fila Aprobado  → [Gestionar] → Modal → Reversar a Pendiente / Rechazado
  → Fila Rechazado → [Gestionar] → Modal → Reversar a Aprobado / Pendiente

[Analista]
  /EventoLaboral  (sin restricción de sede)
  → Mismas acciones de gestión + filtro por sede
```

---

## 4. Rabbit Holes

- **Notificación al empleado:** el requerimiento menciona que el jefe "verá la solicitud en su bandeja". No construir notificaciones por correo en este ciclo — la visibilidad es suficiente. El correo de notificación es un pitch separado.
- **Bandeja propia del Analista:** el `Analista` ya tiene acceso total a `/EventoLaboral`. No construir una vista separada para él; usar los filtros existentes con `SedeId` desbloqueado.
- **Estados `Cancelado` y `EnRevision`:** el enum los define pero el requerimiento no especifica flujo. Excluir de las acciones del jefe en este ciclo.
- **Validación de solapamiento de eventos al aprobar:** al aprobar una solicitud de vacaciones, verificar que no solape con otra aprobada del mismo empleado. Usar la lógica ya existente en `IEventoLaboralService`.
- **Auditoría por campo:** el requerimiento pide auditoría de "estado anterior". Los campos disponibles (`AutorizadoPor`, `MotivoAnulacion`, `FechaModificacion`) no guardan el estado anterior explícitamente. Se registra en `MotivoAnulacion` el texto `"[Estado anterior: Aprobado] Motivo: ..."` como convención — no construir tabla de historial de estados en este ciclo.

---

## 5. No-Gos

- No se construye notificación por correo al empleado cuando el jefe actúa.
- No se construye una tabla de auditoría separada por campo.
- No se gestionan los estados `Cancelado` ni `EnRevision` desde la bandeja del jefe.
- No se modifica el diseño visual existente (misma paleta, componentes y layout).
- No se implementa la jerarquía multinivel (jefe del jefe del jefe) en este ciclo.
- No hay exportación de solicitudes.

---

---

# Plan de Ejecución de Pruebas

> Los casos de prueba están organizados por **scope** del pitch. Cada scope es una pieza completa verificable de forma independiente.

---

## Actores de Prueba

| Actor | Correo | Rol | Sede | Subordinados directos |
|---|---|---|---|---|
| Diana Vargas (crea solicitudes) | `diana.vargas@yopmail.com` | Operario | Medellín | — |
| Laura Sánchez (jefa de Diana) | `laura.sanchez@yopmail.com` | Regente | Medellín | Diana, Andrés, Jorge |
| Andrés Torres | `andres.torres@yopmail.com` | AuxiliarRegente | Medellín | — (reporta a Laura) |
| Carlos Rodríguez | `carlos.rodriguez@yopmail.com` | DirectorTecnico | Medellín | Laura, todos de Medellín |
| Sofía Gómez | `sofia.gomez@yopmail.com` | Analista | Medellín | Todas las sedes |
| Camila Ríos | `camila.rios@yopmail.com` | Operario | Bogotá | — (reporta a Hernán) |
| Hernán Castillo | `hernan.castillo@yopmail.com` | Regente | Bogotá | Camila, Natalia, Paula |

**Contraseña de todos los actores:** `Usuario1`  
**URL base:** `http://localhost:5002`

---

## Precondiciones

1. La aplicación corre en `http://localhost:5002`.
2. El seeding completo (`Seeding_Completo.sql`) está aplicado.
3. Todos los actores tienen `DebeCambiarPassword = 0` y estado `Activo`.
4. Los eventos de prueba usados en cada scope se restauran al estado original antes y después mediante el helper `reset_db()`.

---

## Scope A — Bandeja del jefe inmediato

### TC-APR-01 — Regente ve solicitudes Pendientes de sus subordinados

**Actor:** Laura Sánchez (`Regente`)  
**Precondición:** Existe al menos una solicitud en estado `Pendiente` de Diana Vargas (subordinada directa).

**Pasos:**
1. Iniciar sesión como `laura.sanchez@yopmail.com`.
2. Navegar a `/EventoLaboral`.
3. Observar la tabla de solicitudes.

**Resultado esperado:**
- La tabla muestra la solicitud de Diana en estado `Pendiente`.
- La tabla **no** muestra solicitudes de Camila Ríos (Bogotá, otra sede).
- La columna "Gestionar" tiene botón activo sobre la fila de Diana.

---

### TC-APR-02 — Analista ve solicitudes de todas las sedes

**Actor:** Sofía Gómez (`Analista`)

**Pasos:**
1. Iniciar sesión como `sofia.gomez@yopmail.com`.
2. Navegar a `/EventoLaboral`.
3. Observar la tabla sin filtros activos.

**Resultado esperado:**
- La tabla muestra solicitudes de **ambas sedes** (Medellín y Bogotá).
- El filtro de `Sede` está visible y funcional.
- La columna "Gestionar" tiene botón activo en todas las filas.

---

### TC-APR-03 — Operario NO ve botón Gestionar

**Actor:** Diana Vargas (`Operario`)

**Pasos:**
1. Iniciar sesión como `diana.vargas@yopmail.com`.
2. Navegar a `/EventoLaboral` (si no está bloqueado) o verificar desde `/Solicitud`.

**Resultado esperado:**
- Si `/EventoLaboral` muestra sus propias solicitudes: la columna "Gestionar" **no** tiene botón activo.
- O el sistema redirige/bloquea el acceso a `/EventoLaboral` para Operario.

---

### TC-APR-04 — Regente de Bogotá NO ve solicitudes de Medellín

**Actor:** Hernán Castillo (`Regente`, Bogotá)

**Pasos:**
1. Iniciar sesión como `hernan.castillo@yopmail.com`.
2. Navegar a `/EventoLaboral`.

**Resultado esperado:**
- La tabla muestra solo solicitudes de empleados de **Bogotá** (Camila, Natalia, Paula).
- No aparecen solicitudes de empleados de Medellín.

---

## Scope B — Aprobar y rechazar

### TC-APR-05 — Regente aprueba solicitud Pendiente de subordinado

**Actor:** Laura Sánchez (`Regente`)  
**Precondición:** Existe solicitud en estado `Pendiente` de Diana (ej. evento Id=X).

**Pasos:**
1. Iniciar sesión como `laura.sanchez@yopmail.com`.
2. Navegar a `/EventoLaboral?estado=Pendiente`.
3. Localizar la fila de Diana y hacer clic en **Gestionar**.
4. En el modal, seleccionar nuevo estado: `Aprobado`.
5. Dejar observación vacía (opcional).
6. Hacer clic en **Confirmar**.

**Resultado esperado:**
- Toast de éxito visible.
- La solicitud de Diana ya no aparece en la vista `Pendiente`.
- Al filtrar por `Aprobado`, la fila de Diana aparece.
- `AutorizadoPor` = "Laura Sánchez" (o el nombre del usuario autenticado).
- `FechaModificacion` actualizada.

---

### TC-APR-06 — Regente rechaza solicitud con observación obligatoria

**Actor:** Laura Sánchez (`Regente`)  
**Precondición:** Existe solicitud en estado `Pendiente` de Diana.

**Pasos:**
1. Iniciar sesión como `laura.sanchez@yopmail.com`.
2. Gestionar evento Pendiente de Diana → nuevo estado: `Rechazado`.
3. **Sin llenar** el campo observación.
4. Hacer clic en **Confirmar**.

**Resultado esperado (validación):**
- El sistema muestra mensaje de error: observación obligatoria al rechazar.
- El modal permanece abierto — el evento **no** fue modificado.

**Pasos (flujo exitoso):**
5. Ingresar observación: `"Sin cobertura disponible"`.
6. Confirmar.

**Resultado esperado (guardado):**
- La solicitud pasa a `Rechazado`.
- `MotivoAnulacion` = `"Sin cobertura disponible"`.
- Diana puede ver la observación en `/Solicitud`.

---

### TC-APR-07 — AuxiliarRegente puede aprobar solicitudes de sus subordinados

**Actor:** Andrés Torres (`AuxiliarRegente`)  
**Precondición:** Andrés tiene al menos un subordinado con solicitud `Pendiente`.

**Pasos:**
1. Iniciar sesión como `andres.torres@yopmail.com`.
2. Navegar a `/EventoLaboral?estado=Pendiente`.
3. Gestionar evento de su subordinado → nuevo estado: `Aprobado`.
4. Confirmar.

**Resultado esperado:**
- La aprobación se guarda sin errores.
- `AutorizadoPor` refleja el nombre de Andrés.

---

### TC-APR-08 — DirectorTecnico puede aprobar solicitudes de cualquier empleado de su sede

**Actor:** Carlos Rodríguez (`DirectorTecnico`)

**Pasos:**
1. Iniciar sesión como `carlos.rodriguez@yopmail.com`.
2. Navegar a `/EventoLaboral?estado=Pendiente`.
3. Gestionar evento de Diana (subordinada indirecta) → `Aprobado`.
4. Confirmar.

**Resultado esperado:**
- Aprobación registrada correctamente.

---

### TC-APR-09 — Rol Operario intenta aprobar (acceso denegado)

**Actor:** Diana Vargas (`Operario`)

**Pasos:**
1. Iniciar sesión como `diana.vargas@yopmail.com`.
2. Intentar `POST /EventoLaboral/GestionarEstado` con un `eventoId` válido y nuevo estado `Aprobado`.

**Resultado esperado:**
- El servidor responde con 403 Forbidden o redirección a página de acceso denegado.
- El estado del evento **no cambia**.

---

## Scope C — Reversión de decisiones

### TC-APR-10 — DirectorTecnico revierte Aprobado → Pendiente con observación

**Actor:** Carlos Rodríguez (`DirectorTecnico`)  
**Precondición:** Existe evento en estado `Aprobado` de un empleado de Medellín (ej. evento Id=23 de Camila — restaurado).

**Pasos:**
1. Iniciar sesión como `carlos.rodriguez@yopmail.com`.
2. Navegar a `/EventoLaboral?estado=Aprobado`.
3. Localizar evento aprobado → **Gestionar**.
4. Seleccionar nuevo estado: `Pendiente`.
5. Ingresar observación: `"Requiere revisión adicional"`.
6. Confirmar.

**Resultado esperado:**
- El evento pasa a `Pendiente`.
- `MotivoAnulacion` registra la observación.
- `AutorizadoPor` actualizado al nombre de Carlos.
- El evento reaparece en la vista `Pendiente`.

---

### TC-APR-11 — Analista revierte Rechazado → Aprobado

**Actor:** Sofía Gómez (`Analista`)  
**Precondición:** Existe evento en estado `Rechazado`.

**Pasos:**
1. Iniciar sesión como `sofia.gomez@yopmail.com`.
2. Navegar a `/EventoLaboral?estado=Rechazado`.
3. Gestionar evento → nuevo estado: `Aprobado`.
4. Ingresar observación: `"Aprobado tras revisión"`.
5. Confirmar.

**Resultado esperado:**
- El evento pasa a `Aprobado`.
- Datos de auditoría registrados correctamente.

---

### TC-APR-12 — Reversión requiere observación (campo obligatorio)

**Actor:** Analista o DirectorTecnico  
**Escenario:** Revertir cualquier estado sin llenar la observación.

**Pasos:**
1. Abrir modal de gestión sobre cualquier evento no `Pendiente`.
2. Seleccionar nuevo estado diferente al actual.
3. **No** llenar observación.
4. Confirmar.

**Resultado esperado:**
- El sistema muestra error: observación obligatoria al reversar.
- El modal permanece abierto sin guardar.

---

### TC-APR-13 — Regente NO puede reversar (no tiene permiso de reversión)

**Actor:** Laura Sánchez (`Regente`)  
**Nota:** Según el requerimiento, el `Regente` puede aprobar/rechazar pero la reversión la hacen `DirectorTecnico`, `AuxiliarRegente` y `Analista`. Verificar el comportamiento actual del sistema.

**Pasos:**
1. Iniciar sesión como `laura.sanchez@yopmail.com`.
2. Navegar a `/EventoLaboral?estado=Aprobado`.
3. Intentar gestionar un evento `Aprobado` → nuevo estado: `Pendiente`.

**Resultado esperado:**
- Si el sistema aplica la restricción: la opción de reversar no está disponible para `Regente` o el servidor responde con error.
- Si el sistema aún no aplica la restricción: documentar como **hallazgo** para el siguiente ciclo.

---

## Scope D — Visibilidad del empleado

### TC-APR-14 — Empleado ve estado actualizado en /Solicitud

**Actor:** Diana Vargas (`Operario`)  
**Precondición:** Su solicitud fue aprobada en TC-APR-05.

**Pasos:**
1. Iniciar sesión como `diana.vargas@yopmail.com`.
2. Navegar a `/Solicitud`.

**Resultado esperado:**
- La solicitud aparece con estado `Aprobado`.
- La columna de observación muestra el valor registrado por el jefe (vacío si no se ingresó).

---

### TC-APR-15 — Empleado ve observación de rechazo en /Solicitud

**Actor:** Diana Vargas (`Operario`)  
**Precondición:** Su solicitud fue rechazada con observación en TC-APR-06.

**Pasos:**
1. Iniciar sesión como `diana.vargas@yopmail.com`.
2. Navegar a `/Solicitud`.

**Resultado esperado:**
- La solicitud aparece con estado `Rechazado`.
- La observación `"Sin cobertura disponible"` es visible en la fila.

---

### TC-APR-16 — Empleado NO puede cambiar el estado de su propia solicitud

**Actor:** Diana Vargas (`Operario`)

**Pasos:**
1. Iniciar sesión como `diana.vargas@yopmail.com`.
2. Intentar `POST /EventoLaboral/GestionarEstado` con un eventoId propio y nuevo estado `Aprobado`.

**Resultado esperado:**
- El servidor responde 403 o el botón de gestión no está disponible en `/Solicitud`.

---

## Resumen de Casos de Prueba

| # | Scope | Descripción | Actor |
|---|---|---|---|
| TC-APR-01 | A | Regente ve solicitudes Pendientes de subordinados | Regente |
| TC-APR-02 | A | Analista ve todas las sedes | Analista |
| TC-APR-03 | A | Operario no tiene botón Gestionar | Operario |
| TC-APR-04 | A | Regente Bogotá no ve solicitudes de Medellín | Regente |
| TC-APR-05 | B | Regente aprueba solicitud Pendiente | Regente |
| TC-APR-06 | B | Regente rechaza — observación obligatoria | Regente |
| TC-APR-07 | B | AuxiliarRegente aprueba subordinado | AuxiliarRegente |
| TC-APR-08 | B | DirectorTecnico aprueba cualquier empleado de su sede | DirectorTecnico |
| TC-APR-09 | B | Operario intenta aprobar → 403 | Operario |
| TC-APR-10 | C | DirectorTecnico revierte Aprobado → Pendiente | DirectorTecnico |
| TC-APR-11 | C | Analista revierte Rechazado → Aprobado | Analista |
| TC-APR-12 | C | Reversión sin observación → bloqueada | Analista / Director |
| TC-APR-13 | C | Regente intenta reversar → verificar comportamiento | Regente |
| TC-APR-14 | D | Empleado ve estado actualizado en /Solicitud | Operario |
| TC-APR-15 | D | Empleado ve observación de rechazo | Operario |
| TC-APR-16 | D | Empleado no puede cambiar estado propio | Operario |

---

## Comando de Ejecución

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"
$env:PYTHONIOENCODING='utf-8'
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\aprobacion-solicitudes-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null
.venv\Scripts\python.exe -m pytest "Documentos/Pruebas/Playwright/Plan-AprobacionSolicitudes.py" -v --headed --slowmo 800 -s 2>&1 | Tee-Object -FilePath $informe
Write-Host "`nInforme: $informe"
```

> El archivo `.py` de automatización Playwright se crea en una sesión separada referenciando este plan.
