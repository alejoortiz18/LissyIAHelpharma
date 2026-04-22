# Plan de Ejecución — Pruebas Playwright · Recuperación de Contraseña
## Sistema GestionPersonal — Restablecimiento por Token

> **Stack de pruebas:** Python + pytest-playwright  
> **Modo principal:** Headed (navegador visible) con slowmo para observabilidad  
> **Última actualización:** Abril 2026  
> **Archivo de tests:** `Tests/test_recuperacion.py`  
> **Ver también:** `Documentos/Pruebas/Playwright/Plan-Ejecucion-Playwright-Login.md`

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

> **TC-13 requiere SMTP activo.** Verificar que `appsettings.json` tenga configuración de correo para que el email llegue a yopmail.com.

---

## 3. Preparar Datos de Prueba (Seeding)

```powershell
sqlcmd -S "(localdb)\MSSQLLocalDB" -d GestionPersonal -i "Documentos\BD\Seeding_Completo.sql"
```

> `conftest.py` resetea automáticamente `TK1H6K9M2N` a `Usado=0` y la contraseña de Natalia a `Usuario1` al inicio de cada sesión pytest, garantizando idempotencia para TC-14.

### Tokens en el seeding (fuente de verdad)

| Token | Usuario | Estado | Usado en test |
|---|---|---|---|
| `TK1H6K9M2N` | Natalia Bermúdez | Vigente hasta 2026-04-24 | TC-14 |
| `TK7E4D8F5G` | Andrés Torres | Expirado 2026-04-10 | TC-15a |
| `TK3F9A2B1C` | Laura Sánchez | `Usado=1` | TC-15b |

### Estado de usuarios relevantes

| Usuario | Correo | Contraseña inicial | Rol en esta suite |
|---|---|---|---|
| Carlos Rodríguez | `carlos.rodriguez@yopmail.com` | `Usuario1` | Solicita reseteo (TC-12, TC-13) |
| Natalia Bermúdez | `natalia.bermudez@yopmail.com` | `Usuario1` → `RecuperadaClave2026!` | Usa token válido (TC-14) |

---

## 4. Modos de Ejecución

### 4.1 Modo Headed — Navegador visible

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"

pytest Tests/test_recuperacion.py -v --headed --slowmo 1000
```

> SlowMo de 1000ms recomendado: los flujos de token y email tienen pasos de espera que conviene observar.

### 4.2 Modo sin TC-13 (100% autónomo — sin internet ni SMTP)

```powershell
pytest Tests/test_recuperacion.py -v --headed --slowmo 1000 -k "not tc13"
```

> TC-13 verifica la bandeja de entrada de yopmail.com y requiere conexión a internet + SMTP activo. Los tests TC-12, TC-14, TC-15a y TC-15b son completamente autónomos.

### 4.3 Modo Debug (Playwright Inspector)

```powershell
$env:PWDEBUG=1 ; pytest Tests/test_recuperacion.py -v --headed
```

### 4.4 Captura de Screenshots y Trazas

```powershell
# Screenshot al fallar
pytest Tests/test_recuperacion.py -v --headed --screenshot only-on-failure --output Tests/screenshots/

# Traza completa
pytest Tests/test_recuperacion.py -v --headed --tracing on --output Tests/traces/

# Abrir traza
python -m playwright show-trace Tests/traces/<nombre-del-trace>.zip
```

---

## 5. Casos de Prueba — Scope 4: Recuperación de Contraseña (TC-12 a TC-15b)

> **Requiere conexión a internet** solo para TC-13. Los demás tests son autónomos.

### Tabla de casos

| TC | Caso | Datos | Resultado esperado |
|---|---|---|---|
| TC-12 | Solicitar reseteo de contraseña | `carlos.rodriguez@yopmail.com` | Redirige a `/Cuenta/Login` con mensaje informativo |
| TC-13 | Verificar email recibido en yopmail.com | Bandeja `carlos.rodriguez` | Email con enlace `/Cuenta/RestablecerPassword?token=...` visible en 30s |
| TC-14 | Token válido → establecer nueva contraseña | Token `TK1H6K9M2N`, nueva clave `RecuperadaClave2026!` | Contraseña cambiada, login exitoso con nueva clave |
| TC-15a | Token expirado es rechazado | Token `TK7E4D8F5G` (expiró 2026-04-10) | Error o redirect a `/Cuenta/Login` |
| TC-15b | Token ya usado es rechazado | Token `TK3F9A2B1C` (`Usado=1`) | Error o redirect a `/Cuenta/Login` |

### Ejecución individual por caso

```powershell
# TC-12 — Solicitar reseteo
pytest Tests/test_recuperacion.py::test_tc12_solicitar_reseteo -v --headed --slowmo 1000

# TC-13 — Verificar yopmail (requiere internet + SMTP)
pytest Tests/test_recuperacion.py::test_tc13_verificar_email_yopmail -v --headed --slowmo 1000

# TC-14 — Token válido → nueva contraseña (resetea automáticamente vía conftest)
pytest Tests/test_recuperacion.py::test_tc14_restablecer_con_token_valido -v --headed --slowmo 1000

# TC-15a — Token expirado
pytest Tests/test_recuperacion.py::test_tc15a_token_expirado -v --headed --slowmo 1000

# TC-15b — Token ya usado
pytest Tests/test_recuperacion.py::test_tc15b_token_ya_usado -v --headed --slowmo 1000
```

**Definición de done:** TC-12, TC-14, TC-15a y TC-15b en verde `PASSED`. TC-13 queda sujeto a disponibilidad del servidor SMTP.

---

## 6. Idempotencia de TC-14

TC-14 consume el token `TK1H6K9M2N` (lo marca `Usado=1`) y cambia la contraseña de Natalia Bermúdez. Para que pueda re-ejecutarse, `conftest.py` realiza al inicio de cada sesión:

1. Resetea `TK1H6K9M2N` → `Usado=0`
2. Restaura el hash de contraseña de Natalia al valor original de `Usuario1`

Por esto, **ejecutar siempre la suite completa** en lugar de correr TC-14 aislado en una segunda pasada manual:

```powershell
# Correcto — conftest hace el reset automáticamente
pytest Tests/test_recuperacion.py -v --headed --slowmo 1000

# Cuidado — si se ejecuta solo TC-14 sin que conftest haya corrido en esta sesión,
# el token puede estar ya consumido de una sesión anterior
pytest Tests/test_recuperacion.py::test_tc14_restablecer_con_token_valido -v --headed
```

---

## 7. Flujo de Sesión Recomendado

```
1. Terminal A → levantar la aplicación: dotnet run --launch-profile http
2. Terminal B → activar el entorno virtual: .venv\Scripts\Activate.ps1
3. Terminal B → ejecutar seeding: sqlcmd -S "(localdb)\MSSQLLocalDB" -d GestionPersonal -i "Documentos\BD\Seeding_Completo.sql"
4. Terminal B → correr toda la suite: pytest Tests/test_recuperacion.py -v --headed --slowmo 1000

   Orden de ejecución natural:
   TC-12 (solicitar) → TC-13 (verificar yopmail) → TC-14 (usar token) → TC-15a (expirado) → TC-15b (usado)

5. Si TC-13 falla por SMTP: re-ejecutar sin él → -k "not tc13"
```

> **Nota TC-13:** El test abre una pestaña en `yopmail.com` y espera hasta 30 segundos para que el email aparezca. Si no llega, falla limpiamente sin reintentos. Tener `yopmail.com` a la vista al correrlo.

---

## 8. Comandos de Depuración

```powershell
# Ver qué selector falla en TC-14
$env:PWDEBUG=1 ; pytest Tests/test_recuperacion.py::test_tc14_restablecer_con_token_valido -v --headed

# Suite sin TC-13 (100% autónomo)
pytest Tests/test_recuperacion.py -v --headed --slowmo 1000 -k "not tc13"

# Output detallado de consola (print() visibles)
pytest Tests/test_recuperacion.py -v --headed -s --slowmo 1000
```

---

## 9. Solución de Problemas Frecuentes

| Problema | Causa probable | Solución |
|---|---|---|
| `ERR_CONNECTION_REFUSED` en `http://localhost:5002` | La app no está corriendo | Levantar la app en Terminal A (`dotnet run`) |
| TC-14 falla con "token ya usado" | `TK1H6K9M2N` fue consumido en sesión anterior sin reset | Ejecutar suite completa (conftest resetea al inicio); o reaplicar seeding manualmente |
| TC-13 no encuentra email (timeout 30s) | SMTP no enviando o internet no disponible | Verificar config SMTP en `appsettings.json`; saltar con `-k "not tc13"` |
| TC-15a pasa cuando debería fallar | Token `TK7E4D8F5G` fue re-usado/extendido en BD | Reaplicar `Seeding_Completo.sql` para restaurar estado |
| TC-15b pasa cuando debería fallar | `Usado` de `TK3F9A2B1C` fue reseteado | Reaplicar `Seeding_Completo.sql` |
| `Seeding_Completo.sql` no encontrado | Ruta incorrecta | Usar `Documentos\BD\Seeding_Completo.sql` |
| Test pasa headless pero falla headed | Timing con animaciones CSS | Aumentar `--slowmo` o agregar `wait_for_load_state("networkidle")` |

---

## 10. Estructura del Archivo de Tests

```
Tests/
├── conftest.py           ← Reset BD automático: token TK1H6K9M2N + contraseña Natalia
├── helpers.py            ← hacer_login(), hacer_logout(), hay_error_formulario()
└── test_recuperacion.py  ← TC-12, TC-13, TC-14, TC-15a, TC-15b
```

| Test | Función | Requiere internet |
|---|---|---|
| TC-12 | `test_tc12_solicitar_reseteo` | No |
| TC-13 | `test_tc13_verificar_email_yopmail` | **Sí** |
| TC-14 | `test_tc14_restablecer_con_token_valido` | No |
| TC-15a | `test_tc15a_token_expirado` | No |
| TC-15b | `test_tc15b_token_ya_usado` | No |

---

## 11. Referencia Rápida de Comandos

```powershell
# Suite completa de recuperación (con TC-13)
pytest Tests/test_recuperacion.py -v --headed --slowmo 1000

# Suite autónoma (sin TC-13 — sin internet/SMTP)
pytest Tests/test_recuperacion.py -v --headed --slowmo 1000 -k "not tc13"

# Test individual
pytest Tests/test_recuperacion.py::test_tc14_restablecer_con_token_valido -v --headed --slowmo 1000

# Con inspector (paso a paso)
$env:PWDEBUG=1 ; pytest Tests/test_recuperacion.py::test_tc14_restablecer_con_token_valido -v --headed

# Con screenshots al fallar
pytest Tests/test_recuperacion.py -v --headed --screenshot only-on-failure --output Tests/screenshots/

# Con traza completa
pytest Tests/test_recuperacion.py -v --headed --tracing on --output Tests/traces/

# Abrir traza
python -m playwright show-trace Tests/traces/<archivo>.zip
```
