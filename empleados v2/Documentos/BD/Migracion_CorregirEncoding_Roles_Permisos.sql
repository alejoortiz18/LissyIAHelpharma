-- Corrige textos con encoding incorrecto (ej. CatÃ¡logos -> Catálogos)
USE GestionPersonal;
GO

UPDATE dbo.PermisosPlataforma SET Modulo = N'Empleados', Nombre = N'Ver listado de empleados', Descripcion = N'Listado y búsqueda de personal' WHERE Codigo = N'Empleados.VerListado';
UPDATE dbo.PermisosPlataforma SET Descripcion = N'Proceso de desvinculación' WHERE Codigo = N'Empleados.Desvincular';
UPDATE dbo.PermisosPlataforma SET Descripcion = N'Anulación de eventos registrados' WHERE Codigo = N'EventosLaborales.Anular';
UPDATE dbo.PermisosPlataforma SET Descripcion = N'Enviar solicitudes al área de gestión' WHERE Codigo = N'Solicitudes.Crear';
UPDATE dbo.PermisosPlataforma SET Modulo = N'Catálogos', Nombre = N'Ver catálogos', Descripcion = N'Sedes, cargos y empresas (Director / Admin)' WHERE Codigo = N'Catalogos.Ver';
UPDATE dbo.PermisosPlataforma SET Modulo = N'Catálogos', Nombre = N'Editar catálogos', Descripcion = N'CRUD de catálogos operativos' WHERE Codigo = N'Catalogos.Editar';
UPDATE dbo.PermisosPlataforma SET Descripcion = N'Definir qué puede hacer cada rol' WHERE Codigo = N'RolesSistema.Gestionar';
GO

UPDATE dbo.RolesSistema SET Nombre = N'Administrador', Descripcion = N'Rol técnico con acceso amplio a la plataforma' WHERE Codigo = N'Administrador';
UPDATE dbo.RolesSistema SET Nombre = N'Analista', Descripcion = N'Autoridad superior, visión multi-sede' WHERE Codigo = N'Analista';
UPDATE dbo.RolesSistema SET Nombre = N'Director Técnico', Descripcion = N'Jefe de área / supervisión técnica' WHERE Codigo = N'DirectorTecnico';
UPDATE dbo.RolesSistema SET Descripcion = N'Apoyo al regente en operación de sede' WHERE Codigo = N'AuxiliarRegente';
UPDATE dbo.RolesSistema SET Descripcion = N'Personal operativo — perfil y solicitudes' WHERE Codigo = N'Operario';
UPDATE dbo.RolesSistema SET Descripcion = N'Personal operativo con enfoque en dirección' WHERE Codigo = N'Direccionador';
GO
