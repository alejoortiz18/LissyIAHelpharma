# Shape Up Pitch — Gestión de Asignación de Turnos

> Refinamiento del plan de pruebas original aplicando la metodología **Shape Up** de Basecamp.
> El documento define el problema acotado, el apetito de inversión, la solución en términos de scopes,
> los rabbit holes identificados, los no-gos explícitos y los criterios de aceptación por scope.

---

## 1. Problema

Los jefes inmediatos y superiores no tienen una forma directa de asignar o modificar el turno de trabajo de sus subordinados desde el sistema. Hoy, cuando un jefe necesita cambiar la jornada de un empleado, lo comunica verbalmente o por correo, y el cambio queda fuera del sistema hasta que alguien con acceso lo registra manualmente. Esto genera:

- Turnos vigentes que no reflejan la realidad operativa.
- Empleados sin turno asignado visibles en el módulo de turnos como si estuvieran disponibles en cualquier jornada.
- Ausencia de trazabilidad sobre quién autorizó cada cambio de turno y cuándo.
- Usuarios sin personal a cargo que accidentalmente pueden ver o intentar modificar turnos ajenos.

**Historia representativa:** El jefe de la sede Centro quiere asignar turno nocturno a un empleado que antes trabajaba de día. Hoy no existe un flujo en el sistema para hacer eso; tiene que pedirle al administrador del sistema que lo registre. Si el administrador no lo hace a tiempo, el empleado sigue apareciendo con jornada diurna en los reportes.

---

## 2. Apetito

**Small Batch — 2 semanas** (1 programador + 1 QA)

La lógica de jerarquía ya existe en el modelo de empleados (`JefeInmediatoId`). Las plantillas de turno ya están en el sistema. Lo que falta es exponer el flujo de asignación y edición de forma controlada con los permisos correctos. No es un proyecto nuevo; es completar una funcionalidad ya modelada.

> **Tiempo fijo, alcance variable:** si durante la implementación resulta complejo el control de permisos por jerarquía multinivel (jefe del jefe), esa regla puede quedar para un siguiente ciclo. La asignación por jefe inmediato directo es suficiente para el MVP.

---

## 3. Solución

### Scopes identificados

La solución se organiza en **cuatro scopes** independientes que pueden completarse en paralelo o secuencialmente.

---

### Scope A — Asignación de turno (jefe → subordinado)

El jefe puede asignar un turno a cualquier empleado que reporte directamente a él.

**Elementos:**
- Botón **"Asignar / cambiar turno"** visible únicamente para usuarios que tienen al menos un subordinado activo.
- Modal con dos campos: `Plantilla de turno` (select con las plantillas activas) y `Fecha de vigencia` (datepicker).
- Al guardar, el sistema registra: `EmpleadoId`, `PlantillaTurnoId`, `FechaVigencia`, `ProgramadoPor` (usuario autenticado), `FechaCreacion`.
- El turno asignado aparece en la tabla de **turnos vigentes** del módulo de horarios.

```
[Perfil empleado — Pestaña Horario]
  → [Botón "Asignar / cambiar turno"]  ← visible solo si el usuario tiene subordinados
       → [Modal]
            → Select: Plantilla de turno  (obligatorio)
            → Datepicker: Fecha de vigencia  (obligatorio)
            → [Guardar]  →  POST /Turno/AsignarTurnoAjax
            → [Cancelar] / [X] → cierra sin guardar
```

**Validaciones:**
- Ambos campos son obligatorios. Si alguno está vacío, el botón Guardar muestra un toast de error y el modal permanece abierto.
- Solo usuarios con `JefeInmediatoId` referenciado al menos por un empleado activo pueden ver el botón.

---

### Scope B — Edición de asignación existente

El jefe inmediato o el jefe superior pueden modificar una asignación ya registrada.

**Elementos:**
- Tabla de historial de asignaciones en la pestaña Horario, ordenada por `FechaVigencia` descendente.
- Columnas: Plantilla, Fecha de vigencia, Asignado por.
- Botón **"Editar"** por fila, visible únicamente si el usuario autenticado tiene permisos sobre ese empleado.
- Al pulsar Editar, el mismo modal del Scope A se abre en modo edición: pre-poblado con los datos de esa fila, título cambia a "Editar asignación".
- Al guardar: `PUT /Turno/EditarAsignacionAjax` actualiza `PlantillaTurnoId` y `FechaVigencia`. El campo `ProgramadoPor` **no se sobreescribe** — preserva al asignador original.

```
[Tabla historial de asignaciones]
  Plantilla | Fecha vigencia | Asignado por | [Editar]
  → [Editar] → abre Modal (pre-poblado)
                   → [Guardar] → POST /Turno/EditarAsignacionAjax
```

**Regla de autorización:**
- Puede editar: el jefe inmediato del empleado **o** el jefe del jefe inmediato.
- No puede editar: cualquier otro usuario, aunque tenga rol de Jefe en otra sede.

---

### Scope C — Eliminación de asignación

El usuario que realizó la asignación **o** el jefe inmediato del empleado pueden eliminarla.

**Elementos:**
- Botón **"Eliminar"** por fila en la tabla de historial (visible **solo para el asignador original o el jefe inmediato del empleado**, verificado por `ProgramadoPorUsuarioId` y `JefeInmediatoId` en la vista).
- Confirmación inline (dialog de confirmación sin modal separado).
- Al confirmar: `DELETE /Turno/EliminarAsignacionAjax`.
- El turno eliminado desaparece del historial y deja de aparecer en turnos vigentes.

```
[Tabla historial]
  → [Eliminar] → dialog: "¿Confirmar eliminación?" → [Sí] / [No]
                     → [Sí] → DELETE /Turno/EliminarAsignacionAjax
```

**Regla de autorización:**
- Puede eliminar: quien realizó la asignación (`ProgramadoPor`) **o** el jefe inmediato del empleado.
- No puede eliminar: usuarios sin relación jerárquica con ese empleado.

---

### Scope D — Visualización en turnos vigentes

Los turnos asignados deben aparecer correctamente en el módulo de horarios y en el perfil del empleado.

**Elementos:**
- El módulo `/Turno/Vigentes` lista todos los empleados que tienen al menos una asignación activa (última `FechaVigencia` ≤ hoy).
- Los empleados sin turno asignado **no aparecen** en esa lista (no se muestran con turno vacío).
- Los datos mostrados coinciden con los de la asignación registrada en base de datos.
- La sección **"Turno asignado"** en la pestaña Horario del perfil muestra la plantilla vigente (la asignación más reciente con `FechaVigencia` ≤ hoy) con la cuadrícula de días. Si no existe asignación vigente, muestra "Sin turno asignado".

---

## 4. Rabbit Holes

| Riesgo | Descripción | Mitigación |
|---|---|---|
| **Jerarquía multinivel** | Determinar si el "jefe del jefe" puede editar/eliminar requiere recorrer el árbol jerárquico hacia arriba, lo que puede ser costoso y complejo. | Limitar en este ciclo a dos niveles: jefe inmediato y su jefe directo. Cualquier nivel superior queda para el siguiente ciclo. |
| **Conflicto de fechas de vigencia** | Si se permiten múltiples asignaciones activas para el mismo empleado, la lógica de "turno vigente" puede retornar resultados ambiguos. | Definir claramente que la última asignación por `FechaVigencia DESC` es la vigente. No bloquear inserciones con solapamiento; solo considerar la más reciente. |
| **Eliminación de la única asignación** | Si se elimina la única asignación de un empleado, ese empleado queda sin turno. El sistema debe manejar ese estado sin errores. | La pantalla de perfil debe mostrar "Sin turno asignado" en lugar de un error. No es necesario bloquear la eliminación. |
| **Permisos en usuarios con múltiples roles** | Un usuario que es jefe en una sede pero también AuxiliarRegente en otra puede tener acceso inesperado. | El control de autorización se hace siempre verificando el `JefeInmediatoId` del empleado objetivo, no el rol genérico del usuario autenticado. |
| **Antiforgery en peticiones AJAX** | Si el token CSRF no se incluye correctamente en las llamadas AJAX, los endpoints devuelven 400. | Incluir `__RequestVerificationToken` en el `FormData` de cada fetch. Verificado en implementación actual. |

---

## 5. No-Gos

- **No hay notificaciones** al empleado cuando se le asigna o cambia el turno (correo, push notification). Eso es un módulo de comunicaciones aparte.
- **No hay validación de solapamiento** de turnos con eventos laborales (vacaciones, incapacidades). El sistema registra el turno independientemente de si hay un evento activo.
- **No hay importación masiva** de asignaciones (desde Excel o CSV).
- **No hay árbol organizacional visual** para seleccionar el empleado. La asignación siempre se hace desde el perfil individual del empleado.
- **No hay historial de quién editó qué campo** a nivel de auditoría granular. Solo se conserva el `ProgramadoPor` original de cada asignación; las ediciones posteriores no sobreescriben ese campo.
- **No se construye un endpoint de reportes** de turnos en este ciclo (ej. "todos los empleados con turno nocturno esta semana"). Eso corresponde al módulo de reportes.

---

## 6. Criterios de Aceptación por Scope

Los criterios se verifican con pruebas Playwright automatizadas. Cada caso de prueba (CP) se mapea directamente a un scope.

---

### Scope A — Asignación

| ID | Criterio | Cómo se verifica |
|---|---|---|
| CP-001a | El botón "Asignar / cambiar turno" es visible para usuario con subordinados | Login como Jefe → ir a perfil de subordinado → botón visible |
| CP-001b | El botón no aparece para usuario sin subordinados | Login como Operario → ir a perfil → botón ausente |
| CP-002a | El modal se abre sin navegar a otra página | Click en botón → URL no cambia → `#modal-turno` visible |
| CP-002b | El modal se cierra con Cancelar y con X | Click Cancelar / X → modal oculto |
| CP-002c | Formulario vacío no envía y muestra error | Click Guardar sin datos → modal permanece abierto → toast de error |
| CP-002d | Asignación válida guarda y recarga la pestaña horario | Seleccionar plantilla + fecha → Guardar → recarga en tab horario |

---

### Scope B — Edición

| ID | Criterio | Cómo se verifica |
|---|---|---|
| CP-003a | El botón Editar aparece en cada fila del historial (usuario autorizado) | Login como Jefe → perfil subordinado → tabla historial → botón Editar visible |
| CP-003b | El modal se abre pre-poblado con los datos de la fila | Click Editar → select y datepicker muestran los valores actuales |
| CP-003c | El título del modal cambia a "Editar asignación" | `#turno-title` contiene "Editar" |
| CP-003d | Guardar cambios actualiza el registro y recarga la pestaña | Cambiar fecha → Guardar → nueva fecha visible en historial |
| CP-004  | Jefe superior también puede editar la asignación | Login como jefe del jefe → mismos botones disponibles |
| CP-005  | Usuario no autorizado no puede editar | Login como empleado sin relación → botón Editar ausente |

---

### Scope C — Eliminación

| ID | Criterio | Cómo se verifica |
|---|---|---|
| CP-006  | Regente asignador puede eliminar la asignación | Login como quien la creó → botón Eliminar → confirmación → registro desaparece |
| CP-007  | Jefe inmediato puede eliminar la asignación | Login como jefe directo → botón Eliminar disponible → elimina correctamente |
| CP-008  | Usuario no autorizado no puede eliminar | Login sin relación jerárquica → botón Eliminar ausente |

---

### Scope D — Visualización en turnos vigentes

| ID | Criterio | Cómo se verifica |
|---|---|---|
| CP-009  | Empleado con turno asignado aparece en la lista de turnos vigentes | Asignar turno → ir a `/Turno/Vigentes` → empleado en la lista con datos correctos |
| CP-010  | Empleado sin turno asignado no aparece en turnos vigentes | Usuario sin asignación → `/Turno/Vigentes` → no aparece en la lista |
| CP-012  | Sección "Turno asignado" muestra plantilla cuando `FechaVigencia` ≤ hoy | Asignar turno con fecha pasada → perfil empleado → cuadrícula de días visible |

---

### Bug 1 — Botones per-row y preservación del asignador (correctivos)

| ID | Criterio | Cómo se verifica |
|---|---|---|
| CP-011  | Editar una asignación NO sobreescribe al asignador original | Carlos asigna → edita la fila → columna "Asignado por" sigue mostrando a Carlos; botón Editar sigue visible para Carlos |

---

## 7. Datos de Prueba Requeridos

| Elemento | Datos del sistema |
|---|---|
| Usuario jefe con subordinados | `carlos.rodriguez@yopmail.com` / `Usuario1` (ID=2, Jefe, SedeId=1) |
| Empleado subordinado | ID=4, `Andrés Felipe Torres Ruiz`, JefeInmediatoId=2 |
| Usuario sin subordinados | Cualquier empleado con rol Operario |
| Plantillas de turno activas | Mínimo 1 plantilla en estado `Activa` en `PlantillasTurno` |
| URL base | `http://localhost:5002` |

---

## 8. Scopes en el Hill Chart

```
Scope A — Asignación         [████████████████████] 100% — implementado y probado
Scope B — Edición            [████████████████████] 100% — implementado y probado
Scope C — Eliminación        [████████████████████] 100% — implementado y probado
Scope D — Turnos vigentes    [████████████████████] 100% — implementado y probado
Bug 1  — Botones per-row     [████████████████████] 100% — corregido y probado (CP-011)
Bug 2  — Turno actual null   [████████████████████] 100% — corregido y probado (CP-012)
```

> Todos los scopes y correctivos están **completados** (build verde, **19/19 pruebas Playwright pasando**).

### Resumen de cambios correctivos aplicados

| Bug | Síntoma | Causa raíz | Fix aplicado |
|---|---|---|---|
| Bug 1 | Botones Editar/Eliminar visibles para usuarios sin autorización tras editar | `EditarAsignacionAsync` sobreescribía `ProgramadoPor`; la vista no hacía chequeo per-fila | Se eliminó la línea `asignacion.ProgramadoPor = usuarioId`; se añadió `ProgramadoPorUsuarioId` a `AsignacionTurnoDto`; la vista verifica `h.ProgramadoPorUsuarioId == currentUsuarioId \|\| esJefeInmediatoDelEmpleado` por fila |
| Bug 2 | Sección "Turno asignado" siempre mostraba "Sin turno asignado" | `PlantillaTurnoActualNombre` nunca se populaba en `MapToDto`; la lógica para derivar `TurnoActual` era incorrecta | Se reemplazó la lógica por: obtener el historial primero, tomar la asignación más reciente con `FechaVigencia ≤ today`, y cargar su plantilla con detalles |

---

*Documento actualizado el 23/04/2026 — Metodología Shape Up (Basecamp) — Ryan Singer*
