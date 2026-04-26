# Pitch — Activación de Cuenta por Correo para Usuarios Nuevos

> Formato: [Shape Up](https://basecamp.com/shapeup) · Basecamp / 37signals  
> Apetito: **2 semanas** (Small Batch)  
> Prioridad: Alta

---

## 1. El Problema

### Situación actual

El administrador crea un empleado nuevo. El sistema genera una contraseña temporal aleatoria, la almacena hasheada con PBKDF2-SHA256, y envía un correo **informativo** que le dice al usuario que su cuenta fue creada y que, al ingresar por primera vez, el sistema le pedirá cambiar la contraseña.

![Correo actual](../img/correo-actual-usuario-nuevo.png)  
*Correo actual: informativo, sin acción directa para el usuario.*

Ese flujo tiene dos problemas concretos:

1. **El usuario no puede activar su cuenta de forma autónoma.** Tiene que descubrir por sí mismo que debe ir al sistema, intentar ingresar con credenciales que no conoce, y esperar que el sistema lo redirija al cambio. Es confuso y genera soporte innecesario.

2. **Si el token o sesión de activación expira, no hay salida.** El administrador no tiene ningún mecanismo para reenviar el enlace o generar uno nuevo. La única opción hoy es eliminar y recrear al empleado, lo que es un proceso costoso e incorrecto.

---

## 2. Apetito

**2 semanas.**

La infraestructura crítica ya existe: tokens de recuperación con SHA-256, PBKDF2, servicio de correo con MailKit, plantillas HTML, registro de notificaciones. El patrón está probado en el flujo de recuperación de contraseña (`CuentaService.SolicitarRecuperacionAsync` / `RestablecerPasswordAsync`). No estamos construyendo desde cero — estamos extendiendo un patrón conocido en un contexto nuevo.

Si la solución requiere más de 2 semanas, hay que recortar alcance, no ampliar el tiempo.

---

## 3. La Solución

### Resumen del flujo

Cuando el administrador crea un empleado nuevo:

```
[Admin: Guardar empleado]
    └─→ Sistema genera token de activación (24h, SHA-256, único)
    └─→ Guarda token en tabla TokensActivacion
    └─→ Envía correo al usuario con botón "Crear contraseña"
    └─→ Usuario recibe correo, hace clic

[Usuario: clic en "Crear contraseña"]
    └─→ GET /Cuenta/ActivarCuenta?token=XXXX
    └─→ Valida: token existe + no usado + no vencido
         ├─ Válido → muestra formulario "Crear contraseña"
         └─ Inválido/Vencido → página "Enlace no disponible" con instrucción al admin
    
[Usuario: completa formulario y guarda]
    └─→ Hash de contraseña (PBKDF2-SHA256)
    └─→ DebeCambiarPassword = false
    └─→ Token marcado como Usado
    └─→ Redirige a login con mensaje de éxito
```

### Pantalla de activación (sin wireframe fino)

Una sola página (`/Cuenta/ActivarCuenta`) con:
- Campo **Nueva contraseña** + ojo para mostrar/ocultar
- Campo **Confirmar contraseña**
- Indicador visual de requisitos (se cumple o no se cumple)
- Botón **Guardar contraseña**

El diseño puede reutilizar la misma estructura visual de `/Cuenta/RestablecerPassword`.

### Correo nuevo

El correo reemplaza al actual. Estructura:

| Elemento | Contenido |
|---|---|
| Asunto | `GestionPersonal – Crea tu contraseña de acceso` |
| Saludo | Hola **[NombreCompleto]** |
| Cuerpo | "Tu cuenta fue creada. Para activar tu acceso, crea tu contraseña haciendo clic en el botón:" |
| Botón principal | **Crear contraseña** (enlace con token en query string) |
| Mensaje de seguridad | "Este enlace estará disponible durante 24 horas." |
| Footer | Estándar del sistema — generado automáticamente |

### Botón de reenvío para el administrador: "Reenviar activación"

> **Nombre propuesto:** `Reenviar activación`  
> Alternativas consideradas: "Reenviar enlace", "Enviar nuevo enlace", "Regenerar acceso" → se descartaron por ser menos explícitas sobre qué se reenvía.

En el perfil del empleado (`/Empleado/Perfil/{id}`), cuando la cuenta está en estado **Pendiente de activación**, el administrador verá el botón:

```
[ Reenviar activación ]
```

Al hacer clic:
```
[Admin: clic en "Reenviar activación"]
    └─→ POST /Empleado/RenviarActivacion/{empleadoId}
    └─→ Invalida tokens anteriores del usuario (Usado = true)
    └─→ Genera nuevo token (24h)
    └─→ Envía correo con nuevo enlace
    └─→ Muestra confirmación: "Correo de activación reenviado a [correo]"
```

El botón **solo es visible** cuando el usuario asociado tiene `DebeCambiarPassword = true` y nunca ha activado la cuenta (sin `FechaActivacion`). En cuentas activas, no aparece.

---

## 4. Rabbit Holes

### RH-01 · Tabla nueva vs. reutilizar `TokensRecuperacion`

`TokensRecuperacion` ya existe y tiene exactamente los campos necesarios. Podría parecer tentador agregarle un campo `TipoToken` y reutilizarla.

**No hacerlo.** Las reglas son distintas (24h vs. 30 min), el contexto semántico es diferente (activación != recuperación), y mezclarlas complica las queries y los reportes futuros.

**Solución:** Crear tabla `dbo.TokensActivacion` con la misma estructura que `TokensRecuperacion`. La migración SQL es mínima.

---

### RH-02 · La ruta de activación debe ser pública (sin `[Authorize]`)

`/Cuenta/ActivarCuenta` es accedida por usuarios que no tienen credenciales todavía. Debe quedar fuera del middleware de autenticación, igual que `/Cuenta/Login` y `/Cuenta/RecuperarPassword`.

Si se olvida esto, el usuario llega a una pantalla de login en lugar de la pantalla de activación, y el enlace del correo parece "no funcionar".

---

### RH-03 · Estado de la cuenta: no hay campo `EstadoCuenta` hoy

Actualmente el estado se infiere de `DebeCambiarPassword`. Para este pitch, **no se agrega un campo `EstadoCuenta` nuevo**. El estado "Pendiente de activación" se representa así:

- `DebeCambiarPassword = true` **Y** `FechaActivacion IS NULL`

La visibilidad del botón "Reenviar activación" usa esa misma condición. No se necesita migración de datos para estado — solo para la tabla de tokens.

---

### RH-04 · Contraseña temporal al crear usuario

Hoy `CrearParaEmpleadoAsync` genera una contraseña temporal con `PasswordHelper.GenerarContrasenaTemp()`. Con el nuevo flujo, la cuenta queda sin contraseña funcional hasta que el usuario active.

**Cambio requerido:** Al crear usuario, no generar contraseña temporal. Almacenar `PasswordHash` y `PasswordSalt` como `null` o bytes vacíos. El login debe rechazar el intento de acceso si la cuenta está Pendiente de activación, con mensaje: *"Tu cuenta aún no ha sido activada. Revisa tu correo."*

Este cambio afecta `UsuarioService.CrearParaEmpleadoAsync` y la lógica de autenticación en `CuentaService.ValidarCredencialesAsync`.

---

### RH-05 · El reenvío no debe generar tokens infinitos

Si el admin hace clic en "Reenviar activación" varias veces seguidas, no deben acumularse tokens activos para el mismo usuario.

**Solución:** Al generar el nuevo token, marcar como `Usado = true` todos los tokens de activación anteriores del mismo `UsuarioId` en la misma operación (dentro de la misma transacción).

---

## 5. No-Gos

Los siguientes elementos están **explícitamente fuera del alcance** de esta iteración:

- ❌ **Módulo de historial de activaciones** — no se construirá una vista para que el admin vea cuántos correos se enviaron ni cuándo.
- ❌ **Caducidad configurable del token** — el tiempo de 24 horas es fijo en código/config. No habrá interfaz para cambiarlo.
- ❌ **Notificación interna en el sistema** — el único aviso es por correo. No habrá alertas, badges ni bandejas de entrada dentro de la app.
- ❌ **Verificación en dos pasos (2FA)** — fuera del alcance de este pitch.
- ❌ **Pantalla de "Reenviar activación" masivo** — el reenvío es uno a uno desde el perfil del empleado. No habrá acción en lote desde el listado de empleados.
- ❌ **Indicador de "contraseña fuerte" en tiempo real** — el indicador visual mostrará si se cumplen los requisitos mínimos (8 chars, mayúscula, minúscula, número, especial), pero no un medidor de "fuerza" con barra de progreso.
- ❌ **Bloqueo automático de cuentas nunca activadas** — si el usuario nunca activa, la cuenta queda Pendiente indefinidamente. No hay proceso batch de limpieza en esta iteración.

---

## 6. Modelo de datos

### Nueva tabla: `dbo.TokensActivacion`

```sql
CREATE TABLE dbo.TokensActivacion (
    Id              INT IDENTITY(1,1)  NOT NULL,
    UsuarioId       INT                NOT NULL,
    Token           NVARCHAR(256)      NOT NULL,   -- SHA-256 hex (64 chars)
    FechaCreacion   DATETIME2(0)       NOT NULL DEFAULT GETUTCDATE(),
    FechaExpiracion DATETIME2(0)       NOT NULL,   -- +24 horas
    Usado           BIT                NOT NULL DEFAULT 0,
    FechaUso        DATETIME2(0)       NULL,
    CONSTRAINT PK_TokensActivacion     PRIMARY KEY (Id),
    CONSTRAINT UX_TokensActivacion_Token UNIQUE (Token),
    CONSTRAINT FK_TokensActivacion_Usuario
        FOREIGN KEY (UsuarioId) REFERENCES dbo.Usuarios(Id)
);
```

### Campo nuevo en `dbo.Usuarios`

```sql
ALTER TABLE dbo.Usuarios
    ADD FechaActivacion DATETIME2(0) NULL;
```

Se establece al momento en que el usuario guarda su contraseña exitosamente en el flujo de activación.

---

## 7. Reglas de negocio (referencia rápida)

| ID | Regla |
|---|---|
| RN-01 | Token único por generación — SHA-256 de un código alfanumérico de 12 chars generado con `RandomNumberGenerator` |
| RN-02 | Expiración: **24 horas** desde la creación |
| RN-03 | Token de un solo uso — se marca `Usado = true` al activar exitosamente |
| RN-04 | Al reenviar: tokens anteriores del mismo usuario quedan inactivos (`Usado = true`) en la misma transacción |
| RN-05 | Token enviado en la URL en texto plano; lo que se almacena en BD es el hash SHA-256 |
| RN-06 | Contraseña mínima: 8 chars, 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial (misma regla que el resto del sistema) |
| RN-07 | El botón "Reenviar activación" solo aparece si `DebeCambiarPassword = true` AND `FechaActivacion IS NULL` |
| RN-08 | Cuentas en estado "Pendiente de activación" no pueden ingresar al sistema — login rechaza con mensaje específico |

---

## 8. Casos de prueba clave

| # | Escenario | Resultado esperado |
|---|---|---|
| CP-01 | Admin crea empleado → revisar correo | Correo llega con botón "Crear contraseña" y enlace válido |
| CP-02 | Clic en enlace dentro de 24h | Muestra formulario "Crear contraseña" |
| CP-03 | Clic en enlace después de 24h | Muestra página "Enlace no disponible" |
| CP-04 | Clic en enlace ya usado | Muestra página "Enlace no disponible" |
| CP-05 | Contraseña válida → guardar | Cuenta activa, redirige a login, token marcado Usado |
| CP-06 | Contraseña inválida → guardar | Validación en cliente y servidor, no activa |
| CP-07 | Admin reenvía activación | Nuevo correo llega, token anterior queda inválido |
| CP-08 | Admin reenvía activación dos veces seguidas | Solo el último token es válido |
| CP-09 | Usuario Pendiente intenta ingresar sin activar | Login rechaza con "Tu cuenta aún no ha sido activada" |
| CP-10 | Botón "Reenviar activación" en cuenta ya activa | El botón no aparece |
