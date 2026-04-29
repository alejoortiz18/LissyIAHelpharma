# Plan de Ejecución — Control Jerárquico de Plantillas de Horario
**Sistema:** GestiónRH — Administración de Empleados  
**Requerimiento base:** `Documentos/Requerimientos/RequerimientoCreacionHorario.md`  
**Fecha base:** Abril 2026  
**Archivos de tests:** `Tests/test_plantillas_turno.py` · `Tests/test_asignacion_turnos.py` *(futuros: `test_horario_jerarquia.py`)*  
**Stack de pruebas:** Python + pytest-playwright

---

## Contexto técnico

| Elemento | Valor |
|---|---|
| URL base | `http://localhost:5002` |
| Módulo de horarios | `GET /Turno` |
| Asignación de turno | `GET /Empleado/Perfil/{id}?tab=horario` |
| DB local | `(localdb)\MSSQLLocalDB` · `GestionPersonal` |
| Tabla de plantillas | `dbo.PlantillasTurno` |
| Columna nueva | `CreadoPorId` (FK → `dbo.Empleados.Id`) |

### Usuarios de prueba y jerarquía

```
carlos.rodriguez@yopmail.com  (Jefe nivel 1 — EmpleadoId=1)
 └── laura.sanchez@yopmail.com    (Nivel 2 — EmpleadoId=2, JefeId=1)
       └── andres.torres@yopmail.com   (Colaborador — EmpleadoId=4, JefeId=2)
 └── diana.vargas@yopmail.com     (Colaborador — JefeId=1, sin rol de jefe)
```

> **Contraseña de todos los usuarios de prueba:** `Usuario1`

---

## 1. Levantar la Aplicación

Abrir una **terminal dedicada** y dejarla corriendo durante toda la sesión:

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2\Proyecto MVC"
dotnet run --project GestionPersonal.Web/GestionPersonal.Web.csproj --launch-profile http
```

Esperar hasta ver en consola:
```
Now listening on: http://localhost:5002
```

> **No cerrar esta terminal.** Si se cierra, todos los tests fallarán con `ERR_CONNECTION_REFUSED`.

---

## 2. Preparar Datos de Prueba (Seeding)

Restaurar el estado base de la base de datos antes de ejecutar:

```powershell
sqlcmd -S "(localdb)\MSSQLLocalDB" -d GestionPersonal -i "Documentos\BD\Seeding_Completo.sql"
```

> Reaplicar ante cualquier fallo inesperado por estado sucio en BD.

---

## 3. Activar el Entorno Virtual

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

---

## 4. Categorías de Prueba

| # | Categoría | Casos | Archivo |
|---|---|---|---|
| A | Visibilidad de plantillas propias | TC-HJ-01 a TC-HJ-04 | `test_horario_jerarquia.py` |
| B | Restricción de visibilidad cruzada | TC-HJ-05 a TC-HJ-07 | `test_horario_jerarquia.py` |
| C | Selector de colaboradores al asignar | TC-HJ-08 a TC-HJ-11 | `test_horario_jerarquia.py` |
| D | Restricción de autoasignación | TC-HJ-12 a TC-HJ-13 | `test_horario_jerarquia.py` |
| E | Vista de colaborador (solo-lectura) | TC-HJ-14 a TC-HJ-16 | `test_horario_jerarquia.py` |
| F | Validación backend (HorarioService) | TC-HJ-17 a TC-HJ-19 | `test_horario_jerarquia.py` |

---

## A — Visibilidad de plantillas propias

### TC-HJ-01 · Jefe solo ve sus propias plantillas
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-01 |
| **Precondición** | `carlos.rodriguez` tiene al menos una plantilla con `CreadoPorId = 1` en BD. `laura.sanchez` tiene una plantilla distinta con `CreadoPorId = 2`. |
| **Pasos** | 1. Login como `carlos.rodriguez@yopmail.com` · 2. Navegar a `/Turno` · 3. Revisar las tarjetas visibles |
| **Resultado esperado** | Se muestran SOLO las plantillas de Carlos. No aparecen las de Laura. |
| **Automatizado** | ✅ |

### TC-HJ-02 · Jefe de nivel 2 solo ve sus propias plantillas
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-02 |
| **Precondición** | `laura.sanchez` tiene al menos una plantilla con `CreadoPorId = 2`. Carlos tiene plantillas con `CreadoPorId = 1`. |
| **Pasos** | 1. Login como `laura.sanchez@yopmail.com` · 2. Navegar a `/Turno` · 3. Revisar las tarjetas visibles |
| **Resultado esperado** | Se muestran SOLO las plantillas de Laura. No aparecen las de Carlos. |
| **Automatizado** | ✅ |

### TC-HJ-03 · Jefe nuevo sin plantillas ve lista vacía
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-03 |
| **Precondición** | Usuario jefe sin ninguna plantilla creada por él (`CreadoPorId` sin registros para su ID). |
| **Pasos** | 1. Login como jefe sin plantillas · 2. Navegar a `/Turno` |
| **Resultado esperado** | La sección de plantillas muestra estado vacío ("No hay plantillas creadas") o lista en blanco. No muestra plantillas de otros jefes. |
| **Automatizado** | ✅ |

### TC-HJ-04 · Plantillas recién creadas quedan vinculadas al creador
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-04 |
| **Precondición** | Login como Carlos. |
| **Pasos** | 1. Crear una nueva plantilla de turno desde `/Turno` · 2. Verificar en BD que `CreadoPorId = EmpleadoId de Carlos` |
| **Resultado esperado** | El registro en `dbo.PlantillasTurno` tiene `CreadoPorId` = ID de Carlos. La plantilla aparece en su lista. |
| **Automatizado** | ✅ |

---

## B — Restricción de visibilidad cruzada

### TC-HJ-05 · Plantilla de un jefe NO aparece en la lista de otro jefe del mismo nivel
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-05 |
| **Precondición** | Existen dos jefes del mismo nivel (ej. jefe sede A y jefe sede B), cada uno con plantillas propias. |
| **Pasos** | 1. Login como Jefe sede A · 2. Navegar a `/Turno` · 3. Verificar que las plantillas del Jefe sede B NO aparecen |
| **Resultado esperado** | Cero plantillas del otro jefe son visibles. |
| **Automatizado** | ✅ |

### TC-HJ-06 · Jefe subordinado NO puede ver plantillas del jefe superior
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-06 |
| **Precondición** | Carlos (nivel 1) tiene plantillas. Laura (nivel 2, subordinada de Carlos) tiene login activo. |
| **Pasos** | 1. Login como `laura.sanchez@yopmail.com` · 2. Navegar a `/Turno` · 3. Revisar lista |
| **Resultado esperado** | Laura NO ve las plantillas de Carlos. Solo ve las suyas. |
| **Automatizado** | ✅ |

### TC-HJ-07 · Jefe superior NO puede ver plantillas del jefe subordinado
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-07 |
| **Precondición** | Laura tiene plantillas propias. Carlos está logueado. |
| **Pasos** | 1. Login como `carlos.rodriguez@yopmail.com` · 2. Navegar a `/Turno` · 3. Revisar lista |
| **Resultado esperado** | Carlos NO ve las plantillas de Laura. Solo ve las suyas. |
| **Automatizado** | ✅ |

---

## C — Selector de colaboradores al asignar

### TC-HJ-08 · Selector de asignación muestra solo subordinados directos e indirectos
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-08 |
| **Precondición** | Login como Carlos (nivel 1). Sus subordinados: Laura (directa), Andrés (indirecto vía Laura), Diana (directa). |
| **Pasos** | 1. Login como Carlos · 2. Ir al perfil de un subordinado · 3. Abrir modal de asignación de turno · 4. Revisar el selector de colaboradores |
| **Resultado esperado** | El selector muestra: Laura, Andrés, Diana. NO muestra empleados de otras ramas. |
| **Automatizado** | ✅ |

### TC-HJ-09 · Selector de jefe subordinado muestra solo su propia línea
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-09 |
| **Precondición** | Login como Laura (nivel 2). Su subordinado directo: Andrés. |
| **Pasos** | 1. Login como Laura · 2. Ir al perfil de Andrés · 3. Abrir modal de asignación · 4. Revisar el selector |
| **Resultado esperado** | El selector muestra solo a Andrés. NO muestra a Carlos ni a Diana (subordinados de Carlos, no de Laura). |
| **Automatizado** | ✅ |

### TC-HJ-10 · Colaborador sin subordinados no tiene selector de asignación
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-10 |
| **Precondición** | Login como `andres.torres` (sin subordinados). |
| **Pasos** | 1. Login como Andrés · 2. Navegar al propio perfil · 3. Revisar pestaña de horario |
| **Resultado esperado** | El botón "Asignar / cambiar turno" NO aparece. Solo se muestra el horario asignado (vista lectura). |
| **Automatizado** | ✅ |

### TC-HJ-11 · Selector de plantillas en modal muestra solo las del jefe en sesión
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-11 |
| **Precondición** | Carlos tiene 2 plantillas. Laura tiene 1 plantilla distinta. Login como Carlos. |
| **Pasos** | 1. Login como Carlos · 2. Abrir modal de asignación en perfil de un subordinado · 3. Revisar el `<select>` de plantillas |
| **Resultado esperado** | Solo aparecen las 2 plantillas de Carlos. La plantilla de Laura no está en la lista. |
| **Automatizado** | ✅ |

---

## D — Restricción de autoasignación

### TC-HJ-12 · El jefe NO aparece en el selector de colaboradores (frontend)
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-12 |
| **Precondición** | Login como Carlos. |
| **Pasos** | 1. Login como Carlos · 2. Abrir modal de asignación en perfil de cualquier subordinado · 3. Revisar si Carlos aparece en el selector de "Asignar a" |
| **Resultado esperado** | Carlos (EmpleadoId=1) NO aparece en la lista de colaboradores disponibles. |
| **Automatizado** | ✅ |

### TC-HJ-13 · Backend rechaza asignación cuando `colaboradorId == jefeId`
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-13 |
| **Precondición** | La aplicación está corriendo. |
| **Pasos** | 1. Realizar una llamada HTTP directa (o manipular el request) al endpoint de asignación con `colaboradorId` igual al `EmpleadoId` del jefe en sesión · 2. Verificar la respuesta |
| **Resultado esperado** | El servidor retorna un error (400 o mensaje de validación). El horario NO se guarda en BD. |
| **Resultado NO esperado** | El servidor acepta la asignación y guarda el registro. |
| **Automatizado** | ✅ (requiere request directo via `page.request` o `requests`) |

---

## E — Vista de colaborador (solo-lectura)

### TC-HJ-14 · Colaborador sin rol de jefe solo ve su horario asignado
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-14 |
| **Precondición** | Andrés tiene un horario asignado por Laura. |
| **Pasos** | 1. Login como `andres.torres@yopmail.com` · 2. Navegar a su perfil / sección "Mi Horario" |
| **Resultado esperado** | Se muestra la información del horario asignado en modo solo-lectura. No hay botones de edición ni acceso al listado de plantillas. |
| **Automatizado** | ✅ |

### TC-HJ-15 · Colaborador sin horario asignado ve estado vacío
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-15 |
| **Precondición** | Diana no tiene horario asignado. |
| **Pasos** | 1. Login como `diana.vargas@yopmail.com` · 2. Navegar a su sección de horario |
| **Resultado esperado** | Se muestra mensaje indicando que no tiene horario asignado. No hay plantillas visibles. |
| **Automatizado** | ✅ |

### TC-HJ-16 · Colaborador no puede acceder directamente a `/Turno`
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-16 |
| **Precondición** | Login como Andrés (sin rol de jefe). |
| **Pasos** | 1. Login como Andrés · 2. Navegar directamente a `http://localhost:5002/Turno` |
| **Resultado esperado** | Redirige a página de acceso denegado (403) o al dashboard sin mostrar plantillas. |
| **Automatizado** | ✅ |

---

## F — Validación backend (HorarioService)

### TC-HJ-17 · Asignación a empleado fuera de jerarquía es rechazada por el servicio
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-17 |
| **Precondición** | Laura (nivel 2) intenta asignar un turno a un empleado que NO está bajo su línea (ej. empleado de otra rama de Carlos). |
| **Pasos** | Llamada HTTP directa al endpoint de asignación con `colaboradorId` de un empleado fuera de la jerarquía de Laura |
| **Resultado esperado** | El servidor retorna error de validación. El horario NO se guarda en BD. |
| **Automatizado** | ✅ (request directo) |

### TC-HJ-18 · Asignación con plantilla de otro jefe es rechazada
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-18 |
| **Precondición** | Carlos intenta asignar usando el ID de una plantilla creada por Laura (`CreadoPorId = 2`). |
| **Pasos** | Llamada HTTP directa con `plantillaId` correspondiente a una plantilla de otro jefe |
| **Resultado esperado** | El servidor retorna error. El horario NO se guarda. |
| **Automatizado** | ✅ (request directo) |

### TC-HJ-19 · Asignación válida en jerarquía es aceptada correctamente
| Campo | Detalle |
|---|---|
| **ID** | TC-HJ-19 |
| **Precondición** | Carlos tiene una plantilla propia. Andrés (EmpleadoId=4) está bajo su jerarquía. |
| **Pasos** | 1. Login como Carlos · 2. Asignar plantilla propia a Andrés desde el modal · 3. Verificar en BD que el registro se guardó con los IDs correctos |
| **Resultado esperado** | Registro creado en BD con `EmpleadoId=4`, `PlantillaTurnoId` perteneciente a Carlos, `AsignadoPorId=1`. |
| **Automatizado** | ✅ |

---

## 5. Ejecución y Generación de Informe

### 5.1 Suite completa de jerarquía de horarios

```powershell
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\horario-jerarquia-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null

pytest Tests/test_horario_jerarquia.py `
  -v --headed --slowmo 800 `
  -s `
  2>&1 | Tee-Object -FilePath $informe

Write-Host "`nInforme guardado en: $informe"
```

### 5.2 Solo visibilidad de plantillas (categorías A y B)

```powershell
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\horario-visibilidad-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null

pytest Tests/test_horario_jerarquia.py `
  -v --headed --slowmo 800 `
  -k "tc_hj0[1-7]" `
  -s `
  2>&1 | Tee-Object -FilePath $informe

Write-Host "`nInforme guardado en: $informe"
```

### 5.3 Solo validaciones backend (categoría F)

```powershell
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\horario-backend-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null

pytest Tests/test_horario_jerarquia.py `
  -v --headed --slowmo 600 `
  -k "tc_hj1[7-9]" `
  -s `
  2>&1 | Tee-Object -FilePath $informe

Write-Host "`nInforme guardado en: $informe"
```

### 5.4 Regresión rápida junto con pruebas existentes de turnos

```powershell
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\turnos-regresion-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null

pytest Tests/test_plantillas_turno.py Tests/test_asignacion_turnos.py Tests/test_horario_jerarquia.py `
  -v --headed --slowmo 800 `
  -s `
  2>&1 | Tee-Object -FilePath $informe

Write-Host "`nInforme guardado en: $informe"
```

---

## 6. Precondiciones de BD para pruebas de jerarquía

Antes de ejecutar las categorías A–C, asegurarse de que existan plantillas diferenciadas por jefe.  
Si el seeding no las incluye, ejecutar el siguiente script de preparación:

```sql
-- Plantilla de Carlos (EmpleadoId = 1)
INSERT INTO dbo.PlantillasTurno (Nombre, CreadoPorId)
VALUES ('Turno Mañana Carlos', 1);

-- Plantilla de Laura (EmpleadoId = 2)
INSERT INTO dbo.PlantillasTurno (Nombre, CreadoPorId)
VALUES ('Turno Tarde Laura', 2);
```

> Ajustar los IDs según los datos reales del seeding vigente.

---

## 7. Resumen de criterios de aceptación

| Criterio | TC cubriendo |
|---|---|
| Jefe solo ve sus propias plantillas | TC-HJ-01, TC-HJ-02, TC-HJ-03 |
| Nuevas plantillas quedan vinculadas al creador | TC-HJ-04 |
| No hay visibilidad cruzada entre jefes | TC-HJ-05, TC-HJ-06, TC-HJ-07 |
| Selector de asignación respeta jerarquía | TC-HJ-08, TC-HJ-09 |
| Colaborador sin subordinados no puede asignar | TC-HJ-10 |
| Selector de plantillas en modal es del jefe en sesión | TC-HJ-11 |
| Autoasignación bloqueada en frontend y backend | TC-HJ-12, TC-HJ-13 |
| Colaborador solo ve su horario (solo-lectura) | TC-HJ-14, TC-HJ-15, TC-HJ-16 |
| Backend rechaza operaciones fuera de jerarquía | TC-HJ-17, TC-HJ-18 |
| Asignación válida se persiste correctamente | TC-HJ-19 |
