# Plan — Restablecimiento de Contraseña: Validación de Email y Código
**Sistema:** GestiónRH — Administración de Empleados  
**Fecha base:** 2026-04-24  
**Archivo de pruebas:** `Tests/test_restablecer_password_email_codigo.py`  
**Ejecutar con:** `pytest Tests/test_restablecer_password_email_codigo.py -v --headed --slowmo 800 -s`

---

## Objetivo

Validar de extremo a extremo el flujo de restablecimiento de contraseña, cubriendo:

1. **Inicio automático** de la aplicación ASP.NET Core al comienzo de la suite.
2. **Solicitud de recuperación** desde el formulario `/Cuenta/RecuperarPassword`.
3. **Verificación real del correo** en la bandeja de `yopmail.com` (iframe `#ifinbox` / `#ifmail`).
4. **Extracción del código** enviado en el email (12 caracteres alfanuméricos, código plano — NO el hash SHA-256).
5. **Uso del código** en `/Cuenta/RestablecerPassword?token=CÓDIGO` para establecer la nueva contraseña.
6. **Verificación de login** con la nueva credencial y denegación con la antigua.
7. **Detención automática** de la aplicación al terminar todas las pruebas.

---

## Alcance

| Incluido | Excluido |
|---|---|
| Flujo happy path completo E2E | Pruebas de carga / stress |
| Validación del email en yopmail (iframes) | Pruebas de compatibilidad multinavegador |
| Verificación del código extraído | Pruebas con tokens de seeding fijos |
| Confirmación en BD (TokensRecuperacion) | Flujos paralelos con múltiples usuarios |
| Login exitoso con nueva contraseña | Restablecimiento desde enlace directo (sin email) |
| Login rechazado con contraseña antigua | Casos negativos exhaustivos (ver plan-ejecucion-restablecercontraseña.md) |
| Inicio y detención automática de la app | Pruebas de UI de otros módulos |

---

## Flujo completo del proceso

```
┌──────────────────────────────────────────────────────────────┐
│  FIXTURE: gestionar_aplicacion (scope=module)                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  INICIO: dotnet run (GestionPersonal.Web)               │ │
│  │          Esperar hasta que http://localhost:5002         │ │
│  │          responda → máx. 90 segundos                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-01  Aplicación responde en /Cuenta/Login              │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-02  Formulario de solicitud carga correctamente       │
│            GET /Cuenta/RecuperarPassword                     │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-03  Ingresar correo y enviar                          │
│            Correo: carlos.rodriguez@yopmail.com              │
│            [Enviar instrucciones]                            │
└──────────────────────────────────────────────────────────────┘
           │ Sistema genera token plano (12 chars), almacena
           │ SHA-256(token) en BD y envía email SMTP
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-04  Verificar redirección a /Cuenta/Login             │
│            con mensaje informativo (no revela si el          │
│            correo existe — anti-enumeración)                 │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-05  Navegar a yopmail                                 │
│            https://yopmail.com/en/?login=carlos.rodriguez    │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-06  Email llegó a la bandeja                          │
│            iframe: #ifinbox → localizar email de            │
│            recuperación (timeout 30s)                        │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-07  Abrir email y extraer el código                   │
│            iframe: #ifmail → enlace ?token=XXXXXXXX         │
│            Guardar código en _E["token_codigo"]              │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-08  Verificar código: alfanumérico, 12 chars          │
│            NO es hash SHA-256 (≠ 64 chars hex)              │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-09  Email menciona vigencia de 30 minutos             │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-10  Navegar al formulario de restablecimiento         │
│            GET /Cuenta/RestablecerPassword?token=<CÓDIGO>   │
│            Verificar que los campos NuevoPassword y          │
│            ConfirmarPassword son visibles                    │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-11  Completar el restablecimiento                     │
│            NuevoPassword:    NuevoRp2026!                    │
│            ConfirmarPassword: NuevoRp2026!                   │
│            [Restablecer contraseña]                          │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-12  Verificar redirección a Login con mensaje éxito   │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-13  Verificar en BD: TokensRecuperacion.Usado = 1     │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  TC-RP-14  Login con nueva contraseña → éxito (Dashboard)    │
│  TC-RP-14  Login con contraseña antigua → rechazado          │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│  FIXTURE TEARDOWN: gestionar_aplicacion                      │
│  proc.terminate() → proc.wait(15s) → proc.kill() si timeout │
└──────────────────────────────────────────────────────────────┘
```

---

## Contexto técnico

| Elemento | Valor |
|---|---|
| URL base | `http://localhost:5002` |
| Proyecto .NET | `Proyecto MVC/GestionPersonal.Web` |
| Comando de inicio | `dotnet run` (cwd = directorio del proyecto) |
| Timeout de inicio | 90 segundos |
| Formulario de solicitud | `GET /Cuenta/RecuperarPassword` |
| Formulario de restablecimiento | `GET /Cuenta/RestablecerPassword?token=<CÓDIGO_PLANO>` |
| Correo de prueba | `carlos.rodriguez@yopmail.com` |
| Bandeja yopmail | `https://yopmail.com/en/?login=carlos.rodriguez` |
| iframe de la bandeja | `#ifinbox` |
| iframe del cuerpo del email | `#ifmail` |
| DB local | `(localdb)\MSSQLLocalDB` · `GestionPersonal` |
| Tabla de tokens | `dbo.TokensRecuperacion` |
| Tabla de auditoría | `dbo.RegistroNotificaciones` |
| Nueva contraseña de prueba | `NuevoRp2026!` |

### Cómo funciona el token (implementación en `CuentaService`)

```
1. Usuario envía correo → GenerarCodigoSeguro() → código plano de 12 chars alfanuméricos
2. BD almacena: SHA-256(código_plano) → 64 chars hexadecimal lowercase
3. Email recibe: el código PLANO (12 chars) — en el parámetro ?token= del enlace
4. Al restablecer: servidor hace SHA-256(parámetro) y compara con BD
5. Si coincide y no expiró y Usado=0 → procede; luego marca Usado=1
```

> **Implicación para pruebas:** El valor `?token=XXXX` en el enlace del email es siempre de 12 caracteres.  
> Si aparece un string de 64 caracteres hexadecimales → **fallo crítico de seguridad** (se estaría exponiendo el hash).

---

## Precondiciones

### Estado de BD requerido antes de la ejecución

El fixture `_resetear_bd_modulo` (scope=module, autouse=True) restaura automáticamente el estado antes de las pruebas:

```sql
-- Restaurar contraseña de carlos.rodriguez a "Usuario1"
UPDATE dbo.Usuarios
SET PasswordHash = 0x7DED37B4612147C18EBDFA1F6DEB4709EC9D511DA20641214F1F97612DF2CEAE,
    PasswordSalt = 0xF2B483C7DAC61EC2CA7F1331C95D6800,
    DebeCambiarPassword = 0
WHERE CorreoAcceso = 'carlos.rodriguez@yopmail.com';

-- Limpiar tokens frescos anteriores (NO los del seeding: TK7E4D8F5G, TK3F9A2B1C, TK1H6K9M2N)
DELETE FROM dbo.TokensRecuperacion
WHERE UsuarioId = (SELECT Id FROM dbo.Usuarios WHERE CorreoAcceso = 'carlos.rodriguez@yopmail.com')
  AND Token NOT IN (
      '0e1c89b3abb6ba93d5e8c7f12dc6eb4b6e2b1a5c3d4e7f8a9b0c1d2e3f4a5b6c',
      'faketoken1', 'faketoken2'
  );
```

### SMTP

El servidor debe tener configurado el envío de correos vía Microsoft 365 / SMTP.  
Verificar con `dotnet user-secrets list` en `GestionPersonal.Web`:

```
Email:SmtpHost      = smtp.office365.com
Email:SmtpPort      = 587
Email:RemitenteMail = notificacion.sf@zentria.com.co
```

---

## Ciclo de vida de la suite — Inicio y Detención de la Aplicación

El fixture `gestionar_aplicacion` (scope=module, autouse=True) gestiona el ciclo de vida de la aplicación:

### Inicio (Setup)

```
1. Intenta conectar a http://localhost:5002/Cuenta/Login (timeout 3s)
   ├── Si responde → la app ya está activa, no se inicia una nueva.
   │   Al terminar: NO se detiene (la app seguirá corriendo).
   └── Si no responde → se inicia con dotnet run en el directorio del proyecto
       Esperar hasta 90 segundos a que /Cuenta/Login responda.
       Si el proceso muere antes → pytest.fail() con la salida del proceso.
       Si agota los 90s sin responder → proc.terminate() + pytest.fail().
```

### Detención (Teardown)

```
Si la aplicación fue iniciada por el fixture:
   proc.terminate()  → señal SIGTERM / TerminateProcess
   proc.wait(15s)    → esperar cierre ordenado
   proc.kill()       → forzar si no cerró en 15 segundos
```

---

## Casos de prueba

### Resumen

| ID | Descripción | Grupo | Requiere SMTP | Requiere yopmail |
|---|---|---|---|---|
| TC-RP-01 | Aplicación responde en `/Cuenta/Login` | App | No | No |
| TC-RP-02 | Formulario de solicitud carga correctamente | Solicitud | No | No |
| TC-RP-03 | Enviar solicitud con correo válido | Solicitud | **Sí** | No |
| TC-RP-04 | Verificar redirección a Login con mensaje | Solicitud | No | No |
| TC-RP-05 | Navegar a bandeja de yopmail | Email | No | **Sí** |
| TC-RP-06 | Email de recuperación llegó a la bandeja | Email | **Sí** | **Sí** |
| TC-RP-07 | Abrir email y extraer código del enlace | Email | **Sí** | **Sí** |
| TC-RP-08 | Código es alfanumérico de 12 chars (no hash) | Email | **Sí** | **Sí** |
| TC-RP-09 | Email menciona vigencia de 30 minutos | Email | **Sí** | **Sí** |
| TC-RP-10 | Formulario con código del email es visible | Restablecimiento | **Sí** | **Sí** |
| TC-RP-11 | Completar restablecimiento con nueva contraseña | Restablecimiento | **Sí** | **Sí** |
| TC-RP-12 | Redirección a Login con mensaje de éxito | Restablecimiento | No | No |
| TC-RP-13 | Token marcado Usado=1 en BD | BD | No | No |
| TC-RP-14 | Login con nueva contraseña exitoso / antigua denegada | Login | No | No |

---

### TC-RP-01 · Aplicación responde en `/Cuenta/Login`

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-01 |
| **Objetivo** | Confirmar que la aplicación arrancó correctamente y el endpoint principal está disponible |
| **Precondición** | Fixture `gestionar_aplicacion` completado |
| **Pasos** | 1. Navegar a `http://localhost:5002/Cuenta/Login` · 2. Esperar `networkidle` |
| **Resultado esperado** | Status 200 · Página de login visible · URL contiene `/Cuenta/Login` |
| **Resultado NO esperado** | Error de conexión · Página en blanco · Redirección a error 500 |
| **Función de prueba** | `test_rp01_aplicacion_responde` |

---

### TC-RP-02 · Formulario de solicitud carga correctamente

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-02 |
| **Objetivo** | Verificar que `/Cuenta/RecuperarPassword` muestra el campo de correo y el botón de envío |
| **Precondición** | TC-RP-01 exitoso |
| **Pasos** | 1. Navegar a `http://localhost:5002/Cuenta/RecuperarPassword` · 2. Esperar `networkidle` |
| **Resultado esperado** | Campo `#CorreoAcceso` visible · botón `button[type=submit]` visible |
| **Resultado NO esperado** | Redirección a otra página · Campo de correo ausente |
| **Función de prueba** | `test_rp02_formulario_solicitud_carga` |

---

### TC-RP-03 · Enviar solicitud con correo válido

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-03 |
| **Objetivo** | Enviar el formulario con un correo registrado y verificar que el sistema procesa la solicitud |
| **Precondición** | `carlos.rodriguez@yopmail.com` activo en BD · SMTP configurado |
| **Pasos** | 1. Navegar a `/Cuenta/RecuperarPassword` · 2. Escribir `carlos.rodriguez@yopmail.com` en `#CorreoAcceso` · 3. Clic en `button[type=submit]` |
| **Resultado esperado** | Redirige a `/Cuenta/Login` · Sistema genera token en BD y envía email |
| **Efecto lateral** | Fila nueva en `dbo.TokensRecuperacion` con `Usado=0` y `FechaExpiracion ≈ GETUTCDATE() + 30 min` |
| **Función de prueba** | `test_rp03_enviar_solicitud_correo_valido` |

---

### TC-RP-04 · Verificar redirección a Login con mensaje informativo

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-04 |
| **Objetivo** | Confirmar que tras el envío el sistema redirige a Login con un mensaje genérico (no revela si el correo existe) |
| **Precondición** | TC-RP-03 ejecutado |
| **Pasos** | Revisar URL y buscar elemento `.alert--info, .alert-info, [class*='alert']` |
| **Resultado esperado** | URL contiene `/Cuenta/Login` · Mensaje informativo visible y no vacío |
| **Resultado NO esperado** | Mensaje "Correo no registrado" · Mensaje "Usuario no encontrado" · Sin redirección |
| **Función de prueba** | `test_rp04_redireccion_login_con_mensaje` |

---

### TC-RP-05 · Navegar a bandeja de yopmail

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-05 |
| **Objetivo** | Confirmar que la página de yopmail carga y el iframe `#ifinbox` está disponible |
| **URL** | `https://yopmail.com/en/?login=carlos.rodriguez` |
| **Pasos** | 1. Navegar a la URL · 2. Esperar `networkidle` · 3. Verificar existencia de `#ifinbox` |
| **Resultado esperado** | Página carga · iframe `#ifinbox` presente en el DOM |
| **Nota** | Si yopmail no carga por red corporativa → verificar proxy o usar VPN |
| **Función de prueba** | `test_rp05_navegar_bandeja_yopmail` |

---

### TC-RP-06 · Email de recuperación llegó a la bandeja

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-06 |
| **Objetivo** | Verificar que el email enviado en TC-RP-03 aparece en la bandeja dentro del timeout permitido |
| **Precondición** | TC-RP-03 ejecutado con SMTP activo |
| **Pasos** | 1. Dentro del iframe `#ifinbox` buscar enlace con texto que contenga `contrase`, `recuper`, `GestiónRH`, `password` o `reset` (regex, case-insensitive) · 2. `wait_for(timeout=30_000)` |
| **Resultado esperado** | Email aparece en el inbox en menos de 30 segundos |
| **Resultado NO esperado** | Timeout · No se encuentra ningún email con esos términos |
| **Si falla** | Verificar SMTP en user-secrets · Revisar manualmente `https://yopmail.com/en/?login=carlos.rodriguez` |
| **Función de prueba** | `test_rp06_email_llego_a_bandeja` |

---

### TC-RP-07 · Abrir email y extraer el código del enlace

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-07 |
| **Objetivo** | Abrir el email en el iframe `#ifmail` y extraer el parámetro `token=` del enlace de restablecimiento |
| **Precondición** | TC-RP-06 exitoso |
| **Pasos** | 1. Clic en el email (iframe `#ifinbox`) · 2. Esperar 1500ms · 3. En iframe `#ifmail` localizar `a[href*='RestablecerPassword'], a[href*='token=']` · 4. Extraer `href` · 5. Extraer valor de `?token=` con regex |
| **Resultado esperado** | `href` contiene `RestablecerPassword` o `token=` · Regex extrae el código · Se almacena en `_E["token_codigo"]` y `_E["token_url"]` |
| **Función de prueba** | `test_rp07_abrir_email_extraer_codigo` |

---

### TC-RP-08 · Código es alfanumérico de 12 caracteres (no es hash SHA-256)

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-08 |
| **Objetivo** | Verificar que el código extraído es el código plano (12 chars) y NO el hash SHA-256 (64 chars hex) |
| **Precondición** | TC-RP-07 exitoso — `_E["token_codigo"]` disponible |
| **Pasos** | 1. Obtener `_E["token_codigo"]` · 2. Verificar `len == 12` · 3. Verificar `re.match(r'^[a-zA-Z0-9]+$', token)` · 4. Verificar que NO es 64 chars hexadecimales |
| **Resultado esperado** | `len(token) == 12` · Solo caracteres alfanuméricos |
| **Resultado NO esperado** | `len == 64` con solo hexadecimales → **fallo crítico de seguridad** (hash expuesto) |
| **Función de prueba** | `test_rp08_codigo_es_alfanumerico_12_chars` |

---

### TC-RP-09 · Email menciona vigencia de 30 minutos

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-09 |
| **Objetivo** | Verificar que el cuerpo del email informa al usuario que el código tiene una vigencia de 30 minutos |
| **Precondición** | TC-RP-07 exitoso · Bandeja de yopmail abierta |
| **Pasos** | 1. Leer `body.inner_text()` del iframe `#ifmail` · 2. Buscar `re.search(r'30\s*(minutos?|min)', cuerpo, re.IGNORECASE)` |
| **Resultado esperado** | Texto del email contiene "30 minutos" o "30 min" |
| **Si falla** | Revisar `SeguridadEmailTemplate.RecuperacionContrasena()` y el parámetro `vigenciaMinutos` |
| **Función de prueba** | `test_rp09_email_menciona_vigencia_30_minutos` |

---

### TC-RP-10 · Formulario con código del email es visible

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-10 |
| **Objetivo** | Confirmar que el código extraído del email es un token válido que carga el formulario de restablecimiento |
| **Precondición** | `_E["token_url"]` disponible (URL extraída del email) |
| **Pasos** | 1. Navegar a `_E["token_url"]` · 2. Esperar `networkidle` · 3. Verificar que `#NuevoPassword` y `#ConfirmarPassword` son visibles |
| **Resultado esperado** | Formulario con ambos campos visible · URL contiene `RestablecerPassword` |
| **Resultado NO esperado** | Redirección a Login (token rechazado) · Campos no visibles |
| **Función de prueba** | `test_rp10_formulario_restablecimiento_visible` |

---

### TC-RP-11 · Completar restablecimiento con nueva contraseña

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-11 |
| **Objetivo** | Usar el código del email para establecer una nueva contraseña exitosamente |
| **Precondición** | TC-RP-10 exitoso · Formulario visible |
| **Pasos** | 1. Navegar a `_E["token_url"]` · 2. Llenar `#NuevoPassword` con `NuevoRp2026!` · 3. Llenar `#ConfirmarPassword` con `NuevoRp2026!` · 4. Clic en `button[type=submit]` · 5. Esperar `networkidle` |
| **Resultado esperado** | Sistema procesa el restablecimiento · Redirige a `/Cuenta/Login` |
| **Efecto lateral** | `dbo.TokensRecuperacion.Usado = 1` · Contraseña de `carlos.rodriguez` cambiada |
| **Función de prueba** | `test_rp11_completar_restablecimiento` |

---

### TC-RP-12 · Redirección a Login con mensaje de éxito

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-12 |
| **Objetivo** | Verificar el mensaje de confirmación mostrado al usuario tras el restablecimiento exitoso |
| **Precondición** | TC-RP-11 ejecutado · Página actual es Login |
| **Pasos** | 1. Verificar URL contiene `/Cuenta/Login` · 2. Buscar `.alert--success, .alert-success, [class*='alert']` · 3. Verificar que el texto del mensaje no está vacío |
| **Resultado esperado** | URL = `/Cuenta/Login` · Mensaje de éxito visible |
| **Función de prueba** | `test_rp12_mensaje_exito_en_login` |

---

### TC-RP-13 · Token marcado Usado=1 en BD

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-13 |
| **Objetivo** | Verificar que el token utilizado queda marcado como consumido en la BD, impidiendo reutilización |
| **Precondición** | TC-RP-11 exitoso · `_E["token_codigo"]` disponible |
| **Pasos** | 1. Ejecutar `Invoke-Sqlcmd` para obtener el registro del token · 2. Verificar `Usado = 1` |
| **Query** | `SELECT TOP 1 Usado FROM dbo.TokensRecuperacion t JOIN dbo.Usuarios u ON u.Id=t.UsuarioId WHERE u.CorreoAcceso='carlos.rodriguez@yopmail.com' ORDER BY t.FechaCreacion DESC;` |
| **Resultado esperado** | `Usado = 1` |
| **Resultado NO esperado** | `Usado = 0` → **fallo de seguridad** (token reutilizable) |
| **Función de prueba** | `test_rp13_token_marcado_usado_en_bd` |

---

### TC-RP-14 · Login con nueva contraseña exitoso / antigua denegada

| Campo | Detalle |
|---|---|
| **ID** | TC-RP-14 |
| **Objetivo** | Confirmar que la nueva contraseña funciona para autenticarse y que la antigua queda inválida |
| **Precondición** | TC-RP-11 exitoso |
| **Pasos (nueva)** | 1. Navegar a `/Cuenta/Login` · 2. Ingresar `carlos.rodriguez@yopmail.com` + `NuevoRp2026!` · 3. Submit · 4. Verificar NO permanece en Login |
| **Resultado esperado (nueva)** | Redirección al Dashboard · URL ≠ `/Cuenta/Login` |
| **Pasos (antigua)** | 1. Logout · 2. Navegar a `/Cuenta/Login` · 3. Ingresar `carlos.rodriguez@yopmail.com` + `Usuario1` · 4. Submit |
| **Resultado esperado (antigua)** | Permanece en `/Cuenta/Login` · Mensaje de error de autenticación |
| **Función de prueba** | `test_rp14_login_nueva_y_antigua_contrasena` |

---

## Código de la prueba

El código completo de todos los casos anteriores está implementado en:

```
Tests/test_restablecer_password_email_codigo.py
```

### Estructura del archivo

```python
# ─── Imports ────────────────────────────────────────────────────
# pathlib, subprocess, time, urllib.request, re, json, os, tempfile
# pytest, helpers

# ─── Estado compartido entre tests ──────────────────────────────
_E: dict = {
    "solicitud_enviada": False,
    "token_codigo":      None,   # 12 chars alfanuméricos extraídos del email
    "token_url":         None,   # URL completa del enlace (incluye ?token=...)
    "reset_exitoso":     False,
    "password_nueva":    "NuevoRp2026!",
}

# ─── Fixture: Inicio/Stop de la aplicación (scope=module) ───────
@pytest.fixture(scope="module", autouse=True)
def gestionar_aplicacion(): ...

# ─── Fixture: Reset de BD (scope=module) ────────────────────────
@pytest.fixture(scope="module", autouse=True)
def _resetear_bd_modulo(): ...

# ─── Helper: Consultar BD via Invoke-Sqlcmd ──────────────────────
def _consultar(query: str) -> list[dict]: ...
def _ejecutar(sql: str) -> None: ...

# ─── Tests (orden secuencial A → Z) ─────────────────────────────
def test_rp01_aplicacion_responde(page): ...
def test_rp02_formulario_solicitud_carga(page): ...
def test_rp03_enviar_solicitud_correo_valido(page): ...
def test_rp04_redireccion_login_con_mensaje(page): ...
def test_rp05_navegar_bandeja_yopmail(page): ...
def test_rp06_email_llego_a_bandeja(page): ...
def test_rp07_abrir_email_extraer_codigo(page): ...
def test_rp08_codigo_es_alfanumerico_12_chars(page): ...
def test_rp09_email_menciona_vigencia_30_minutos(page): ...
def test_rp10_formulario_restablecimiento_visible(page): ...
def test_rp11_completar_restablecimiento(page): ...
def test_rp12_mensaje_exito_en_login(page): ...
def test_rp13_token_marcado_usado_en_bd(page): ...
def test_rp14_login_nueva_y_antigua_contrasena(page): ...
```

---

## Comandos de ejecución

### Suite completa (inicio y detención automática de la app)

```powershell
# Activar entorno virtual
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1

# Ejecutar con salida en tiempo real y modo headed (slowmo 800ms)
$env:PYTHONIOENCODING = 'utf-8'
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\rp-email-codigo-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null

pytest Tests/test_restablecer_password_email_codigo.py -v --headed --slowmo 800 -s 2>&1 |
    Tee-Object -FilePath $informe

Write-Host "`nInforme guardado en: $informe"
```

### Solo los tests que no requieren yopmail

```powershell
pytest Tests/test_restablecer_password_email_codigo.py -v --headed -m "not yopmail"
```

### Un test específico

```powershell
pytest Tests/test_restablecer_password_email_codigo.py::test_rp07_abrir_email_extraer_codigo -v --headed -s
```

### Con slowmo mayor para inspección visual

```powershell
pytest Tests/test_restablecer_password_email_codigo.py -v --headed --slowmo 1500 -s
```

---

## Criterios de aceptación

| # | Criterio | Obligatorio |
|---|---|---|
| 1 | La aplicación inicia sin errores en menos de 90 segundos | ✅ Bloqueante |
| 2 | El formulario de solicitud muestra el campo de correo | ✅ Bloqueante |
| 3 | El sistema redirige a Login tras la solicitud (sin revelar si el correo existe) | ✅ Bloqueante |
| 4 | El email llega a yopmail en menos de 30 segundos | ✅ Bloqueante |
| 5 | El código en el email tiene exactamente 12 caracteres alfanuméricos | ✅ Bloqueante |
| 6 | El código NO es el hash SHA-256 (≠ 64 chars hex) | ✅ Bloqueante (seguridad) |
| 7 | El email menciona vigencia de 30 minutos | ⚠️ Importante |
| 8 | El formulario de restablecimiento carga con el código del email | ✅ Bloqueante |
| 9 | El restablecimiento con contraseña válida redirige a Login con éxito | ✅ Bloqueante |
| 10 | El token queda Usado=1 en BD tras el restablecimiento | ✅ Bloqueante (seguridad) |
| 11 | Login con nueva contraseña es exitoso | ✅ Bloqueante |
| 12 | Login con contraseña antigua es rechazado | ✅ Bloqueante (seguridad) |
| 13 | La aplicación se detiene correctamente al finalizar la suite | ✅ Bloqueante |

---

## Notas adicionales

### yopmail y iframes

yopmail carga la interfaz en iframes anidados:
- `#ifinbox` → lista de emails recibidos (clic para abrir)
- `#ifmail`  → cuerpo del email seleccionado

Playwright accede a ellos con `page.frame_locator("#ifinbox")` y `page.frame_locator("#ifmail")`.

### Si el email no llega en 30 segundos

1. Verificar SMTP: `dotnet user-secrets list` en `GestionPersonal.Web`
2. Revisar permisos "Send As" en Exchange Admin para `notificacion.sf@zentria.com.co`
3. Verificar manualmente: `https://yopmail.com/en/?login=carlos.rodriguez`
4. Ejecutar sin el grupo Email: `pytest ... -m "not yopmail"`

### Re-ejecución sin reseteo manual

El fixture `_resetear_bd_modulo` restaura automáticamente:
- Contraseña de `carlos.rodriguez@yopmail.com` a `Usuario1`
- Elimina tokens frescos (conserva los del seeding)

Esto garantiza que la suite puede ejecutarse múltiples veces sin intervención manual.

### Relación con otros planes de prueba

| Plan | Cobertura adicional |
|---|---|
| `plan-ejecucion-restablecercontraseña.md` | 32 casos (casos negativos, seguridad, XSS, SQLi, borde) |
| `Plan-Ejecucion-Pruebas.md` | Suite completa del sistema |
| `test_recuperacion_completo.py` | Implementación de los 32 casos del plan base |
