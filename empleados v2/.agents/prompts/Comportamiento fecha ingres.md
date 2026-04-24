# Regla Funcional: Vinculación Laboral y Fecha de Ingreso

## Objetivo

Definir el comportamiento de los campos relacionados con la antigüedad laboral del empleado dentro de la empresa, diferenciando entre ingreso por empresa temporal y contratación directa.

---

## Campos involucrados

* **Contrato temporal**: Información asociada a una empresa temporal.
* **Vinculación laboral / Fecha de ingreso**: Fecha desde la cual la persona comenzó a trabajar realmente en la empresa.
* **FechaInicioContrato**: Fecha en la que la empresa realizó contratación directa al empleado.

---

## Reglas de negocio

## 1. Empleado que ingresó por empresa temporal

Cuando una persona inicia labores mediante una empresa temporal y presta servicios en la compañía:

* La fecha en que comenzó por la temporal debe considerarse como la **fecha real de ingreso a la empresa**.
* Esta fecha debe mostrarse en **Vinculación laboral** o **Fecha de ingreso**.

Si posteriormente la empresa decide contratarlo directamente:

* El campo **FechaInicioContrato** almacenará la fecha del contrato directo.
* **No debe perderse la antigüedad anterior** trabajada por temporal.
* Debe mantenerse como fecha inicial de vinculación la fecha en la que ingresó mediante la temporal.

---

## 2. Empleado contratado directamente por la empresa

Si el trabajador ingresó desde el comienzo contratado directamente por la empresa:

* **FechaInicioContrato** contendrá la fecha de inicio del contrato.
* El campo relacionado con temporal quedará vacío o no aplicará.

---

## Tabla de comportamiento esperado

| Escenario                                     | Vinculación laboral / Fecha ingreso | FechaInicioContrato           |
| --------------------------------------------- | ----------------------------------- | ----------------------------- |
| Ingreso por temporal y luego contrato directo | Fecha de ingreso por temporal       | Fecha de contrato directo     |
| Ingreso directo con la empresa                | Fecha inicio contrato directo       | Fecha inicio contrato directo |

---

## Resultado esperado

La empresa debe poder consultar **desde cuándo una persona trabaja realmente en la organización**, independientemente de si inició por empresa temporal o por contratación directa.
