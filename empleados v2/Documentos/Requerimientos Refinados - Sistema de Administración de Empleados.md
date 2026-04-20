# Requerimientos Refinados — Sistema de Administración de Empleados

> **Versión:** 1.1 — Actualización: fusión con Pitches v1.0 y alineación con metodología Shape Up oficial  
> **Metodología:** Shape Up (Basecamp) — https://basecamp.com/shapeup  
> **Fecha de refinamiento:** Abril 2026  
> **Fuentes:** *Shape Up — Pitches Sistema de Gestión de Personal (v1.0)* · *Requerimientos Refinados (v1.0)* · *Shape Up Book — 37signals*

---

## Marco Metodológico — Shape Up

Este documento sigue la metodología **Shape Up** de Basecamp (37signals). Los siguientes conceptos son los pilares que guían la estructura de cada Pitch y la toma de decisiones del equipo.

### Los cinco ingredientes de cada Pitch

Todo módulo se documenta con exactamente cinco ingredientes:

| # | Ingrediente | Propósito |
|---|---|---|
| 1 | **Problema** | La historia concreta que motiva el trabajo. Sin problema claro, no hay base para evaluar si la solución es adecuada. |
| 2 | **Appetite** | Cuánto tiempo se quiere invertir. No es una estimación — es un límite que define el alcance máximo de la solución. |
| 3 | **Solución** | Los elementos concretos del diseño, presentados con suficiente detalle para que el equipo pueda implementarlos. Se usan *breadboards* y bocetos gruesos (*fat marker sketches*), **no** wireframes detallados ni maquetas de alta fidelidad. |
| 4 | **Rabbit Holes** | Problemas conocidos que el equipo debe evitar o decisiones que hay que tomar antes de construir. |
| 5 | **No-Gos** | Funcionalidad explícitamente excluida del alcance de este ciclo. |

### Ciclos de 6 semanas y Cool-down

- **Ciclo:** período de 6 semanas de trabajo ininterrumpido. Seis semanas es suficiente para construir algo significativo y corto para mantener el sentido de urgencia y deadline real.
- **Cool-down:** período de **2 semanas** entre ciclos sin trabajo programado. Los equipos lo usan para corregir bugs, explorar ideas técnicas y preparar los próximos pitches. La **Betting Table** se reúne durante el cool-down.
- **Big Batch:** un equipo (1 diseñador + 2 programadores) dedica el ciclo completo a un solo proyecto.
- **Small Batch:** un equipo (1 diseñador + 1 programador) trabaja en varios proyectos cortos (1–2 semanas cada uno) dentro del mismo ciclo.

### La Betting Table

Reunión que ocurre durante el cool-down para decidir qué se construye en el próximo ciclo. Solo participan quienes tienen autoridad para comprometer tiempo y recursos. Los pitches se leen de forma asíncrona antes de la reunión. La salida es un **plan de ciclo** — no un backlog ni una hoja de ruta.

Principios clave:
- Se apuesta **un ciclo a la vez**. No se planifica más allá del siguiente ciclo.
- Si algo no cabe en este ciclo, no se "acumula" en un backlog — simplemente compite en el próximo cool-down si sigue siendo relevante.
- Una vez iniciado el ciclo, **el equipo no se interrumpe** por peticiones externas ni bugs no críticos.

### Circuit Breaker

Si un equipo no termina dentro del ciclo apostado, **el proyecto no recibe extensión automática**. El circuit breaker garantiza que ningún proyecto se desborde indefinidamente:

1. El pitch se descarta y el problema se reformula para una apuesta futura.
2. Se recorta el alcance hasta lo que se puede entregar en el tiempo restante.
3. Solo en crisis reales (pérdida de datos, caída total) se rompe el ciclo — las crisis verdaderas son raras.

### Tiempo fijo, alcance variable

El tiempo del ciclo es **fijo**. El alcance es **variable**. Si durante la construcción algo resulta más complejo de lo esperado, se recorta la solución — no se extiende el tiempo. Este es el mecanismo central de control de riesgo de Shape Up.

---

## Contexto del Sistema

| Atributo | Valor validado |
|---|---|
| Plataforma | Aplicación web — acceso desde red interna (intranet) |
| Alcance empresarial | Una sola empresa con múltiples sedes |
| Identificación de empleados | Únicamente Cédula de Ciudadanía (CC) |
| Idioma del sistema | Español |

---

## Matriz de Roles y Permisos

El sistema tiene **4 roles**. Cada sede tiene **exactamente un Jefe asignado**. El Jefe es el único rol con visibilidad y gestión sobre **todas las sedes** y el único habilitado para crear nuevos usuarios en el sistema.

| Acción | Jefe | Regente | Auxiliar de Regente | Operario |
|---|:---:|:---:|:---:|:---:|
| **Ver empleados de TODAS las sedes** | ✅ | ❌ | ❌ | ❌ |
| Crear y editar empleados *(solo su sede)* | ✅ | ✅ | ✅ | ❌ |
| **Crear nuevos usuarios en el sistema** | ✅ *(único)* | ❌ | ❌ | ❌ |
| Desactivar (desvincular) empleados | ✅ | ❌ | ❌ | ❌ |
| Registrar eventos laborales | ✅ | ✅ | ✅ | ❌ |
| Solicitar horas extras | ✅ | ✅ | ✅ | ❌ |
| **Aprobar / rechazar** horas extras | ✅ | ❌ | ❌ | ❌ |
| Asignar y modificar turnos | ✅ | ✅ | ✅ | ❌ |
| Ver historial de empleados de su sede | ✅ | ✅ | ✅ | ❌ |
| **Acceso al Panel de Datos Maestros** | ✅ | ❌ | ❌ | ❌ |
| Ver su propio perfil y sus solicitudes | ✅ | ✅ | ✅ | ✅ |

> **Creación de usuarios:** el formulario "Nuevo empleado/usuario" solo es accesible desde el rol Jefe. El Regente y el Auxiliar pueden **editar** datos de empleados de su sede, pero no crear cuentas nuevas.

> **Nota sobre Regente vs. Auxiliar de Regente:** ambos comparten los mismos permisos en esta versión. Si en el futuro se requiere diferenciarlos, se tratará como un pitch separado.

---

---

# Pitch 1 — Gestión de Empleados

## 1. Problema

Los coordinadores de cada sede no tienen un único lugar donde consultar la información completa de un empleado. Hoy esa información está dispersa en hojas de cálculo o registros en papel. Cuando alguien se desvincula no queda trazabilidad del motivo ni de la fecha. Tampoco existe distinción formal entre los empleados con contrato directo y los que llegan a través de una empresa temporal, lo que genera confusión sobre quién responde por ese trabajador y hasta cuándo.

**Historia representativa:** El regente de una sede necesita saber si el contrato temporal de un operario vence este mes. No hay registro formal: tiene que llamar a quien contrató a esa persona o buscar el contrato físico.

## 2. Appetite

**Big Batch — 6 semanas** (1 diseñador + 2 programadores)

Es el núcleo del sistema. Todos los demás pitches dependen de que los empleados estén registrados aquí.

## 3. Solución

### Pantalla principal — Lista de empleados activos

Tabla con filtros rápidos por: Sede, Cargo, Tipo de vinculación (`Directo` / `Temporal`).

- **El Jefe** ve empleados de **todas las sedes** sin restricción.
- **Regente y Auxiliar** ven solo los empleados de **su propia sede**.
- El botón **"Nuevo empleado"** es visible únicamente para el rol `Jefe`.
- La tabla soporta **paginación editable**: el usuario puede seleccionar cuántos registros mostrar por página (opciones: 10 / 25 / 50 / 100). La selección persiste durante la sesión.

### Sección aparte — Empleados desvinculados

Los empleados con estado `Inactivo` (independientemente de si eran directos o temporales) **no aparecen en la lista principal de empleados activos**. Tienen una vista dedicada accesible desde un enlace o pestaña separada: **"Empleados desvinculados"**.

Esta vista es de **solo-lectura** para todos los roles. Muestra:

| Columna | Descripción |
|---|---|
| Nombre completo | |
| CC | |
| Sede | Sede a la que pertenecía |
| Cargo | Cargo que tenía al momento del retiro |
| Tipo de vinculación | `Directo` o `Temporal` |
| Empresa temporal | Si aplica |
| Fecha de ingreso | |
| Fecha de desvinculación | |
| Motivo de retiro | |

Desde esta vista el Jefe puede acceder al perfil completo (modo solo-lectura) y al historial del empleado. La tabla también tiene **paginación editable** (10 / 25 / 50 / 100 registros).

### Formulario de registro y edición

| Sección | Campos | Observaciones |
|---|---|---|
| **Datos personales** | Nombre completo, CC, Fecha de nacimiento, Teléfono, Correo electrónico | CC es único en el sistema |
| **Residencia** | Dirección, Ciudad, Departamento | Campos de texto libre |
| **Contacto de emergencia** | Nombre completo del contacto, Teléfono del contacto | Obligatorio |
| **Formación** | Nivel de escolaridad | Lista: Primaria / Bachillerato / Técnico / Tecnológico / Profesional / Posgrado |
| **Seguridad social** | EPS, ARL | Texto libre con nombre de entidad |
| **Vinculación** | Sede, Cargo, Rol en el sistema, Tipo de vinculación (`Directo` / `Temporal`), Jefe inmediato, Fecha de ingreso | Al seleccionar la **Sede**, el campo **Jefe inmediato** se actualiza automáticamente mostrando solo los jefes activos asignados a esa sede. Si la sede no tiene Jefe asignado aún, el campo muestra “Sin Jefe asignado” (no bloquea el guardado) |
| **Contrato temporal** *(condicional)* | Nombre de empresa temporal, Fecha inicio contrato, Fecha fin contrato | Solo visible y obligatorio si Tipo = `Temporal` |
| **Estado** | `Activo` / `Inactivo` | Al pasar a Inactivo → activar formulario de desvinculación |
| **Credenciales** | Correo de acceso, Contraseña (hash HMACSHA512 + salt aleatorio por usuario) | Solo el Jefe puede crear usuarios |

### Flujo de desvinculación

Al hacer clic en **"Desvincular empleado"** (solo Jefe), el sistema abre un modal que obliga a ingresar:
- Motivo de retiro
- Fecha de desvinculación

Al confirmar, el empleado pasa a estado `Inactivo`, **desaparece de la lista principal** y queda disponible en la sección **"Empleados desvinculados"**. Su perfil e historial son accesibles en modo solo-lectura.

### Validaciones de integridad (servicio: `EmpleadoService`)

| Validación | Regla | Mensaje de error al usuario |
|---|---|---|
| **Unicidad de CC** | No pueden existir dos empleados con el mismo número de cédula. Validado con índice único en base de datos **y** en el servicio antes de guardar. | *"Ya existe un empleado con esta identificación."* |
| **Correo electrónico único y obligatorio** | Todo empleado debe tener correo. Se valida formato RFC y unicidad en el sistema. | *"Ya existe un usuario con este correo electrónico."* |
| **Auto-referencia de jefe** | `EmpleadoId` ≠ `JefeInmediatoId`. Un empleado no puede ser su propio jefe inmediato. | *"Un empleado no puede ser su propio jefe inmediato."* |
| **Jefe obligatorio para no-Jefes** | Si el rol es `Regente`, `Auxiliar de Regente` u `Operario`, el campo `JefeInmediatoId` es obligatorio. | *"El campo Jefe inmediato es obligatorio para este rol."* |
| **Regente único por sede** | Una sede no puede tener más de un `Regente` activo asignado simultáneamente. | *"La sede ya tiene un Regente activo asignado."* |
| **Coherencia de fechas** | `FechaNacimiento` ≤ `FechaActual`; si se registra `FechaDesvinculacion`, debe ser ≥ `FechaIngreso`. | *"La fecha ingresada no es válida."* |

### Catálogos de soporte (ABM simples — acceso solo Jefe)

- **Sedes:** Nombre, Dirección, Ciudad
- **Cargos:** Nombre del cargo
- **Empresas Temporales:** Nombre de la empresa
- **Niveles de escolaridad:** (predefinidos, no editables)

### Historial del empleado (pestaña dentro del perfil)

Vista de solo-lectura, ordenada cronológicamente (más reciente primero). Consolida todos los registros asociados al empleado sin importar su estado actual:

| Tipo de registro | Datos visibles |
|---|---|
| Eventos laborales | Tipo, fechas, autorizante, estado, documento de soporte |
| Horas extras | Fecha, horas, motivo, estado, quién aprobó/rechazó |
| Asignaciones de turno | Turno asignado, vigente desde, programado por |
| Desvinculación | Motivo y fecha (si aplica) |

**Botón "Exportar historial":** genera un archivo Excel (.xlsx) con todas las filas del historial del empleado seleccionado.

### Breadboard

```
[Lista de empleados activos]
  → Filtrar: Sede | Cargo | Tipo de vinculación
  → Paginación: 10 | 25 | 50 | 100 registros por página
  → [Nuevo empleado]  (solo Jefe)
  → Click en fila → [Perfil del empleado]
      ├── Pestaña "Datos"
      │     → Editar campos
      │     → Si sede cambia → Jefe inmediato se filtra automáticamente
      │     → Si tipo = Temporal → Sección contrato temporal (obligatoria)
      ├── Pestaña "Historial"
      │     → Línea de tiempo de todos los registros
      │     → Botón "Exportar a Excel"
      └── Botón "Desvincular empleado" (solo Jefe)
            → Modal: Motivo + Fecha → Confirmar
            → Empleado pasa a Sección "Empleados desvinculados"

[Pestaña / Enlace "Empleados desvinculados"]
  → Filtrar: Sede | Cargo | Tipo de vinculación | Fecha de retiro
  → Paginación: 10 | 25 | 50 | 100 registros por página
  → Click en fila → [Perfil en modo solo-lectura + Historial]
```

## 4. Rabbit Holes

- **Jefe inmediato dependiente de sede:** al cambiar la sede en el formulario, el selector de Jefe inmediato recarga su lista vía consulta filtrada. Si el usuario ya tenía un Jefe inmediato asignado de otra sede, ese valor se limpia automáticamente.
- **Vencimiento de contrato temporal:** el sistema guarda la fecha de fin del contrato pero **no** genera alertas automáticas de vencimiento en este ciclo. El seguimiento es responsabilidad del Regente o Jefe.
- **Contraseña inicial:** cuando el Jefe crea un usuario, el sistema genera una contraseña temporal. El usuario debe cambiarla en su primer inicio de sesión. No construir un flujo de recuperación por SMS ni OTP; solo recuperación por correo electrónico.
- **Exportación del historial:** la exportación es por empleado individual, no masiva. Un exportador de todos los empleados es un pitch posterior.
- **EPS/ARL:** se guardan como texto libre (nombre de la entidad). No hay integración con bases de datos de entidades.

## 5. No-Gos

- No hay importación masiva de empleados (Excel/CSV) en este ciclo.
- No hay árbol organizacional visual ni organigramas.
- No hay alertas automáticas por vencimiento de contrato temporal.
- No hay auditoría de cambios a nivel de campo (quién modificó qué valor puntual). El historial de actividades sí se guarda; la auditoría de ediciones del formulario queda para un ciclo posterior.
- No hay integración con sistemas externos de empresas temporales.
- No hay gestión de documentos del empleado (hoja de vida, certificados) más allá del soporte de eventos.

---

---

# Pitch 2 — Control de Eventos Laborales

## 1. Problema

Los eventos de ausentismo (vacaciones, incapacidades, permisos) se aprueban verbalmente o por correo y nadie tiene visibilidad centralizada de quién está disponible. No hay control del saldo de vacaciones disponibles, lo que lleva a que algunos empleados tomen más días de los que les corresponden sin que nadie lo detecte a tiempo. Las incapacidades se registran sin datos médicos básicos que permitan categorizarlas o hacer seguimiento.

**Historia representativa:** Un regente aprueba verbalmente una semana de vacaciones a un operario. Al mes siguiente, otro supervisor también le aprueba otra semana. Al cierre del año, el empleado tomó 20 días pero solo tenía 15 acumulados.

## 2. Appetite

**Big Batch — 6 semanas** (1 diseñador + 2 programadores)

Requiere lógica de saldo de vacaciones, validación de solapamiento y gestión de adjuntos. Es el módulo con mayor impacto en la operación diaria.

## 3. Solución

### Vista principal — Calendario

Vista semanal/mensual que muestra los eventos activos de los empleados de la sede. El objetivo es **ver quién está disponible y quién no** — no reemplazar un sistema de calendario completo.

Filtros: Sede (solo Jefe en otras sedes), Empleado, Tipo de evento, Rango de fechas.

### Registro de evento

Campos según el tipo de evento:

**Vacaciones:**

| Campo | Tipo |
|---|---|
| Empleado | Selector (empleados activos de la sede) |
| Fecha inicio / Fecha fin | Fechas |
| Saldo disponible | Solo lectura — calculado automáticamente |
| Días solicitados | Calculado automáticamente (fechas seleccionadas) |
| Autorizado por | Texto obligatorio (nombre de quien autoriza) |
| Documento de soporte | Adjunto PDF/JPG/PNG — opcional |

> **Regla de saldo:** el sistema calcula los días hábiles acumulados a partir de la **fecha de ingreso** del empleado (15 días hábiles por cada año trabajado, proporcional a los meses si lleva menos de un año). Al guardar el evento, descuenta los días del saldo. Si no hay saldo suficiente, muestra advertencia y bloquea el guardado.

**Incapacidad:**

| Campo | Tipo |
|---|---|
| Empleado | Selector |
| Fecha inicio / Fecha fin | Fechas |
| Tipo de incapacidad | Lista: `Enfermedad general` / `Accidente de trabajo` / `Enfermedad laboral` / `Maternidad/Paternidad` |
| Entidad que expide | Texto: nombre de la EPS o ARL |
| Autorizado por | Texto obligatorio |
| Documento de soporte | Adjunto obligatorio (certificado médico) |

**Permiso:**

| Campo | Tipo |
|---|---|
| Empleado | Selector |
| Fecha inicio / Fecha fin | Fechas |
| Descripción / justificación | Texto obligatorio |
| Autorizado por | Texto obligatorio |
| Documento de soporte | Adjunto — opcional |

### Reglas de validación transversales a todos los eventos

- **Evento único activo:** el sistema verifica que el empleado no tenga otro evento activo en el mismo rango de fechas. Si hay solapamiento, bloquea el guardado con un mensaje claro.
- **Estados:** `Activo` → `Finalizado` (automático al vencer la fecha fin) | `Anulado` (manual, requiere motivo de anulación).

### Definición formal de "evento activo"

Un evento se considera **activo** cuando se cumplen **simultáneamente** estas dos condiciones:

```
FechaInicio <= FechaActual <= FechaFin
Y  Estado != "Anulado"
```

Esta definición es la misma que usa `HoraExtraService` al validar la disponibilidad del empleado (ver Pitch 4), garantizando criterio consistente en todos los módulos.

### Breadboard

```
[Vista calendario de sede]
  → Filtrar: Empleado | Tipo | Rango de fechas
  → Click en día → [Nuevo evento]
      ├── Seleccionar tipo: Vacaciones | Incapacidad | Permiso
      ├── Si Vacaciones → mostrar saldo disponible → validar suficiencia
      ├── Si Incapacidad → campos tipo + entidad + adjunto obligatorio
      ├── Validar solapamiento con otros eventos del mismo empleado
      └── Guardar con autorizante
  → Click en evento existente → [Detalle]
      └── Botón "Anular" (requiere motivo)
```

## 4. Rabbit Holes

- **Cálculo de días hábiles para vacaciones:** el sistema cuenta días corridos entre las fechas seleccionadas y descuenta los domingos. Los festivos nacionales de Colombia **no** se descontarán automáticamente en este ciclo (rabbit hole de datos); el cálculo es sobre días hábiles = días sin domingos.
- **Saldo inicial de empleados ya existentes:** al migrar datos, se debe ingresar manualmente el saldo de días ya tomados antes del sistema. El Jefe puede ajustar el saldo manualmente al crear el empleado (campo "Días ya tomados anteriormente").
- **Adjuntos:** 1 archivo por evento, máximo 5 MB, formatos PDF/JPG/PNG. No construir un gestor de documentos.

## 5. No-Gos

- No hay flujo de solicitud/aprobación por parte del empleado (workflow). El autorizante se registra manualmente por quien crea el evento.
- No hay integración con nómina ni cálculo de descuentos por ausentismo.
- No hay notificaciones por correo al empleado cuando se registra un evento.
- No hay subtipos de permiso (remunerado vs. no remunerado) en este ciclo.
- No se descuentan festivos nacionales del saldo de vacaciones en este ciclo.

---

---

# Pitch 3 — Administración de Jornadas y Horarios

## 1. Problema

No existe un registro formal de los turnos de cada empleado. Los supervisores tienen el horario en la cabeza o en un papel, pero cuando hay cambio de personal o se necesita cubrir un turno, nadie sabe con exactitud quién tiene jornada configurada para qué día y a qué hora. El problema se complica porque hay empleados que trabajan sábados pero no domingos, o que tienen horarios distintos según el día de la semana.

**Historia representativa:** Un regente nuevo entra a cubrir una sede por dos semanas. No sabe qué días trabajan los operarios ni a qué hora entran, porque esa información no está registrada en ningún sistema; estaba solo en la memoria del regente anterior.

## 2. Appetite

**Small Batch — 2 semanas** (1 diseñador + 1 programador)

La lógica es un formulario de configuración por día de la semana. No requiere algoritmos complejos.

## 3. Solución

### Catálogo de Plantillas de Turno (ABM)

Una **plantilla de turno** define el horario para cada día de la semana. Se crean plantillas reutilizables que luego se asignan a empleados.

**Campos de la plantilla:**

| Campo | Descripción |
|---|---|
| Nombre de la plantilla | Ej: "Turno L-V mañana", "Turno completo", "Turno fin de semana" |
| Configuración por día | Para cada día (Lun, Mar, Mié, Jue, Vie, Sáb, Dom): Hora entrada / Hora salida / `No labora` |

**Ejemplo:**

| Día | Entrada | Salida |
|---|---|---|
| Lunes | 07:00 | 15:00 |
| Martes | 07:00 | 15:00 |
| Miércoles | 07:00 | 15:00 |
| Jueves | 07:00 | 15:00 |
| Viernes | 07:00 | 15:00 |
| Sábado | 08:00 | 12:00 |
| Domingo | No labora | — |

### Asignación de turno al empleado

Desde el perfil del empleado (sección "Horario"):
- Seleccionar plantilla de turno activa
- Campo **"Programado por"**: referencia al usuario que asignó el turno
- **Fecha de vigencia** (desde cuándo aplica esta asignación)

Al asignar una nueva plantilla, la asignación anterior queda registrada como historial (no se sobreescribe).

### Breadboard

```
[Catálogo de plantillas de turno]
  → Nueva plantilla → Nombre + configuración día a día (entrada | salida | no labora)
  → Editar / Ver plantilla existente

[Perfil del empleado → Sección "Horario"]
  → Asignación actual: plantilla activa | vigente desde | programado por
  → Botón "Cambiar turno" → seleccionar nueva plantilla + fecha de vigencia
  → Historial de asignaciones anteriores (solo lectura)
```

## 4. Rabbit Holes

- **Plantilla con todos los días en "No labora":** no debe permitirse guardar una plantilla donde todos los días estén marcados como "No labora". El sistema valida que al menos un día tenga horario configurado.
- **Cambio de turno retroactivo:** la fecha de vigencia no puede ser anterior a la fecha de ingreso del empleado. El sistema valida esto al guardar.
- **Festivos:** no existe lógica especial para festivos en este módulo. Si un festivo cae en día laboral según la plantilla, eso lo gestiona el módulo de eventos (permiso o incapacidad).

## 5. No-Gos

- No hay control de asistencia ni marcación de entrada/salida (fichaje).
- No hay generación automática de cuadrantes o grillas de turnos rotativos.
- No hay alertas por incumplimiento de horario.
- No hay integración con biométrico o reloj de fichaje.
- No hay cálculo de horas trabajadas a partir del turno.

---

---

# Pitch 4 — Gestión de Horas Extras

## 1. Problema

Las horas extras se reportan verbalmente o por correo y al final del mes alguien las transcribe a una hoja de cálculo. No hay constancia formal de quién aprobó qué ni cuándo. El único que puede aprobar es el jefe inmediato, pero cuando el Jefe de sede solicita sus propias horas extras no hay un flujo definido de quién las aprueba.

**Historia representativa:** Un operario reporta 8 horas extras en el mes pero nómina solo registra 5. El correo de aprobación del jefe no se encontró. No hay forma de resolver la disputa.

## 2. Appetite

**Small Batch — 2 semanas** (1 diseñador + 1 programador)

Formulario de registro con flujo de estados simple. La lógica más delicada es el caso del Jefe que solicita sus propias horas.

## 3. Solución

### Solicitud de horas extras

**Quién puede crear una solicitud:** Jefe, Regente, Auxiliar de Regente (para sí mismos o para empleados de su sede).

**Campos:**

| Campo | Descripción |
|---|---|
| Empleado | Selector (empleados activos de la sede) |
| Fecha en que se trabajaron las horas | Fecha |
| Cantidad de horas | Número decimal (ej. 2.5) |
| Motivo / justificación | Texto obligatorio |
| Estado inicial | `Pendiente` (automático) |

### Reglas de validación (servicio: `HoraExtraService`)

| Regla | Descripción | Mensaje de error |
|---|---|---|
| **Unicidad por día** | No puede existir más de una solicitud activa para el mismo empleado en la misma fecha. | *"Ya existe una solicitud de horas extras para este empleado en la fecha indicada."* |
| **Disponibilidad del empleado** | El empleado no puede tener un evento activo (Vacaciones, Incapacidad o Permiso) en la fecha de las horas. Se usa la misma definición de evento activo del Pitch 2. | *"El empleado no está disponible en la fecha seleccionada."* |
| **Cantidad de horas válida** | Solo se aceptan valores entre 1 y 24 (enteros o con decimales). No se permiten valores ≤ 0 ni > 24. | *"La cantidad de horas debe estar entre 1 y 24."* |
| **Control de concurrencia** | Antes de aprobar, rechazar o anular, el servicio verifica que el estado actual en base de datos siga siendo el esperado. Evita condiciones de carrera si dos usuarios actúan sobre la misma solicitud simultáneamente. | *"El registro ya fue procesado por otro usuario. Refresca la página."* |

### Flujo de aprobación y estados

```
[Solicitud creada → estado: Pendiente]
        ↓
[Jefe inmediato revisa]
        ├── Aprobar  → estado: Aprobado  + fecha, usuario y motivo (opcional)
        └── Rechazar → estado: Rechazado + motivo de rechazo obligatorio

[Solicitud Aprobada]
        └── Anular (solo Jefe) → estado: Anulado + motivo de anulación obligatorio
```

> **Distinción Rechazo vs. Anulación:** el **Rechazo** ocurre sobre solicitudes `Pendiente` que el Jefe considera improcedentes desde el origen. La **Anulación** es una corrección posterior sobre solicitudes ya `Aprobadas` (ej: la información estaba incorrecta o se aprobó por error). Ambas acciones registran el responsable, la fecha y el motivo.

**Caso especial — El Jefe solicita sus propias horas extras:**  
La solicitud queda en estado `Pendiente` y **no puede ser aprobada por el mismo Jefe**. Requiere la intervención de un **administrador global** del sistema (ver Rabbit Holes).

### Vista de listado

Filtros: Empleado, Fecha, Estado (`Pendiente` / `Aprobado` / `Rechazado`).

- El Jefe ve todas las solicitudes de su sede y puede aprobar/rechazar las `Pendiente`.
- El Regente y Auxiliar ven las solicitudes de su sede pero no pueden aprobar.
- El Operario ve solo sus propias solicitudes.

### Breadboard

```
[Lista de horas extras]
  → Filtrar: Empleado | Fecha | Estado
  → [Nueva solicitud] → Empleado | Fecha | Horas | Motivo → guardar como Pendiente
  → Click en solicitud Pendiente (solo Jefe)
      ├── Aprobar → confirmar + guardar quién aprobó y cuándo
      └── Rechazar → ingresar motivo → guardar
```

## 4. Rabbit Holes

- **Administrador global:** el sistema necesita un mecanismo para que alguien apruebe las horas extras del Jefe de sede. En este ciclo se define como un usuario especial con rol `Administrador` que tiene visibilidad de todas las sedes y puede aprobar cualquier solicitud. Este rol **no** aparece en la matriz de roles principal (no gestiona empleados ni eventos), solo tiene acceso a esta función puntual. Si más adelante se necesita expandir sus permisos, es un pitch separado.
- **Horas fraccionarias:** el campo de horas acepta decimales (ej. 1.5 horas). No construir un selector de minutos; el usuario escribe el valor directamente.
- **Tipos de hora extra (diurna, nocturna, festivo):** el sistema registra solo la cantidad y la fecha. El cálculo del recargo monetario según la normativa laboral colombiana queda fuera de este ciclo.

## 5. No-Gos

- No hay cálculo de valor monetario de horas extras.
- No hay límite automático de horas extras por empleado (semanal o mensual).
- No hay integración con nómina.
- No hay notificaciones automáticas al empleado cuando su solicitud cambia de estado.
- No hay distinción entre horas extras diurnas, nocturnas y en festivos en este ciclo.

---

---

# Pitch 5 — Autenticación y Seguridad de Acceso

## 1. Problema

El sistema maneja información sensible de los empleados (datos personales, salud, contrato). Sin un control de acceso adecuado, cualquier persona con acceso a la red interna podría ver o modificar información que no le corresponde.

## 2. Appetite

**Small Batch — 1 semana** (1 programador)

Es infraestructura base. Debe construirse en paralelo o antes del Pitch 1, no al final.

## 3. Solución

- **Inicio de sesión:** correo electrónico + contraseña. Contraseñas almacenadas con **hash HMACSHA512 + salt aleatorio por usuario** (`PasswordHash` + `PasswordSalt`, ambos `VARBINARY` en BD). Nunca se persiste la contraseña en texto plano ni como hash reversible.
- **Contraseña temporal:** cuando el Jefe crea un usuario, el sistema asigna una contraseña temporal de un solo uso. El usuario debe cambiarla en el primer inicio de sesión.
- **Recuperación de contraseña:** flujo estándar por correo electrónico (enlace de restablecimiento con token de un solo uso, expiración de 1 hora).
- **Cierre de sesión por inactividad:** la sesión expira tras **30 minutos sin actividad** (configurable por el administrador global).
- **Control de acceso por rol y sede:** el servidor valida en cada petición que el usuario tiene permiso sobre el recurso solicitado, considerando su rol y su sede asignada. No se confía solo en la UI.

## 4. Rabbit Holes

- **Tiempo de inactividad:** el valor de 30 minutos es una propuesta razonable. Si el cliente necesita ajustarlo, basta con un parámetro de configuración; no es un cambio de arquitectura.
- **Token de recuperación:** se invalida tras su primer uso o tras expirar (1 hora). No se reutiliza.

## 5. No-Gos

- No hay autenticación con cuentas corporativas (Google/Microsoft) en este ciclo.
- No hay doble factor de autenticación (2FA).
- No hay gestión de sesiones múltiples (forzar logout en otros dispositivos).

---

---

# Pitch 6 — Dashboard del Jefe

## 1. Problema

El Jefe de sede no tiene una vista consolidada del estado de su personal. Para saber cuántos empleados tiene en total, cuántos están en novedad o quiénes no están disponibles hoy, debe revisar manualmente cada módulo por separado. Esto hace lento el proceso de tomar decisiones operativas rápidas al inicio del día o durante una contingencia.

**Historia representativa:** El Jefe llega a la empresa un lunes y necesita saber rápidamente cuántas personas tiene disponibles esa semana. Tiene que entrar a eventos laborales, revisar incapacidades, mirar permisos y cruzar esa información con el total de empleados activos. El proceso le toma 15 minutos que podría reducirse a una mirada de 30 segundos.

## 2. Appetite

**Small Batch — 1 semana** (1 diseñador + 1 programador)

El dashboard solo lee datos que ya existen en el sistema. No requiere lógica nueva, solo consultas agrupadas y una vista clara.

## 3. Solución

### Pantalla de inicio (vista exclusiva para el rol `Jefe`)

Al iniciar sesión, el Jefe llega directamente al Dashboard. El resto de roles llegan a la pantalla genérica de su módulo principal.

### Tarjetas de indicadores

| Tarjeta | Descripción | Alcance |
|---|---|---|
| **Total de empleados activos** | Número total de empleados con estado `Activo` sumando **todas las sedes** | Global (todas las sedes) |
| **Total de Jefes** | Cantidad de usuarios con rol `Jefe` activos en el sistema | Global (todas las sedes) |
| **No disponibles hoy** | Cantidad de empleados con un evento laboral activo (`Vacaciones`, `Incapacidad` o `Permiso`) cuya fecha de inicio ≤ hoy ≤ fecha de fin | Global (todas las sedes) |

> **Regla de "No disponibles hoy":** un empleado se cuenta como no disponible si tiene al menos un evento en estado `Activo` que cubre la fecha del día actual, sin importar el tipo de evento. Un empleado no se cuenta dos veces aunque tenga más de un evento registrado (caso que el sistema ya bloquea por la regla de solapamiento del Pitch 2).

### Detalle al hacer clic en cada tarjeta — tablas con acordeón

Cada tarjeta es **navegable**. Al hacer clic, el sistema **expande una tabla interna debajo de la tarjeta** (comportamiento tipo acordeón) sin abandonar la pantalla del dashboard. El Jefe puede abrir varios acordeones a la vez o cerrarlos.

Cada tabla del acordeón tiene **paginación editable** (10 / 25 / 50 / 100 registros por página).

| Tarjeta | Columnas en la tabla del acordeón |
|---|---|
| **Total de empleados activos** | Nombre, CC, Sede, Cargo, Tipo de vinculación |
| **Total de Jefes** | Nombre, CC, Sede asignada, Estado |
| **No disponibles hoy** | Nombre, Sede, Tipo de evento (Vacaciones/Incapacidad/Permiso), Fecha inicio, Fecha fin |

El acordeón muestra en su encabezado el nombre de la tarjeta y el conteo actual. Un icono de chevron (`∨` / `∧`) indica si está expandido o colapsado.

### Breadboard

```
[Dashboard — vista del Jefe]
  ├── Tarjeta "Total de empleados activos"  [N] [∨]
  │     └── Acordeón expandido:
  │           Tabla: Nombre | CC | Sede | Cargo | Vinculación
  │           Paginación: 10 | 25 | 50 | 100 registros
  ├── Tarjeta "Total de Jefes"  [N] [∨]
  │     └── Acordeón expandido:
  │           Tabla: Nombre | CC | Sede asignada | Estado
  │           Paginación: 10 | 25 | 50 | 100 registros
  └── Tarjeta "No disponibles hoy"  [N] [∨]
        └── Acordeón expandido:
              Tabla: Nombre | Sede | Tipo de evento | Fecha inicio | Fecha fin
              Paginación: 10 | 25 | 50 | 100 registros
```

## 4. Rabbit Holes

- **Datos en tiempo real:** el dashboard muestra los datos al momento de cargar la página. No hay actualización automática en vivo. Si el Jefe quiere datos frescos, recarga la página.
- **Acordeones múltiples:** el Jefe puede tener los tres acordeones abiertos al mismo tiempo. No hay lógica de "solo uno abierto a la vez".
- **Paginación de acordeones:** la selección de registros por página es independiente para cada acordeón y persiste mientras el acordeón esté abierto. Al cerrar y volver a abrir, regresa a la página 1.
- **"No disponibles" incluye empleados temporales:** un empleado temporal en novedad cuenta igual que uno con contrato directo.
- **El conteo de Jefes incluye al Jefe que está viendo el dashboard:** es el comportamiento esperado y correcto.

## 5. No-Gos

- No hay gráficas ni visualizaciones tipo torta o barras en este ciclo. Solo tarjetas numéricas con drill-down.
- No hay filtro por sede dentro del dashboard (el Jefe ve siempre el consolidado total).
- No hay comparativas históricas (ej. “este mes vs. mes pasado”).
- No hay exportación directa desde el dashboard; para exportar, el Jefe navega al módulo correspondiente.
- El dashboard no está disponible para Regente, Auxiliar ni Operario en este ciclo.

---

---

# Pitch 7 — Panel de Datos Maestros

## 1. Problema

El sistema depende de tablas de referencia (sedes, cargos, empresas temporales, plantillas de turno) que hoy no tienen un lugar centralizado de administración. Cuando se necesita agregar una nueva sede o corregir el nombre de un cargo, no hay un flujo definido ni validaciones que impidan dejar datos en un estado inconsistente (ej: desactivar un cargo que todavía tiene empleados asignados).

**Historia representativa:** La empresa abre una nueva sede. El Jefe necesita registrarla para poder asignarle empleados. No existe un formulario para eso dentro del sistema; tendría que pedírselo al desarrollador.

## 2. Appetite

**Small Batch — 1 semana** (1 diseñador + 1 programador)

Son formularios ABM estándar. El valor está en las validaciones y los modales de alerta, no en lógica de negocio compleja.

## 3. Datos Maestros del Sistema

Los **datos maestros** son las tablas de referencia que alimentan los selectores y catálogos del resto de módulos. Cualquier cambio en ellos impacta en todo el sistema.

| Tabla maestra | Campos | Usada en |
|---|---|---|
| **Sedes** | Nombre, Dirección, Ciudad, Estado (`Activa` / `Inactiva`) | Registro de empleados, Eventos, Dashboard |
| **Cargos** | Nombre del cargo, Estado (`Activo` / `Inactivo`) | Registro de empleados, Filtros |
| **Empresas Temporales** | Nombre, Estado (`Activa` / `Inactiva`) | Registro de empleados con vinculación `Temporal` |
| **Plantillas de Turno** | Nombre, Configuración por día (Lun–Dom), Estado (`Activa` / `Inactiva`) | Asignación de horarios |

> **¿Por qué no Roles?** Los roles (`Jefe`, `Regente`, `Auxiliar de Regente`, `Operario`) son fijos en el sistema y no deben ser editables por ningún usuario. No son datos maestros modificables.

## 3. Solución

### Panel de Datos Maestros (acceso exclusivo: rol `Jefe`)

Vista con **pestañas**, una por cada tabla maestra. Al entrar al panel, la pestaña activa por defecto es **Sedes**.

#### CRUD por tabla

Cada tabla presenta:
- **Listado** con paginación editable (10 / 25 / 50 / 100 registros) y columnas clave.
- **Botón "Nuevo"** → abre modal con formulario de creación.
- **Botón "Editar"** por fila → abre modal con los campos precargados para modificar.
- **Botón "Desactivar"** por fila → abre modal de confirmación con advertencia contextual.

#### Modales de alerta — reglas de bloqueo

El sistema **nunca elimina físicamente** un dato maestro. En cambio, lo desactiva. Pero antes de desactivar, valida y muestra el modal correspondiente:

| Caso | Comportamiento del modal |
|---|---|
| Intentar desactivar una **Sede** que tiene empleados activos asignados | ⚠️ Modal de bloqueo: *"No se puede desactivar. La sede tiene N empleados activos. Reasígnalos antes de continuar."* Botón "Desactivar" deshabilitado. |
| Intentar desactivar un **Cargo** que tiene empleados activos asignados | ⚠️ Modal de bloqueo: *"No se puede desactivar. El cargo está asignado a N empleados activos."* |
| Intentar desactivar una **Empresa Temporal** con empleados activos vinculados | ⚠️ Modal de bloqueo: *"No se puede desactivar. Hay N empleados activos contratados por esta empresa."* |
| Intentar desactivar una **Plantilla de Turno** asignada a empleados activos | ⚠️ Modal de advertencia: *"Esta plantilla está asignada a N empleados. Al desactivarla seguirá visible en sus perfiles pero no podrá asignarse a nuevos empleados."* Permite confirmar o cancelar. |
| Intentar desactivar cualquier maestro sin dependencias activas | Modal de confirmación estándar: *"¿Desactivar [nombre]? Esta acción se puede revertir."* |
| Crear un dato maestro con nombre duplicado (exacto) | Modal de error: *"Ya existe un registro con ese nombre. Usa un nombre diferente."* Botón "Guardar" deshabilitado hasta corregir. |

#### Campos de cada formulario

**Sede:**
- Nombre *(obligatorio)*
- Ciudad *(obligatorio)*
- Dirección *(obligatorio)*

**Cargo:**
- Nombre del cargo *(obligatorio)*

**Empresa Temporal:**
- Nombre de la empresa *(obligatorio)*

**Plantilla de Turno:**
- Nombre de la plantilla *(obligatorio)*
- Para cada día (Lun, Mar, Mié, Jue, Vie, Sáb, Dom): Hora entrada / Hora salida / `No labora`
- Validación: al menos un día debe tener horario configurado (no puede guardarse una plantilla con todos los días en `No labora`)

### Breadboard

```
[Panel de Datos Maestros] — solo Jefe
  ├── Pestaña "Sedes"
  │     → Tabla con paginación (10|25|50|100) + Filtrar por Estado
  │     → [Nueva sede] → Modal formulario
  │     → Fila: [Editar] → Modal precargado | [Desactivar] → Modal validación
  ├── Pestaña "Cargos"
  │     → Tabla con paginación + Filtrar por Estado
  │     → [Nuevo cargo] → Modal formulario
  │     → Fila: [Editar] | [Desactivar] → Modal validación
  ├── Pestaña "Empresas Temporales"
  │     → Tabla con paginación + Filtrar por Estado
  │     → [Nueva empresa] → Modal formulario
  │     → Fila: [Editar] | [Desactivar] → Modal validación
  └── Pestaña "Plantillas de Turno"
        → Tabla con paginación + Filtrar por Estado
        → [Nueva plantilla] → Modal formulario con grilla L–Dom
        → Fila: [Editar] | [Desactivar] → Modal validación
```

## 4. Rabbit Holes

- **Reactivar datos maestros:** un dato desactivado puede volver a activarse desde la misma pantalla (botón "Activar" visible en registros con estado `Inactivo`). No requiere flujo especial.
- **Duplicados con diferente capitalización:** "Norte" y "norte" se consideran duplicados. La validación es case-insensitive en el servidor.
- **Eliminar datos maestros:** la eliminación física **no existe** en ningún caso. Solo desactivación. El botón visible siempre dice "Desactivar", nunca "Eliminar".
- **Plantillas con empleados activos y desactivación con advertencia:** el empleado conserva su turno asignado para consulta en el historial, pero en el selector de asignación de nuevos turnos no aparecerá la plantilla desactivada.

## 5. No-Gos

- No hay gestión de roles desde el panel. Los roles son fijos.
- No hay importación masiva de datos maestros desde Excel.
- No hay auditoría de cambios en datos maestros en este ciclo (quién cambió qué campo).
- No hay versioning de plantillas de turno (si se edita una plantilla, los empleados que la tienen asignada conservan los horarios al momento de la asignación, no la versión nueva — eso se trata en un ciclo posterior).

---

---

## Resumen de Apuestas (Betting Table)

| # | Pitch | Tipo | Ciclo sugerido | Dependencias |
|---|---|---|---|---|
| 1 | Gestión de Empleados | Big Batch | Ciclo 1 | Ninguna — es la base |
| 5 | Autenticación y Seguridad | Small Batch | Ciclo 1 (en paralelo) | Ninguna |
| 7 | Panel de Datos Maestros | Small Batch | Ciclo 1 (en paralelo) | Ninguna |
| 2 | Control de Eventos Laborales | Big Batch | Ciclo 2 | Requiere Pitch 1 |
| 3 | Jornadas y Horarios | Small Batch | Ciclo 2 (paralelo con Pitch 2) | Requiere Pitches 1 y 7 |
| 4 | Gestión de Horas Extras | Small Batch | Ciclo 2 (paralelo con Pitch 2) | Requiere Pitch 1 |
| 6 | Dashboard del Jefe | Small Batch | Ciclo 2 (paralelo, al final) | Requiere Pitches 1, 2, 3 y 4 |

### Principios Shape Up aplicados a este proyecto

> **Tiempo fijo, alcance variable.** Si algo resulta más complejo de lo esperado durante la construcción, se recorta el alcance — no se extiende el ciclo.

> **Circuit Breaker.** Si un pitch no se completa dentro del ciclo apostado, no recibe extensión automática. El equipo reformula el problema o recorta el alcance. El Ciclo 1 tiene 6 semanas; si los Pitches 1, 5 y 7 no se terminan, cada uno compite de nuevo en la Betting Table del cool-down siguiente.

> **Un ciclo a la vez.** El Ciclo 2 no se confirma hasta la Betting Table del cool-down que sigue al Ciclo 1. La secuencia sugerida en esta tabla es orientativa, no un compromiso definitivo.

> **Cool-down entre ciclos.** Dos semanas después del Ciclo 1 (y del Ciclo 2) sin trabajo programado. El equipo usa ese tiempo para corregir bugs, explorar deuda técnica y preparar los pitches del siguiente ciclo. La Betting Table se reúne en ese período.

---

## Método `ObtenerResponsable(empleado)`

El sistema debe garantizar que **siempre** haya un responsable identificado para cualquier empleado. Este método reside en `EmpleadoService` y es consumido por `EventoService`, `HoraExtraService` y cualquier proceso que requiera escalar acciones de supervisión.

```
ObtenerResponsable(empleado):
  1. Si el empleado tiene JefeInmediatoId asignado y activo   → devolver ese Jefe
  2. Si no tiene Jefe asignado                               → devolver el Jefe de la sede del empleado
  3. Si la sede no tiene Jefe activo                         → devolver el Jefe con mayor antigüedad activo en el sistema
  4. Si no hay ningún Jefe activo en el sistema              → lanzar excepción controlada (caso de configuración incorrecta)
```

---

## Reglas de Negocio Transversales

1. **Integridad referencial:** todo empleado debe tener Sede, Cargo, Rol y Fecha de ingreso antes de poder ser guardado.
2. **Tipo de vinculación obligatorio:** todo empleado indica si su contrato es `Directo` o `Temporal`. Si es `Temporal`, el nombre de la empresa temporal, la fecha de inicio y la fecha de fin del contrato son obligatorios.
3. **Un Jefe por sede:** cada sede tiene exactamente un usuario con rol `Jefe` asignado. El sistema no permite asignar un segundo Jefe a la misma sede.
4. **Visibilidad global del Jefe:** el Jefe ve y puede actuar sobre empleados de **todas las sedes**. El Regente y el Auxiliar ven únicamente los empleados de su propia sede.
5. **Creación de usuarios exclusiva del Jefe:** solo el rol `Jefe` tiene acceso al formulario de nuevo empleado/usuario. El Regente y el Auxiliar solo pueden editar registros existentes de su sede.
6. **Empleados desvinculados en sección separada:** los empleados con estado `Inactivo` no aparecen en la lista activa. Se accede a ellos desde la vista "Empleados desvinculados" (solo-lectura para todos los roles).
7. **Jefe inmediato filtrado por sede:** al seleccionar la sede en el formulario de un empleado, el selector de Jefe inmediato muestra solo los jefes activos de esa sede.
8. **Paginación editable en todas las tablas:** toda tabla del sistema (empleados activos, desvinculados, eventos, horas extras, datos maestros, acordeones del dashboard) expone un selector de registros por página con las opciones 10 / 25 / 50 / 100.
9. **Datos maestros no eliminables:** ninguna tabla maestra (Sedes, Cargos, Empresas Temporales, Plantillas de Turno) permite eliminación física. Solo desactivación, con validación de dependencias activas y modal de alerta contextual.
10. **Historial perpetuo:** todos los registros de actividades y novedades (eventos laborales, horas extras, cambios de turno, desvinculación) quedan vinculados al empleado de forma permanente, incluso si pasa a estado `Inactivo`.
11. **Soft delete general:** ningún registro del sistema se elimina físicamente.
12. **Saldo de vacaciones:** se calcula automáticamente a partir de la fecha de ingreso (15 días hábiles por año trabajado). El sistema descuenta los días al registrar un evento de vacaciones y bloquea el registro si no hay saldo suficiente.
13. **Seguridad:** las contraseñas se almacenan con **hash HMACSHA512 + salt aleatorio por usuario** (campos `PasswordHash` y `PasswordSalt` en la tabla `Usuarios`). El servidor valida permisos en cada petición (nunca solo en el cliente).
14. **Auditoría mínima:** toda acción de aprobación, rechazo o cambio de estado registra el usuario que la realizó y la fecha/hora exacta.
15. **Sesión segura:** cierre de sesión automático por inactividad (30 minutos por defecto). Los tokens de recuperación de contraseña son de un solo uso y expiran en 1 hora.

---

## Pendientes y Decisiones Abiertas

> Estos puntos surgieron durante el refinamiento y deben resolverse antes de iniciar la construcción del ciclo correspondiente.

| # | Punto abierto | Afecta | Prioridad |
|---|---|---|---|
| A | Definir si Regente y Auxiliar de Regente tienen alguna diferencia de permisos, o son equivalentes | Pitch 1 / Matriz de roles | Alta — antes del Ciclo 1 |
| B | Definir quién es el **Administrador Global** (persona o cargo) que aprueba horas extras del Jefe de sede | Pitch 4 | Alta — antes del Ciclo 2 |
| C | Confirmar si el cálculo de vacaciones debe excluir festivos nacionales (requiere mantener un catálogo de festivos) | Pitch 2 | Media — antes del Ciclo 2 |
| D | Definir el saldo inicial de días de vacaciones para empleados que ya existían antes de implementar el sistema | Pitch 2 | Alta — antes del Ciclo 2 |
| E | **Conflicto de diseño — aprobación de horas extras:** el documento de Pitches v1.0 asigna la facultad de aprobar/rechazar al `Regente` (sobre su equipo), mientras que la Matriz de Roles de este documento la asigna exclusivamente al `Jefe`. Deben alinearse ambas fuentes antes de construir el Pitch 4. | Pitch 4 / Matriz de roles | Alta — antes del Ciclo 2 |
