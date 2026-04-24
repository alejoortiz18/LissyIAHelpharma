# Pitch: Trazabilidad de Eventos Laborales y Cálculo de Vacaciones Disponibles

> Formato: Shape Up Pitch — [basecamp.com/shapeup](https://basecamp.com/shapeup)

---

## 1. Problema

El tab **Historial** del perfil del empleado muestra la tabla de Eventos Laborales sin suficiente información para que RRHH pueda tomar decisiones rápidas. Actualmente:

- La tabla no indica cuántos días duró cada evento: el usuario debe hacer el cálculo manualmente entre la fecha inicial y final.
- No existe forma de consultar eventos por período: para revisar las incapacidades de un trimestre, RRHH debe desplazarse por toda la tabla sin poder acotar el rango.
- No hay un resumen que indique cuántos días de cada tipo ha acumulado el empleado dentro del período consultado.

**Caso concreto:** Un jefe necesita aprobar vacaciones a un empleado y quiere saber cuántos días de vacaciones ha disfrutado en el último año. Hoy debe abrir cada fila, restar fechas mentalmente y sumar el total. Es lento y propenso a error.

Sumado a esto, el campo **Días de vacaciones previos** en el tab **Datos** (sección Vinculación laboral) no refleja las vacaciones *disponibles* del empleado: no existe una lógica que calcule automáticamente cuánto ha causado y cuánto ya ha disfrutado desde el inicio de su contrato directo.

---

## 2. Appetite

**Alcance:** Small Batch — mejoras de visualización y cálculo dentro de pantallas existentes.

No se requieren nuevos módulos, nuevas entidades en base de datos ni cambios en el flujo de registro de eventos. Los cambios afectan:

- La vista del tab **Historial** del perfil (`Perfil.cshtml` + lógica de filtrado en el service/controller)
- La vista del tab **Datos** del perfil (campo `DiasVacacionesPrevios` como valor calculado)
- El servicio de consulta de eventos laborales del empleado

Se espera resolver dentro del ciclo actual. Si el cálculo de vacaciones disponibles requiere más trabajo del esperado, puede separarse en un segundo ciclo.

---

## 3. Solución

### 3.1 Nueva columna **Días** en la tabla de Eventos Laborales

Agregar una columna **Días** entre "Período" y "Autorizado por" en la tabla del tab **Historial**.

El valor se calcula así:

```
Días = (FechaFin - FechaInicio).TotalDays + 1
```

Reglas:
- Incluye ambos extremos del rango (inicio y fin cuentan como días hábiles del evento).
- Si `FechaInicio == FechaFin`, el resultado es **1**.
- El cálculo se realiza en el backend al construir el DTO; no se almacena en base de datos.

**Ejemplo:**

| Tipo       | Período                 | Días | Autorizado por   | Estado |
|------------|-------------------------|------|------------------|--------|
| Vacaciones | 14/04/2026 — 27/04/2026 | 14   | Carlos Rodríguez | Activo |

---

### 3.2 Filtro por rango de fechas en la tabla de Eventos Laborales

Agregar encima de la tabla dos campos de fecha y un par de botones:

- **Fecha Desde** (date input)
- **Fecha Hasta** (date input)
- Botón **Filtrar**
- Botón **Limpiar**

**Criterio de filtrado:** se incluyen los eventos cuya `FechaInicio` esté dentro del rango `[Desde, Hasta]` (inclusive en ambos extremos).

> ⚠️ Decisión pendiente para el equipo: ¿el filtro debe aplicar sobre `FechaInicio`, sobre `FechaFin`, o sobre cualquier evento que *solape* el rango? La propuesta aquí usa `FechaInicio` por simplicidad; si RRHH necesita ver eventos que "caen dentro del período aunque terminen después", se debe ajustar la lógica.

Al limpiar, se restablece la tabla completa sin filtro.

---

### 3.3 Resumen totalizado por tipo de evento

Agregar una sección de tarjetas o tabla resumen **encima de la tabla de eventos**, debajo de los filtros.

Estructura del resumen:

| Tipo de Evento         | Total Días |
|------------------------|------------|
| Vacaciones             | 28         |
| Incapacidad            | 12         |
| Licencia no remunerada | 5          |

Reglas:
- Solo se muestran tipos de eventos que tengan al menos un registro en el período consultado.
- El resumen **respeta los filtros de fecha** aplicados: si el usuario filtra por rango, el resumen refleja solo los eventos visibles.
- Se recalcula automáticamente al aplicar o limpiar el filtro.
- El cálculo puede hacerse en el service con LINQ o directamente en la consulta SQL, según lo más eficiente dado el volumen de datos.

---

### 3.4 Campo **Días de vacaciones previos** (tab Datos) como valor calculado

El campo existente `DiasVacacionesPrevios` en la sección Vinculación laboral del tab **Datos** debe mostrar las vacaciones *disponibles* del empleado, calculadas en tiempo real al cargar el perfil.

**Fórmula:**

```
Meses laborados = meses entre FechaInicioContrato y fecha de hoy (redondeado a enteros)
Vacaciones causadas = Meses laborados × 1.25
Vacaciones disfrutadas = suma de Días de todos los eventos tipo "Vacaciones"
                         con FechaInicio >= FechaInicioContrato

Vacaciones disponibles = Vacaciones causadas − Vacaciones disfrutadas
```

**Reglas adicionales:**
- Solo se considera `FechaInicioContrato` (contrato directo). El tiempo en empresa temporal no genera vacaciones.
- Solo se descuentan eventos tipo **Vacaciones** con `FechaInicio >= FechaInicioContrato`.
- Si el resultado es negativo (más días disfrutados que causados), mostrar **0**.
- Si `FechaInicioContrato` es nulo, mostrar `—`.
- El valor se calcula al cargar el perfil; no se almacena en base de datos.

**Ejemplo:**

| Dato | Valor |
|------|-------|
| `FechaInicioContrato` | 01/01/2025 |
| Fecha de hoy | 23/04/2026 |
| Meses laborados | 15 |
| Vacaciones causadas | 18.75 días |
| Vacaciones disfrutadas (registradas) | 8 días |
| **Vacaciones disponibles** | **10.75 días** |

> ⚠️ Decisión pendiente para el equipo: ¿se muestra el valor con decimales (10.75) o se redondea? Sugerencia: mostrar con un decimal para mayor precisión.

---

### 3.5 Orden visual en el tab Historial

La disposición propuesta dentro del tab **Historial** es:

1. Filtros por fecha (Desde / Hasta / Filtrar / Limpiar)
2. Resumen totalizado por tipo de evento
3. Tabla detallada de Eventos Laborales (con nueva columna Días)

---

## 4. Rabbit Holes

- **Paginación con filtros:** Si la tabla de eventos ya tiene paginación, el filtro debe operar sobre el dataset completo, no solo la página visible. No implementar el filtro sobre el DOM del cliente; debe ir al backend (query parameter o form submit).

- **Años bisiestos y cambios de mes:** El cálculo de días debe usar la diferencia real entre `DateOnly` (o `DateTime`) sin asunciones de "mes = 30 días". En C#: `(fechaFin.ToDateTime(TimeOnly.MinValue) - fechaInicio.ToDateTime(TimeOnly.MinValue)).Days + 1`.

- **Meses laborados para vacaciones:** "Meses transcurridos" debe calcularse con diferencia real de calendario (no dividir días entre 30). En C#: `((today.Year - start.Year) * 12) + today.Month - start.Month`, ajustado si el día de hoy es anterior al día del mes de inicio.

- **Eventos sin FechaFin:** Si existe algún evento sin fecha de cierre (estado abierto), la columna Días no puede calcularse. Mostrar `—` en ese caso. No lanzar excepción.

- **Recalculado automático de vacaciones al registrar evento:** El documento indica que el campo debe recalcularse "al registrar nuevas vacaciones". Dado que el valor es calculado al cargar el perfil, esto se cumple automáticamente si el usuario recarga o navega al perfil después del registro. No se requiere lógica adicional de notificación ni WebSocket.

---

## 5. No-Gos

- **No se almacenan los valores calculados en base de datos.** Ni la columna Días, ni las vacaciones disponibles se persistirán. Son valores derivados calculados al vuelo.

- **No se construyen reportes exportables** (Excel, PDF) en este ciclo. El resumen es solo visual en pantalla.

- **No se validan reglas de negocio complejas** de vacaciones (proporcionales por terminación de contrato, vacaciones anticipadas, etc.). Solo aplica la regla base: 1.25 días por mes.

- **No se contempla historial de múltiples contratos directos.** Solo se usa `FechaInicioContrato` como única fecha base. Si el empleado tuvo múltiples contratos, ese escenario queda fuera de este ciclo.

- **No se construye una vista de calendario** de los eventos. La tabla y el resumen son suficientes para este ciclo.

- **No se notifica al empleado** cuando sus vacaciones disponibles cambian. Solo es visible para quien consulta el perfil.
