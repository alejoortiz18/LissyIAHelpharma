# Plan de Ejecución — Restablecimiento de Contraseña
**Sistema:** GestiónRH — Administración de Empleados  
**Fecha base:** 2026-04-24  
**Archivo de tests:** `Tests/test_recuperacion_completo.py`  
**Ejecutar con:** `pytest Tests/test_recuperacion_completo.py -v --headed`

---

## Contexto técnico

| Elemento | Valor |
|---|---|
| URL base | `http://localhost:5002` |
| Formulario solicitud | `GET /Cuenta/RecuperarPassword` |
| Formulario restablecimiento | `GET /Cuenta/RestablecerPassword?token=<CÓDIGO_PLANO>` |
| Email de prueba | `carlos.rodriguez@yopmail.com` |
| Bandeja yopmail | `https://yopmail.com/en/?login=carlos.rodriguez` |
| DB local | `(localdb)\MSSQLLocalDB` · `GestionPersonal` |
| Tabla de tokens | `dbo.TokensRecuperacion` |
| Tabla de auditoría | `dbo.RegistroNotificaciones` |

### Cómo funciona el flujo de token (implementación real)
1. El usuario ingresa su correo en `/Cuenta/RecuperarPassword`
2. El servidor genera un **código plano alfanumérico de 12 caracteres** (`GenerarCodigoSeguro()`)
3. Se almacena **SHA-256(código_plano)** en `dbo.TokensRecuperacion.Token` (64 chars hex)
4. El código **plano** llega al correo del usuario
5. El usuario usa ese código como `?token=` en la URL de restablecimiento
6. El servidor hashea el parámetro recibido y lo compara con el hash en BD

> **Implicación para pruebas:** El `?token=` en el enlace del email es el código legible (12 chars), NO el hash. Los tokens del seeding (`TK7E4D8F5G`, `TK3F9A2B1C`) son texto plano antiguo — se usan **solo** para pruebas negativas (expirado/usado).

---

## Tokens de seeding disponibles

| Token | Usuario | Estado | Uso en pruebas |
|---|---|---|---|
| `TK1H6K9M2N` | natalia.bermudez@yopmail.com | Vigente hasta 2026-04-24, Usado=0 | **Invalidado** (pre-migración) |
| `TK7E4D8F5G` | andres.torres@yopmail.com | Expirado 2026-04-10, Usado=0 | TC-RC-14 (token expirado) |
| `TK3F9A2B1C` | laura.sanchez@yopmail.com | Expirado, Usado=1 | TC-RC-15 (token usado) |

---

## Categorías de prueba

| # | Categoría | Casos | Modo |
|---|---|---|---|
| A | Formulario de solicitud | TC-RC-01 a TC-RC-06 | Automatizado |
| B | Email en yopmail.com | TC-RC-07 a TC-RC-12 | Automatizado + revisión manual |
| C | Formulario de restablecimiento | TC-RC-13 a TC-RC-21 | Automatizado |
| D | Seguridad del token en BD | TC-RC-22 a TC-RC-24 | Automatizado (DB query) |
| E | Login posterior | TC-RC-25 a TC-RC-26 | Automatizado |
| F | Auditoría (RegistroNotificaciones) | TC-RC-27 a TC-RC-28 | Automatizado (DB query) |
| G | Casos borde / resiliencia | TC-RC-29 a TC-RC-32 | Automatizado / Manual |

---

## A — Formulario de solicitud (`/Cuenta/RecuperarPassword`)

### TC-RC-01 · Correo válido registrado
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-01 |
| **Precondición** | carlos.rodriguez@yopmail.com existe en BD y está activo |
| **Pasos** | 1. Navegar a `/Cuenta/RecuperarPassword` · 2. Ingresar `carlos.rodriguez@yopmail.com` · 3. Submit |
| **Resultado esperado** | Redirige a `/Cuenta/Login` con mensaje informativo (no de error) |
| **Resultado NO esperado** | Mostrar si el correo existe o no ("Correo no registrado") |
| **Automatizado** | ✅ |

### TC-RC-02 · Correo no registrado — respuesta idéntica (anti-enumeración)
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-02 |
| **Precondición** | `correonoexiste@yopmail.com` no existe en BD |
| **Pasos** | 1. Navegar a `/Cuenta/RecuperarPassword` · 2. Ingresar correo inexistente · 3. Submit |
| **Resultado esperado** | Misma respuesta y redirección que TC-RC-01 (no diferencia visible) |
| **Resultado NO esperado** | Mensaje de error "usuario no encontrado" o similar |
| **Automatizado** | ✅ |

### TC-RC-03 · Campo vacío
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-03 |
| **Precondición** | Ninguna |
| **Pasos** | 1. Navegar a `/Cuenta/RecuperarPassword` · 2. No ingresar nada · 3. Submit |
| **Resultado esperado** | Error de validación en el campo, NO submit al servidor |
| **Automatizado** | ✅ |

### TC-RC-04 · Formato de correo inválido
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-04 |
| **Pasos** | Ingresar `noescorreo` o `@dominio.com` · Submit |
| **Resultado esperado** | Error de validación de formato antes del envío |
| **Automatizado** | ✅ |

### TC-RC-05 · Correo en mayúsculas / con espacios
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-05 |
| **Pasos** | Ingresar `  CARLOS.RODRIGUEZ@YOPMAIL.COM  ` · Submit |
| **Resultado esperado** | El sistema lo trata como el correo registrado y envía el email (case-insensitive) |
| **Automatizado** | ✅ (verificar DB) |

### TC-RC-06 · Múltiples solicitudes consecutivas
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-06 |
| **Precondición** | carlos.rodriguez@yopmail.com activo |
| **Pasos** | Solicitar recuperación dos veces seguidas para el mismo correo |
| **Resultado esperado** | Cada solicitud genera un nuevo token; el token anterior queda **Usado=1 o expirado** |
| **Nota** | Verifica en BD que solo el último token sea válido |
| **Automatizado** | ✅ (DB query) |

---

## B — Email en yopmail.com

> **Nota de ejecución:** yopmail carga la bandeja en un `<iframe id="ifinbox">` y el cuerpo del email en `<iframe id="ifmail">`. El test navega a `https://yopmail.com/en/?login=carlos.rodriguez` y opera sobre esos iframes.

### TC-RC-07 · Email llega a la bandeja de yopmail
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-07 |
| **Precondición** | TC-RC-01 ejecutado previamente en la misma sesión |
| **Pasos** | 1. Navegar a yopmail con el usuario `carlos.rodriguez` · 2. Esperar hasta 30s |
| **Resultado esperado** | Aparece un email con asunto que contiene "contraseña", "recuper" o "GestiónRH" |
| **Automatizado** | ✅ (con iframe) |
| **Manual si falla** | Abrir `https://yopmail.com/en/?login=carlos.rodriguez` en navegador |

### TC-RC-08 · El email NO contiene la contraseña actual ni el hash SHA-256
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-08 |
| **Pasos** | Abrir el email de recuperación · Inspeccionar el cuerpo |
| **Resultado esperado** | El cuerpo NO contiene hashes hex de 64 chars ni la contraseña en texto plano |
| **Automatizado** | ✅ (regex en el texto del iframe ifmail) |

### TC-RC-09 · El cuerpo contiene el código legible (no el hash)
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-09 |
| **Pasos** | Abrir el email · Buscar el código o enlace de restablecimiento |
| **Resultado esperado** | Se detecta un código alfanumérico o un enlace con `?token=` que contiene el código plano |
| **Automatizado** | ✅ |

### TC-RC-10 · El código del email es alfanumérico de ≤ 20 caracteres
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-10 |
| **Pasos** | Extraer el parámetro `token=` del enlace en el email |
| **Resultado esperado** | El valor es alfanumérico (a-z, A-Z, 0-9), longitud 12 (según `GenerarCodigoSeguro()`) |
| **Resultado NO esperado** | String de 64 chars hex (eso sería el hash — error grave de seguridad) |
| **Automatizado** | ✅ |

### TC-RC-11 · El email menciona la vigencia de 30 minutos
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-11 |
| **Pasos** | Inspeccionar el cuerpo del email |
| **Resultado esperado** | Texto que mencione "30 minutos" o "30 min" |
| **Automatizado** | ✅ |

### TC-RC-12 · El enlace del email funciona para restablecer la contraseña
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-12 |
| **Pasos** | 1. Extraer `href` del enlace · 2. Navegar a ese `href` · 3. Completar el formulario |
| **Resultado esperado** | El formulario se muestra y el restablecimiento es exitoso |
| **Automatizado** | ✅ (test de integración completa) |
| **Nota** | Es el "happy path" completo: solicitud → email → uso del token del email |

---

## C — Formulario de restablecimiento (`/Cuenta/RestablecerPassword`)

### TC-RC-13 · Token válido → formulario visible
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-13 |
| **Precondición** | Token fresco generado en TC-RC-01 |
| **Pasos** | Navegar a `/Cuenta/RestablecerPassword?token=<código_del_email>` |
| **Resultado esperado** | Formulario con campos `NuevoPassword` y `ConfirmarPassword` visible |
| **Automatizado** | ✅ |

### TC-RC-14 · Token expirado → rechazado
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-14 |
| **Precondición** | Token `TK7E4D8F5G` en seeding (expirado 2026-04-10) |
| **Pasos** | Navegar a `/Cuenta/RestablecerPassword?token=TK7E4D8F5G` |
| **Resultado esperado** | Redirige a Login con mensaje de error O muestra error sin formulario de nueva contraseña |
| **Automatizado** | ✅ |

### TC-RC-15 · Token ya usado → rechazado
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-15 |
| **Precondición** | Token `TK3F9A2B1C` con `Usado=1` en seeding |
| **Pasos** | Navegar a `/Cuenta/RestablecerPassword?token=TK3F9A2B1C` |
| **Resultado esperado** | Redirige a Login con mensaje de error O muestra error sin formulario |
| **Automatizado** | ✅ |

### TC-RC-16 · Token aleatorio inválido → rechazado
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-16 |
| **Pasos** | Navegar a `/Cuenta/RestablecerPassword?token=TOKEN_INVENTADO_FALSO` |
| **Resultado esperado** | Rechazado — no muestra formulario de nueva contraseña |
| **Automatizado** | ✅ |

### TC-RC-17 · Sin parámetro token → rechazado
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-17 |
| **Pasos** | Navegar a `/Cuenta/RestablecerPassword` sin `?token=` |
| **Resultado esperado** | Redirección a Login o error 400 (no formulario de nueva contraseña) |
| **Automatizado** | ✅ |

### TC-RC-18 · Contraseña nueva demasiado corta
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-18 |
| **Precondición** | Token válido cargado |
| **Pasos** | Ingresar contraseña `Ab1!` (< 8 chars) en ambos campos · Submit |
| **Resultado esperado** | Error de validación — no procesado |
| **Automatizado** | ✅ |

### TC-RC-19 · Confirmación de contraseña no coincide
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-19 |
| **Precondición** | Token válido cargado |
| **Pasos** | `NuevoPassword=Clave2026!` · `ConfirmarPassword=Diferente2026!` · Submit |
| **Resultado esperado** | Error de validación "Las contraseñas no coinciden" |
| **Automatizado** | ✅ |

### TC-RC-20 · Ambos campos vacíos con token válido
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-20 |
| **Pasos** | No llenar nada · Submit |
| **Resultado esperado** | Errores de validación en campos requeridos |
| **Automatizado** | ✅ |

### TC-RC-21 · Restablecimiento exitoso → redirección a Login
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-21 |
| **Precondición** | Token válido generado en la sesión actual |
| **Pasos** | Ingresar `NuevaContrasena2026!` en ambos campos · Submit |
| **Resultado esperado** | Redirige a `/Cuenta/Login` con mensaje de éxito |
| **Automatizado** | ✅ |

---

## D — Seguridad del token en BD

### TC-RC-22 · Token almacenado en BD es SHA-256 hex (64 chars)
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-22 |
| **Pasos** | Solicitar recuperación · Consultar `dbo.TokensRecuperacion` |
| **Resultado esperado** | `Token` tiene exactamente 64 caracteres hexadecimales lowercase |
| **Resultado NO esperado** | Token de 12 chars (código plano guardado sin hash — fallo crítico de seguridad) |
| **Automatizado** | ✅ (DB query via Invoke-Sqlcmd) |

### TC-RC-23 · Token marcado como Usado=1 tras restablecimiento exitoso
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-23 |
| **Pasos** | Completar restablecimiento · Consultar `Usado` en BD |
| **Resultado esperado** | `Usado = 1` |
| **Automatizado** | ✅ |

### TC-RC-24 · Token expirado en 30 minutos (FechaExpiracion)
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-24 |
| **Pasos** | Solicitar recuperación · Consultar `FechaExpiracion` en BD |
| **Resultado esperado** | `FechaExpiracion` ≈ `GETUTCDATE() + 30 minutos` (±1 min de margen) |
| **Automatizado** | ✅ |

---

## E — Login posterior al restablecimiento

### TC-RC-25 · Login con nueva contraseña → exitoso
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-25 |
| **Precondición** | TC-RC-21 completado |
| **Pasos** | Login con `carlos.rodriguez@yopmail.com` + nueva contraseña |
| **Resultado esperado** | Redirige al Dashboard (no queda en `/Cuenta/Login`) |
| **Automatizado** | ✅ |

### TC-RC-26 · Login con contraseña anterior → denegado
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-26 |
| **Precondición** | TC-RC-21 completado |
| **Pasos** | Login con `carlos.rodriguez@yopmail.com` + contraseña antigua `Usuario1` |
| **Resultado esperado** | Error de autenticación — permanece en `/Cuenta/Login` |
| **Automatizado** | ✅ |

---

## F — Auditoría en RegistroNotificaciones

### TC-RC-27 · Solicitud genera registro de auditoría
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-27 |
| **Pasos** | Solicitar recuperación · Consultar `dbo.RegistroNotificaciones` |
| **Resultado esperado** | Existe fila con `TipoEvento='RecuperacionContrasena'`, `Exitoso=1`, `Destinatario='carlos.rodriguez@yopmail.com'` |
| **Automatizado** | ✅ |

### TC-RC-28 · Restablecimiento exitoso genera registro de confirmación
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-28 |
| **Pasos** | Completar restablecimiento · Consultar `dbo.RegistroNotificaciones` |
| **Resultado esperado** | Fila con `TipoEvento='CambioContrasenaExitoso'`, `Exitoso=1` |
| **Automatizado** | ✅ |

---

## G — Casos borde y resiliencia

### TC-RC-29 · Correo inactivo / dado de baja
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-29 |
| **Precondición** | Usuario con `Activo=0` en BD (si aplica la regla) |
| **Pasos** | Solicitar recuperación con el correo del usuario inactivo |
| **Resultado esperado** | Respuesta genérica — sin token generado en BD (no se puede recuperar cuenta inactiva) |
| **Manual si no hay usuario inactivo** | ⚠️ Requiere preparar dato en BD |
| **Automatizado** | Parcial |

### TC-RC-30 · Inyección en el campo de correo (seguridad)
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-30 |
| **Pasos** | Ingresar `' OR '1'='1` en el campo correo · Submit |
| **Resultado esperado** | Respuesta genérica sin error de aplicación (sin SQL Injection) |
| **Automatizado** | ✅ |

### TC-RC-31 · Parámetro token con caracteres especiales (seguridad)
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-31 |
| **Pasos** | Navegar a `/Cuenta/RestablecerPassword?token=<script>alert(1)</script>` |
| **Resultado esperado** | Rechazado limpiamente — sin XSS ejecutado |
| **Automatizado** | ✅ |

### TC-RC-32 · Token con longitud anormal
| Campo | Detalle |
|---|---|
| **ID** | TC-RC-32 |
| **Pasos** | Token de 1000 chars · Token de 0 chars |
| **Resultado esperado** | Rechazado en ambos casos sin error 500 |
| **Automatizado** | ✅ |

---

## Orden de ejecución recomendado

```
Grupo 1 — Sin email (rápidos, solo UI + BD negativa)
  TC-RC-03, TC-RC-04, TC-RC-14, TC-RC-15, TC-RC-16, TC-RC-17,
  TC-RC-18, TC-RC-19, TC-RC-20, TC-RC-30, TC-RC-31, TC-RC-32

Grupo 2 — Solicitud + verificaciones BD (requiere SMTP activo)
  TC-RC-01 → TC-RC-22 → TC-RC-24 → TC-RC-27

Grupo 3 — Verificación email yopmail (requiere que correo haya llegado)
  TC-RC-07 → TC-RC-08 → TC-RC-09 → TC-RC-10 → TC-RC-11

Grupo 4 — Happy path completo (encadenado)
  TC-RC-12 → TC-RC-21 → TC-RC-23 → TC-RC-25 → TC-RC-26 → TC-RC-28

Grupo 5 — Anti-enumeración y casos borde
  TC-RC-02, TC-RC-05, TC-RC-06, TC-RC-29
```

---

## Paso de verificación manual (cuando el SMTP falla o yopmail no carga)

Si el test **TC-RC-07** falla por timeout o error de iframe, sigue estos pasos:

1. Abrir manualmente: `https://yopmail.com/en/?login=carlos.rodriguez`
2. Confirmar que aparece un email con asunto `[Recuperación de Contraseña]`
3. Abrir el email → copiar el código del enlace (`?token=XXXXX`)
4. Navegar a `http://localhost:5002/Cuenta/RestablecerPassword?token=XXXXX`
5. Ingresar nueva contraseña `ManualTest2026!` en ambos campos
6. Verificar redirección a Login con mensaje de éxito
7. Verificar login con `ManualTest2026!` funciona

---

## Precondiciones de BD para ejecución limpia

Ejecutar antes de la suite completa (o dejar que `conftest.py` lo haga):

```sql
-- Restaurar contraseña de carlos.rodriguez a Usuario1
UPDATE dbo.Usuarios
SET PasswordHash = 0x7DED37B4612147C18EBDFA1F6DEB4709EC9D511DA20641214F1F97612DF2CEAE,
    PasswordSalt = 0xF2B483C7DAC61EC2CA7F1331C95D6800,
    DebeCambiarPassword = 0
WHERE CorreoAcceso = 'carlos.rodriguez@yopmail.com';

-- Borrar tokens previos del test para evitar contaminación
DELETE FROM dbo.TokensRecuperacion
WHERE UsuarioId = (SELECT Id FROM dbo.Usuarios WHERE CorreoAcceso = 'carlos.rodriguez@yopmail.com')
  AND Token NOT IN ('TK7E4D8F5G', 'TK3F9A2B1C', 'TK1H6K9M2N');
-- Nota: los 3 tokens del seeding son para pruebas negativas — NO borrarlos
```

---

## Resumen de cobertura

| Categoría | Total casos | Automatizados | Manuales / Asistidos |
|---|---|---|---|
| A — Formulario solicitud | 6 | 6 | 0 |
| B — Email yopmail | 6 | 5 | 1 (TC-RC-07 si hay timeout) |
| C — Formulario restablecimiento | 9 | 9 | 0 |
| D — Seguridad token BD | 3 | 3 | 0 |
| E — Login posterior | 2 | 2 | 0 |
| F — Auditoría | 2 | 2 | 0 |
| G — Casos borde | 4 | 3 | 1 (TC-RC-29 requiere dato) |
| **Total** | **32** | **30** | **2** |
