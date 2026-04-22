-- ============================================================
-- SEEDING DATOS — Completa todas las tablas faltantes
-- Tablas objetivo:
--   · PlantillasTurno / PlantillasTurnoDetalle  → 2ª plantilla (turno rotativo)
--   · EventosLaborales                          → vacaciones, incapacidades, permisos
--   · HorasExtras                               → solicitudes en distintos estados
-- Tabla ya completa (no se toca):
--   · Sedes, Cargos, EmpresasTemporales, Usuarios, Empleados,
--     ContactosEmergencia, AsignacionesTurno, HistorialDesvinculaciones
-- ============================================================
USE GestionPersonal;
GO
SET QUOTED_IDENTIFIER ON;
GO

-- ── Referencias de IDs ya existentes ────────────────────────
DECLARE @UsuJefe    INT = (SELECT Id FROM dbo.Usuarios WHERE CorreoAcceso = N'carlos.rodriguez@yopmail.com');
DECLARE @UsuReg1    INT = (SELECT Id FROM dbo.Usuarios WHERE CorreoAcceso = N'laura.sanchez@yopmail.com');
DECLARE @UsuReg2    INT = (SELECT Id FROM dbo.Usuarios WHERE CorreoAcceso = N'hernan.castillo@yopmail.com');

-- Empleados (por cédula para evitar depender del Id autonumérico)
DECLARE @EmpJefe    INT = (SELECT Id FROM dbo.Empleados WHERE Cedula = N'10234567'); -- Carlos
DECLARE @EmpReg1    INT = (SELECT Id FROM dbo.Empleados WHERE Cedula = N'20345678'); -- Laura
DECLARE @EmpReg2    INT = (SELECT Id FROM dbo.Empleados WHERE Cedula = N'30456789'); -- Hernán
DECLARE @EmpAux     INT = (SELECT Id FROM dbo.Empleados WHERE Cedula = N'40567890'); -- Andrés Torres
DECLARE @EmpDiana   INT = (SELECT Id FROM dbo.Empleados WHERE Cedula = N'50678901'); -- Diana Vargas
DECLARE @EmpVale    INT = (SELECT Id FROM dbo.Empleados WHERE Cedula = N'60789012'); -- Valentina Ospina
DECLARE @EmpSeba    INT = (SELECT Id FROM dbo.Empleados WHERE Cedula = N'70890123'); -- Sebastián Moreno
DECLARE @EmpNata    INT = (SELECT Id FROM dbo.Empleados WHERE Cedula = N'80901234'); -- Natalia Bermúdez
DECLARE @EmpPaula   INT = (SELECT Id FROM dbo.Empleados WHERE Cedula = N'91012345'); -- Paula Quintero

DECLARE @SedeId     INT = (SELECT TOP 1 Id FROM dbo.Sedes);

-- ============================================================
-- A. SEGUNDA PLANTILLA DE TURNO: Turno Fin de Semana
-- ============================================================
IF NOT EXISTS (SELECT 1 FROM dbo.PlantillasTurno WHERE Nombre = N'Turno Fin de Semana')
BEGIN
    INSERT INTO dbo.PlantillasTurno (Nombre, Estado, FechaCreacion)
    VALUES (N'Turno Fin de Semana', N'Activa', GETUTCDATE());

    DECLARE @P2 INT = SCOPE_IDENTITY();

    INSERT INTO dbo.PlantillasTurnoDetalle (PlantillaTurnoId, DiaSemana, HoraEntrada, HoraSalida)
    VALUES
        (@P2, 1, NULL,    NULL   ),  -- Lunes    (no labora)
        (@P2, 2, NULL,    NULL   ),  -- Martes
        (@P2, 3, NULL,    NULL   ),  -- Miércoles
        (@P2, 4, NULL,    NULL   ),  -- Jueves
        (@P2, 5, NULL,    NULL   ),  -- Viernes
        (@P2, 6, '08:00', '17:00'),  -- Sábado
        (@P2, 7, '08:00', '14:00');  -- Domingo (medio día)
END;

-- ============================================================
-- B. TERCERA PLANTILLA DE TURNO: Turno Rotativo Completo
-- ============================================================
IF NOT EXISTS (SELECT 1 FROM dbo.PlantillasTurno WHERE Nombre = N'Turno Rotativo 6x1')
BEGIN
    INSERT INTO dbo.PlantillasTurno (Nombre, Estado, FechaCreacion)
    VALUES (N'Turno Rotativo 6x1', N'Activa', GETUTCDATE());

    DECLARE @P3 INT = SCOPE_IDENTITY();

    INSERT INTO dbo.PlantillasTurnoDetalle (PlantillaTurnoId, DiaSemana, HoraEntrada, HoraSalida)
    VALUES
        (@P3, 1, '07:00', '15:00'),
        (@P3, 2, '07:00', '15:00'),
        (@P3, 3, '07:00', '15:00'),
        (@P3, 4, '07:00', '15:00'),
        (@P3, 5, '07:00', '15:00'),
        (@P3, 6, '07:00', '15:00'),
        (@P3, 7, NULL,    NULL   );  -- Domingo descanso
END;

-- ============================================================
-- C. EVENTOS LABORALES — Vacaciones, Incapacidades, Permisos
-- ============================================================

-- C1. Carlos (Jefe) — Vacaciones aprobadas (ya finalizadas)
IF NOT EXISTS (SELECT 1 FROM dbo.EventosLaborales WHERE EmpleadoId = @EmpJefe AND FechaInicio = '2025-12-22')
INSERT INTO dbo.EventosLaborales
    (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado,
     TipoIncapacidad, EntidadExpide, Descripcion,
     AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento,
     CreadoPor, FechaCreacion, AnuladoPor)
VALUES
    (@EmpJefe, N'Vacaciones', '2025-12-22', '2026-01-04', N'Finalizado',
     NULL, NULL, NULL,
     N'Junta Directiva', NULL, NULL, NULL,
     @UsuJefe, GETUTCDATE(), NULL);

-- C2. Laura (Regente1) — Permiso activo por cita médica
IF NOT EXISTS (SELECT 1 FROM dbo.EventosLaborales WHERE EmpleadoId = @EmpReg1 AND FechaInicio = '2026-04-25')
INSERT INTO dbo.EventosLaborales
    (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado,
     TipoIncapacidad, EntidadExpide, Descripcion,
     AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento,
     CreadoPor, FechaCreacion, AnuladoPor)
VALUES
    (@EmpReg1, N'Permiso', '2026-04-25', '2026-04-25', N'Activo',
     NULL, NULL, N'Cita médica de control programada',
     N'Carlos Rodríguez', NULL, NULL, NULL,
     @UsuJefe, GETUTCDATE(), NULL);

-- C3. Hernán (Regente2) — Vacaciones activas
IF NOT EXISTS (SELECT 1 FROM dbo.EventosLaborales WHERE EmpleadoId = @EmpReg2 AND FechaInicio = '2026-04-14')
INSERT INTO dbo.EventosLaborales
    (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado,
     TipoIncapacidad, EntidadExpide, Descripcion,
     AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento,
     CreadoPor, FechaCreacion, AnuladoPor)
VALUES
    (@EmpReg2, N'Vacaciones', '2026-04-14', '2026-04-27', N'Activo',
     NULL, NULL, NULL,
     N'Carlos Rodríguez', NULL, NULL, NULL,
     @UsuJefe, GETUTCDATE(), NULL);

-- C4. Andrés Torres — Incapacidad por Enfermedad General (finalizada)
IF NOT EXISTS (SELECT 1 FROM dbo.EventosLaborales WHERE EmpleadoId = @EmpAux AND FechaInicio = '2026-03-10')
INSERT INTO dbo.EventosLaborales
    (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado,
     TipoIncapacidad, EntidadExpide, Descripcion,
     AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento,
     CreadoPor, FechaCreacion, AnuladoPor)
VALUES
    (@EmpAux, N'Incapacidad', '2026-03-10', '2026-03-14', N'Finalizado',
     N'EnfermedadGeneral', N'Sura EPS', NULL,
     N'Laura Sánchez', NULL, NULL, NULL,
     @UsuReg1, GETUTCDATE(), NULL);

-- C5. Diana Vargas — Permiso anulado (ejemplo de flujo anulación)
IF NOT EXISTS (SELECT 1 FROM dbo.EventosLaborales WHERE EmpleadoId = @EmpDiana AND FechaInicio = '2026-02-14')
INSERT INTO dbo.EventosLaborales
    (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado,
     TipoIncapacidad, EntidadExpide, Descripcion,
     AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento,
     CreadoPor, FechaCreacion, AnuladoPor)
VALUES
    (@EmpDiana, N'Permiso', '2026-02-14', '2026-02-14', N'Anulado',
     NULL, NULL, N'Diligencias personales',
     N'Laura Sánchez', N'El empleado pospuso la solicitud',  NULL, NULL,
     @UsuReg1, GETUTCDATE(), @UsuReg1);

-- C6. Valentina Ospina — Vacaciones activas (temporal, aprobadas)
IF NOT EXISTS (SELECT 1 FROM dbo.EventosLaborales WHERE EmpleadoId = @EmpVale AND FechaInicio = '2026-05-05')
INSERT INTO dbo.EventosLaborales
    (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado,
     TipoIncapacidad, EntidadExpide, Descripcion,
     AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento,
     CreadoPor, FechaCreacion, AnuladoPor)
VALUES
    (@EmpVale, N'Vacaciones', '2026-05-05', '2026-05-15', N'Activo',
     NULL, NULL, NULL,
     N'Laura Sánchez', NULL, NULL, NULL,
     @UsuReg1, GETUTCDATE(), NULL);

-- C7. Sebastián Moreno — Incapacidad por Accidente de Trabajo (finalizada)
IF NOT EXISTS (SELECT 1 FROM dbo.EventosLaborales WHERE EmpleadoId = @EmpSeba AND FechaInicio = '2026-01-20')
INSERT INTO dbo.EventosLaborales
    (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado,
     TipoIncapacidad, EntidadExpide, Descripcion,
     AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento,
     CreadoPor, FechaCreacion, AnuladoPor)
VALUES
    (@EmpSeba, N'Incapacidad', '2026-01-20', '2026-01-31', N'Finalizado',
     N'AccidenteTrabajo', N'AXA Colpatria', NULL,
     N'Hernán Castillo', NULL, NULL, NULL,
     @UsuReg2, GETUTCDATE(), NULL);

-- C8. Natalia Bermúdez — Permiso activo por lactancia
IF NOT EXISTS (SELECT 1 FROM dbo.EventosLaborales WHERE EmpleadoId = @EmpNata AND FechaInicio = '2026-04-21')
INSERT INTO dbo.EventosLaborales
    (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado,
     TipoIncapacidad, EntidadExpide, Descripcion,
     AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento,
     CreadoPor, FechaCreacion, AnuladoPor)
VALUES
    (@EmpNata, N'Permiso', '2026-04-21', '2026-04-21', N'Activo',
     NULL, NULL, N'Permiso de lactancia materna',
     N'Hernán Castillo', NULL, NULL, NULL,
     @UsuReg2, GETUTCDATE(), NULL);

-- C9. Paula Quintero — Incapacidad por Enfermedad Laboral (activa)
IF NOT EXISTS (SELECT 1 FROM dbo.EventosLaborales WHERE EmpleadoId = @EmpPaula AND FechaInicio = '2026-04-18')
INSERT INTO dbo.EventosLaborales
    (EmpleadoId, TipoEvento, FechaInicio, FechaFin, Estado,
     TipoIncapacidad, EntidadExpide, Descripcion,
     AutorizadoPor, MotivoAnulacion, RutaDocumento, NombreDocumento,
     CreadoPor, FechaCreacion, AnuladoPor)
VALUES
    (@EmpPaula, N'Incapacidad', '2026-04-18', '2026-04-24', N'Activo',
     N'EnfermedadLaboral', N'Comfama', NULL,
     N'Hernán Castillo', NULL, NULL, NULL,
     @UsuReg2, GETUTCDATE(), NULL);

-- ============================================================
-- D. HORAS EXTRAS — distintos estados del flujo
-- ============================================================

-- D1. Andrés Torres — Pendiente de aprobación
IF NOT EXISTS (SELECT 1 FROM dbo.HorasExtras WHERE EmpleadoId = @EmpAux AND FechaTrabajada = '2026-04-19')
INSERT INTO dbo.HorasExtras
    (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado,
     AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo,
     AnuladoPor, FechaAnulacion, MotivoAnulacion,
     CreadoPor, FechaCreacion)
VALUES
    (@EmpAux, '2026-04-19', 2.0, N'Inventario mensual de medicamentos',
     N'Pendiente', NULL, NULL, NULL, NULL, NULL, NULL,
     @UsuReg1, GETUTCDATE());

-- D2. Diana Vargas — Aprobada
IF NOT EXISTS (SELECT 1 FROM dbo.HorasExtras WHERE EmpleadoId = @EmpDiana AND FechaTrabajada = '2026-04-12')
INSERT INTO dbo.HorasExtras
    (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado,
     AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo,
     AnuladoPor, FechaAnulacion, MotivoAnulacion,
     CreadoPor, FechaCreacion)
VALUES
    (@EmpDiana, '2026-04-12', 3.0, N'Cierre de caja y conteo de efectivo',
     N'Aprobado', @UsuReg1, GETUTCDATE(), NULL, NULL, NULL, NULL,
     @UsuReg1, GETUTCDATE());

-- D3. Valentina Ospina — Rechazada
IF NOT EXISTS (SELECT 1 FROM dbo.HorasExtras WHERE EmpleadoId = @EmpVale AND FechaTrabajada = '2026-04-05')
INSERT INTO dbo.HorasExtras
    (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado,
     AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo,
     AnuladoPor, FechaAnulacion, MotivoAnulacion,
     CreadoPor, FechaCreacion)
VALUES
    (@EmpVale, '2026-04-05', 4.0, N'Apoyo en punto de venta adicional',
     N'Rechazado', @UsuReg1, GETUTCDATE(),
     N'No se autorizó por falta de presupuesto de horas extras',
     NULL, NULL, NULL,
     @UsuReg1, GETUTCDATE());

-- D4. Sebastián Moreno — Aprobada
IF NOT EXISTS (SELECT 1 FROM dbo.HorasExtras WHERE EmpleadoId = @EmpSeba AND FechaTrabajada = '2026-04-08')
INSERT INTO dbo.HorasExtras
    (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado,
     AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo,
     AnuladoPor, FechaAnulacion, MotivoAnulacion,
     CreadoPor, FechaCreacion)
VALUES
    (@EmpSeba, '2026-04-08', 2.5, N'Recepción de pedido especial de vacunas',
     N'Aprobado', @UsuReg2, GETUTCDATE(), NULL, NULL, NULL, NULL,
     @UsuReg2, GETUTCDATE());

-- D5. Natalia Bermúdez — Anulada (aprobada luego anulada)
IF NOT EXISTS (SELECT 1 FROM dbo.HorasExtras WHERE EmpleadoId = @EmpNata AND FechaTrabajada = '2026-03-28')
INSERT INTO dbo.HorasExtras
    (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado,
     AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo,
     AnuladoPor, FechaAnulacion, MotivoAnulacion,
     CreadoPor, FechaCreacion)
VALUES
    (@EmpNata, '2026-03-28', 3.0, N'Capacitación a nuevo personal',
     N'Anulado', @UsuReg2, GETUTCDATE(), NULL,
     @UsuJefe, GETUTCDATE(), N'Capacitación reprogramada para horario regular',
     @UsuReg2, GETUTCDATE());

-- D6. Hernán Castillo — Pendiente
IF NOT EXISTS (SELECT 1 FROM dbo.HorasExtras WHERE EmpleadoId = @EmpReg2 AND FechaTrabajada = '2026-04-20')
INSERT INTO dbo.HorasExtras
    (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado,
     AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo,
     AnuladoPor, FechaAnulacion, MotivoAnulacion,
     CreadoPor, FechaCreacion)
VALUES
    (@EmpReg2, '2026-04-20', 1.5, N'Revisión de cierre contable mensual',
     N'Pendiente', NULL, NULL, NULL, NULL, NULL, NULL,
     @UsuJefe, GETUTCDATE());

-- D7. Paula Quintero — Pendiente
IF NOT EXISTS (SELECT 1 FROM dbo.HorasExtras WHERE EmpleadoId = @EmpPaula AND FechaTrabajada = '2026-04-17')
INSERT INTO dbo.HorasExtras
    (EmpleadoId, FechaTrabajada, CantidadHoras, Motivo, Estado,
     AprobadoRechazadoPor, FechaAprobacion, MotivoRechazo,
     AnuladoPor, FechaAnulacion, MotivoAnulacion,
     CreadoPor, FechaCreacion)
VALUES
    (@EmpPaula, '2026-04-17', 2.0, N'Reemplazo por ausencia de compañera',
     N'Pendiente', NULL, NULL, NULL, NULL, NULL, NULL,
     @UsuReg2, GETUTCDATE());

-- ============================================================
-- E. VERIFICACIÓN FINAL
-- ============================================================
SELECT 'PlantillasTurno'        AS Tabla, COUNT(*) AS Total FROM dbo.PlantillasTurno
UNION ALL SELECT 'PlantillasTurnoDetalle',  COUNT(*) FROM dbo.PlantillasTurnoDetalle
UNION ALL SELECT 'EventosLaborales',        COUNT(*) FROM dbo.EventosLaborales
UNION ALL SELECT 'HorasExtras',             COUNT(*) FROM dbo.HorasExtras
UNION ALL SELECT 'TokensRecuperacion',      COUNT(*) FROM dbo.TokensRecuperacion
UNION ALL SELECT 'HistorialDesvinculaciones', COUNT(*) FROM dbo.HistorialDesvinculaciones;

-- Detalle de EventosLaborales
SELECT e.NombreCompleto, ev.TipoEvento, ev.FechaInicio, ev.FechaFin, ev.Estado,
       ev.TipoIncapacidad, ev.Descripcion
FROM   dbo.EventosLaborales ev
JOIN   dbo.Empleados e ON e.Id = ev.EmpleadoId
ORDER  BY ev.FechaInicio;

-- Detalle de HorasExtras
SELECT e.NombreCompleto, hx.FechaTrabajada, hx.CantidadHoras, hx.Estado, hx.Motivo
FROM   dbo.HorasExtras hx
JOIN   dbo.Empleados e ON e.Id = hx.EmpleadoId
ORDER  BY hx.FechaTrabajada;
GO
