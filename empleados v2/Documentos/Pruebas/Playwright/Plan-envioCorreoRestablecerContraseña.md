# Pitch — Prueba de Token de Uso Único y Mensajes en Restablecimiento de Contraseña
**Sistema:** GestiónRH — Administración de Empleados  
**Fecha:** 2026-04-25  
**Archivo de tests:** `Tests/test_envio_correo_restablecercontrasena.py`

---

## Problema

Un usuario que recibe el correo de recuperación de contraseña y hace clic en el enlace debe poder restablecer su contraseña **exactamente una vez**. Si el enlace puede usarse más de una vez, cualquier persona que intercepte o reutilice la URL podría cambiar la contraseña arbitrariamente — un fallo de seguridad crítico.

Además, el sistema debe comunicar al usuario **el estado exacto** en cada paso: qué ocurrió al solicitar, qué ocurrió al restablecer exitosamente, y qué ocurrió si intentó usar un enlace ya consumido. Si los mensajes son incorrectos, vacíos o ausentes, el usuario no sabe qué pasó y pierde confianza en el sistema.

---

## Apetito

**Ciclo pequeño — 1 semana.** La validación no requiere esperar entrega de correo real. Con un token inyectado directamente en BD se pueden ejercitar todos los flujos en menos de 5 minutos por ejecución.

Fuera del apetito: integración end-to-end con yopmail en tiempo real (corre como `xfail` opcional, no es el núcleo de la prueba).

---

## Solución

Dos scopes independientes, cada uno con una condición de éxito clara:

### Scope A — Token de uso único

| Paso | Acción | Resultado esperado |
|---|---|---|
| 1 | Inyectar token válido en BD (`Usado=0`, expira en UTC+30min) | Token `Usado=0` confirmado en BD |
| 2 | GET `/Cuenta/RestablecerPassword?token=CODIGO` | Formulario carga correctamente |
| 3 | POST con nueva contraseña `usuario2` | Redirige a `/Cuenta/Login` |
| 4 | Intentar POST nuevamente con la **misma URL** | **No redirige a Login** — permanece en `/Cuenta/RestablecerPassword` |
| 5 | Verificar mensaje de rechazo | Texto exacto: `"El código es inválido o ha expirado."` |

**Condición de éxito del scope:** el segundo POST con el mismo token es rechazado y muestra el mensaje exacto. No hay ambigüedad en el resultado.

### Scope B — Mensajes correctos en cada paso

| Momento | Selector | Texto exacto esperado |
|---|---|---|
| Tras solicitar recuperación | `.alert--info` en `/Cuenta/Login` | `"Si el correo está registrado, recibirás las instrucciones de recuperación."` |
| Tras restablecer exitosamente | `.alert--success` en `/Cuenta/Login` | `"Contraseña restablecida correctamente. Inicia sesión."` |
| Tras reusar un token ya consumido | `.validation-summary-errors li` en `/Cuenta/RestablecerPassword` | `"El código es inválido o ha expirado."` |

**Condición de éxito del scope:** los tres mensajes aparecen con el texto exacto, no simplemente "algo visible". Cualquier cambio en el texto de la aplicación fallará el test inmediatamente.

---

## Agujeros de conejo (a evitar)

| Riesgo | Por qué es un agujero | Cómo está resuelto |
|---|---|---|
| Esperar entrega real de correo vía SMTP | Office 365 tarda +10 minutos; bloquea toda la suite | Fallback BD: se inyecta un token con hash SHA-256 conocido cuando yopmail no responde en 10 intentos |
| Zona horaria de SQL Server vs. `DateTime.UtcNow` | `GETDATE()` puede dar expiración en el pasado si el servidor está en UTC-5 | El INSERT usa `GETUTCDATE()` explícitamente |
| Selector de mensajes demasiado amplio | `[class*='alert']` puede capturar elementos equivocados | Selectores específicos: `.alert--info`, `.alert--success`, `.validation-summary-errors li` |

---

## No-Gos

- **No se prueba** el diseño visual del email ni el botón CTA en el contexto de estos dos scopes.
- **No se prueba** la latencia de entrega del servidor SMTP.
- **No se prueba** la validación HTML5 de los campos del formulario.
- **No se valida** el contenido del correo HTML en estas pruebas (eso corresponde a tests de plantillas de email, separados).

---

## Datos de prueba

| Variable | Valor |
|---|---|
| Correo | `carlos.rodriguez@yopmail.com` |
| Contraseña nueva | `usuario2` |
| Contraseña restaurada en teardown | `Usuario1` |
| Expiración del token inyectado | `GETUTCDATE() + 30 minutos` |

---

## Estructura de tests y resultados esperados

| Test | Scope | Resultado esperado |
|---|---|---|
| `test_paso1` | B — Mensajes | `PASS` — `.alert--info` con texto exacto |
| `test_paso5` | — BD | `PASS` — token SHA-256, 64 chars, expira 30 min |
| `test_paso6` | — BD | `PASS` — auditoría `RecuperacionContrasena` Exitoso=1 |
| `test_paso7` | — Email | `XFAIL` si email no llega; fallback BD activo |
| `test_paso9` | — Email | `SKIP` si no hay botón CTA (modo fallback) |
| `test_paso11` | B — Mensajes | `PASS` — redirige a Login + `.alert--success` con texto exacto |
| `test_paso15` | A — Token único | `PASS` — `Usado=1` en BD tras restablecimiento |
| `test_paso16` | — BD | `PASS` — auditoría `CambioContrasenaExitoso` Exitoso=1 |
| `test_paso17` | A — Token único | `PASS` — login con `usuario2` → Dashboard |
| `test_paso18` | A — Token único | `PASS` — login con `Usuario1` → denegado |
| **`test_paso19`** | **A — Token único** | **`PASS` — segundo intento rechazado + mensaje exacto** |

---

## Correcciones conocidas (historial)

### CE-01 — `SendAsDenied`
`sistemas.helpharma@zentria.com.co` no tiene permiso _Send As_ sobre `notificacion.sf@zentria.com.co`. El fixture parchea `appsettings.json` antes de iniciar la app. **Corrección definitiva:** agregar permiso en Exchange Online Admin.

### CE-03 — Email tarda +10 min
Latencia real de Office 365. **Resuelto:** fallback BD inyecta token directamente cuando yopmail no responde en 10 intentos (≈600s). La prueba marca `test_paso7` como `xfail` y continúa todos los demás tests.

### CE-05 — Tokens del seeding inválidos
Tokens `TK7E4D8F5G` etc. son texto plano y el sistema espera SHA-256. Son inválidos por diseño. Excluidos explícitamente de las queries.

### CE-06 — Botón CTA en el email
Implementado: `SeguridadEmailTemplate.RecuperacionContrasena()` recibe `urlRestablecimiento` y renderiza botón azul con `href`. El test `test_paso9` lo verifica cuando el email llega.

---

## Comando de ejecución

```powershell
cd "c:\...\empleados v2"

# Suite completa (incluye espera yopmail ~10 min)
.venv\Scripts\python.exe -m pytest Tests/test_envio_correo_restablecercontrasena.py -v --headed --slowmo 800 -s

# Solo scopes A y B sin esperar email (~3 min con fallback BD)
# (test_paso7 hará xfail tras 10 reintentos y el resto continúa)
.venv\Scripts\python.exe -m pytest Tests/test_envio_correo_restablecercontrasena.py -v --headed --slowmo 800 -s
```

**Sistema:** GestiónRH — Administración de Empleados  
**Fecha:** 2026-04-24 (actualizado 2026-04-25)  
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
5. Extrae el **enlace y el botón CTA** del email y completa el restablecimiento con nueva contraseña (`usuario2`)
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
- El test reintenta la actualización del iframe **5 veces × 60 s = hasta 300 s** antes de marcar `xfail`  
- **Nota:** El `xfail` ocurría en el intento 1/5 por un bug de indentación (el `pytest.xfail()` estaba dentro del `for` en lugar de después). **Corregido 2026-04-25**: el xfail solo se lanza si `not encontrado` al salir del bucle.  
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

### CE-06 — Botón CTA «Restablecer contraseña» en el email *(Mejora implementada 2026-04-25)*

**Descripción:** El email de recuperación no tenía un botón/enlace clicable — el usuario debía copiar
el código manualmente en el formulario, lo cual es una mala experiencia de usuario.

**Mejora implementada:**
- `SeguridadEmailTemplate.RecuperacionContrasena()` ahora acepta `string? urlRestablecimiento`
- Cuando se provee la URL, renderiza un botón azul «Restablecer contraseña» con `href` a la URL
- También incluye el enlace en texto plano como fallback accesible
- `CuentaController` genera la URL con `Url.Action("RestablecerPassword", "Cuenta", protocol: Request.Scheme)`
- `CuentaService` construye `"{urlBase}?token={Uri.EscapeDataString(codigoPlano)}"`

**Prueba asociada:** `test_paso9_boton_cta_en_email` — verifica que el botón existe con href válido
apuntando a `RestablecerPassword?token=CODIGO`.

---

## Datos de prueba

| Variable | Valor |
|---|---|
| `CORREO` | `carlos.rodriguez@yopmail.com` |
| `YOPMAIL_USUARIO` | `carlos.rodriguez` |
| `PASSWORD_NUEVA` | `usuario2` |
| Contraseña de restauración | `Usuario1` (hash restaurado por teardown) |

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
  ├── PASO 8  Playwright → esperar email con asunto del sistema (max 300 s, 5 reintentos × 60 s)
  ├── PASO 9a Playwright → extraer href del botón CTA «Restablecer contraseña» (iframe #ifmail)
  ├── PASO 9b Playwright → extraer href enlace token= (fallback si no hay botón CTA)
  ├── PASO 10 Verificar: token en email es alfanumérico (NO hash de 64 chars)
  │
  ├── [test_paso9] Verificar: boton_href != None, contiene RestablecerPassword?token=
  │
  ├── PASO 11 Playwright → navegar al enlace de restablecimiento (URL del botón CTA)
  ├── PASO 12 Playwright → fill NuevoPassword = "usuario2"
  ├── PASO 13 Playwright → fill ConfirmarPassword = "usuario2"
  ├── PASO 14 Playwright → submit → verificar redirección a /Cuenta/Login con mensaje de éxito
  │
  ├── PASO 15 DB query  → verificar token Usado=1
  ├── PASO 16 DB query  → verificar RegistroNotificaciones TipoEvento='CambioContrasenaExitoso' Exitoso=1
  │
  ├── PASO 17 Playwright → login con nueva contraseña (`usuario2`) → ✅ acceso al Dashboard
  ├── PASO 18 Playwright → login con contraseña antigua (`Usuario1`) → ❌ denegado
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

| Paso | Descripción | Resultado esperado |
|---|---|---|
| test_paso1 | Formulario solicitud → redirige a Login con mensaje | ✅ PASS |
| test_paso5 | Token en BD — 64 chars hex SHA-256, expira en 30 min | ✅ PASS |
| test_paso6 | Auditoría `RecuperacionContrasena` Exitoso=1 | ✅ PASS |
| test_paso7 | Email en yopmail — recibido con botón CTA y enlace | ✅ PASS |
| test_paso7 | Token en email — código plano (no hash de 64 chars) | ✅ PASS |
| **test_paso9** | **Botón CTA «Restablecer contraseña» — href con token=** | **✅ PASS** |
| test_paso11 | Formulario restablecimiento — contraseña `usuario2` aceptada | ✅ PASS |
| test_paso15 | Token marcado `Usado=1` en BD | ✅ PASS |
| test_paso16 | Auditoría `CambioContrasenaExitoso` Exitoso=1 | ✅ PASS |
| test_paso17 | Login con `usuario2` → acceso al Dashboard | ✅ PASS |
| test_paso18 | Login con `Usuario1` (antigua) → denegado | ✅ PASS |
| Teardown | Aplicación detenida y BD restaurada a `Usuario1` | ✅ OK |

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
