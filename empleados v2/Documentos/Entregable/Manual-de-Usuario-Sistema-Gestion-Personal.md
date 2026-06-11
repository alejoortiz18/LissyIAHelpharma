# Manual de Usuario — Sistema de Gestión de Personal

> **Versión:** 1.0  
> **Fecha:** Mayo 2026  
> **Sistema:** GestionPersonal  
> **Dirigido a:** Todos los usuarios del sistema

---

## Tabla de Contenido

1. [Introducción](#1-introducción)
2. [Roles y Permisos](#2-roles-y-permisos)
3. [Acceso al Sistema](#3-acceso-al-sistema)
   - 3.1 [Iniciar Sesión](#31-iniciar-sesión)
   - 3.2 [Cambiar Contraseña (Primer Ingreso)](#32-cambiar-contraseña-primer-ingreso)
   - 3.3 [Recuperar Contraseña Olvidada](#33-recuperar-contraseña-olvidada)
   - 3.4 [Cerrar Sesión](#34-cerrar-sesión)
4. [Dashboard — Panel Principal](#4-dashboard--panel-principal)
5. [Módulo de Empleados](#5-módulo-de-empleados)
   - 5.1 [Ver Lista de Empleados Activos](#51-ver-lista-de-empleados-activos)
   - 5.2 [Registrar un Nuevo Empleado](#52-registrar-un-nuevo-empleado)
   - 5.3 [Ver y Editar el Perfil de un Empleado](#53-ver-y-editar-el-perfil-de-un-empleado)
   - 5.4 [Historial del Empleado](#54-historial-del-empleado)
   - 5.5 [Desvincular un Empleado](#55-desvincular-un-empleado)
   - 5.6 [Empleados Desvinculados](#56-empleados-desvinculados)
   - 5.7 [Cambio de Tipo de Vinculación (Temporal → Directo)](#57-cambio-de-tipo-de-vinculación-temporal--directo)
6. [Módulo de Eventos Laborales](#6-módulo-de-eventos-laborales)
   - 6.1 [Ver Eventos Laborales](#61-ver-eventos-laborales)
   - 6.2 [Registrar un Evento (Vacaciones, Incapacidad o Permiso)](#62-registrar-un-evento-vacaciones-incapacidad-o-permiso)
   - 6.3 [Aprobar, Rechazar o Anular un Evento](#63-aprobar-rechazar-o-anular-un-evento)
   - 6.4 [Cálculo del Saldo de Vacaciones](#64-cálculo-del-saldo-de-vacaciones)
7. [Módulo de Horas Extras](#7-módulo-de-horas-extras)
   - 7.1 [Ver Horas Extras](#71-ver-horas-extras)
   - 7.2 [Registrar una Solicitud de Horas Extras](#72-registrar-una-solicitud-de-horas-extras)
   - 7.3 [Aprobar o Rechazar una Solicitud](#73-aprobar-o-rechazar-una-solicitud)
   - 7.4 [Anular una Solicitud Aprobada](#74-anular-una-solicitud-aprobada)
8. [Módulo de Horarios y Turnos](#8-módulo-de-horarios-y-turnos)
   - 8.1 [Ver Plantillas y Asignaciones](#81-ver-plantillas-y-asignaciones)
   - 8.2 [Crear una Plantilla de Turno](#82-crear-una-plantilla-de-turno)
   - 8.3 [Asignar un Turno a un Empleado](#83-asignar-un-turno-a-un-empleado)
9. [Módulo de Mis Solicitudes (Operario y Direccionador)](#9-módulo-de-mis-solicitudes-operario-y-direccionador)
   - 9.1 [Ver Mis Solicitudes](#91-ver-mis-solicitudes)
   - 9.2 [Registrar una Nueva Solicitud](#92-registrar-una-nueva-solicitud)
10. [Panel de Catálogos — Datos Maestros](#10-panel-de-catálogos--datos-maestros)
    - 10.1 [Gestionar Sedes](#101-gestionar-sedes)
    - 10.2 [Gestionar Cargos](#102-gestionar-cargos)
    - 10.3 [Gestionar Empresas Temporales](#103-gestionar-empresas-temporales)
11. [Mi Perfil de Usuario](#11-mi-perfil-de-usuario)
12. [Preguntas Frecuentes y Errores Comunes](#12-preguntas-frecuentes-y-errores-comunes)

---

## 1. Introducción

El **Sistema de Gestión de Personal** es una aplicación web accesible desde la red interna (intranet) de la empresa. Centraliza toda la administración del personal en un único lugar: desde el registro de empleados y el control de novedades laborales, hasta la gestión de horarios y horas extras.

**¿Para qué sirve el sistema?**

- Registrar y consultar la información completa de cada empleado.
- Llevar el control de eventos laborales: vacaciones, incapacidades y permisos.
- Administrar los turnos de trabajo de cada sede.
- Gestionar y aprobar solicitudes de horas extras.
- Consultar el historial completo de cada empleado en un solo lugar.
- Mantener los datos maestros actualizados (sedes, cargos, empresas temporales).

**Requisitos para usar el sistema:**

- Contar con un usuario y contraseña proporcionados por el Director Técnico o Administrador.
- Tener acceso a la red interna de la empresa.
- Usar un navegador web actualizado (Chrome, Edge o Firefox recomendados).

---

## 2. Roles y Permisos

El sistema cuenta con **siete roles**. Cada usuario tiene asignado uno de ellos, y ese rol determina qué puede ver y qué acciones puede realizar dentro del sistema.

| Rol | Descripción General |
|---|---|
| **Administrador** | Acceso completo. Gestiona catálogos, ve todo el personal de todas las sedes. |
| **Director Técnico** | Acceso a empleados y eventos de toda su línea jerárquica. Puede gestionar catálogos. |
| **Analista** | Visibilidad global de empleados, eventos y horas extras de todas las sedes. No puede crear usuarios ni gestionar catálogos. |
| **Regente** | Gestión de empleados, eventos, horas extras y turnos de su sede y subordinados directos. |
| **Auxiliar de Regente** | Mismos permisos que el Regente dentro de su sede y su equipo. |
| **Direccionador** | Puede registrar y consultar sus propias solicitudes de novedad. Ve sus propias horas extras. |
| **Operario** | Puede registrar y consultar sus propias solicitudes de novedad. Ve sus propias horas extras. |

### Tabla Detallada de Permisos por Módulo

| Acción | Administrador | Director Técnico | Analista | Regente | Aux. Regente | Direccionador | Operario |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Dashboard con KPIs** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Ver empleados (todas las sedes)** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Ver empleados (su sede / su equipo)** | ✅ | ✅ | ✅ | ✅ | ✅ | Solo perfil propio | Solo perfil propio |
| **Crear nuevo empleado** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Editar empleado** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Desvincular empleado** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Ver eventos laborales** | ✅ | ✅ (su jerarquía) | ✅ | ✅ (su equipo) | ✅ (su equipo) | ❌ | ❌ |
| **Registrar eventos laborales** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Aprobar / rechazar eventos** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Ver horas extras** | ✅ | ✅ | ✅ | ✅ (su equipo) | ✅ (su equipo) | Solo propias | Solo propias |
| **Registrar horas extras** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Aprobar / rechazar horas extras** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Ver y crear plantillas de turno** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Asignar turnos** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Mis Solicitudes (novedad propia)** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Gestionar catálogos (sedes, cargos, etc.)** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

> **Nota sobre visibilidad:** Los roles Regente y Auxiliar de Regente solo ven a sus subordinados directos dentro de su sede; no ven al personal de otras sedes ni a empleados que no dependan de ellos jerárquicamente.

---

## 3. Acceso al Sistema

### 3.1 Iniciar Sesión

Al ingresar a la dirección del sistema en el navegador, aparece la pantalla de inicio de sesión.

**Pasos para iniciar sesión:**

1. Abrir el navegador e ingresar la dirección del sistema (proporcionada por el área de TI).
2. En el campo **Correo electrónico**, digitar el correo corporativo asignado (p. ej. `nombre.apellido@empresa.com`).
3. En el campo **Contraseña**, digitar la contraseña.
4. Hacer clic en el botón **Ingresar**.

**Resultado esperado:** El sistema lo redirige automáticamente al Dashboard principal.

**Si las credenciales son incorrectas:** Aparece un mensaje en rojo: *"Credenciales inválidas."* Verifique que el correo y la contraseña estén escritos correctamente. Las contraseñas distinguen mayúsculas y minúsculas.

> **Importante:** Después de **30 minutos sin actividad**, la sesión se cierra automáticamente por seguridad. Si esto ocurre, el sistema lo redirige a la pantalla de inicio de sesión.

---

### 3.2 Cambiar Contraseña (Primer Ingreso)

Cuando el Director Técnico o Administrador crea su cuenta, el sistema le asigna una **contraseña temporal**. Al iniciar sesión por primera vez, el sistema obliga a cambiarla antes de continuar.

**Pasos:**

1. Iniciar sesión con las credenciales temporales proporcionadas.
2. El sistema lo redirige automáticamente a la pantalla **Cambiar Contraseña**.
3. En el campo **Contraseña actual**, digitar la contraseña temporal recibida.
4. En el campo **Nueva contraseña**, digitar la contraseña que desea establecer.
5. En el campo **Confirmar contraseña**, digitar nuevamente la nueva contraseña.
6. Hacer clic en **Guardar**.

**Resultado esperado:** La contraseña queda actualizada y el sistema lo redirige al Dashboard.

> Las contraseñas se almacenan de forma cifrada. El sistema nunca guarda ni puede revelar su contraseña en texto plano.

---

### 3.3 Recuperar Contraseña Olvidada

Si olvidó su contraseña, puede restablecerla a través de su correo electrónico.

**Pasos:**

1. En la pantalla de inicio de sesión, hacer clic en **"¿Olvidaste tu contraseña?"**.
2. En el campo que aparece, digitar el **correo electrónico** asociado a su cuenta.
3. Hacer clic en **Enviar**.
4. Revisar su bandeja de entrada (y la carpeta de spam si no lo encuentra).
5. Abrir el correo recibido con asunto relacionado con el restablecimiento de contraseña.
6. Hacer clic en el **enlace de restablecimiento** dentro del correo.
7. Digitar su **nueva contraseña** en los campos indicados.
8. Hacer clic en **Guardar**.

**Resultado esperado:** La contraseña queda actualizada. El enlace del correo es de **un solo uso** y expira en **1 hora**.

> Si el enlace ya fue usado o expiró, repita el proceso desde el paso 1.

---

### 3.4 Cerrar Sesión

**Pasos:**

1. Hacer clic en su nombre de usuario en la esquina superior derecha de la pantalla.
2. Seleccionar la opción **Cerrar sesión** en el menú desplegable.

**Resultado esperado:** La sesión se cierra y el sistema lo redirige a la pantalla de inicio de sesión.

> **Buenas prácticas de seguridad:** Cierre siempre la sesión cuando termine de trabajar, especialmente si usa un equipo compartido.

---

## 4. Dashboard — Panel Principal

Al iniciar sesión, todos los usuarios llegan al **Dashboard**. Esta es la pantalla de inicio del sistema y muestra un resumen en tiempo real del estado del personal.

### ¿Qué muestra el Dashboard?

El Dashboard presenta **tarjetas de indicadores (KPIs)** con información clave, adaptada al rol del usuario que inicia sesión:

| Tarjeta | ¿Qué muestra? | ¿Quién la ve? |
|---|---|---|
| **Total de empleados activos** | Número total de empleados con estado Activo | Todos los roles |
| **No disponibles hoy** | Empleados con evento laboral activo (vacaciones, incapacidad o permiso) en el día de hoy | Todos los roles |
| **Horas extras pendientes** | Solicitudes de horas extras que aún están en estado Pendiente de aprobación | Roles con capacidad de aprobar |

### Ver el detalle de cada tarjeta

Cada tarjeta es **interactiva**. Al hacer clic sobre ella, se despliega una tabla debajo (comportamiento de acordeón) con el listado detallado de los registros que conforman ese indicador.

**Columnas visibles al expandir:**

- **Empleados activos:** Nombre, Cédula, Sede, Cargo, Tipo de vinculación.
- **No disponibles hoy:** Nombre, Sede, Tipo de evento, Fecha inicio, Fecha fin.
- **Horas extras pendientes:** Empleado, Fecha, Cantidad de horas, Motivo.

**Para cerrar el detalle:** haga clic nuevamente sobre la tarjeta o sobre el ícono de flecha (∧) que aparece al expandirse.

> El Dashboard muestra los datos del momento en que cargó la página. Para ver información actualizada, recargue la página (tecla F5).

---

## 5. Módulo de Empleados

Este módulo es el núcleo del sistema. Aquí se registran, consultan y administran todos los empleados de la empresa.

**Para acceder:** Hacer clic en **"Empleados"** en el menú lateral izquierdo.

> **Operarios y Direccionadores:** al ingresar al módulo de Empleados, el sistema los redirige automáticamente a su propio perfil.

---

### 5.1 Ver Lista de Empleados Activos

Al ingresar al módulo, se muestra una tabla con todos los empleados activos visibles según el rol del usuario.

**¿Qué información aparece en la tabla?**

- Nombre completo
- Cédula de ciudadanía
- Sede
- Cargo
- Rol en el sistema
- Tipo de vinculación (Directo / Temporal)
- Estado (Activo / Inactivo)

**Opciones de filtro disponibles:**

| Filtro | Descripción |
|---|---|
| **Buscar** | Busca por nombre o número de cédula |
| **Sede** | Filtra por sede específica (disponible para roles con acceso multi-sede) |
| **Cargo** | Filtra por cargo |
| **Estado** | Filtra por empleados Activos o Inactivos |
| **Tipo de vinculación** | Filtra por Directo o Temporal |

**Cómo aplicar un filtro:**

1. Completar uno o más campos de filtro en la parte superior de la tabla.
2. El sistema actualiza los resultados automáticamente o al presionar **Enter**.
3. Para limpiar los filtros, borrar los campos y actualizar.

**Paginación:** la tabla muestra 15 registros por página. Use los botones de navegación en la parte inferior para avanzar o retroceder entre páginas.

---

### 5.2 Registrar un Nuevo Empleado

> **Roles que pueden crear empleados:** Administrador, Director Técnico, Analista, Regente, Auxiliar de Regente.

**Pasos:**

1. Ir al módulo **Empleados** desde el menú lateral.
2. Hacer clic en el botón **"Nuevo empleado"** (esquina superior derecha de la tabla).
3. Completar el formulario con los datos del empleado (ver campos a continuación).
4. Hacer clic en **Guardar**.

**Campos del formulario — sección por sección:**

#### Datos Personales *(todos obligatorios salvo indicación)*

| Campo | Descripción | Obligatorio |
|---|---|:---:|
| Nombre completo | Nombre y apellidos completos del empleado | ✅ |
| Cédula de ciudadanía | Número único. El sistema no permite duplicados. | ✅ |
| Fecha de nacimiento | Fecha de nacimiento | No |
| Teléfono | Número de contacto del empleado | ✅ |
| Correo electrónico | Correo personal o corporativo. También es el correo de acceso al sistema. Debe ser único. | ✅ |

#### Residencia

| Campo | Obligatorio |
|---|:---:|
| Dirección | ✅ |
| Ciudad | ✅ |
| Departamento | ✅ |

#### Contacto de Emergencia *(opcional)*

| Campo | Descripción |
|---|---|
| Nombre del contacto | Nombre completo del familiar o persona de contacto |
| Teléfono del contacto | Número de contacto |

> Si se llena uno de estos dos campos, el otro también se vuelve necesario. Si no tiene la información al momento del registro, puede dejarse en blanco y completarse después.

#### Formación y Seguridad Social *(opcionales)*

| Campo | Descripción |
|---|---|
| Nivel de escolaridad | Primaria / Bachillerato / Técnico / Tecnológico / Profesional / Posgrado |
| EPS | Nombre de la entidad promotora de salud |
| ARL | Nombre de la administradora de riesgos laborales |

#### Vinculación Laboral

| Campo | Descripción | Obligatorio |
|---|---|:---:|
| Sede | Sede donde labora el empleado | ✅ |
| Cargo | Cargo que desempeña | ✅ |
| Rol en el sistema | Rol de acceso (Administrador, Director Técnico, Analista, Regente, Auxiliar de Regente, Direccionador, Operario) | ✅ |
| Tipo de vinculación | **Contrato Directo** o **Empresa Temporal** | ✅ |
| Jefe inmediato | Se carga automáticamente según la sede seleccionada | Según rol |
| Fecha de ingreso | Fecha en que el empleado comenzó a laborar en la empresa | ✅ |
| Días de vacaciones previos | Días ya disfrutados antes del ingreso al sistema | No |

#### Contrato Temporal *(solo si Tipo de Vinculación = Empresa Temporal)*

| Campo | Descripción | Obligatorio |
|---|---|:---:|
| Empresa Temporal | Empresa que contrata al empleado | ✅ |
| Fecha fin de contrato | Fecha en que vence el contrato temporal | No |

> Al seleccionar **Empresa Temporal**, el sistema muestra automáticamente esta sección. Al seleccionar **Contrato Directo**, esta sección se oculta.

**Validaciones importantes:**

- No puede existir otro empleado con la misma cédula.
- No puede existir otro usuario con el mismo correo electrónico.
- Un empleado no puede ser su propio jefe inmediato.
- Si el rol es Regente, Auxiliar de Regente, Direccionador u Operario, debe tener un Jefe Inmediato asignado.
- No puede haber más de un Regente activo en la misma sede.

**Resultado esperado:** El empleado queda registrado, aparece en la lista de empleados activos y el sistema le asigna automáticamente una contraseña temporal para su primer ingreso.

---

### 5.3 Ver y Editar el Perfil de un Empleado

**Pasos para acceder al perfil:**

1. Ir al módulo **Empleados**.
2. Hacer clic sobre el nombre del empleado en la tabla, o en el ícono de acción de la fila.

**¿Qué muestra el perfil?**

El perfil está organizado en pestañas:

- **Pestaña "Datos":** muestra toda la información del empleado (datos personales, residencia, formación, seguridad social y vinculación laboral).
- **Pestaña "Historial":** registro cronológico de todas las novedades del empleado (ver sección 5.4).

**Cómo editar los datos de un empleado:**

1. En la pestaña **Datos**, hacer clic en el botón **Editar**.
2. Modificar los campos deseados.
3. Hacer clic en **Guardar cambios**.

> **Nota:** Si cambia la **Sede** del empleado, el campo **Jefe Inmediato** se actualiza automáticamente para mostrar solo los jefes asignados a la nueva sede. El jefe anterior se desmarca.

---

### 5.4 Historial del Empleado

La pestaña **Historial** dentro del perfil consolida todos los registros asociados a ese empleado en un solo lugar, ordenados de más reciente a más antiguo.

**¿Qué aparece en el historial?**

| Tipo de registro | Información visible |
|---|---|
| Eventos laborales | Tipo de evento, fechas, estado, nombre del autorizante, documento de soporte |
| Horas extras | Fecha, cantidad de horas, motivo, estado, quién aprobó o rechazó |
| Asignaciones de turno | Plantilla asignada, vigente desde, quién programó el turno |
| Desvinculación | Motivo y fecha (si el empleado fue desvinculado) |

**Exportar historial a Excel:**

1. Dentro de la pestaña Historial, hacer clic en el botón **"Exportar historial"**.
2. El sistema genera y descarga automáticamente un archivo Excel (`.xlsx`) con todos los registros del empleado.

---

### 5.5 Desvincular un Empleado

La desvinculación retira al empleado de la lista activa y deja constancia del motivo y la fecha de retiro. Esta acción **solo puede realizarla el Administrador o el Director Técnico**.

**Pasos:**

1. Ir al perfil del empleado que se desea desvincular (módulo Empleados → clic en el empleado).
2. Hacer clic en el botón **"Desvincular empleado"** (aparece en la parte inferior de la pestaña Datos).
3. En el modal que se abre, completar:
   - **Motivo de retiro:** descripción de la razón de la desvinculación (obligatorio).
   - **Fecha de desvinculación:** fecha en que se hizo efectiva la salida (obligatorio).
4. Hacer clic en **Confirmar**.

**Resultado esperado:**

- El empleado pasa a estado **Inactivo**.
- Desaparece de la lista principal de empleados activos.
- Queda disponible en la sección **"Empleados desvinculados"** (solo lectura).
- Su historial completo permanece accesible.

> Esta acción es irreversible desde la interfaz. Si fue un error, contacte al Administrador.

---

### 5.6 Empleados Desvinculados

Esta sección muestra todos los empleados que han sido retirados de la empresa. Es de **solo lectura** para todos los roles.

**Para acceder:**

- En el módulo Empleados, buscar el enlace o pestaña **"Empleados desvinculados"** (generalmente en la parte superior o como filtro de Estado = Inactivo).

**Información visible:**

| Columna | Descripción |
|---|---|
| Nombre completo | |
| Cédula | |
| Sede | Sede a la que pertenecía |
| Cargo | Cargo al momento del retiro |
| Tipo de vinculación | Directo o Temporal |
| Empresa temporal | Si aplica |
| Fecha de ingreso | |
| Fecha de desvinculación | |
| Motivo de retiro | |

Desde esta vista se puede acceder al perfil completo del empleado (modo solo lectura) y a su historial.

---

### 5.7 Cambio de Tipo de Vinculación (Temporal → Directo)

Cuando un empleado que ingresó con contrato temporal pasa a tener un contrato directo con la empresa, el tipo de vinculación debe actualizarse en el sistema.

**Pasos:**

1. Ir al perfil del empleado.
2. Hacer clic en **Editar**.
3. En el campo **Tipo de vinculación**, cambiar de `Empresa Temporal` a `Contrato Directo`.
4. Al hacer el cambio:
   - El sistema **oculta automáticamente** los campos de empresa temporal.
   - Ingresar la **Fecha de inicio del contrato directo** (fecha desde la cual aplica el nuevo tipo de vinculación; debe ser igual o posterior a la fecha de ingreso).
5. Hacer clic en **Guardar cambios**.

**¿Qué cambia en el sistema?**

| Campo | Antes (Temporal) | Después (Directo) |
|---|---|---|
| Empresa temporal | Tenía empresa asignada | Queda en blanco |
| Fecha fin de contrato | Tenía fecha | Queda en blanco |
| Fecha inicio de contrato | NULL | Fecha del cambio (ingresada por el analista) |
| Cálculo de vacaciones | No aplica | Comienza desde cero, contando desde la nueva fecha de inicio del contrato directo |

> El saldo de vacaciones de un contrato temporal **no se hereda** al pasar a contrato directo. El conteo comienza desde cero.

---

## 6. Módulo de Eventos Laborales

En este módulo se registran las novedades laborales de los empleados: **vacaciones**, **incapacidades** y **permisos**.

**Para acceder:** Hacer clic en **"Eventos laborales"** en el menú lateral.

> **Operarios y Direccionadores:** No tienen acceso a este módulo. Su módulo equivalente es **"Mis Solicitudes"** (ver sección 9).

---

### 6.1 Ver Eventos Laborales

Al ingresar al módulo se muestra una tabla con todos los eventos registrados visibles según el rol del usuario.

**Columnas de la tabla:**

- Empleado
- Tipo de evento (Vacaciones / Incapacidad / Permiso)
- Fecha inicio
- Fecha fin
- Estado (Pendiente / Activo / Finalizado / Anulado)
- Autorizado por

**Opciones de filtro:**

| Filtro | Descripción |
|---|---|
| Buscar | Por nombre de empleado |
| Tipo de evento | Vacaciones, Incapacidad, Permiso |
| Estado | Pendiente, Activo, Finalizado, Anulado |
| Desde / Hasta | Rango de fechas del evento |

**Paginación:** 15 registros por página.

---

### 6.2 Registrar un Evento (Vacaciones, Incapacidad o Permiso)

**Pasos:**

1. En el módulo Eventos Laborales, hacer clic en el botón **"Nuevo evento"**.
2. En el modal que aparece, seleccionar el **Tipo de evento**: Vacaciones, Incapacidad o Permiso.
3. Seleccionar el **Empleado** al que aplica el evento (búsqueda por nombre o cédula).
4. Completar los campos según el tipo de evento (ver tablas a continuación).
5. Adjuntar el **documento de soporte** si corresponde.
6. Hacer clic en **Guardar**.

#### Campos para Vacaciones

| Campo | Descripción | Obligatorio |
|---|---|:---:|
| Empleado | Empleado al que se le registran las vacaciones | ✅ |
| Fecha inicio | Primer día de las vacaciones | ✅ |
| Fecha fin | Último día de las vacaciones | ✅ |
| Saldo disponible | Se muestra automáticamente (solo lectura) | — |
| Días solicitados | Se calcula automáticamente al elegir las fechas | — |
| Autorizado por | Nombre de la persona que autoriza las vacaciones | ✅ |
| Documento de soporte | Adjunto PDF/JPG/PNG (máx. 5 MB) | No |

> **Importante:** Si el empleado no tiene suficiente saldo de vacaciones acumulado, el sistema muestra una advertencia y **no permite guardar** el evento.

#### Campos para Incapacidad

| Campo | Descripción | Obligatorio |
|---|---|:---:|
| Empleado | Empleado incapacitado | ✅ |
| Fecha inicio | Primer día de incapacidad | ✅ |
| Fecha fin | Último día de incapacidad | ✅ |
| Tipo de incapacidad | Enfermedad general / Accidente de trabajo / Enfermedad laboral / Maternidad-Paternidad | ✅ |
| Entidad que expide | Nombre de la EPS o ARL que emite el certificado | ✅ |
| Autorizado por | Nombre de quien autoriza el registro | ✅ |
| Documento de soporte | Certificado médico (PDF/JPG/PNG, máx. 5 MB) | **✅ Obligatorio** |

#### Campos para Permiso

| Campo | Descripción | Obligatorio |
|---|---|:---:|
| Empleado | Empleado que toma el permiso | ✅ |
| Fecha inicio | Primer día del permiso | ✅ |
| Fecha fin | Último día del permiso | ✅ |
| Descripción / Justificación | Motivo del permiso | ✅ |
| Autorizado por | Nombre de quien autoriza | ✅ |
| Documento de soporte | Adjunto (PDF/JPG/PNG, máx. 5 MB) | No |

**Regla importante — Evento único activo:**
El sistema **no permite** que un mismo empleado tenga dos eventos activos en el mismo período de fechas. Si intenta registrar un evento cuyas fechas se solapan con otro ya activo del mismo empleado, el sistema bloquea el guardado con un mensaje de error.

---

### 6.3 Aprobar, Rechazar o Anular un Evento

Los eventos tienen los siguientes estados posibles:

| Estado | Descripción |
|---|---|
| **Pendiente** | Solicitud creada, aún no gestionada |
| **Activo** | Evento aprobado y vigente en la fecha actual |
| **Finalizado** | El evento llegó a su fecha fin (automático) |
| **Anulado** | El evento fue cancelado manualmente |

**Para cambiar el estado de un evento:**

1. En la tabla de eventos, hacer clic sobre el evento que desea gestionar.
2. En el detalle del evento, encontrará los botones disponibles según su estado actual:
   - **Aprobar:** disponible para eventos en estado Pendiente. Cambia el estado a Activo.
   - **Rechazar:** disponible para eventos en estado Pendiente. Cambia el estado a Rechazado. Requiere ingresar un **motivo de rechazo**.
   - **Anular:** disponible para eventos en estado Activo o Finalizado. Requiere ingresar un **motivo de anulación**.

> Al anular un evento de vacaciones, los días descontados del saldo **se devuelven automáticamente** al empleado.

---

### 6.4 Cálculo del Saldo de Vacaciones

El sistema calcula automáticamente el saldo de vacaciones disponible de cada empleado con **contrato directo**.

**Fórmula:**

- Todo empleado con contrato directo acumula **15 días hábiles por año trabajado** (equivalente a 1.25 días por mes).
- El cálculo parte desde la **Fecha de Inicio del Contrato Directo**.
- Al registrar vacaciones, el sistema descuenta los días solicitados del saldo acumulado.

**Ejemplo:**
Si un empleado lleva 6 meses de contrato directo, ha acumulado **7.5 días** de vacaciones. Si solicita 5 días, le quedan 2.5 días de saldo disponible.

**Consideraciones:**

- Los **domingos no se cuentan** como días hábiles en el cálculo.
- Los festivos nacionales **sí se cuentan** como días hábiles (no se descuentan automáticamente del saldo).
- Los empleados con **contrato temporal no acumulan saldo** de vacaciones mientras mantienen ese tipo de vinculación.
- Si un empleado tenía días ya disfrutados antes de ingresar al sistema, el Administrador puede registrar ese valor inicial en el campo **"Días de vacaciones previos"** al crear o editar el empleado.

---

## 7. Módulo de Horas Extras

En este módulo se registran, gestionan y aprueban las solicitudes de tiempo suplementario trabajado por los empleados.

**Para acceder:** Hacer clic en **"Horas extras"** en el menú lateral.

---

### 7.1 Ver Horas Extras

Al ingresar al módulo se muestran:

- **Tarjetas de resumen:** solicitudes pendientes de aprobación, horas extras aprobadas este mes, total de horas aprobadas acumuladas.
- **Tabla de solicitudes:** listado con todas las solicitudes visibles según el rol del usuario.

**Columnas de la tabla:**

- Empleado
- Fecha en que se trabajaron las horas
- Cantidad de horas
- Motivo
- Estado (Pendiente / Aprobado / Rechazado / Anulado)
- Aprobado/Rechazado por
- Fecha de aprobación

**Visibilidad según rol:**

| Rol | ¿Qué ve? |
|---|---|
| Administrador | Todas las solicitudes |
| Director Técnico | Solicitudes de su línea jerárquica |
| Analista | Todas las solicitudes |
| Regente / Aux. Regente | Solicitudes propias y de sus subordinados directos |
| Operario / Direccionador | Solo sus propias solicitudes |

---

### 7.2 Registrar una Solicitud de Horas Extras

**Pasos:**

1. En el módulo Horas Extras, hacer clic en **"Nueva solicitud"**.
2. En el modal que aparece, completar los campos:

| Campo | Descripción | Obligatorio |
|---|---|:---:|
| Empleado | Empleado que trabajó las horas (para el propio usuario, su nombre aparece preseleccionado si aplica) | ✅ |
| Fecha | Fecha en que se trabajaron las horas extras | ✅ |
| Cantidad de horas | Número de horas (puede ser decimal, ej. 2.5). Mínimo: 1. Máximo: 24. | ✅ |
| Motivo / Justificación | Razón por la cual se trabajó tiempo adicional | ✅ |

3. Hacer clic en **Guardar**.

**Resultado esperado:** La solicitud queda registrada con estado **Pendiente** y aparece en la tabla de horas extras, pendiente de aprobación por el jefe correspondiente.

**Validaciones del sistema:**

- No puede existir más de una solicitud activa para el mismo empleado en la misma fecha.
- El empleado no puede tener un evento laboral activo (vacaciones, incapacidad o permiso) en la misma fecha.
- La cantidad de horas debe estar entre **1 y 24**.

---

### 7.3 Aprobar o Rechazar una Solicitud

> **Roles con permiso de aprobación:** Administrador, Director Técnico, Analista, Regente, Auxiliar de Regente.

**Pasos para aprobar:**

1. En la tabla de horas extras, identificar la solicitud con estado **Pendiente**.
2. Hacer clic en el ícono de acción o abrir el detalle de la solicitud.
3. Hacer clic en **Aprobar**.
4. Confirmar la acción.

**Resultado esperado:** La solicitud cambia a estado **Aprobado**. Queda registrado quién aprobó y en qué fecha.

**Pasos para rechazar:**

1. Abrir el detalle de la solicitud con estado **Pendiente**.
2. Hacer clic en **Rechazar**.
3. En el campo que aparece, ingresar el **motivo de rechazo** (obligatorio).
4. Confirmar.

**Resultado esperado:** La solicitud cambia a estado **Rechazado** con el motivo registrado.

> **Límite de jerarquía:** Un Regente o Auxiliar de Regente solo puede aprobar o rechazar las solicitudes de los empleados que dependen directamente de él. No puede gestionar solicitudes de empleados de otras áreas o sedes.

---

### 7.4 Anular una Solicitud Aprobada

Si una solicitud ya fue aprobada pero la información era incorrecta, puede anularse.

**Pasos:**

1. Abrir el detalle de la solicitud con estado **Aprobado**.
2. Hacer clic en **Anular**.
3. Ingresar el **motivo de anulación** (obligatorio).
4. Confirmar.

**Resultado esperado:** La solicitud cambia a estado **Anulado**, con el motivo y el responsable de la anulación registrados.

> La diferencia entre **Rechazo** (aplica sobre solicitudes Pendiente) y **Anulación** (aplica sobre solicitudes Aprobadas) es importante: el rechazo evita que algo incorrecto se apruebe; la anulación corrige algo que ya fue aprobado.

---

## 8. Módulo de Horarios y Turnos

En este módulo se administran las plantillas de turno y las asignaciones de horario de cada empleado.

**Para acceder:** Hacer clic en **"Horarios"** en el menú lateral.

> **Operarios y Direccionadores:** No tienen acceso a este módulo. Su turno asignado es visible en su perfil de empleado.

---

### 8.1 Ver Plantillas y Asignaciones

La pantalla principal del módulo está dividida en dos secciones:

1. **Plantillas de turno:** lista de todas las plantillas de horario creadas (filtradas por el creador según el rol).
2. **Asignaciones de turno:** lista de los empleados de la sede y el turno que tienen asignado actualmente.

**Columnas de asignaciones:**

- Empleado
- Plantilla de turno asignada
- Vigente desde
- Programado por

---

### 8.2 Crear una Plantilla de Turno

Una **plantilla de turno** define el horario de trabajo para cada día de la semana. Una vez creada, puede asignarse a múltiples empleados.

**Pasos:**

1. En el módulo Horarios, hacer clic en el botón **"Nueva plantilla"**.
2. En el formulario que aparece, completar:

| Campo | Descripción | Obligatorio |
|---|---|:---:|
| Nombre de la plantilla | Nombre descriptivo del turno (ej. "Turno L-V mañana", "Turno fin de semana") | ✅ |
| Configuración por día | Para cada día de la semana (Lunes a Domingo): hora de entrada, hora de salida, o marcar como "No labora" | ✅ |

3. Hacer clic en **Guardar**.

**Ejemplo de configuración:**

| Día | Entrada | Salida |
|---|---|---|
| Lunes | 07:00 | 15:00 |
| Martes | 07:00 | 15:00 |
| Miércoles | 07:00 | 15:00 |
| Jueves | 07:00 | 15:00 |
| Viernes | 07:00 | 15:00 |
| Sábado | 08:00 | 12:00 |
| Domingo | No labora | — |

**Validación:** La plantilla debe tener **al menos un día con horario configurado**. No se puede guardar una plantilla donde todos los días estén marcados como "No labora".

---

### 8.3 Asignar un Turno a un Empleado

**Desde el módulo de Horarios:**

1. En la tabla de asignaciones, encontrar al empleado al que se le asignará el turno.
2. Hacer clic en el ícono de acción de su fila.
3. Seleccionar la **plantilla de turno** que se le asignará.
4. Indicar la **fecha de vigencia** (desde qué fecha aplica este turno).
5. Confirmar.

**Desde el perfil del empleado:**

1. Ir al perfil del empleado (módulo Empleados → clic en el empleado).
2. Dentro del perfil, buscar la sección **"Horario"**.
3. Hacer clic en **"Cambiar turno"**.
4. Seleccionar la plantilla y la fecha de vigencia.
5. Guardar.

**Resultado esperado:** La nueva asignación queda activa. La asignación anterior **no se elimina**; queda guardada en el historial del empleado como registro de las asignaciones anteriores.

**Validación:** La fecha de vigencia del turno no puede ser anterior a la fecha de ingreso del empleado.

---

## 9. Módulo de Mis Solicitudes (Operario y Direccionador)

Este módulo está diseñado exclusivamente para los roles **Operario** y **Direccionador**, permitiéndoles registrar y consultar sus propias novedades laborales sin necesidad de que un superior lo haga por ellos.

**Para acceder:** Hacer clic en **"Mis Solicitudes"** en el menú lateral (visible solo para estos dos roles).

---

### 9.1 Ver Mis Solicitudes

Al ingresar al módulo se muestra una tabla con todas las solicitudes que el usuario ha registrado.

**Columnas de la tabla:**

| Columna | Descripción |
|---|---|
| # | Número de la solicitud |
| Tipo de solicitud | Vacaciones / Incapacidad / Permiso |
| Fecha de solicitud | Cuándo se registró la solicitud |
| Fecha inicio | Inicio del evento solicitado |
| Fecha fin | Fin del evento solicitado |
| Estado | Pendiente / Aprobado / Rechazado / Anulado |
| Aprobado por | Nombre del jefe que gestionó la solicitud (muestra "—" si está Pendiente) |
| Fecha de aprobación | Fecha en que se tomó la decisión |

**Opciones de filtro:**

- **Tipo de solicitud:** Vacaciones, Incapacidad, Permiso.
- **Estado:** Pendiente, Aprobado, Rechazado, Anulado.

**Paginación:** 15 registros por página.

---

### 9.2 Registrar una Nueva Solicitud

**Pasos:**

1. En el módulo **Mis Solicitudes**, hacer clic en el botón **"Nueva solicitud"**.
2. En el modal que aparece, completar los campos:

| Campo | Descripción | Obligatorio |
|---|---|:---:|
| Tipo de solicitud | Vacaciones / Incapacidad / Permiso | ✅ |
| Fecha inicio | Primer día de la novedad | ✅ |
| Fecha fin | Último día de la novedad | ✅ |
| Motivo | Descripción del motivo de la solicitud | ✅ |
| Observaciones | Información adicional (opcional) | No |
| Documento de soporte | Adjunto PDF/JPG/PNG (máx. 5 MB) | Solo para Incapacidad |

3. Hacer clic en **Guardar**.

**Resultado esperado:** La solicitud queda registrada con estado **Pendiente**. Su jefe inmediato la verá en el módulo de Eventos Laborales para gestionarla.

> **¿Cuándo se aprueba la solicitud?** La solicitud no se aprueba desde este módulo. El jefe inmediato debe acceder al módulo **Eventos Laborales** para revisarla y tomar una decisión. El estado se actualiza automáticamente en la vista de Mis Solicitudes.

---

## 10. Panel de Catálogos — Datos Maestros

El Panel de Catálogos contiene los datos maestros del sistema: sedes, cargos y empresas temporales. Estos datos son la base sobre la que se construye toda la información de los empleados.

**Para acceder:** Hacer clic en **"Catálogos"** en el menú lateral.

> **Roles con acceso:** Solo **Administrador** y **Director Técnico**.

---

### 10.1 Gestionar Sedes

Desde la pestaña **Sedes** puede ver, crear, editar y desactivar sedes.

**Crear una nueva sede:**

1. Hacer clic en **"Nueva sede"**.
2. Completar los campos:
   - **Nombre** *(obligatorio)*
   - **Ciudad** *(obligatorio)*
   - **Dirección** *(obligatorio)*
3. Hacer clic en **Guardar**.

**Editar una sede:**

1. En la tabla de sedes, hacer clic en el ícono de editar de la fila correspondiente.
2. Modificar los campos deseados.
3. Hacer clic en **Guardar cambios**.

**Desactivar una sede:**

1. Hacer clic en el ícono de desactivar de la sede.
2. El sistema verifica si la sede tiene empleados activos:
   - **Si tiene empleados activos:** aparece un mensaje de bloqueo indicando que primero debe reasignar a los empleados.
   - **Si no tiene empleados activos:** aparece un modal de confirmación. Al confirmar, la sede queda inactiva y no puede asignarse a nuevos empleados.

> Una sede desactivada puede reactivarse. La desactivación no elimina los datos históricos.

---

### 10.2 Gestionar Cargos

Desde la pestaña **Cargos** puede ver, crear y editar los cargos disponibles en el sistema.

**Crear un nuevo cargo:**

1. Hacer clic en **"Nuevo cargo"**.
2. Ingresar el **Nombre del cargo** *(obligatorio)*.
3. Hacer clic en **Guardar**.

**Desactivar un cargo:**

- Si el cargo tiene empleados activos asignados, el sistema bloquea la desactivación con un mensaje de error.
- Si no tiene empleados activos, se puede desactivar normalmente con confirmación.

**Validación:** No pueden existir dos cargos con exactamente el mismo nombre.

---

### 10.3 Gestionar Empresas Temporales

Desde la pestaña **Empresas Temporales** se administran las empresas de tercerización que proveen personal temporal.

**Crear una nueva empresa temporal:**

1. Hacer clic en **"Nueva empresa temporal"**.
2. Ingresar el **Nombre de la empresa** *(obligatorio)*.
3. Hacer clic en **Guardar**.

**Desactivar una empresa temporal:**

- Si hay empleados activos vinculados a esa empresa, el sistema bloquea la desactivación.
- Si no hay empleados activos vinculados, se puede desactivar con confirmación.

**Validación:** No pueden existir dos empresas con exactamente el mismo nombre.

---

## 11. Mi Perfil de Usuario

Todos los usuarios del sistema pueden consultar y actualizar su propia información de perfil.

**Para acceder:**

1. Hacer clic en el nombre de usuario en la esquina superior derecha.
2. Seleccionar **"Mi perfil"** en el menú desplegable.

**¿Qué puede ver y hacer desde Mi Perfil?**

- Ver sus datos personales registrados en el sistema.
- **Cambiar su contraseña:**
  1. Hacer clic en **"Cambiar contraseña"**.
  2. Ingresar la contraseña actual.
  3. Ingresar la nueva contraseña.
  4. Confirmar la nueva contraseña.
  5. Hacer clic en **Guardar**.

> Los cambios de contraseña aplican de forma inmediata. La próxima vez que inicie sesión deberá usar la nueva contraseña.

---

## 12. Preguntas Frecuentes y Errores Comunes

### ¿Por qué no puedo ver a todos los empleados?

La visibilidad de empleados depende del rol y la sede asignada:
- **Regente y Auxiliar de Regente:** solo ven a sus subordinados directos dentro de su sede.
- **Operario y Direccionador:** solo pueden ver su propio perfil.
- **Administrador, Director Técnico y Analista:** ven todos los empleados.

---

### El sistema dice "Ya existe un empleado con esta identificación". ¿Qué hago?

Significa que ya hay un empleado registrado con esa cédula. Verifique si el empleado ya fue ingresado previamente (puede estar en la lista de empleados desvinculados si ya fue retirado). Si es un error, contacte al Administrador.

---

### El sistema no me deja guardar las vacaciones. ¿Por qué?

Puede ser por dos razones:
1. **El empleado no tiene saldo suficiente:** el saldo disponible se muestra en el formulario. Verifique que los días solicitados no superen el saldo acumulado.
2. **El empleado tiene otro evento activo en esas fechas:** el sistema no permite solapamiento de eventos. Revise si hay una incapacidad, permiso u otro evento ya registrado en ese período.

---

### ¿Qué significa que la solicitud de horas extras está en estado "Pendiente"?

Significa que la solicitud fue registrada correctamente pero aún no ha sido revisada por el jefe inmediato del empleado. El jefe debe ingresar al módulo Horas Extras y aprobarla o rechazarla.

---

### El enlace de recuperación de contraseña ya no funciona. ¿Por qué?

Los enlaces de recuperación de contraseña expiran **1 hora** después de enviarse o se invalidan al ser usados una vez. Si el enlace ya no funciona, repita el proceso de recuperación desde la pantalla de inicio de sesión.

---

### ¿Cómo sé qué turno tiene asignado un empleado?

Puede consultarlo de dos maneras:
1. Desde el **perfil del empleado** (pestaña de perfil → sección Horario).
2. Desde el **módulo de Horarios** (tabla de asignaciones, buscando al empleado por nombre).

---

### No puedo desvincular a un empleado. ¿Por qué?

La acción de desvinculación solo está disponible para el **Administrador** y el **Director Técnico**. Si su rol es diferente, no verá el botón. Solicite la acción al responsable correspondiente.

---

### El sistema cerró mi sesión automáticamente. ¿Es normal?

Sí. Por seguridad, el sistema cierra la sesión automáticamente después de **30 minutos de inactividad**. Vuelva a iniciar sesión para continuar trabajando.

---

### ¿Puedo recuperar la información de un empleado desvinculado?

Sí. Los empleados desvinculados y todo su historial (eventos, horas extras, turnos) quedan almacenados en el sistema en modo de **solo lectura**. Puede acceder a esa información desde la sección **"Empleados desvinculados"** en el módulo de Empleados.

---

*Fin del Manual de Usuario — Sistema de Gestión de Personal v1.0*
