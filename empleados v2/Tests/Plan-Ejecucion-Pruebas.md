# Plan de Ejecución — Suite Completa de Pruebas
## Sistema GestionPersonal

> **Stack de pruebas:** Python + pytest-playwright  
> **Última actualización:** Abril 2026  
> **Archivos cubiertos:** `test_login.py` · `test_recuperacion.py`

---

## 1. Levantar la Aplicación

Abrir una **terminal dedicada** y dejarla corriendo durante toda la sesión de pruebas:

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

Antes de ejecutar cualquier suite, restaurar el estado base de la base de datos:

```powershell
sqlcmd -S "(localdb)\MSSQLLocalDB" -d GestionPersonal -i "Documentos\BD\Seeding_Completo.sql"
```

> Reaplicar también antes de re-ejecutar `test_login.py` (TC-05 modifica `DebeCambiarPassword`) y ante cualquier fallo inesperado por estado sucio en BD.

---

## 3. Activar el Entorno Virtual

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

---

## 4. Ejecución y Generación del Informe de Resultados

El informe se genera automáticamente en `Tests/resultados/` con nombre que incluye la fecha y hora exactas de ejecución.

### 4.1 Suite completa (login + recuperación)

```powershell
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\plan-pruebas-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null

pytest Tests/test_login.py Tests/test_recuperacion.py `
  -v --headed --slowmo 800 `
  -s `
  2>&1 | Tee-Object -FilePath $informe

Write-Host "`nInforme guardado en: $informe"
```

### 4.2 Solo login (TC-01 a TC-07)

```powershell
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\plan-pruebas-login-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null

pytest Tests/test_login.py `
  -v --headed --slowmo 800 `
  -s `
  2>&1 | Tee-Object -FilePath $informe

Write-Host "`nInforme guardado en: $informe"
```

### 4.3 Solo recuperación de contraseña (TC-12 a TC-15b)

```powershell
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\plan-pruebas-resetpassword-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null

pytest Tests/test_recuperacion.py `
  -v --headed --slowmo 1000 `
  -s `
  2>&1 | Tee-Object -FilePath $informe

Write-Host "`nInforme guardado en: $informe"
```

### 4.4 Suite autónoma — sin TC-13 (sin internet / SMTP)

```powershell
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\plan-pruebas-autonomo-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null

pytest Tests/ -v --headed --slowmo 800 -k "not tc13" `
  -s `
  2>&1 | Tee-Object -FilePath $informe

Write-Host "`nInforme guardado en: $informe"
```

> `Tee-Object` muestra la salida en consola **y** la escribe al archivo simultáneamente.

---

## 5. Formato del Nombre de Informe

```
plan-pruebas-{YYYY-MM-DD_HH-mm-ss}.txt
```

**Ejemplos:**
```
plan-pruebas-2026-04-22_14-35-07.txt
plan-pruebas-login-2026-04-22_14-35-07.txt
plan-pruebas-resetpassword-2026-04-22_14-35-07.txt
plan-pruebas-autonomo-2026-04-22_14-35-07.txt
```

Los archivos se acumulan en `Tests/resultados/` sin sobrescribirse entre ejecuciones.

---

## 6. Contenido del Informe Generado

Cada `.txt` captura la salida completa de pytest, incluyendo:

```
============================= test session starts ==============================
platform win32 -- Python 3.14.2, pytest-8.x, pluggy-1.x
collected 12 items

Tests/test_login.py::test_tc01_login_credenciales_correctas PASSED    [ 8%]
Tests/test_login.py::test_tc02_password_incorrecta PASSED             [16%]
...
Tests/test_recuperacion.py::test_tc14_restablecer_con_token_valido PASSED

============================== 12 passed in 47.3s ==============================
```

---

## 7. Flujo de Sesión Completo

```
1. Terminal A → levantar app:
   dotnet run --project GestionPersonal.Web/GestionPersonal.Web.csproj --launch-profile http

2. Terminal B → activar entorno virtual:
   .venv\Scripts\Activate.ps1

3. Terminal B → aplicar seeding:
   sqlcmd -S "(localdb)\MSSQLLocalDB" -d GestionPersonal -i "Documentos\BD\Seeding_Completo.sql"

4. Terminal B → ejecutar suite con informe:
   $fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
   $informe = "Tests\resultados\plan-pruebas-$fecha.txt"
   New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null
   pytest Tests/ -v --headed --slowmo 800 -k "not tc13" -s 2>&1 | Tee-Object -FilePath $informe

5. Revisar informe en: Tests\resultados\plan-pruebas-<fecha>.txt
```

---

## 8. Estructura de Resultados

```
Tests/
├── resultados/
│   ├── plan-pruebas-2026-04-22_14-35-07.txt
│   ├── plan-pruebas-login-2026-04-22_15-10-22.txt
│   └── ...
├── conftest.py
├── helpers.py
├── test_login.py
└── test_recuperacion.py
```

---

## 9. Referencia de Planes por Módulo

| Plan | Ubicación | Contenido |
|---|---|---|
| Login | `Documentos/Pruebas/Playwright/Plan-Ejecucion-Playwright-Login.md` | TC-01 a TC-07 — autenticación y sesión |
| Reset Password | `Documentos/Pruebas/Playwright/Plan-Ejecucion-Playwright-ResetPassword.md` | TC-12 a TC-15b — recuperación por token |

```

---

## 10. Referencia de Planes por Módulo
terminado todo el proceso de pruebas detener la aplicación