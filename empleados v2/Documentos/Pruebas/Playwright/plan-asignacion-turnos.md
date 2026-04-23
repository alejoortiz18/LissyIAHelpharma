# Casos de Prueba - Gestión de Asignación de Turnos

## Objetivo
Validar las reglas de negocio relacionadas con la asignación, edición, eliminación y visualización de turnos para personal subordinado.

---

# Alcance Funcional

Solo los usuarios que tengan personal a cargo podrán asignar turnos a sus subordinados.

---

# Casos de Prueba

## CP-001 - Validar que solo usuarios con personal a cargo puedan asignar turnos

**Precondiciones:**
- Existe un usuario con subordinados.
- Existe un usuario sin subordinados.

**Pasos:**
1. Iniciar sesión con usuario que tiene personal a cargo.
2. Intentar asignar turno a subordinado.
3. Iniciar sesión con usuario sin subordinados.
4. Intentar asignar turno.

**Resultado Esperado:**
- El usuario con subordinados puede asignar turnos.
- El usuario sin subordinados no puede acceder a la opción o recibe mensaje de restricción.

---

## CP-002 - Validar asignación correcta de turno al usuario subordinado

**Precondiciones:**
- Usuario jefe autenticado.
- Subordinado activo.

**Pasos:**
1. Seleccionar subordinado.
2. Seleccionar turno disponible.
3. Guardar asignación.

**Resultado Esperado:**
- El turno queda asignado correctamente al subordinado.
- El registro queda almacenado en la tabla de asignación de turnos.
- Se registra usuario creador, fecha y hora.

---

## CP-003 - Validar edición de turno asignado por jefe inmediato

**Precondiciones:**
- Existe turno previamente asignado.
- Usuario autenticado es jefe inmediato del subordinado.

**Pasos:**
1. Consultar asignación existente.
2. Editar turno.
3. Guardar cambios.

**Resultado Esperado:**
- El sistema permite editar el turno.
- La información queda actualizada correctamente.

---

## CP-004 - Validar edición de turno asignado por jefe del jefe

**Precondiciones:**
- Existe turno asignado.
- Usuario autenticado es superior jerárquico del jefe inmediato.

**Pasos:**
1. Consultar asignación existente.
2. Modificar turno.
3. Guardar cambios.

**Resultado Esperado:**
- El sistema permite editar el turno.
- Se actualiza correctamente la asignación.

---

## CP-005 - Validar restricción de edición por usuario no autorizado

**Precondiciones:**
- Existe turno asignado.
- Usuario autenticado no es jefe inmediato ni jefe superior.

**Pasos:**
1. Intentar editar turno asignado.

**Resultado Esperado:**
- El sistema bloquea la edición.
- Muestra mensaje de permisos insuficientes.

---

## CP-006 - Validar eliminación de turno por regente asignado

**Precondiciones:**
- Existe turno asignado.
- Usuario autenticado es quien realizó la asignación.

**Pasos:**
1. Consultar turno asignado.
2. Seleccionar eliminar.
3. Confirmar acción.

**Resultado Esperado:**
- El sistema elimina la asignación correctamente.

---

## CP-007 - Validar eliminación de turno por jefe

**Precondiciones:**
- Existe turno asignado.
- Usuario autenticado es jefe inmediato o superior.

**Pasos:**
1. Buscar turno asignado.
2. Eliminar registro.

**Resultado Esperado:**
- El sistema permite eliminar la asignación.

---

## CP-008 - Validar restricción de eliminación por usuario no autorizado

**Precondiciones:**
- Existe turno asignado.
- Usuario sin permisos.

**Pasos:**
1. Intentar eliminar turno.

**Resultado Esperado:**
- El sistema bloquea la acción.
- Muestra mensaje de acceso denegado.

---

## CP-009 - Validar visualización en turnos vigentes

**Precondiciones:**
- Existe turno asignado activo.

**Pasos:**
1. Asignar turno al subordinado.
2. Consultar módulo de turnos vigentes.

**Resultado Esperado:**
- El turno aparece en la lista de turnos vigentes.
- Los datos coinciden con la asignación realizada.

---

## CP-010 - Validar que no aparezcan turnos no asignados en turnos vigentes

**Precondiciones:**
- Usuario sin turno asignado.

**Pasos:**
1. Consultar turnos vigentes.

**Resultado Esperado:**
- No se muestran turnos inexistentes o no asignados.

---

# Criterios de Aceptación

- Solo jefes con personal a cargo pueden asignar turnos.
- Solo jefe inmediato o jefe superior pueden editar.
- Solo regente asignador o jefe pueden eliminar.
- Toda asignación válida debe reflejarse en turnos vigentes.
- Deben existir controles de permisos y trazabilidad.

---