# Mejora Funcional: Eventos Laborales - Tab Historial del Perfil del Usuario

## Objetivo

Implementar mejoras en la sección **Eventos Laborales** ubicada dentro del tab **Historial** del perfil del usuario, permitiendo mayor trazabilidad, control y análisis de novedades laborales.

---

# 1. Nueva columna: Días

## Requerimiento

Agregar una nueva columna llamada **Días** en la tabla **Eventos Laborales**.

Esta columna debe calcular automáticamente la cantidad de días comprendidos entre la fecha inicial y la fecha final del período registrado.

## Ejemplo actual

| Tipo       | Período                 | Autorizado por   | Estado |
| ---------- | ----------------------- | ---------------- | ------ |
| Vacaciones | 14/04/2026 — 27/04/2026 | Carlos Rodríguez | Activo |

## Resultado esperado con nueva columna

| Tipo       | Período                 | Días | Autorizado por   | Estado |
| ---------- | ----------------------- | ---- | ---------------- | ------ |
| Vacaciones | 14/04/2026 — 27/04/2026 | 14   | Carlos Rodríguez | Activo |

## Regla de cálculo

* El cálculo debe realizarse entre la fecha inicial y fecha final.
* Debe incluir ambos días dentro del rango.
* Si inicia y termina el mismo día, debe mostrar **1 día**.

---

# 2. Filtro entre fechas

## Requerimiento

La tabla **Eventos Laborales** debe contar con filtros por rango de fechas para consultar eventos ocurridos dentro de un período específico.

## Componentes sugeridos

* Fecha Desde
* Fecha Hasta
* Botón Buscar / Filtrar
* Botón Limpiar filtros

## Objetivo funcional

Permitir validar fácilmente qué novedades ha tenido el empleado dentro del rango consultado.

## Ejemplos de uso

* Vacaciones del último año.
* Incapacidades entre enero y marzo.
* Eventos ocurridos durante un contrato específico.

---

# 3. Resumen totalizado por tipo de evento

## Requerimiento

Agregar una sección resumen ubicada **encima de la tabla Eventos Laborales**, dentro del tab **Historial**.

Esta sección debe agrupar los eventos por tipo y sumar el total de días registrados por cada categoría.

## Ejemplo esperado

| Tipo de Evento         | Total Días |
| ---------------------- | ---------- |
| Vacaciones             | 28         |
| Incapacidad            | 12         |
| Licencia no remunerada | 5          |
| Permiso                | 3          |

## Reglas

* El resumen debe respetar los filtros aplicados por fechas.
* Debe recalcularse automáticamente al filtrar.
* Solo deben mostrarse tipos de eventos con registros existentes.

---

# 4. Ubicación visual sugerida

Dentro del tab **Historial** del perfil del usuario:

1. Filtros por fecha.
2. Resumen totalizado por tipo de evento.
3. Tabla detallada de Eventos Laborales.

---

# 5. Beneficios esperados

* Mejor control histórico del empleado.
* Consulta rápida de días disfrutados o utilizados.
* Validación de novedades por períodos específicos.
* Mejor apoyo para gestión humana y auditoría.
* Visualización clara de acumulados por tipo de evento.

---

# 6. Cálculo de vacaciones acumuladas

## Requerimiento

Se debe calcular el total de vacaciones disponibles de una persona teniendo en cuenta el tiempo laborado con contrato directo en la empresa.

## Regla base

Por cada año laborado, la persona tiene derecho a **15 días de vacaciones**.

Equivalencia mensual:

* **1 mes laborado = 1.25 días de vacaciones**
* Fórmula general:

```text
Meses laborados x 1.25 = días causados
```

---

## Campo involucrado

Dentro de la pestaña **Datos** del perfil, en la sección **Vinculación laboral**, existe el ítem:

* **Días de vacaciones previos**

Este campo debe mostrar la cantidad acumulada de vacaciones disponibles del empleado.

---

## Regla de cálculo del campo

El cálculo debe realizarse tomando como base **únicamente la FechaInicioContrato**, ya que corresponde a la fecha en que inició contrato directo con la empresa.

### Debe calcular:

1. Tiempo transcurrido desde **FechaInicioContrato** hasta la fecha actual o fecha de corte.
2. Convertir el tiempo laborado en días de vacaciones causados.
3. Restar el total de días ya disfrutados en eventos tipo **Vacaciones** registrados en Eventos Laborales.

### Fórmula esperada

```text
Vacaciones disponibles = Vacaciones causadas - Vacaciones disfrutadas
```

---

## Ejemplo práctico

* FechaInicioContrato: 01/01/2025
* Meses laborados: 12
* Vacaciones causadas: 15 días
* Vacaciones disfrutadas registradas: 8 días
* Resultado en campo Días de vacaciones previos: **7 días**

---

## Reglas adicionales

* Si el resultado es negativo, mostrar 0 o validar según política interna.
* Debe recalcularse automáticamente al registrar nuevas vacaciones.
* Solo se toman vacaciones disfrutadas posteriores a la FechaInicioContrato.
* No se deben considerar periodos trabajados por empresa temporal para este cálculo, salvo futura regla distinta.

---

# 7. Consideraciones técnicas

* El cálculo de días debe manejar años bisiestos y cambios de mes.
* El filtro debe ser eficiente incluso con grandes volúmenes de datos.
* El resumen puede realizarse vía SQL o backend según arquitectura del sistema.
* Debe mantener consistencia con paginación actual de la tabla si aplica.
