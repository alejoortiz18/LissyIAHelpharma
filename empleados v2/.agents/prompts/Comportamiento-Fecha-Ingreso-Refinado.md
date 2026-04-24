# Pitch: Vinculación Laboral y Fecha de Ingreso Real del Empleado

> Formato: Shape Up Pitch — [basecamp.com/shapeup](https://basecamp.com/shapeup)

---

## 1. Problema

Actualmente no existe una distinción clara entre la **fecha en que una persona empezó a trabajar realmente en la empresa** y la **fecha en que fue contratada directamente**. Esto genera confusión al consultar la antigüedad de empleados que ingresaron primero por empresa temporal y luego fueron absorbidos.

**Caso concreto:** Un empleado lleva 3 años prestando servicios en la empresa, pero los primeros 2 años fueron a través de una empresa temporal. Al momento del contrato directo, el sistema registra solo 1 año de antigüedad, lo cual no refleja la realidad laboral ni cumple con las expectativas del área de RRHH.

Sin esta diferenciación, la empresa no puede responder con precisión a la pregunta:
> *"¿Desde cuándo trabaja realmente esta persona en nuestra organización?"*

---

## 2. Appetite

**Alcance:** Small Batch — trabajo de configuración de lógica de negocio en modelo de datos y UI del perfil de empleado.

Esta es una regla funcional acotada. No requiere nuevos módulos ni rediseño de pantallas. El cambio afecta:
- El modelo de datos (`Empleado` / `ContratoTemporal`)
- La lógica de cálculo de `FechaVinculacion` (fecha de ingreso real)
- La visualización en el perfil del empleado

Se espera resolver dentro del ciclo actual sin bloquear otras funcionalidades.

---

## 3. Solución

### Campos involucrados

| Campo | Descripción |
|---|---|
| `FechaVinculacion` | Fecha real desde la que la persona trabaja en la empresa (por temporal o directamente). Siempre visible en el perfil. |
| `FechaInicioContrato` | Fecha del contrato directo con la empresa. Solo aplica cuando hay contratación directa. |
| `FechaInicioTemporal` | Fecha de inicio por empresa temporal. Origen de `FechaVinculacion` cuando aplica. |

### Comportamiento esperado por escenario

| Escenario | `FechaVinculacion` (mostrada en perfil) | `FechaInicioContrato` |
|---|---|---|
| Ingresó por temporal → luego contrato directo | Fecha de inicio por la temporal | Fecha del contrato directo |
| Ingresó directamente desde el inicio | Fecha de inicio del contrato directo | Fecha de inicio del contrato directo |
| Solo por temporal (sin contrato directo aún) | Fecha de inicio por la temporal | Vacío / No aplica |

### Lógica de derivación de `FechaVinculacion`

```
Si existe FechaInicioTemporal
    → FechaVinculacion = FechaInicioTemporal
Si no existe FechaInicioTemporal
    → FechaVinculacion = FechaInicioContrato
```

Esta lógica debe aplicarse tanto al crear como al editar el perfil del empleado.

---

## 4. Rabbit Holes

- **No recalcular antigüedad automáticamente al ingresar el contrato directo.** La `FechaVinculacion` ya fue fijada al registrar la entrada por temporal; no debe sobreescribirse al agregar `FechaInicioContrato`.
- **El campo `FechaVinculacion` no debe ser editable directamente por el usuario.** Es derivado. Editarlo manualmente podría generar inconsistencias. Si se necesita corregir, debe hacerse ajustando la fecha de origen (temporal o contrato).
- **No asumir que todos los empleados con empresa temporal fueron luego absorbidos.** Un empleado puede tener `FechaInicioTemporal` sin `FechaInicioContrato` y eso es válido.

---

## 5. No-Gos

- **No se contempla historial de múltiples contratos temporales** para este ciclo. Solo se registra el inicio de la vinculación más antigua.
- **No se construirán reportes de antigüedad** en este alcance. El campo `FechaVinculacion` queda disponible como insumo para futuros reportes.
- **No se migrarán registros históricos** de empleados existentes en este ciclo. La regla aplica a nuevos registros y ediciones explícitas.
- **No se valida contra sistemas externos** de nómina o empresa temporal. Los datos se ingresan manualmente por RRHH.
