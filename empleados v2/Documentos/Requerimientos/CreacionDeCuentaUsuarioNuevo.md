# Requerimiento Funcional  
# Activación de Cuenta y Creación de Contraseña para Usuarios Nuevos

---

## Objetivo

Optimizar el proceso de creación de usuarios nuevos en el sistema **GestionPersonal**, reemplazando el correo actual informativo por una experiencia más segura, moderna y orientada al autoservicio.

Cuando se cree un usuario nuevo, el sistema deberá enviar un correo electrónico al usuario con un enlace seguro para **crear su contraseña inicial**, permitiendo activar su cuenta sin intervención manual.

---

# Situación Actual

Actualmente, al crear un usuario nuevo, el sistema envía un correo indicando que la cuenta fue creada y que posteriormente el usuario deberá crear contraseña al ingresar.

Esto genera fricción en la experiencia de usuario y no aprovecha un flujo moderno de activación inmediata.

---

# Nuevo Flujo Requerido (UX/UI Mejorado)

## 1. Creación de Usuario

Cuando el administrador registre un nuevo usuario:

- Se crea la cuenta en estado **Pendiente de Activación**
- Se genera un **Token Único de Seguridad**
- Se registra fecha y hora de expiración del token (**24 horas**)
- Se envía correo automático al usuario

---

# Diseño del Correo (Nuevo)

## Asunto:

**Bienvenido a GestionPersonal – Activa tu cuenta**

---

## Cuerpo del Correo

Hola **[NombreUsuario]**,

Tu cuenta en **GestionPersonal** ha sido creada exitosamente.

Para activar tu acceso, necesitas crear tu contraseña inicial haciendo clic en el siguiente botón:

### Botón principal:

**[ Crear Contraseña ]**

(Enlace seguro con token)

---

### Mensaje secundario:

Por seguridad, este enlace estará disponible durante **24 horas**.

Si no realizas el proceso dentro de este tiempo, deberás solicitar una nueva activación al administrador.

---

### Footer:

Este correo fue generado automáticamente por el sistema.  
No respondas este mensaje.

---

# Reglas de Negocio

## RN001 - Token Seguro

Al crear usuario nuevo, el sistema debe generar:

- Token único
- Asociado al usuario
- No reutilizable
- Fecha de vencimiento = 24 horas

---

## RN002 - Vigencia del Enlace

El enlace enviado por correo tendrá duración máxima de:

**1 día calendario (24 horas)**

---

## RN003 - Validación al dar clic

Cuando el usuario pulse **Crear Contraseña**:

El sistema validará:

- Token existe
- Token pertenece al usuario
- Token no usado
- Token no vencido

---

## RN004 - Token Válido

Si el token es válido:

Mostrar pantalla:

# Crear Contraseña

Campos:

- Nueva contraseña
- Confirmar contraseña

Botón:

**Guardar Contraseña**

---

## RN005 - Token Inválido o Expirado

Si el token no cumple validación:

Mostrar pantalla amigable:

# Enlace no disponible

Este enlace ya expiró o no es válido.

Por favor comunícate con el administrador para generar una nueva solicitud de creación de contraseña.

Botón opcional:

**Volver al inicio**

---

## RN006 - Activación Exitosa

Cuando el usuario cree contraseña correctamente:

- Marcar cuenta como **Activa**
- Marcar token como **Usado**
- Registrar fecha activación
- Permitir inicio de sesión inmediato

---

## RN007 - Seguridad de Contraseña

Aplicar reglas mínimas:

- Mínimo 8 caracteres
- Una mayúscula
- Una minúscula
- Un número
- Un carácter especial

---

# Estados del Usuario

| Estado | Descripción |
|--------|-------------|
| Pendiente Activación | Usuario creado sin contraseña |
| Activo | Usuario ya creó contraseña |
| Bloqueado | Definido por administración |

---

# Experiencia UX/UI Recomendada

## Pantalla Crear Contraseña

Diseño limpio con:

- Logo empresa
- Mensaje de bienvenida
- Indicador de seguridad de contraseña
- Mostrar/Ocultar contraseña
- Confirmación visual de requisitos cumplidos

---

## Mensaje Éxito

# Contraseña creada exitosamente

Tu cuenta ya está activa. Ahora puedes iniciar sesión.

Botón:

**Ir al Login**

---

# Base de Datos Sugerida

## Tabla Usuarios

Agregar / validar campos:

- PasswordHash
- PasswordSalt
- EstadoCuenta
- FechaActivacion

## Tabla TokensActivacion

| Campo |
|------|
| Id |
| UsuarioId |
| Token |
| FechaCreacion |
| FechaExpiracion |
| Usado |
| FechaUso |

---

# Casos de Prueba

## Caso 1

Crear usuario nuevo → llega correo con botón.

## Caso 2

Clic dentro de 24 horas → permite crear contraseña.

## Caso 3

Clic después de 24 horas → mensaje expirado.

## Caso 4

Token usado nuevamente → inválido.

## Caso 5

Contraseña válida → activa usuario.

---

# Beneficios

- Mejor experiencia de usuario
- Menos soporte manual
- Mayor seguridad
- Activación inmediata
- Trazabilidad completa

---

# Prioridad

**Alta**

---

# Nombre sugerido del desarrollo

**Modulo Activación Inicial de Usuarios por Correo**