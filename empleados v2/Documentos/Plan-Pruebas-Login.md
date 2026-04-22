# Pitch — Pruebas del Flujo de Login
## Sistema de Administración de Empleados — GestionPersonal

> **Metodología:** Shape Up (Basecamp)  
> **Stack:** C# ASP.NET Core MVC / .NET 10  
> **Última actualización:** Abril 2026

---

## Problema

El módulo de autenticación es la puerta de entrada a todo el sistema. Sin una suite de pruebas que lo valide, cualquier cambio en `CuentaController`, `CuentaService` o el helper de contraseñas puede romper silenciosamente el acceso de los empleados sin que nadie lo note hasta que alguien intenta entrar en producción.

**El estado actual sin pruebas automatizadas significa:**
- No sabemos si el flujo de cambio de contraseña obligatorio funciona tras cada build.
- No sabemos si las rutas protegidas realmente bloquean usuarios no autenticados.
- Validar manualmente cada escenario antes de un despliegue toma tiempo y es propenso a errores humanos.

---

## Appetite

**Ciclo corto — 2 días de trabajo.**

El objetivo no es la cobertura total del sistema. Es tener una red de seguridad confiable para el flujo de login que se pueda correr en menos de 60 segundos y que detecte regresiones inmediatamente. Cualquier caso fuera de ese alcance queda explícitamente marcado como fuera de este ciclo.

---

## Solución

### Ambiente y herramientas

| Elemento | Valor |
|---|---|
| **Herramienta** | Python + Playwright (pytest-playwright) |
| **Navegador** | Chromium headless |
| **Ambiente** | Desarrollo local — `http://localhost:5002` |
| **BD** | `GestionPersonal` en `(localdb)\MSSQLLocalDB` |
| **Seeding** | `Documentos/Seeding_Completo.sql` |

### Prerequisitos de entorno

**1. Verificar Python**
```powershell
python --version    # Requerido: 3.9 o superior — Actual: 3.14.2 ✅
```

**2. Instalar dependencias (una sola vez)**
```powershell
pip install pytest pytest-playwright
python -m playwright install chromium
```

**3. Levantar la aplicación** (terminal separada, dejarla corriendo)
```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2\Proyecto MVC"
dotnet run --project GestionPersonal.Web/GestionPersonal.Web.csproj --launch-profile http
```
Esperar: `Now listening on: http://localhost:5002`

### Datos de prueba

Todos los datos provienen de `Documentos/Seeding_Completo.sql`. Dominio obligatorio: `@yopmail.com`.

| Rol | Correo | Contraseña | Estado |
|---|---|---|---|
| Jefe | `carlos.rodriguez@yopmail.com` | `Usuario1` | Activo |
| Regente | `laura.sanchez@yopmail.com` | `Usuario1` | Activo |
| Operario inactivo | `valentina.ospina@yopmail.com` | `Usuario1` | Inactivo |
| Correo inexistente | `noexiste@yopmail.com` | — | — |
| Contraseña incorrecta | cualquier usuario válido | `WrongPass123` | — |

> Todos los usuarios del seeding tienen `DebeCambiarPassword = 1` al inicio, excepto Carlos Rodríguez (`DebeCambiarPassword = 0`). El Jefe accede directo al Dashboard; los demás son redirigidos a `/Cuenta/CambiarPassword`.

### Scopes de prueba

El trabajo se divide en 4 scopes independientes. Cada scope puede completarse y verificarse por separado.

---

#### Scope 1 — Acceso (Login válido e inválido)

Cubre todas las variantes del formulario de login: éxito, credenciales erróneas y campos vacíos.

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-01 | Login exitoso — rol Jefe (`DebeCambiarPassword=0`) | `carlos.rodriguez@yopmail.com` / `Usuario1` | Redirige directo a `/Dashboard` |
| TC-02 | Login exitoso — rol Regente (`DebeCambiarPassword=1`) | `laura.sanchez@yopmail.com` / `Usuario1` | Redirige a `/Cuenta/CambiarPassword` |
| TC-03 | Contraseña incorrecta | `carlos.rodriguez@yopmail.com` / `WrongPass123` | Permanece en `/Cuenta/Login`, mensaje `"Datos incorrectos"` |
| TC-04 | Correo inexistente | `noexiste@yopmail.com` / `Usuario1` | Permanece en `/Cuenta/Login`, mensaje `"Datos incorrectos"` |
| TC-05 | Campos vacíos | Click en "Iniciar sesión" sin datos | Errores de validación en ambos campos |

**Selectores HTML:** `#CorreoAcceso`, `#Password`, `button[type=submit]`

**Definición de "done":** Los 5 casos pasan en verde con Chromium headless.

---

#### Scope 2 — Primer Ingreso (CambiarPassword obligatorio)

Cubre el flujo completo desde login hasta el Dashboard cuando el usuario debe cambiar su contraseña.

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-06 | Flujo completo primer ingreso | Login con `laura.sanchez@yopmail.com` / `Usuario1` → ingresar nueva contraseña `NuevaClave2026!` | Redirige a `/Dashboard`, sesión activa, `DebeCambiarPassword=0` en BD |
| TC-07 | Contraseña nueva no cumple reglas | Ingresar nueva contraseña débil (ej. `abc`) | Permanece en `/Cuenta/CambiarPassword`, mensaje de validación |
| TC-08 | Confirmación no coincide | Nueva contraseña y confirmación diferentes | Permanece en `/Cuenta/CambiarPassword`, mensaje de error |

**Definición de "done":** El flujo completo pasa y la BD refleja `DebeCambiarPassword=0`.

> **Nota de re-ejecución:** Tras TC-06, el usuario queda con contraseña `NuevaClave2026!`. Para re-ejecutar, reaplicar `Documentos/Seeding_Completo.sql`.

---

#### Scope 3 — Protección de Rutas y Sesión

Valida que el sistema no permite acceso a rutas privadas sin autenticación, y que el logout limpia correctamente la sesión.

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-09 | Ruta protegida sin sesión | Navegar directo a `http://localhost:5002/Dashboard` sin cookie | Redirige a `/Cuenta/Login` |
| TC-10 | Logout | Navegar a `http://localhost:5002/Cuenta/Logout` con sesión activa | Cookie eliminada, redirige a `/Cuenta/Login` |
| TC-11 | Ruta protegida post-logout | Navegar a `/Dashboard` inmediatamente después del logout | Redirige a `/Cuenta/Login` (no permite re-entrada con sesión anterior) |

**Definición de "done":** Las 3 rutas prueban correctamente el ciclo sesión/sin sesión.

---

#### Scope 4 — ~ Recuperación de Contraseña *(nice-to-have)*

> **Marcado con `~`: Este scope queda fuera del appetite de 2 días.** Se ejecuta solo si los Scopes 1–3 se completan antes del límite y queda tiempo disponible.

Cubre el flujo completo de reset de contraseña usando correos `@yopmail.com` verificables en tiempo real.

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| ~ TC-12 | Solicitar reseteo | Ingresar `carlos.rodriguez@yopmail.com` en `/Cuenta/RecuperarPassword` | Sistema envía email con token a yopmail.com |
| ~ TC-13 | Verificar recepción del email | Abrir https://yopmail.com con usuario `carlos.rodriguez` | Email con enlace de reset visible en bandeja |
| ~ TC-14 | Usar enlace de reset | Hacer click en el enlace y establecer nueva contraseña | `DebeCambiarPassword` actualizado, login exitoso con nueva clave |
| ~ TC-15 | Token expirado/ya usado | Reusar el mismo enlace de reset | Sistema rechaza el token, mensaje de error |

**Definición de "done":** Flujo E2E de reset completo con verificación real en yopmail.com.

---

### Estructura de archivos de prueba

```
empleados v2/
└── Tests/
    ├── conftest.py          ← Playwright config: browser, base_url, fixtures
    ├── helpers.py           ← do_login(), do_logout(), reset_seeding()
    ├── test_acceso.py       ← Scope 1: TC-01 a TC-05
    ├── test_primer_ingreso.py  ← Scope 2: TC-06 a TC-08
    └── test_sesion.py       ← Scope 3: TC-09 a TC-11
```

### Comandos de ejecución

```powershell
# Desde la raíz del proyecto
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"

# Correr todos los scopes
pytest Tests/ -v

# Correr un scope específico
pytest Tests/test_acceso.py -v
pytest Tests/test_primer_ingreso.py -v
pytest Tests/test_sesion.py -v

# Modo headed (útil para depuración)
pytest Tests/ -v --headed

# Screenshots solo al fallar
pytest Tests/ -v --screenshot only-on-failure --output Tests/screenshots/
```

---

## Rabbit Holes

Situaciones que podrían expandir el scope inesperadamente — se resuelven con las decisiones anotadas abajo, no con investigación durante el ciclo.

| Riesgo | Decisión |
|---|---|
| `DebeCambiarPassword` ya en `0` para algún usuario antes de correr TC-06 | Siempre reaplicar `Seeding_Completo.sql` antes del Scope 2. El helper `reset_seeding()` en `helpers.py` lo automatiza. |
| El email de yopmail.com tarda en llegar durante el Scope 4 | Usar `page.wait_for_selector()` con timeout de 30s. Si no llega, el test falla limpiamente — no se retried manualmente. |
| Diferencias entre `http` y `https` en cookies de sesión | Las pruebas usan exclusivamente `http://localhost:5002`. No se prueban escenarios HTTPS en este ciclo. |
| Selectores HTML cambian tras refactor de vistas | Los selectores usan IDs (`#CorreoAcceso`, `#Password`). Si se renombran los campos, actualizar `helpers.py` en un solo lugar. |

---

## No-gos

Lo siguiente queda **explícitamente fuera** de este ciclo:

- ❌ Pruebas de roles distintos a Jefe y Regente (Operario, AuxiliarRegente)
- ❌ Pruebas de login con usuarios de múltiples sedes simultáneas
- ❌ Pruebas de rendimiento o carga sobre el endpoint de login
- ❌ Pruebas en navegadores distintos a Chromium (Firefox, WebKit)
- ❌ Pruebas de HTTPS / certificados SSL
- ❌ Pruebas de la API (solo UI end-to-end)

---

## Hill Chart — Estado del Ciclo

Seguimiento del progreso por scope. Cada scope sube la colina mientras se investiga/define, y baja mientras se ejecuta/verifica.

```
Subiendo ↑          Cima          Bajando ↓
(figuring it out)              (getting it done)

Scope 1 — Acceso            [ ████████████ ] ✅ Done
Scope 2 — Primer Ingreso    [      ██████  ] 🔄 En curso
Scope 3 — Protección Rutas  [    ████      ] ⏳ Pendiente
~ Scope 4 — Recuperación    [              ] 🔕 Nice-to-have
```

---

## Circuit Breaker

Si al final del appetite de 2 días los Scopes 1–3 no están todos en verde:

1. **No se extiende el ciclo.** Se registra qué scope falló y por qué.
2. El scope fallido se convierte en un nuevo pitch acotado para el siguiente ciclo.
3. El código que causa el fallo **no se despliega** hasta que la prueba pase.

