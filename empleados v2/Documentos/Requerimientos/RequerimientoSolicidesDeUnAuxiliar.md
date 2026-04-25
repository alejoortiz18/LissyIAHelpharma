#requerimiento-autogestion-auxiliar-farmacia-eventos-solicitudes

## Objetivo

Implementar funcionalidad para que un usuario con perfil **Auxiliar de Farmacia** cuyo **CargoId = 3** pueda gestionar sus propios eventos o solicitudes dentro del sistema, conservando completamente la experiencia visual actual, el estándar gráfico existente y sin afectar otras funcionalidades ya operativas.

---

# Alcance Funcional

## Perfil autorizado

Únicamente usuarios con:

```text
CargoId = 3
Nombre Rol = Auxiliar de Farmacia

Funcionalidades requeridas
1. Registrar sus propios eventos o solicitudes

El usuario podrá crear solicitudes personales tales como:

Permisos
Novedades
Solicitud de cambio de turno
Incapacidad
Vacaciones
Eventos administrativos
Otras categorías definidas por parametrización
Campos mínimos sugeridos
Campo	Tipo
Tipo Solicitud	Lista
Fecha Solicitud	Fecha
Fecha Inicio	Fecha
Fecha Fin	Fecha
Motivo	Texto
Observaciones	Texto
Adjuntos	Opcional
Estado Inicial	Pendiente
2. Consultar sus propias solicitudes

Debe visualizar únicamente sus registros.

Columnas mínimas:

Item	Tipo	Fecha Solicitud	Estado	Aprobado Por	Fecha Aprobación	Observación
3. Visualizar aprobador

Debe mostrar claramente:

Nombre del jefe aprobador
Cargo del aprobador (opcional)
Fecha aprobación
Estado actual

Ejemplo:

Aprobado por: María Gómez
Fecha: 2026-04-25 09:35 AM
Estado: Aprobado
4. Estados permitidos
Pendiente
Aprobado
Rechazado
Cancelado
En revisión
Reglas de negocio
Seguridad

El usuario Auxiliar:

✅ Solo puede ver sus propias solicitudes
✅ Solo puede registrar solicitudes propias
✅ No puede aprobar solicitudes
✅ No puede modificar solicitudes ajenas
✅ No puede visualizar solicitudes de otros empleados

Integridad
Toda solicitud debe guardar usuario creador.
Registrar fecha creación.
Registrar IP / auditoría si existe módulo log.
Registrar aprobador cuando cambie estado.
UI / UX Obligatorio
Mantener diseño actual del sistema

Se debe conservar:

Colores actuales
Tipografía actual
Menú actual
Iconografía existente
Responsive actual
Estructura visual actual
Muy importante

No rediseñar vistas existentes.

No cambiar navegación global.

No alterar estilos maestros.

Tablas

Las tablas nuevas deben usar exactamente el mismo estándar visual usado en otros formularios del sistema.

Mantener:
Mismo ancho de columnas
Misma paginación
Mismo buscador
Mismo estilo de encabezados
Mismos botones de acciones
Mismos íconos
Misma separación y márgenes
Mismo formato de fechas
Compatibilidad

Debe asegurarse que esta implementación:

✅ No dañe otras vistas
✅ No rompa CSS existente
✅ No afecte JS global
✅ No altere layouts maestros
✅ No modifique permisos existentes de otros cargos

Backend sugerido
Tablas posibles
SolicitudesEmpleado
SolicitudEstadoHistorial
SolicitudAdjuntos
Validaciones
No permitir fechas inválidas.
No permitir motivo vacío.
No permitir duplicados si aplica regla.
Validar sesión activa.
Validar CargoId = 3.
Pruebas mínimas
Caso	Resultado Esperado
Auxiliar crea solicitud	Correcto
Ve solo sus solicitudes	Correcto
Ve aprobador	Correcto
Ve fechas	Correcto
Otro rol no autorizado	Según permisos
Diseño intacto	Correcto
Otras vistas sin daño	Correcto
Prioridad

Alta

Entrega esperada

Módulo estable, visualmente integrado al sistema actual y sin impacto colateral.