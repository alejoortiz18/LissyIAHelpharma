# Plan de Ejecución — Pruebas Playwright · Login
## Sistema GestionPersonal — Autenticación y Sesión

> **Stack de pruebas:** Python + pytest-playwright  
> **Modo principal:** Headed (navegador visible) con slowmo para observabilidad  
> **Última actualización:** Abril 2026  
> **Archivo de tests:** `Tests/test_login.py`  
> **Referencia base:** `Documentos/Pruebas/Playwright/Plan-Pruebas-Login.md`

---

## 1. Prerequisitos

### 1.1 Verificar entorno Python

```powershell
python --version
# Requerido: 3.9 o superior — Actual: 3.14.2
```

### 1.2 Instalar dependencias (una sola vez)

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"

pip install pytest pytest-playwright
python -m playwright install chromium
```

> Si ya tienes el `.venv` activo, sustituye `pip` por el pip del entorno virtual.

### 1.3 Verificar instalación

```powershell
pytest --version
python -m playwright --version
```

---

## 2. Levantar la Aplicación

En una **terminal separada** (dejarla corriendo durante toda la sesión de pruebas):

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2\Proyecto MVC"
dotnet run --project GestionPersonal.Web/GestionPersonal.Web.csproj --launch-profile http
```

Esperar hasta ver en consola:
```
Now listening on: http://localhost:5002
```

> No cerrar esta terminal. Abrirla primero antes de ejecutar cualquier prueba.

---

## 3. Preparar Datos de Prueba (Seeding)

Antes de cada sesión de pruebas, ejecutar el seeding completo para asegurar el estado base de la BD:

```powershell
sqlcmd -S "(localdb)\MSSQLLocalDB" -d GestionPersonal -i "Documentos\BD\Seeding_Completo.sql"
```

> **Regla:** `Documentos/BD/Seeding_Completo.sql` es la fuente de verdad. Reaplicarlo **siempre antes** de ejecutar TC-05 (flujo completo primer ingreso), ya que ese test modifica `DebeCambiarPassword` en la BD.

### Estado inicial garantizado por el seeding

| Usuario | Correo | Contraseña | `DebeCambiarPassword` |
|---|---|---|---|
| Carlos Rodríguez | `carlos.rodriguez@yopmail.com` | `Usuario1` | `0` — accede directo al Dashboard |
| Laura Sánchez | `laura.sanchez@yopmail.com` | `Usuario1` | `1` — redirige a CambiarPassword |
| Valentina Ospina | `valentina.ospina@yopmail.com` | `Usuario1` | Inactivo |

---

## 4. Modos de Ejecución

### 4.1 Modo Headed — Navegador visible (recomendado para observar)

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"

pytest Tests/test_login.py -v --headed
```

### 4.2 Modo Headed con SlowMo — Para observar cada acción

```powershell
# 1 segundo entre acciones (recomendado para demostraciones)
pytest Tests/test_login.py -v --headed --slowmo 1000

# 500ms (recomendado para revisión de flujo)
pytest Tests/test_login.py -v --headed --slowmo 500
```

> **Nota:** `--slowmo` solo funciona en modo `--headed`.

### 4.3 Modo Debug (Playwright Inspector)

```powershell
# Inspector abierto — pausa en cada acción, avanzar con Step Over / Continue
$env:PWDEBUG=1 ; pytest Tests/test_login.py -v --headed
```

### 4.4 Captura de Screenshots y Trazas

```powershell
# Screenshot solo al fallar
pytest Tests/test_login.py -v --headed --screenshot only-on-failure --output Tests/screenshots/

# Traza completa (video + red + snapshots DOM)
pytest Tests/test_login.py -v --headed --tracing on --output Tests/traces/

# Abrir una traza grabada
python -m playwright show-trace Tests/traces/<nombre-del-trace>.zip
```

---

## 5. Casos de Prueba

### Scope 1 — Acceso (TC-01 a TC-04)

| TC | Caso | Datos | Resultado esperado |
|---|---|---|---|
| TC-01 | Login Jefe (`DebeCambiarPassword=0`) | `carlos.rodriguez@yopmail.com` / `Usuario1` | Redirige a `/Dashboard` |
| TC-02 | Contraseña incorrecta | `carlos.rodriguez@yopmail.com` / `WrongPass123` | Permanece en `/Cuenta/Login`, mensaje `"Datos incorrectos"` |
| TC-03 | Correo inexistente | `noexiste@yopmail.com` / `Usuario1` | Permanece en `/Cuenta/Login`, mensaje `"Datos incorrectos"` |
| TC-04 | Campos vacíos | — | Errores de validación en ambos campos |

```powershell
pytest Tests/test_login.py -k "tc01 or tc02 or tc03 or tc04" -v --headed --slowmo 800
```

**Definición de done:** Los 4 casos en verde `PASSED`.

---

### Scope 2 — Primer Ingreso / CambiarPassword (TC-05)

> **IMPORTANTE:** Reaplicar el seeding antes. TC-05 establece `DebeCambiarPassword=0` en BD y no es reversible sin seeding.

| TC | Caso | Datos | Resultado esperado |
|---|---|---|---|
| TC-05 | Flujo completo primer ingreso | `laura.sanchez@yopmail.com` / `Usuario1` → nueva clave `NuevaClave2026!` | Dashboard activo, `DebeCambiarPassword=0` en BD |

```powershell
# 1. Reaplicar seeding
sqlcmd -S "(localdb)\MSSQLLocalDB" -d GestionPersonal -i "Documentos\BD\Seeding_Completo.sql"

# 2. Ejecutar TC-05
pytest Tests/test_login.py::test_tc05_flujo_completo -v --headed --slowmo 1000
```

**Verificar en BD tras TC-05:**
```sql
SELECT DebeCambiarPassword FROM Usuarios WHERE CorreoAcceso = 'laura.sanchez@yopmail.com'
-- Esperado: 0
```

---

### Scope 3 — Protección de Rutas y Sesión (TC-06 y TC-07)

| TC | Caso | Resultado esperado |
|---|---|---|
| TC-06 | Ruta protegida sin sesión → navegar a `/Dashboard` sin cookie | Redirige a `/Cuenta/Login` |
| TC-07 | Logout → acceder a `/Dashboard` inmediatamente después | Cookie eliminada, redirige a `/Cuenta/Login` |

```powershell
pytest Tests/test_login.py -k "tc06 or tc07" -v --headed --slowmo 800
```

**Definición de done:** Los 2 casos en verde.

---

### Ejecución de Toda la Suite de Login

```powershell
# Suite completa — TC-01 a TC-07
pytest Tests/test_login.py -v --headed --slowmo 800

# Con output detallado en consola
pytest Tests/test_login.py -v --headed --slowmo 800 -s
```

---

## 6. Comandos de Depuración

```powershell
# Test individual por nombre
pytest Tests/test_login.py::test_tc01_login_credenciales_correctas -v --headed --slowmo 1000

# Test individual por keyword
pytest Tests/test_login.py -v --headed -k "tc02"

# Inspector en un test específico que falla
$env:PWDEBUG=1 ; pytest Tests/test_login.py::test_tc02_password_incorrecta -v --headed

# Con output detallado de consola (print() visibles)
pytest Tests/test_login.py -v --headed -s --slowmo 500
```

---

## 7. Flujo de Sesión Recomendado

```
1. Terminal A → levantar la aplicación: dotnet run --launch-profile http
2. Terminal B → activar el entorno virtual: .venv\Scripts\Activate.ps1
3. Terminal B → ejecutar seeding: sqlcmd -S "(localdb)\MSSQLLocalDB" -d GestionPersonal -i "Documentos\BD\Seeding_Completo.sql"
4. Terminal B → correr suite completa: pytest Tests/test_login.py -v --headed --slowmo 800
   ↳ Si TC-05 necesita re-ejecutarse: reaplicar seeding primero
```

---

## 8. Solución de Problemas Frecuentes

| Problema | Causa probable | Solución |
|---|---|---|
| `ERR_CONNECTION_REFUSED` en `http://localhost:5002` | La app no está corriendo | Levantar la app en Terminal A (`dotnet run`) |
| TC-05 falla en segunda ejecución | `DebeCambiarPassword` ya está en `0` | Reaplicar `Documentos/BD/Seeding_Completo.sql` |
| `reset_estado_db` falla en fixture | `Invoke-Sqlcmd` no disponible | Instalar SQLPS o usar `sqlcmd` directamente |
| Selector `#CorreoAcceso` no encontrado | Vista de Login cambió | Inspeccionar HTML de `/Cuenta/Login` |
| Test pasa headless pero falla headed | Timing con animaciones CSS | Aumentar `--slowmo` o agregar `wait_for_load_state("networkidle")` |
| `playwright: command not found` | Playwright no instalado | `pip install pytest-playwright ; python -m playwright install chromium` |

---

## 9. Estructura del Archivo de Tests

```
Tests/
├── conftest.py        ← Reset BD automático antes de cada sesión (usuarios + tokens)
├── helpers.py         ← hacer_login(), hacer_logout(), hay_error_formulario()
└── test_login.py      ← TC-01 a TC-07
```

| Test | Función | Scope |
|---|---|---|
| TC-01 | `test_tc01_login_credenciales_correctas` | Acceso — Jefe → Dashboard |
| TC-02 | `test_tc02_password_incorrecta` | Acceso — error credenciales |
| TC-03 | `test_tc03_correo_inexistente` | Acceso — correo no registrado |
| TC-04 | `test_tc04_campos_vacios` | Acceso — validación frontend |
| TC-05 | `test_tc05_flujo_completo` | Primer ingreso → CambiarPassword → Dashboard |
| TC-06 | `test_tc06_proteccion_rutas_sin_sesion` | Rutas protegidas sin sesión |
| TC-07 | `test_tc07_logout` | Logout y destrucción de sesión |

---

## 10. Referencia Rápida de Comandos

```powershell
# Suite completa de login
pytest Tests/test_login.py -v --headed --slowmo 800

# Test individual
pytest Tests/test_login.py::test_tc01_login_credenciales_correctas -v --headed --slowmo 1000

# Con inspector (paso a paso)
$env:PWDEBUG=1 ; pytest Tests/test_login.py -v --headed

# Con screenshots al fallar
pytest Tests/test_login.py -v --headed --screenshot only-on-failure --output Tests/screenshots/

# Con traza completa
pytest Tests/test_login.py -v --headed --tracing on --output Tests/traces/

# Abrir traza
python -m playwright show-trace Tests/traces/<archivo>.zip
```
