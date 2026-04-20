# Reglas de Negocio — Sistema de Administración de Empleados

## 🔐 Seguridad
- Las contraseñas se almacenan usando:
  - password_hash
  - password_salt
- Nunca se guarda la contraseña en texto plano

---

## 👤 Unicidad de empleados
- No puede existir:
  - mismo TipoIdentificacion + NumeroIdentificacion
- Validar:
  - Base de datos (índice único)
  - Backend

---

## 📧 Correo electrónico
- Obligatorio
- Formato válido
- Único en el sistema

---

## 📅 Coherencia de fechas
- FechaNacimiento <= hoy
- FechaDesvinculacion >= FechaIngreso
- Eventos:
  - FechaFin >= FechaInicio

---

## 🚫 Estado del empleado
Si está Inactivo:
- No puede:
  - Registrar eventos
  - Registrar horas extras
  - Cambiar turno
- Solo consulta

---

## 🧑‍💼 Roles del sistema
- Empleado
- Regente
- Jefe

---

## 🔐 Control de acceso
- Empleado → solo su info
- Regente → su equipo
- Jefe → todo

---

## 🗑️ Soft Delete
Todas las tablas deben tener:
- IsActive
- FechaInactivacion

---

## 🧱 Arquitectura
- Controller → orquesta
- Service → lógica
- Repository → datos
- ❌ NO lógica en controllers

---

## 🏢 Estructura organizacional
- Cada sede:
  - 1 solo regente activo
- Todo empleado pertenece a una sede

---

## 🔗 Jerarquía obligatoria
- Todo empleado tiene jefe
- Excepto:
  - Rol Jefe

---

## 🧠 Lógica de responsable

### ObtenerResponsable(empleado):
1. Si tiene jefe → usar jefe
2. Si no:
   - usar regente de sede
3. Si no:
   - usar jefe general

👉 Siempre debe existir responsable

---

## ⏱️ Turnos
- Un empleado:
  - solo 1 turno activo
- Mantener historial

---

## ⚡ Horas extras

### Reglas

#### 1. Unicidad
- 1 registro por empleado por día

#### 2. Disponibilidad
No permitir si tiene evento activo:
- Vacaciones
- Incapacidad
- Permiso

#### 3. Validación
- Horas > 0
- Horas <= 24

#### 4. Aprobación
- Regente → aprueba su equipo
- Jefe → supervisa y anula

#### 5. Anulación
Requiere:
- Motivo
- Usuario
- Fecha

#### 6. Concurrencia
Validar estado antes de aprobar

---

## 📅 Evento activo
Un evento es activo si:
- FechaInicio <= hoy <= FechaFin
- Estado != Anulado

---

## 📧 Eventos + Email

### Flujo
1. Validar evento
2. Enviar correo (SMTP)
3. Adjuntar archivo en memoria
4. Si falla:
   - ❌ NO guardar evento
5. Si OK:
   - Guardar
   - Registrar log

---

## 📬 Email Log

Campos:
- FechaEnvio
- EmpleadoId
- Tipo
- Destinatarios
- Estado
- Error
- NombreArchivo
- Usuario

---

## ⚙️ Servicios requeridos
- EmpleadoService
- EventoService
- HoraExtraService
- EmailService
- EmailLogService