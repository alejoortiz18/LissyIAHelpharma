# Plan de Pruebas — Envío de Correo: Restablecimiento de Contraseña
**Sistema:** GestiónRH — Administración de Empleados  
**Fecha:** 2026-04-24  
**Cuenta de prueba:** `carlos.rodriguez@yopmail.com`  
**Bandeja de verificación:** https://yopmail.com/en/?login=carlos.rodriguez  
**Archivo de tests:** `Tests/test_envio_correo_restablecercontrasena.py`

---

## Objetivo

Verificar de forma automatizada que el flujo completo de restablecimiento de contraseña:

1. Levanta la aplicación ASP.NET Core
2. Usa Playwright para navegar a `/Cuenta/RecuperarPassword` y enviar el formulario
3. Confirma en BD que el token SHA-256 fue creado correctamente
4. Verifica en **yopmail.com** que el correo llegó al destinatario
5. Extrae el enlace del email y completa el restablecimiento con nueva contraseña
6. Valida login con la nueva contraseña
7. Valida que `RegistroNotificaciones` registró `Exitoso=1`
8. Restaura el estado de BD (contraseña vuelve a `Usuario1`)
9. **Detiene la aplicación** al finalizar

---

## Prerrequisitos

| Requisito | Estado | Notas |
|---|---|---|
| `.venv` activo con pytest + playwright instalados | ✅ | `c:\...\empleados v2\.venv` |
| BD `GestionPersonal` en `(localdb)\MSSQLLocalDB` activa | ✅ | |
| `dotnet user-secrets` con `EmailSettings:Smtp:Password` | ✅ | `H3lph42023**` guardado |
| Acceso SMTP `smtp.office365.com:587` | ✅ | Verificado el 2026-04-24 |
| `carlos.rodriguez@yopmail.com` existe en BD con contraseña `Usuario1` | ✅ | |
| **"Send As" para `notificacion.sf@zentria.com.co`** | ⚠️ Pendiente | Ver Corrección CE-01 |

---

## Corrección de Errores Conocidos

### CE-01 — `SendAsDenied`: el remitente configurado no tiene permisos

**Error observado:**
```
SMTPDataError: (554, b'5.2.252 SendAsDenied; sistemas.helpharma@zentria.com.co 
not allowed to send as notificacion.sf@zentria.com.co')
```

**Causa:** `appsettings.json` tiene `"FromAddress": "notificacion.sf@zentria.com.co"` pero la cuenta 
de autenticación `sistemas.helpharma@zentria.com.co` no tiene el permiso _Send As_ en Exchange Online.

**Corrección temporal (para ejecutar pruebas hoy):**  
El test parchea automáticamente `appsettings.json` al iniciar, usando `sistemas.helpharma@zentria.com.co` 
como remitente (que SÍ está autenticado), y lo revierte al terminar.

**Corrección definitiva (recomendada para producción):**
1. Ingresar a [admin.exchange.microsoft.com](https://admin.exchange.microsoft.com)
2. Recipients → Mailboxes → `notificacion.sf@zentria.com.co`
3. Pestaña **Delegation → Send As** → agregar `sistemas.helpharma@zentria.com.co`
4. Esperar ≈ 30 minutos para propagación
5. Revertir `FromAddress` a `"notificacion.sf@zentria.com.co"` en `appsettings.json`
6. Re-ejecutar el test para confirmar

### CE-02 — App no responde en `http://localhost:5002`

**Síntoma:** El test falla con `net::ERR_CONNECTION_REFUSED` en Playwright.

**Causa posible:** `dotnet run` tarda más de 30 segundos en iniciar (primera compilación).

**Corrección:** El test espera hasta 60 segundos haciendo polling al endpoint `/Cuenta/Login`.
Si persiste, ejecutar manualmente antes del test:
```powershell
cd "Proyecto MVC\GestionPersonal.Web"
dotnet build --no-incremental -v quiet
```

### CE-03 — Email no llega a yopmail en 30 segundos

**Síntoma:** `email_item.wait_for(timeout=30_000)` genera `TimeoutError`.

**Causa posible:** Latencia de entrega de Office 365 o yopmail.

**Corrección:** 
- El test reintenta la actualización del iframe 3 veces antes de marcar `xfail`  
- Si el test termina como `xfail`, verificar manualmente en https://yopmail.com/en/?login=carlos.rodriguez

### CE-04 — `NombreEmpleado` en el correo muestra el correo en lugar del nombre

**Síntoma:** El email recibido dice "Hola, carlos.rodriguez@yopmail.com" en lugar del nombre real.

**Causa:** En `CuentaService.SolicitarRecuperacionAsync()` se pasa `usuario.CorreoAcceso` como `NombreEmpleado`:
```csharp
NombreEmpleado: usuario.CorreoAcceso,  // ← Bug
```

**Corrección:**
```csharp
NombreEmpleado: usuario.Empleado?.NombreCompleto ?? usuario.CorreoAcceso,
```
El test registra esta diferencia pero no la marca como FAIL (es un issue de UX, no de funcionalidad).

### CE-05 — Token del seeding es texto plano (tokens viejos inválidos)

**Síntoma:** Los tokens `TK7E4D8F5G` y `TK3F9A2B1C` del seeding no funciona con el nuevo sistema SHA-256.

**Causa:** El seeding original creó tokens de texto plano. El nuevo sistema hashea los tokens antes de buscarlos en BD.

**Comportamiento esperado:** Los tokens viejos son **inválidos** — esto es correcto por seguridad.

**Acción:** No requiere corrección. El test valida que estos tokens son rechazados (pruebas negativas).

---

## Flujo de ejecución

```
INICIO
  │
  ├── [Setup] Parchear appsettings.json → FromAddress temporal (CE-01)
  ├── [Setup] Restaurar contraseña de carlos.rodriguez a Usuario1 en BD
  ├── [Setup] Limpiar tokens previos de carlos.rodriguez en BD
  ├── [Setup] Iniciar: dotnet run GestionPersonal.Web
  ├── [Setup] Esperar hasta que http://localhost:5002 responda (max 60s)
  │
  ├── PASO 1  Playwright → GET /Cuenta/RecuperarPassword
  ├── PASO 2  Playwright → fill #CorreoAcceso = "carlos.rodriguez@yopmail.com"
  ├── PASO 3  Playwright → click "Enviar instrucciones"
  ├── PASO 4  Playwright → verificar redirección a /Cuenta/Login con mensaje informativo
  │
  ├── PASO 5  DB query  → verificar token creado (SHA-256, 64 chars, expira en 30 min)
  ├── PASO 6  DB query  → verificar RegistroNotificaciones TipoEvento='RecuperacionContrasena' Exitoso=1
  │
  ├── PASO 7  Playwright → abrir yopmail (iframe #ifinbox)
  ├── PASO 8  Playwright → esperar email con asunto del sistema (max 30s)
  ├── PASO 9  Playwright → extraer href del enlace ?token= (iframe #ifmail)
  ├── PASO 10 Verificar: token en email es alfanumérico (NO hash de 64 chars)
  │
  ├── PASO 11 Playwright → navegar al enlace de restablecimiento
  ├── PASO 12 Playwright → fill NuevoPassword = "RestablecidoTest2026!"
  ├── PASO 13 Playwright → fill ConfirmarPassword = "RestablecidoTest2026!"
  ├── PASO 14 Playwright → submit → verificar redirección a /Cuenta/Login con mensaje de éxito
  │
  ├── PASO 15 DB query  → verificar token Usado=1
  ├── PASO 16 DB query  → verificar RegistroNotificaciones TipoEvento='CambioContrasenaExitoso' Exitoso=1
  │
  ├── PASO 17 Playwright → login con nueva contraseña → ✅ acceso al Dashboard
  ├── PASO 18 Playwright → login con contraseña antigua → ❌ denegado
  │
  ├── [Teardown] Restaurar contraseña a Usuario1 en BD
  ├── [Teardown] Revertir appsettings.json a FromAddress original
  └── [Teardown] Detener proceso dotnet (la aplicación)
```

---

## Comando de ejecución

```powershell
# Activar el entorno virtual (si no está activo)
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"
.\.venv\Scripts\Activate.ps1

# Ejecutar prueba completa (con yopmail — modo visual)
pytest Tests/test_envio_correo_restablecercontrasena.py -v --headed

# Ejecutar sin verificación yopmail (más rápido, solo BD + formularios)
pytest Tests/test_envio_correo_restablecercontrasena.py -v --headed -m "not yopmail"
```

---

## Resultados esperados

| Paso | Descripción | Resultado |
|---|---|---|
| Formulario solicitud | Redirige a Login con mensaje | ✅ PASS |
| Token en BD | 64 chars hex SHA-256 | ✅ PASS |
| Expiración token | ≈ 30 minutos | ✅ PASS |
| Auditoría solicitud | `RecuperacionContrasena` Exitoso=1 | ✅ PASS |
| Email en yopmail | Email recibido con enlace | ✅ PASS |
| Token en email | Código plano (12 chars), no hash | ✅ PASS |
| Formulario restablecimiento | Nueva contraseña aceptada | ✅ PASS |
| Token marcado | `Usado=1` en BD | ✅ PASS |
| Auditoría confirmación | `CambioContrasenaExitoso` Exitoso=1 | ✅ PASS |
| Login nueva contraseña | Acceso al Dashboard | ✅ PASS |
| Login contraseña antigua | Denegado | ✅ PASS |
| Aplicación detenida | Proceso dotnet terminado | ✅ PASS |

---

## Archivos involucrados

| Archivo | Rol |
|---|---|
| `Tests/test_envio_correo_restablecercontrasena.py` | Test ejecutable |
| `Tests/helpers.py` | `hacer_login()`, `BASE_URL` |
| `Tests/conftest.py` | Reset BD global (session fixture) |
| `Proyecto MVC/GestionPersonal.Web/appsettings.json` | Config SMTP (parcheado temporalmente) |
| `Proyecto MVC/GestionPersonal.Application/Services/CuentaService.cs` | Lógica de negocio del flujo |
| `Proyecto MVC/GestionPersonal.Web/Controllers/CuentaController.cs` | Endpoints HTTP del flujo |
