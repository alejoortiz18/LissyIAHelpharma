#requerimiento-flujo-aprobacion-solicitudes-jefes

## Objetivo

Implementar flujo de aprobación y gestión de solicitudes donde, al momento en que un usuario crea una solicitud, su jefe inmediato tenga la capacidad de aprobarla o rechazarla. Adicionalmente ciertos cargos estratégicos podrán visualizar solicitudes aprobadas y modificar decisiones previamente tomadas.

---

# Alcance Funcional

## Evento inicial

Cuando cualquier usuario registre una solicitud en el sistema:

- La solicitud debe quedar en estado **Pendiente**.
- Debe asociarse automáticamente al jefe inmediato configurado del empleado.
- El jefe inmediato deberá verla en su bandeja de aprobaciones.

---

# Cargos con capacidad de aprobación inicial

Los siguientes cargos podrán aprobar o rechazar solicitudes de su personal a cargo:
## 3. Analista servicios farmacéuticos

## 1. Director Técnico

## 2. Auxiliar Regente

Estos cargos actuarán como jefes inmediatos según estructura jerárquica del empleado.

---

# Acciones permitidas al jefe inmediato

Cada solicitud pendiente deberá permitir:

- Aprobar solicitud
- Rechazar solicitud
- Ver detalle completo
- Registrar observación de aprobación o rechazo

---

# Cambio de Estado

## Estados posibles

-- ver documentos y requisitos
---

# Cargo con visualización global

## Analista de Servicios Farmacéuticos

Debe poder visualizar todos los permisos o solicitudes que se encuentren:

- Aprobadas
- Rechazadas
- Pendientes
- Reabiertas

Sin restricción por sede o jefe inmediato, salvo que exista política adicional.

---

# Reversión de decisiones

Los siguientes tres cargos podrán modificar decisiones anteriores:

- Director Técnico
- Auxiliar Regente
- Analista de Servicios Farmacéuticos

## Escenarios permitidos

### Si estaba aprobada:

- Puede deshacer aprobación
- Cambiar a Pendiente
- Cambiar a Rechazada

### Si estaba rechazada:

- Puede cambiar a Aprobada
- Puede cambiar a Pendiente

### Si estaba pendiente:

- Puede aprobar
- Puede rechazar

---

# Auditoría obligatoria

Toda modificación debe registrar:

- Usuario que realizó acción
- Cargo del usuario
- Fecha y hora
- Estado anterior
- Estado nuevo
- Observación obligatoria al reversar decisión

---

# Bandejas requeridas

## Bandeja jefe inmediato

Mostrar solicitudes de subordinados:

- Pendientes
- En revisión
- Historial

## Bandeja analista servicios farmacéuticos

Mostrar todas las solicitudes:

- Filtro por sede
- Filtro por empleado
- Filtro por fecha
- Filtro por estado

---

# UI / UX Obligatorio

Se debe mantener completamente el diseño actual del sistema:

- Misma apariencia visual
- Mismos colores
- Misma estructura de tablas
- Mismos botones
- Mismos íconos
- Mismo estándar responsive

No alterar vistas existentes ni romper funcionalidades actuales.

---

# Tablas y listados

Las tablas deben conservar el mismo estándar utilizado en otros módulos:

- Buscador
- Paginación
- Ordenamiento por columnas
- Formato de fechas actual
- Acciones laterales o botones estándar

---

# Reglas de Seguridad

- Solo cargos autorizados pueden aprobar o rechazar.
- Solo cargos autorizados pueden reversar decisiones.
- Un usuario común solo ve sus propias solicitudes.
- La jerarquía debe respetarse según jefe configurado.

---

# Validaciones mínimas

| Caso | Resultado Esperado |
|------|--------------------|
| Usuario crea solicitud | Queda pendiente |
| Jefe inmediato aprueba | Estado aprobada |
| Jefe inmediato rechaza | Estado rechazada |
| Analista visualiza todas | Correcto |
| Reversar aprobación | Correcto |
| Cambiar rechazo a aprobación | Correcto |
| Auditoría registrada | Correcto |
| UI intacta | Correcto |

---

# Prioridad

Alta

---

# Resultado esperado

Flujo completo, trazable, jerárquico y alineado con la operación real del sistema.

---

# Decisiones de Implementación Confirmadas

| Pregunta | Decisión |
|---|---|
| ¿Regente puede aprobar? | **Sí** — igual que AuxiliarRegente |
| ¿Tabla de auditoría nueva? | **No** — `AutorizadoPor` (último aprobador/rechazador), `MotivoAnulacion` (observación), `FechaModificacion` (fecha) |
| ¿Dónde está la bandeja del jefe? | **En `/EventoLaboral`** — dropdown/botón para cambiar estado |
| ¿Exportación? | **No aplica** — eliminado del alcance |
| ¿Roles que pueden aprobar/rechazar/reversar? | `Regente`, `AuxiliarRegente`, `DirectorTecnico`, `Analista` |