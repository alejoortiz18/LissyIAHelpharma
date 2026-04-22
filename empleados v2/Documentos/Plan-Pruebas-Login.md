# Plan de Pruebas — Flujo de Login
## Sistema de Administración de Empleados — GestiónRH

---

## 1. Resumen del alcance

Las pruebas cubren el flujo completo de autenticación de la aplicación ASP.NET Core MVC:

| Módulo | URL | Descripción |
|---|---|---|
| Login | `http://localhost:5002/Cuenta/Login` | Formulario de inicio de sesión |
| Cambiar Password | `http://localhost:5002/Cuenta/CambiarPassword` | Obligatorio en primer ingreso |
| Dashboard | `http://localhost:5002/Dashboard` | Destino tras login exitoso (rol Jefe) |
| Recuperar Password | `http://localhost:5002/Cuenta/RecuperarPassword` | Flujo de recuperación |

**Herramienta:** Python + Playwright (scripts funcionales automatizados)  
**Ambiente:** Desarrollo local — `http://localhost:5002`  
**BD:** `GestionPersonal` en `(localdb)\MSSQLLocalDB`

---

## 2. Prerequisitos de instalación

### 2.1 Verificar Python

```powershell
python --version    # Requerido: 3.9 o superior — Actual: 3.14.2 ✅
```

### 2.2 Instalar dependencias de testing

Ejecutar en orden desde cualquier directorio:

```powershell
# Instalar Playwright y pytest-playwright
pip install pytest pytest-playwright

# Instalar los navegadores de Playwright (solo la primera vez)
python -m playwright install chromium
```

> **Tiempo estimado:** 2-5 minutos (descarga ~150 MB para Chromium).

### 2.3 Levantar la aplicación antes de correr las pruebas

En una terminal separada (dejarla corriendo):

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2\Proyecto MVC"
dotnet run --project GestionPersonal.Web/GestionPersonal.Web.csproj --launch-profile http
```

Esperar hasta ver: `Now listening on: http://localhost:5002`

---

## 3. Datos de prueba

| Campo | Valor |
|---|---|
| **Usuario válido (Jefe)** | `carlos.rodriguez@helpharma.com` |
| **Contraseña válida** | `Admin2026` |
| **Usuario válido (Regente)** | `laura.sanchez@helpharma.com` |
| **Contraseña válida** | `Admin2026` |
| **Usuario inactivo** | _(ninguno en seed — todos en Estado=Activo)_ |
| **Correo inexistente** | `noexiste@helpharma.com` |
| **Contraseña incorrecta** | `WrongPass123` |

> Todos los usuarios tienen `DebeCambiarPassword = 1`, por lo que tras el primer login exitoso el sistema **redirige a `/Cuenta/CambiarPassword`** antes de llegar al Dashboard.

---

## 4. Casos de prueba

### TC-01 — Login con credenciales correctas (rol Jefe)

| | |
|---|---|
| **Precondición** | App corriendo, BD con seeding aplicado |
| **Acción** | Ingresar `carlos.rodriguez@helpharma.com` / `Admin2026` y hacer click en "Iniciar sesión" |
| **Resultado esperado** | Redirige a `/Cuenta/CambiarPassword` (por `DebeCambiarPassword=true`) |
| **Selectores HTML** | `#CorreoAcceso`, `#Password`, `button[type=submit]` |

---

### TC-02 — Login con contraseña incorrecta

| | |
|---|---|
| **Precondición** | App corriendo |
| **Acción** | Ingresar `carlos.rodriguez@helpharma.com` / `WrongPass123` |
| **Resultado esperado** | Permanece en `/Cuenta/Login`, aparece mensaje de error en el formulario |
| **Mensaje esperado** | `"Datos incorrectos"` |

---

### TC-03 — Login con correo inexistente

| | |
|---|---|
| **Precondición** | App corriendo |
| **Acción** | Ingresar `noexiste@helpharma.com` / `Admin2026` |
| **Resultado esperado** | Permanece en `/Cuenta/Login`, aparece mensaje de error |
| **Mensaje esperado** | `"Datos incorrectos"` |

---

### TC-04 — Login con campos vacíos (validación cliente/servidor)

| | |
|---|---|
| **Precondición** | App corriendo |
| **Acción** | Hacer click en "Iniciar sesión" sin ingresar datos |
| **Resultado esperado** | Permanece en `/Cuenta/Login`, muestra errores de validación en ambos campos |

---

### TC-05 — Flujo completo: Login → CambiarPassword → Dashboard

| | |
|---|---|
| **Precondición** | App corriendo, usuario con `DebeCambiarPassword=true` |
| **Acción 1** | Login con `carlos.rodriguez@helpharma.com` / `Admin2026` |
| **Resultado 1** | Redirige a `/Cuenta/CambiarPassword` |
| **Acción 2** | Ingresar contraseña actual `Admin2026`, nueva contraseña `NuevaClave2026!`, confirmar |
| **Resultado 2** | Redirige a `/Dashboard` con sesión activa y mensaje de éxito |

---

### TC-06 — Protección de rutas autenticadas sin sesión

| | |
|---|---|
| **Precondición** | Sin cookie de sesión activa |
| **Acción** | Navegar directamente a `http://localhost:5002/Dashboard` |
| **Resultado esperado** | Redirige a `/Cuenta/Login` |

---

### TC-07 — Logout

| | |
|---|---|
| **Precondición** | Sesión activa |
| **Acción** | Navegar a `http://localhost:5002/Cuenta/Logout` |
| **Resultado esperado** | Cookie eliminada, redirige a `/Cuenta/Login` |
| **Verificación extra** | Navegar a `/Dashboard` después del logout → redirige a Login |

---

## 5. Estructura de archivos de prueba

```
empleados v2/
└── Tests/
    ├── conftest.py          ← Configuración de Playwright (browser, base_url)
    ├── test_login.py        ← TC-01 a TC-07
    └── helpers.py           ← Funciones reutilizables (login, logout)
```

---

## 6. Comandos para ejecutar las pruebas

```powershell
# Desde la carpeta empleados v2/
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"

# Correr todas las pruebas con salida detallada
pytest Tests/ -v

# Correr con navegador visible (útil para depuración)
pytest Tests/ -v --headed

# Correr solo un caso específico
pytest Tests/test_login.py::test_login_credenciales_correctas -v

# Guardar screenshots automáticos al fallar
pytest Tests/ -v --screenshot only-on-failure --output Tests/screenshots/
```

---

## 7. Criterios de aprobación

| Criterio | Umbral |
|---|---|
| TC-01 Login exitoso y redirección | ✅ Obligatorio |
| TC-02 Error con contraseña incorrecta | ✅ Obligatorio |
| TC-03 Error con correo inexistente | ✅ Obligatorio |
| TC-04 Validaciones de campos vacíos | ✅ Obligatorio |
| TC-05 Flujo completo hasta Dashboard | ✅ Obligatorio |
| TC-06 Protección de rutas | ✅ Obligatorio |
| TC-07 Logout | ✅ Obligatorio |

**Todos los casos son obligatorios.** Si alguno falla, se corrige el código antes de continuar con las pruebas de otros módulos.

---

## 8. Notas adicionales

- Las pruebas usan `http` (no HTTPS) para evitar errores de certificado en local.
- Playwright usa **Chromium headless** por defecto (más rápido, sin ventana).
- Si `DebeCambiarPassword` ya fue cambiado a `false` en algún usuario, el TC-01 redirigirá directamente a `/Dashboard` en vez de `/Cuenta/CambiarPassword` — esto es comportamiento correcto.
- En TC-05, tras cambiar la contraseña la nueva contraseña queda en BD. Para re-ejecutar la prueba, correr nuevamente el script `Migracion_PasswordVarbinary256.sql` para restablecer `Admin2026`.
