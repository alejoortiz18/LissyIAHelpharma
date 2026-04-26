# Pitch — Ajuste al Formulario de Creación de Empleado

> **Metodología:** Shape Up (Basecamp) — https://basecamp.com/shapeup  
> **Versión:** 1.0  
> **Fecha:** 25 de abril de 2026  
> **Sistema:** GestionPersonal — Módulo Gestión de Empleados  
> **Módulo afectado:** Formulario de creación (`/Empleado/Crear`) y edición (`/Empleado/Editar`)

---

## 1. Problema

El formulario de creación de empleado exige datos que no siempre están disponibles en el momento del registro, bloqueando el alta del empleado hasta que se consigan. Específicamente:

- **EPS** está marcada como obligatoria (`[Required]`), pero en muchos ingresos nuevos esa información aún no está confirmada. El coordinador se ve forzado a escribir un valor inventado o esperar días para poder registrar al empleado.
- **Contacto de emergencia** también está marcado como obligatorio, pero no todos los empleados entregan ese dato desde el primer día.
- Adicionalmente, el formulario no diferencia qué campos aplican según el **tipo de vinculación** elegido, lo que genera confusión: para un empleado de **Contrato Directo** se muestra y exige lo mismo que para uno de **Empresa Temporal**, siendo que la lógica de cada uno es distinta.

**Historia representativa:** La regente de una sede quiere registrar a un nuevo operario que entró ese mismo día. El empleado aún no ha entregado el dato de su EPS ni el teléfono de un familiar. El sistema le impide guardar el formulario porque esos campos son obligatorios. La regente termina escribiendo `"Pendiente"` en EPS y dejando el contacto en blanco con un número ficticio. Los datos quedan sucios en la base de datos.

---

## 2. Appetite

**Small Batch — 1 semana** (1 programador)

Se trata de ajustes de validación y comportamiento condicional de campos en capas ya existentes (DTO, Vista, Service). No requiere cambios de esquema en la base de datos. El modelo de datos ya soporta estos campos como nullable.

---

## 3. Solución

### 3.1 Campos que pasan a ser opcionales

Los siguientes campos dejan de ser obligatorios en creación **y** edición:

| Campo | Estado actual | Estado nuevo |
|---|---|---|
| `Eps` | `[Required]` — muestra `*` en formulario | Opcional — sin `*` |
| `Arl` | Ya era opcional | Sin cambio (confirmar comportamiento) |
| `NivelEscolaridad` | Ya era opcional | Sin cambio (confirmar comportamiento) |
| `ContactoEmergenciaNombre` | `[Required]` — muestra `*` en formulario | Opcional — sin `*` |
| `ContactoEmergenciaTelefono` | `[Required]` — muestra `*` en formulario | Opcional — sin `*` |

> Los campos quedan disponibles en el formulario para que el coordinador los complete cuando tenga la información; simplemente dejan de bloquear el guardado.

### 3.2 Comportamiento condicional según Tipo de Vinculación

El formulario se comporta diferente según la opción elegida en el selector **Tipo de Vinculación**.

**`FechaIngreso` es SIEMPRE visible y obligatoria** para ambos tipos. Representa la fecha en que el empleado comenzó a laborar en la organización.

#### Al seleccionar `Contrato Directo`

```
[Tipo Vinculación = Contrato Directo]
  → Muestra: Fecha de ingreso (obligatorio *)
  → El servicio deriva: FechaInicioContrato = FechaIngreso (misma fecha)
  → Oculta: sección completa de Empresa Temporal
             (Empresa Temporal, Fecha fin contrato)
```

- `FechaIngreso` es **obligatoria** y visible.
- `FechaInicioContrato` **no se ingresa en el formulario** — el servicio la asigna igual a `FechaIngreso` automáticamente.
- La sección de empresa temporal se **oculta completamente**.

#### Al seleccionar `Empresa Temporal`

```
[Tipo Vinculación = Empresa Temporal]
  → Muestra: Fecha de ingreso (obligatorio *)
             sección Empresa Temporal
             (Empresa Temporal *, Fecha fin contrato)
  → FechaInicioContrato = NULL (el servicio siempre la ignora para este tipo)
```

- `FechaIngreso` es **obligatoria** — registra cuándo entró el empleado a la organización.
- `FechaInicioContrato` **siempre queda en `NULL`** en base de datos. El acumulado de vacaciones NO aplica mientras el contrato es temporal.
- `EmpresaTemporalId` es **obligatoria** cuando el tipo es Temporal.

### 3.3 Breadboard del formulario

```
[Formulario Nuevo Empleado]
  ├── Datos personales
  │     NombreCompleto *, Cedula *, FechaNacimiento, Telefono *, CorreoElectronico *
  ├── Residencia
  │     Direccion *, Ciudad *, Departamento *
  ├── Contacto de emergencia          ← sin * (ahora opcional)
  │     ContactoEmergenciaNombre, ContactoEmergenciaTelefono
  ├── Formación
  │     NivelEscolaridad              ← sin * (ya era opcional)
  ├── Seguridad social
  │     Eps                           ← sin * (ahora opcional)
  │     Arl                           ← sin * (ya era opcional)
  └── Vinculación laboral
        Sede *, Cargo *, Rol *, TipoVinculacion *
        JefeInmediato, DiasVacacionesPrevios
        FechaIngreso *          ← SIEMPRE visible y obligatorio (ambos tipos)
        │
        ├── [Si Contrato Directo]
        │     FechaInicioContrato = FechaIngreso (derivado por el servicio)
        │     (ocultar bloque temporal)
        │
        └── [Si Empresa Temporal]
              EmpresaTemporalId *     ← visible y obligatorio
              FechaFinContrato
              FechaInicioContrato = NULL (siempre, gestionado por el servicio)
```

### 3.4 Capas de código afectadas

| Capa | Archivo | Cambio |
|---|---|---|
| DTO (entrada) | `CrearEmpleadoDto.cs` | Quitar `[Required]` de `Eps`, `ContactoEmergenciaNombre`, `ContactoEmergenciaTelefono`. Hacer `FechaIngreso` nullable (`DateOnly?`) con validación condicional en Service. |
| DTO (edición) | `EditarEmpleadoDto.cs` | Mismos ajustes que `CrearEmpleadoDto`. |
| Service | `EmpleadoService.CrearAsync` | Validar `FechaIngreso` requerida solo si `TipoVinculacion == Directo`. |
| Service | `EmpleadoService.EditarAsync` | Ídem. |
| Vista creación | `Crear.cshtml` | Quitar `*` de EPS y Contacto. Lógica JS: mostrar/ocultar `FechaIngreso` y bloque temporal según selector. |
| Vista edición | `Editar.cshtml` | Ídem — ya existe el JS para ocultar empresa temporal; extender para ocultar también `FechaIngreso` cuando tipo = Temporal. |

---

## 4. Rabbit Holes

- **`ContactoEmergencia` como entidad separada:** El contacto de emergencia es una entidad `ContactoEmergencia` con su propia tabla y FK al empleado. Al hacerlo opcional, el Service debe manejar correctamente el caso en que `ContactoEmergenciaNombre` y `ContactoEmergenciaTelefono` vengan vacíos: **no crear la entidad** (dejar `ContactoEmergencia = null`) en lugar de crear un registro vacío. Este caso también aplica en edición: si ya existía y ahora ambos campos se dejan vacíos, ¿se elimina el registro o se deja intacto?  
  **Decisión:** si ambos campos están vacíos, no se crea/actualiza el registro. Si uno tiene valor, ambos son necesarios (validación cruzada del par).

- **`FechaIngreso` en la base de datos:** La columna `FechaIngreso` en la tabla `Empleados` está definida como `NOT NULL`. `FechaIngreso` es **siempre obligatoria** para ambos tipos de vinculación.
  **Regla definitiva para Contrato Directo:** el servicio asigna `FechaInicioContrato = FechaIngreso` automáticamente (misma fecha, no se muestra en el formulario de creación).
  **Regla definitiva para Empresa Temporal:** el servicio siempre asigna `FechaInicioContrato = NULL`. El cálculo de vacaciones no aplica mientras el contrato es temporal. Al cambiar a Directo, el analista ingresa manualmente la `FechaInicioContrato` (que debe ser ≥ `FechaIngreso`).

- **Validación en servidor sin JS:** el comportamiento condicional es en el cliente (JavaScript). Pero si el formulario se envía con JS deshabilitado o por manipulación directa, el servidor debe validar también. El Service debe rechazar cualquier combinación inválida (ej. `TipoVinculacion = Directo` sin `FechaIngreso`).

---

## 5. No-Gos

- **No se modificará el esquema de la base de datos** en este ciclo. `FechaIngreso` permanece `NOT NULL`.
- **No se rediseñará el formulario completo.** Solo se ajustan los campos y la lógica condicional del tipo de vinculación.
- **No se cambiará la validación de otros campos obligatorios** (Nombre, Cédula, Teléfono, Correo, Dirección, Ciudad, Departamento, Sede, Cargo, Rol). Esos siguen siendo requeridos.
- **No se contempla en este ciclo** agregar más tipos de vinculación ni nuevos campos al formulario.
- **No se aplicarán estos cambios al formulario de Desvinculación** (`DesvincularEmpleadoDto`) — ese flujo es independiente.
