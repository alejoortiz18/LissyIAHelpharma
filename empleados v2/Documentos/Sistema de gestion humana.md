# 📘 Sistema de Gestión de Personal

## 1. Propósito del Sistema
La aplicación tiene como objetivo centralizar la administración de los empleados y el control operativo de sus actividades diarias, permitiendo un seguimiento riguroso de su ciclo de vida dentro de la organización.

---

## 2. Módulos Funcionales

### 👤 Gestión de Empleados
Permite administrar la información personal y profesional de los trabajadores:
* **Registro Completo:** Captura de datos personales, identificación, contacto y ubicación física (Sede).
* **Estructura Organizacional:** Asignación de cargos, tipos de contrato y definición de jerarquías (Jefes inmediatos).
* **Control de Estado:** Seguimiento del personal activo e inactivo, incluyendo el registro de motivos de retiro y fechas de desvinculación.

### 📄 Control de Eventos Laborales
Gestiona las novedades y situaciones administrativas del personal:
* **Registro de Novedades:** Gestión de vacaciones, incapacidades y permisos.
* **Regla de Evento Único:** El sistema garantiza que un empleado solo pueda tener un estado activo a la vez.
* **Gestión de Soportes:** Posibilidad de adjuntar documentos o evidencias que justifiquen cada evento.
* **Auditoría de Autorización:** Registro obligatorio de quién autorizó cada movimiento.

### 🕒 Administración de Jornadas y Horarios
Controla la disponibilidad de tiempo del equipo:
* **Programación de Turnos:** Definición de horas de entrada y salida.
* **Flexibilidad:** Configuración de trabajo para fines de semana y días festivos.
* **Responsables:** Identificación del personal que realiza la programación de los horarios.

### ⏱️ Gestión de Horas Extras
Módulo para el control del tiempo suplementario:
* **Reporte de Tiempo:** Registro exacto de fechas y cantidad de horas adicionales trabajadas.
* **Justificación y Aprobación:** Cada registro requiere un motivo y debe pasar por un proceso de aprobación mediante estados de solicitud.

---

## 3. Reglas de Negocio Principales
* **Integridad Institucional:** Todo empleado debe pertenecer obligatoriamente a una sede y tener un cargo definido.
* **Transparencia:** Las solicitudes de horas extras y eventos deben estar vinculadas a un estado (Aprobado, Pendiente, etc.).
* **Seguridad:** Acceso restringido mediante credenciales cifradas para la protección de la información del personal.

---

## 4. Beneficios Operativos
* Visibilidad en tiempo real de quién está laborando y quién está en permiso.
* Historial completo de movimientos por empleado.
* Control administrativo sobre el gasto de horas extras y cumplimiento de horarios.