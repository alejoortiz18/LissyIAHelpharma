# Corrección de Permisos por Cargo

## Objetivo

Ajustar únicamente la matriz de permisos para los cargos definidos en el sistema, garantizando que cada rol tenga acceso solo a las funcionalidades autorizadas según su nivel jerárquico y responsabilidades operativas.

---

# Cargos Involucrados

| Id | Nombre |
|----|--------|
| 1 | Jefe de Sede |
| 2 | Farmacéutico Regente |
| 3 | Auxiliar de Farmacia |
| 4 | Auxiliar Regente |

---

# Funcionalidades del Sistema

- Ver Dashboard  
- Ver Empleados  
- Ver Todo el Personal  
- Ver Personal a su Cargo  
- Crear Personas  
- Asignar Horarios  
- Ver Horarios y Turnos de Otras Personas  
- Ver Horarios y Turnos Propios  
- Ver Horas Extras  
- Catálogo de Sistemas  
- Permisos del Personal  

---

# Reglas de Negocio

## CargoId = 1 | Jefe de Sede

Debe tener acceso total al sistema.

### Permisos:

- Ver Dashboard
- Ver Empleados
- Ver Todo el Personal
- Ver Personal a su Cargo
- Crear Personas
- Asignar Horarios
- Ver Horarios y Turnos de Otras Personas
- Ver Horarios y Turnos Propios
- Ver Horas Extras
- Catálogo de Sistemas
- Permisos del Personal
- Gestión total de personal subordinado

---

## CargoId = 2 | Farmacéutico Regente

Debe tener acceso únicamente a la gestión de su personal subordinado y su propia información.

### Permisos:

- Ver Dashboard
- Ver Personal a su Cargo
- Ver Empleados (solo subordinados)
- Ver Horarios y Turnos de Personal a Cargo
- Ver Horarios y Turnos Propios
- Asignar Horarios a subordinados
- Ver Horas Extras de subordinados
- Gestionar Horas Extras de subordinados
- Permisos del Personal subordinado
- Gestionar su propia información

### Restricciones:

- No puede ver todo el personal
- No puede gestionar personal fuera de su jerarquía
- No puede administrar configuraciones globales

---

## CargoId = 4 | Auxiliar Regente

Debe heredar exactamente los mismos permisos del Farmacéutico Regente.

### Permisos:

- Ver Dashboard
- Ver Personal a su Cargo
- Ver Empleados (solo subordinados)
- Ver Horarios y Turnos de Personal a Cargo
- Ver Horarios y Turnos Propios
- Asignar Horarios a subordinados
- Ver Horas Extras de subordinados
- Gestionar Horas Extras de subordinados
- Permisos del Personal subordinado
- Gestionar su propia información

### Restricciones:

- No puede ver todo el personal
- No puede administrar personal externo a su dependencia

---

## CargoId = 3 | Auxiliar de Farmacia

Debe tener acceso únicamente a su información personal dentro del sistema.

### Permisos:

- Ver Horarios y Turnos Propios
- Ver Horas Extras Propias
- Solicitar Permisos
- Ver Estado de Solicitudes
- Ver Historial Laboral dentro de la empresa
- Consultar información personal

### Restricciones:

- No puede ver otros empleados
- No puede crear personas
- No puede asignar horarios
- No puede aprobar permisos
- No puede ver personal a cargo
- No puede ver horas extras de terceros
- No puede acceder al dashboard administrativo

---

# Matriz Resumida de Permisos

| Funcionalidad | Jefe Sede | Regente | Aux. Farmacia | Aux. Regente |
|--------------|-----------|---------|---------------|--------------|
| Dashboard | Sí | Sí | No | Sí |
| Ver empleados | Sí | Solo subordinados | No | Solo subordinados |
| Ver todo personal | Sí | No | No | No |
| Ver personal a cargo | Sí | Sí | No | Sí |
| Crear personas | Sí | No | No | No |
| Asignar horarios | Sí | Sí | No | Sí |
| Ver horarios terceros | Sí | Solo subordinados | No | Solo subordinados |
| Ver horario propio | Sí | Sí | Sí | Sí |
| Ver horas extras | Sí | Subordinados y propias | Propias | Subordinados y propias |
| Catálogo sistemas | Sí | No | No | No |
| Permisos personal | Sí | Sí subordinados | Solicitar únicamente | Sí subordinados |

---

# Validaciones Técnicas Requeridas

## Backend

- Validar permisos por `CargoId`
- Validar jerarquía por `JefeId`
- Restringir consultas masivas según rol
- Proteger endpoints por autorización

## Frontend

- Ocultar menús no permitidos
- Mostrar opciones según rol autenticado
- Restringir botones de edición según permisos

---

# Resultado Esperado

El sistema deberá permitir que cada usuario visualice y gestione únicamente la información correspondiente a su rol y nivel jerárquico, evitando accesos indebidos y fortaleciendo la seguridad operativa.