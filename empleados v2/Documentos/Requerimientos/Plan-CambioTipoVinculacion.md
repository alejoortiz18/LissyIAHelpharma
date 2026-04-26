# Plan de Ejecución — Cambio de Tipo de Vinculación (Temporal → Directo)

> **Versión:** 1.0  
> **Fecha:** 25 de abril de 2026  
> **Sistema:** GestionPersonal — Módulo Gestión de Empleados  
> **Funcionalidad bajo prueba:** Cambio del tipo de vinculación de un empleado de `Temporal` a `Directo`

---

## 1. Objetivo

Verificar que el sistema permite cambiar correctamente el tipo de vinculación de un empleado de `Temporal` a `Directo`, y que tras el cambio:

- Los campos del contrato temporal se limpian correctamente.
- La `FechaIngreso` del empleado permanece inalterada.
- La `FechaInicioContrato` se actualiza a la fecha del cambio.
- El saldo de vacaciones comienza a calcularse **desde la nueva `FechaInicioContrato`**, no desde la fecha de ingreso original ni desde el contrato temporal anterior.
- El saldo anterior (acumulado durante el período temporal) **no se hereda** — el contador inicia en cero.

---

## 2. Reglas de Negocio Aplicables

| # | Regla |
|---|-------|
| RN-01 | `TipoVinculacion` cambia de `Temporal` a `Directo`. |
| RN-02 | `EmpresaTemporalId` pasa a `NULL` al cambiar a Directo. |
| RN-03 | `FechaFinContrato` pasa a `NULL` (ya no aplica). |
| RN-04 | `FechaInicioContrato` se establece como la **fecha en que se realiza el cambio** (hoy). |
| RN-05 | `FechaIngreso` **no cambia** — sigue siendo la fecha en que el empleado comenzó a laborar en la empresa. |
| RN-06 | El cálculo de vacaciones usa `FechaInicioContrato` como base: **1.25 días/mes = 15 días/año**. |
| RN-07 | Los días acumulados durante el contrato temporal **no se trasladan** — el nuevo contrato directo comienza con saldo `0`. |
| RN-08 | Solo el rol **Analista** (`sofia.gomez@yopmail.com`) puede editar y guardar este cambio. |
| RN-09 | La sección de contrato temporal (Empresa Temporal, Fecha Inicio, Fecha Fin) debe ocultarse/limpiarse al seleccionar `Directo` en el formulario. |

---

## 3. Datos del Empleado de Prueba

> El empleado de prueba debe **crearse** durante la ejecución del plan (no existe en el seeding base).

| Campo | Valor |
|---|---|
| **Nombre completo** | Marco Antonio Díaz Peña |
| **Cédula** | `99887766` |
| **Fecha de nacimiento** | `1995-05-10` |
| **Teléfono** | `3001234567` |
| **Correo electrónico** | `marco.diaz@yopmail.com` |
| **Correo de acceso (login)** | `marco.diaz@yopmail.com` |
| **Contraseña inicial** | `Usuario1` |
| **Dirección** | `Cra 30 #20-15` |
| **Ciudad** | Medellín |
| **Departamento** | Antioquia |
| **Nivel de escolaridad** | Técnico |
| **EPS** | Sura EPS |
| **ARL** | Sura ARL |
| **Sede** | Medellín |
| **Cargo** | Cajero |
| **Rol en el sistema** | Direccionador |
| **Jefe inmediato** | Laura Patricia Sánchez Gómez |
| **Tipo de vinculación** | `Temporal` |
| **Empresa temporal** | ManpowerGroup Colombia |
| **Fecha de ingreso** | `2025-04-25` (hace exactamente 1 año) |
| **Fecha inicio contrato** | `2025-04-25` |
| **Fecha fin contrato** | `2026-04-25` |
| **Días vacaciones previos** | `0` |
| **Contacto de emergencia** | Rosa Peña — 3009876543 |

### Credenciales del Analista (ejecuta la prueba)

| Campo | Valor |
|---|---|
| Correo | `sofia.gomez@yopmail.com` |
| Contraseña | `Usuario1` |

---

## 4. Precondiciones

1. La aplicación está corriendo en `http://localhost:5002`.
2. La base de datos tiene el seeding completo aplicado (`Seeding_Completo.sql`).
3. El empleado **Marco Antonio Díaz Peña** **no existe** en la BD antes de iniciar (si existe de ejecuciones anteriores, eliminarlo o reusar el existente ajustando las fechas).
4. La empresa temporal **ManpowerGroup Colombia** existe en los catálogos.
5. El cargo **Cajero** existe en los catálogos.
6. El usuario Analista (`sofia.gomez@yopmail.com`) tiene estado `Activo` y `DebeCambiarPassword = 0`.

---

## 5. Casos de Prueba

---

### TC-VIN-01 — Crear empleado con contrato temporal (configuración inicial)

**Objetivo:** Crear el empleado de prueba con todos los datos del contrato temporal.

**Actor:** Analista (`sofia.gomez@yopmail.com`)

**Pasos:**

1. Iniciar sesión como Analista.
2. Ir a `/Empleado`.
3. Hacer clic en **"Nuevo empleado"**.
4. Completar todos los campos según la tabla de datos del empleado de prueba (sección 3).
5. En **Tipo de vinculación** seleccionar `Temporal`.
6. Verificar que aparece la sección de contrato temporal con los campos: Empresa temporal, Fecha inicio contrato, Fecha fin contrato.
7. Completar:
   - Empresa temporal: `ManpowerGroup Colombia`
   - Fecha inicio contrato: `2025-04-25`
   - Fecha fin contrato: `2026-04-25`
8. Hacer clic en **Guardar**.

**Resultado esperado:**

- El empleado aparece en la lista de empleados activos.
- El perfil muestra `TipoVinculacion = Temporal`.
- La sección de contrato temporal muestra empresa, fecha inicio y fecha fin correctas.
- `FechaIngreso` = `2025-04-25`.

---

### TC-VIN-02 — Verificar saldo de vacaciones ANTES del cambio (con contrato temporal)

**Objetivo:** Confirmar el saldo de vacaciones acumulado durante 1 año de contrato temporal.

**Actor:** Analista

**Pasos:**

1. Navegar al perfil de **Marco Antonio Díaz Peña**.
2. Ir a la pestaña **"Historial"** o al módulo de eventos.
3. Registrar un evento de tipo **Vacaciones** para verificar el saldo disponible que muestra el sistema.

**Cálculo esperado:**

> La fecha de hoy es `2026-04-25`.  
> `FechaInicioContrato` = `2025-04-25`.  
> Meses laborados = 12 meses exactos.  
> Días acumulados = `12 × 1.25 = 15 días`.  
> Días tomados = 0.  
> **Saldo disponible = 15 días**.

| Dato | Valor esperado |
|---|---|
| Días acumulados | `15` |
| Días tomados | `0` |
| Días disponibles | `15` |

**Resultado esperado:**

- El saldo disponible muestra **15 días**.

---

### TC-VIN-03 — Cambiar tipo de vinculación de Temporal a Directo

**Objetivo:** Ejecutar el cambio de contrato usando el formulario de edición.

**Actor:** Analista

**Pasos:**

1. Navegar al perfil de **Marco Antonio Díaz Peña**.
2. Hacer clic en **"Editar"**.
3. En el campo **Tipo de vinculación**, cambiar de `Temporal` a `Directo`.
4. Verificar que la sección de contrato temporal (Empresa temporal, Fecha fin contrato) **desaparece o se limpia**.
5. En el campo **Fecha inicio contrato** (ahora del contrato directo) ingresar la fecha de hoy: `2026-04-25`.
6. Verificar que **Fecha fin contrato** queda en blanco / NULL.
7. Verificar que **Empresa temporal** queda en blanco / NULL.
8. Verificar que **Fecha de ingreso** sigue mostrando `2025-04-25` (sin cambio).
9. Hacer clic en **Guardar**.

**Resultado esperado:**

- El sistema guarda sin errores.
- El perfil muestra un mensaje de confirmación.
- El empleado permanece en estado `Activo`.

---

### TC-VIN-04 — Verificar datos del empleado DESPUÉS del cambio

**Objetivo:** Confirmar que los campos quedaron guardados correctamente.

**Actor:** Analista

**Pasos:**

1. Abrir el perfil de **Marco Antonio Díaz Peña** (modo lectura / pestaña Datos).
2. Revisar cada campo de vinculación.

**Resultado esperado:**

| Campo | Valor esperado |
|---|---|
| Tipo de vinculación | `Directo` |
| Empresa temporal | — (vacío / no aplica) |
| Fecha de ingreso | `2025-04-25` |
| Fecha inicio contrato | `2026-04-25` |
| Fecha fin contrato | — (vacío / NULL) |

---

### TC-VIN-05 — Verificar saldo de vacaciones DESPUÉS del cambio

**Objetivo:** Confirmar que el saldo de vacaciones se calcula desde la nueva `FechaInicioContrato` y **no** hereda los 15 días del período temporal.

**Actor:** Analista

**Pasos:**

1. Ir al módulo de eventos o intentar registrar una **Vacación** para Marco Antonio.
2. Observar el saldo disponible mostrado por el sistema.

**Cálculo esperado:**

> `FechaInicioContrato` nueva = `2026-04-25` (hoy, mismo día del cambio).  
> Meses laborados bajo contrato directo = 0 meses (o < 1 mes si se ejecuta el día del cambio).  
> Días acumulados = `0 × 1.25 = 0 días`.  
> Días disponibles = **0 días**.

| Dato | Valor esperado |
|---|---|
| Días acumulados | `0` |
| Días tomados | `0` |
| Días disponibles | `0` |

**Resultado esperado:**

- El saldo muestra **0 días disponibles** — el contador comenzó desde cero con el nuevo contrato directo.
- El sistema **no hereda** los 15 días del período temporal.

---

### TC-VIN-06 — Intentar registrar vacaciones con saldo cero (validación de bloqueo)

**Objetivo:** Confirmar que el sistema bloquea el guardado de vacaciones si el saldo es insuficiente.

**Actor:** Analista

**Pasos:**

1. Ir a **Nuevo evento → Vacaciones** para Marco Antonio Díaz Peña.
2. Seleccionar un rango de fechas de 5 días (ej: `2026-04-28` al `2026-05-02`).
3. Observar el mensaje de saldo disponible.
4. Intentar guardar.

**Resultado esperado:**

- El sistema muestra advertencia de saldo insuficiente.
- El guardado **es bloqueado** (no se crea el evento de vacaciones).
- Mensaje de error visible al usuario.

---

### TC-VIN-07 — Verificar que la FechaIngreso no cambió en el historial

**Objetivo:** Confirmar que la fecha de ingreso original se preserva como dato histórico.

**Actor:** Analista

**Pasos:**

1. Abrir el perfil de Marco Antonio.
2. Ir a la pestaña **"Historial"**.
3. Verificar la sección de datos del empleado o del evento de alta.

**Resultado esperado:**

- `FechaIngreso` = `2025-04-25` — intacta, refleja cuándo inició en la empresa.

---

### TC-VIN-08 — Verificar que el saldo crece proporcionalmente con el nuevo contrato (proyección a 1 mes)

**Objetivo:** Confirmar que el cálculo de acumulación funciona correctamente bajo el contrato directo.

> **Nota:** Este caso se ejecuta **simulando** la consulta de saldo como si hubiera pasado 1 mes desde el cambio, o bien se ejecuta en una fecha futura. Si el sistema no permite manipular la fecha, documentar este caso como **verificación manual** o **prueba diferida**.

**Cálculo esperado a 1 mes del cambio (`2026-05-25`):**

> Meses bajo contrato directo = 1.  
> Días acumulados = `1 × 1.25 = 1.25` → truncado a `1` (integer).  
> Días disponibles = **1 día**.

| Dato | Valor esperado |
|---|---|
| Días acumulados | `1` |
| Días disponibles | `1` |

---

### TC-VIN-09 — Rol sin permisos no puede editar el tipo de vinculación

**Objetivo:** Confirmar que un Operario o Direccionador no puede acceder a editar el empleado para cambiar su contrato.

**Actor:** Marco Antonio Díaz Peña (`marco.diaz@yopmail.com` — rol Direccionador)

**Pasos:**

1. Iniciar sesión como `marco.diaz@yopmail.com` / `Usuario1`.
   - Si el sistema exige cambio de contraseña en primer login, saltear con la nueva contraseña y volver al test.
2. Intentar navegar a `/Empleado/Editar/{id-de-Marco}`.

**Resultado esperado:**

- El sistema redirige a una vista de acceso denegado o no muestra el botón de editar.
- No es posible modificar el tipo de vinculación desde este rol.

---

## 6. Resumen de Resultados Esperados

| TC | Descripción | Resultado esperado |
|---|---|---|
| TC-VIN-01 | Crear empleado temporal | Creado correctamente con datos temporales |
| TC-VIN-02 | Saldo vacaciones ANTES del cambio | 15 días disponibles (1 año × 1.25/mes) |
| TC-VIN-03 | Ejecutar cambio Temporal → Directo | Guardado sin errores, campos limpios |
| TC-VIN-04 | Verificar campos tras el cambio | TipoVinculacion=Directo, EmpresaTemporal=NULL, FechaFinContrato=NULL, FechaInicioContrato=hoy, FechaIngreso inalterada |
| TC-VIN-05 | Saldo vacaciones DESPUÉS del cambio | 0 días (nuevo contrato, sin herencia del temporal) |
| TC-VIN-06 | Bloqueo al registrar vacaciones con saldo 0 | Sistema bloquea el guardado con mensaje de error |
| TC-VIN-07 | FechaIngreso preservada en historial | `2025-04-25` sin cambios |
| TC-VIN-08 | Proyección 1 mes bajo contrato directo | 1 día acumulado |
| TC-VIN-09 | Rol Direccionador no puede editar | Acceso denegado |

---

## 7. Ejecución del Plan

### Comando sugerido

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"
$env:PYTHONIOENCODING='utf-8'
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\cambio-vinculacion-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null
.venv\Scripts\python.exe -m pytest "Documentos/Pruebas/Playwright/Plan-CambioTipoVinculacion.py" -v --headed --slowmo 800 -s 2>&1 | Tee-Object -FilePath $informe
Write-Host "`nInforme: $informe"
```

> **Nota:** El archivo de pruebas Playwright aún no existe — este plan describe los escenarios a automatizar. El script se creará en una sesión separada.

---

## 8. Notas y Consideraciones

- **Acumulación proporcional:** el sistema usa la fórmula `(int)(meses * 1.25)`. El resultado siempre se trunca al entero inferior (ej: 1.25 días al primer mes se muestra como `1`).
- **Primer día del contrato directo:** si el test se ejecuta el mismo día del cambio, los meses calculados son `0` → saldo = `0`. Esto es correcto.
- **Cédula única:** la cédula `99887766` no debe existir previamente en la BD.
- **Correo único:** `marco.diaz@yopmail.com` no debe estar ya registrado.
- **Dominio de correo:** todos los correos de prueba usan `@yopmail.com` obligatoriamente.
- **Contraseña inicial del nuevo empleado:** el sistema crea la cuenta con `DebeCambiarPassword = 1`. Al hacer login como Marco, será redirigido al cambio de contraseña.
