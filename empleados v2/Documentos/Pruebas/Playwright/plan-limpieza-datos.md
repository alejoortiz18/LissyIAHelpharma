Plan de Preparación de Base de Datos para Pruebas
Objetivo

Definir el proceso para dejar el ambiente listo para pruebas funcionales, realizando una limpieza controlada de la base de datos, conservando únicamente la estructura y datos maestros necesarios, y recreando la información base de usuarios, roles, cargos y configuraciones iniciales.

Alcance

Se requiere:

Limpiar la información transaccional del sistema.
Conservar únicamente catálogos maestros necesarios.
Ajustar documentos funcionales existentes:
#plan-asignacion-turnos-refinados.md
#plan-permisos-roles.md
Crear roles y cargos mínimos requeridos para pruebas.
Crear un único usuario administrador inicial.
Insertar datos maestros base para operación del sistema.
Reglas de Negocio para la Preparación
1. Fuente oficial de roles

Los roles deben tomarse como base desde:

#plan-permisos-roles.md

Solo se deben crear los roles que aparezcan en la sección:

Cargos involucrados

2. Cambio obligatorio de cargo

El cargo:

Jefe de Sede

Debe reemplazarse por:

Analista de Servicios Farmacéuticos

Este cambio debe reflejarse en:

#plan-asignacion-turnos-refinados.md
#plan-permisos-roles.md
3. Usuario Administrador Inicial

Se debe crear únicamente un usuario principal con rol:

Administrador

Este usuario tendrá acceso total al sistema.

Permisos esperados:
Crear, editar, eliminar usuarios
Gestionar roles
Gestionar sedes
Gestionar horarios
Gestionar turnos
Gestionar empleados
Ver dashboards
Ver reportes
Configurar parámetros
Administración total del CRUD general
Limpieza de Base de Datos
Eliminar información transaccional

Se debe vaciar contenido de tablas como:

Usuarios operativos
Asignación de turnos
Horarios generados
Solicitudes
Logs funcionales
Históricos de operación
Notificaciones
Relaciones temporales de pruebas
Conservar estructuras

No eliminar:

Tablas
Llaves foráneas
Índices
Procedimientos almacenados
Vistas
Datos Maestros a Conservar / Insertar
Cargos

Crear únicamente los definidos en documento actualizado.

Ejemplo:

Administrador
Analista de Servicios Farmacéuticos
Farmacéutico Regente
Auxiliar de Farmacia
Auxiliar Regente
Sedes

Crear sedes base de prueba:

Principal
Norte
Sur