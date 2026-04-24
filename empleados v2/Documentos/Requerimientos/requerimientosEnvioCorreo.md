# Análisis de Requerimiento – Mensajería y Notificaciones del Sistema de Gestión de Personal

## Objetivo

Definir todos los mensajes, correos electrónicos, notificaciones internas y eventos automáticos que debe generar el sistema de gestión de personal, alineado con buenas prácticas de arquitectura en capas (.NET Layered Architecture), trazabilidad, seguridad y mantenibilidad.

---

## Fuentes Base a Revisar

* Analisis de requerimiento para el sistema de gestion personal.md
* plan-permisos-roles
* gestionrh-schema.sql
* Documentos funcionales previos del proyecto

> Nota: Este documento consolida requerimientos explícitos y puntos de control evidentes. Requiere validación final contra modelo real de BD.

---

# Arquitectura Recomendada (.NET Layered)

## Capas sugeridas

* Presentation (MVC / API)
* Application (Casos de uso / Servicios)
* Domain (Entidades / Reglas)
* Infrastructure (Email, SMS, DB, Queue)
* Shared (DTOs, constantes, plantillas)

## Componentes de mensajería

* INotificationService
* IEmailService
* ITemplateRenderer
* IUserPreferenceService
* IAuditService
* Background Job Processor (Hangfire / Quartz / Worker Service)

---

# Tipos de Mensajes del Sistema

## 1. Seguridad y Acceso

* Creación de cuenta
* Activación de cuenta
* Restablecimiento de contraseña
* Cambio exitoso de contraseña
* Bloqueo por intentos fallidos
* Desbloqueo de cuenta
* Inicio de sesión desde nuevo dispositivo (opcional)
* Cambio de correo electrónico

## 2. Gestión de Personal

* Asignación de horario
  n- Modificación de horario
* Cancelación de turno
* Cambio de jefe inmediato
* Cambio de sede
* Cambio de cargo
* Registro de nuevo empleado
* Inactivación de empleado

## 3. Solicitudes

* Solicitud creada
* Solicitud recibida por aprobador
* Solicitud escalada a jefe apoyo
* Solicitud aprobada
* Solicitud rechazada
* Solicitud devuelta con observaciones
* Solicitud cancelada por solicitante
* Solicitud vencida sin respuesta

## 4. Novedades Operativas

* Incapacidad registrada
* Vacaciones aprobadas
* Permiso aprobado/rechazado
* Horas extra aprobadas
* Ausencia reportada

## 5. Sistema

* Error crítico administrativo
* Mantenimiento programado
* Confirmación de actualización de datos
* Resumen diario/semanal pendiente de aprobaciones

---

# Reglas de Negocio Solicitadas

## Regla 1: Solicitud creada por Auxiliar

Cuando un Auxiliar genera una solicitud:

* Enviar correo al jefe inmediato.
* Enviar correo al jefe apoyo.
* Crear notificación interna a ambos.
* Registrar auditoría.

## Regla 2: Asignación o reporte realizado por jefe

Cuando un jefe asigna horario o reporta novedad a un usuario:

* Enviar correo al usuario afectado.
* Enviar copia o confirmación al jefe que ejecutó la acción.
* Crear notificación interna.

## Regla 3: Aprobación de evento de Auxiliar

Cuando un jefe aprueba un evento:

* Enviar correo al auxiliar indicando aprobación.
* Detallar fecha, tipo, observación y aprobador.

---

# Flujo de Restablecimiento de Contraseña

## Paso 1. Solicitud

Usuario ingresa correo electrónico.

## Paso 2. Generación segura

Sistema genera:

* Token único aleatorio
* Fecha de expiración (ej. 30 minutos)
* Estado: Pendiente
* Hash del token almacenado (recomendado)

## Paso 3. Envío correo

Asunto: Restablecimiento de contraseña
Contenido:

* Nombre del usuario
* Botón validar cuenta
* Tiempo de vigencia
* Mensaje de seguridad

## Paso 4. Validación enlace

Al hacer clic:

* Sistema recibe token
* Valida existencia
* Valida expiración
* Valida uso único

## Paso 5. Resultado

### Si válido:

Mostrar formulario nueva contraseña.

### Si inválido:

Mostrar:

* Token vencido
* Token inválido
* Token usado
* Solicite una nueva recuperación

## Paso 6. Cambio exitoso

* Actualizar hash de contraseña + salt
* Invalidar token
* Enviar correo confirmación de cambio exitoso

---

# Plantillas de Mensajes

## Creación de cuenta

Asunto: Bienvenido al sistema
Mensaje: Su cuenta fue creada exitosamente.

## Solicitud creada a jefe

Asunto: Nueva solicitud pendiente de revisión
Mensaje: El usuario {Empleado} registró una solicitud {TipoSolicitud}.

## Solicitud aprobada

Asunto: Solicitud aprobada
Mensaje: Su solicitud {TipoSolicitud} fue aprobada por {Aprobador}.

## Solicitud rechazada

Asunto: Solicitud rechazada
Mensaje: Su solicitud fue rechazada. Motivo: {Observacion}.

## Nuevo horario

Asunto: Nueva asignación de horario
Mensaje: Se le asignó horario para {Fecha} turno {Turno}.

## Horario modificado

Asunto: Cambio de horario
Mensaje: Su horario fue actualizado.

## Restablecer contraseña

Asunto: Recuperación de contraseña
Mensaje: Use el botón para continuar el proceso.

## Contraseña actualizada

Asunto: Contraseña cambiada exitosamente
Mensaje: Si no realizó esta acción contacte soporte.

---

# Eventos Detectables Adicionales desde Base de Datos (Validar Schema)

## Tablas típicas a revisar

* Empleados
* Usuarios
* Roles / Cargos
* Solicitudes
* Horarios
* Turnos
* Sedes
* Auditoria
* TokensRecuperacion
* Notificaciones

## Correos adicionales posibles

* Cumpleaños (opcional)
* Contrato próximo a vencer
* Documento pendiente por actualizar
* Usuario sin marcar asistencia
* Jefe con pendientes sin aprobar
* Recordatorio vacaciones disponibles

---

# Buenas Prácticas Técnicas

## Seguridad

* No enviar contraseñas por correo.
* Tokens firmados o aleatorios criptográficos.
* Expiración corta.
* Rate limit recuperación.
* Auditoría completa.

## Código

* Templates versionados.
* Cola asíncrona para emails.
* Reintentos controlados.
* Logs estructurados.
* Idempotencia de eventos.

## Review Checklist

* ¿Existe doble envío?
* ¿Valida destinatarios activos?
* ¿Respeta jerarquía real?
* ¿Tiene trazabilidad?
* ¿Plantilla parametrizada?
* ¿Sin datos sensibles expuestos?

---

# Tabla Resumen de Destinatarios

| Evento             | Destinatario Principal | Copia       |
| ------------------ | ---------------------- | ----------- |
| Solicitud auxiliar | Jefe inmediato         | Jefe apoyo  |
| Horario asignado   | Empleado               | Jefe emisor |
| Evento aprobado    | Auxiliar               | —           |
| Recuperación clave | Usuario                | —           |
| Cambio cargo       | Empleado               | RRHH        |
| Nuevo empleado     | Empleado               | Jefe        |

---

# Pendientes para Cierre Final

1. Confirmar nombres reales de tablas en gestionrh-schema.sql.
2. Confirmar si existe jefe apoyo como campo directo.
3. Confirmar canales: correo, SMS, WhatsApp, push.
4. Confirmar idioma y branding de plantillas.
5. Confirmar SLA de expiración tokens.
