# Pitch — Control Jerárquico de Plantillas de Horario

> Refinamiento aplicando la metodología **Shape Up** de Basecamp.
> Este pitch cubre la restricción de visibilidad y asignación de plantillas de horario según la jerarquía de cada jefe dentro de la organización.

---

## 1. Problema

Actualmente, cualquier jefe puede crear plantillas de horarios y todas quedan visibles y disponibles para **todos los jefes de la organización**, independientemente de su nivel jerárquico o del personal que tengan a cargo. Esto genera:

- Contaminación visual: un jefe ve decenas de plantillas que no le corresponden.
- Asignaciones incorrectas: un jefe puede utilizar —o sobrescribir— una plantilla creada por otro jefe de distinta área o nivel.
- Sin trazabilidad: no es posible saber quién creó cada plantilla ni para qué equipo fue pensada.

**Historia representativa:** Un jefe de turno de una sede ve en el selector de plantillas 40 horarios mezclados, muchos de ellos creados por jefes de otras sedes o de niveles superiores. Al asignar un horario a uno de sus colaboradores, elige por error una plantilla que no corresponde a ese equipo. El colaborador trabaja con un horario incorrecto durante semanas sin que nadie lo detecte.

---

## 2. Apetito

**Small Batch — 2 semanas** (1 programador + validación con 1 diseñador)

El módulo de horarios ya existe. No se construye desde cero: se añade una capa de filtrado y restricción jerárquica sobre la lógica existente. Dos semanas son suficientes para implementar las reglas de visibilidad, las validaciones en el servicio y los ajustes en las vistas. Si la solución requiere más tiempo que eso, se recorta el alcance — no se extiende el ciclo.

---

## 3. Solución

### Regla central: la plantilla pertenece al jefe que la crea

Cada plantilla de horario queda vinculada al `EmpleadoId` del jefe que la creó (`CreadoPorId`). Este campo determina toda la lógica de visibilidad y asignación.

---

### Visibilidad de plantillas

| Actor | ¿Qué plantillas puede ver? |
|---|---|
| Jefe de cualquier nivel | Solo las que él mismo creó |
| Subordinado (colaborador) | Solo el horario que su jefe le asignó |
| Sin asignación | No ve ninguna plantilla |

No existe una vista global de plantillas. Cada jefe opera en su propio catálogo.

---

### Asignación de horarios

Un jefe puede asignar una de sus plantillas **únicamente a colaboradores que se encuentren dentro de su línea jerárquica directa o subordinada.**

```
Jefe A (nivel 1)
 └── Jefe B (nivel 2)  ← subordinado directo de A
       └── Empleado C  ← subordinado indirecto de A

Jefe A puede asignar plantillas a: Jefe B, Empleado C
Jefe B puede asignar plantillas a: Empleado C
Jefe B NO puede asignar plantillas a: Jefe A ni a empleados de otras ramas
```

La lista de colaboradores disponibles en el selector de asignación se construye dinámicamente consultando la jerarquía real registrada en el sistema (`JefeId` del empleado).

---

### Restricción de autoasignación

Ningún jefe puede asignarse a sí mismo una plantilla de horario. La validación debe aplicarse tanto en el frontend (el usuario no aparece en su propio selector) como en el backend (`HorarioService`) antes de persistir.

---

### Flujo resumido (breadboard)

```
[Módulo Horarios]
  → [Mis Plantillas]          ← solo las creadas por el jefe en sesión
      → Crear nueva plantilla
      → Editar / Eliminar (solo propias)
      → [Asignar a colaborador]
            → Selector: solo subordinados directos e indirectos
            → Validación: el jefe no aparece en la lista (autoasignación bloqueada)

[Colaborador en sesión]
  → [Mi Horario]              ← solo el horario que le fue asignado por su jefe
      → Vista de solo lectura
      → Sin acceso a plantillas
```

---

### Cambios técnicos necesarios

| Capa | Cambio |
|---|---|
| **Base de datos** | Agregar columna `CreadoPorId` (FK a `Empleados`) en la tabla de plantillas de horario |
| **Domain / Models** | Añadir propiedad `CreadoPorId` a la entidad `PlantillaHorario` |
| **HorarioService** | Filtrar plantillas por `CreadoPorId == usuarioEnSesion` en todos los métodos de consulta |
| **HorarioService** | Validar que el colaborador destino pertenece a la jerarquía del jefe antes de asignar |
| **HorarioService** | Rechazar asignación si `colaboradorId == jefeId` (autoasignación) |
| **Vistas / Controllers** | Actualizar selectores para mostrar solo plantillas propias y solo subordinados válidos |

---

## 4. Rabbit Holes

- **Jerarquía multi-nivel:** El sistema ya tiene registrado el `JefeId` de cada empleado. Para recorrer subordinados indirectos (nietos, bisnietos, etc.) se necesita una consulta recursiva (CTE en SQL Server o recorrido en el servicio). Hay que decidir si se navega toda la jerarquía hacia abajo o solo un nivel. **Decisión recomendada:** navegar toda la jerarquía hacia abajo para mantener coherencia con el resto del sistema (historial, aprobaciones, etc.). Si esto resulta complejo para el tiempo del ciclo, se limita a **un nivel de profundidad** como primera versión.

- **Plantillas huérfanas:** Si un jefe es desvinculado del sistema, sus plantillas quedan sin propietario activo. No se resuelve en este ciclo. Las plantillas existentes permanecen visibles para el nuevo jefe asignado al área solo si se hace una reasignación manual. Esto se documenta como deuda técnica conocida.

- **Migración de datos existentes:** Las plantillas actuales no tienen `CreadoPorId`. Al aplicar la migración, este campo queda `NULL`. Se debe decidir si se ocultan esas plantillas hasta que un jefe las reclame, o si se asignan automáticamente a un administrador del sistema. **Decisión recomendada:** asignarlas al primer administrador registrado para no perder datos, con una nota visible de que requieren revisión.

---

## 5. No-Gos

Los siguientes puntos están **explícitamente fuera del alcance** de este ciclo:

- ❌ No se construye un panel de administración global de plantillas para roles de administrador o superusuario.
- ❌ No se implementa la capacidad de compartir o transferir plantillas entre jefes.
- ❌ No se crean notificaciones cuando se asigna o modifica un horario.
- ❌ No se modifica la estructura interna de las plantillas (días, turnos, franjas horarias); solo se restringe quién puede verlas y asignarlas.
- ❌ No se construye historial de cambios de propietario de plantilla.
- ❌ No se agrega lógica de herencia de plantillas entre niveles jerárquicos (un jefe superior no "hereda" las plantillas de sus subordinados).

---

## Criterios de aceptación

- [ ] Un jefe, al ingresar al módulo de horarios, solo ve las plantillas que él mismo creó.
- [ ] Al intentar asignar un horario, el selector de colaboradores muestra únicamente a los empleados dentro de su jerarquía directa e indirecta.
- [ ] El jefe no aparece como opción en el selector de asignación (autoasignación bloqueada en frontend y backend).
- [ ] Un colaborador que accede al sistema solo puede ver el horario que su jefe le asignó; no tiene acceso al listado de plantillas.
- [ ] Las validaciones del `HorarioService` rechazan en backend cualquier intento de asignación fuera de jerarquía, aunque se eluda el frontend.
- [ ] Todos los empleados con plantillas existentes (migración) quedan bajo el administrador del sistema y son visibles para su gestión posterior.
