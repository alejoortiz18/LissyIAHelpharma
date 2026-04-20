/* ============================================================
   GESTIÓN RH — data.js  |  Mock data for prototype
   ============================================================ */
'use strict';

const DB = {

  /* ── Sedes ──────────────────────────────────────────────── */
  sedes: [
    { id: 1, nombre: 'Sede Central', direccion: 'Cra 7 #12-45', ciudad: 'Bogotá' },
    { id: 2, nombre: 'Sede Norte',   direccion: 'Cll 80 #50-20', ciudad: 'Medellín' },
    { id: 3, nombre: 'Sede Sur',     direccion: 'Av 3N #23-10',  ciudad: 'Cali' },
  ],

  /* ── Cargos ─────────────────────────────────────────────── */
  cargos: [
    { id: 1, nombre: 'Jefe de Sede' },
    { id: 2, nombre: 'Farmacéutico Regente' },
    { id: 3, nombre: 'Auxiliar de Farmacia' },
    { id: 4, nombre: 'Auxiliar Administrativo' },
    { id: 5, nombre: 'Cajero(a)' },
    { id: 6, nombre: 'Asesor(a) Comercial' },
    { id: 7, nombre: 'Mensajero' },
    { id: 8, nombre: 'Coordinador de Sede' },
  ],

  /* ── Empresas Temporales ────────────────────────────────── */
  empresasTemporales: [
    { id: 1, nombre: 'Tempo Servicios S.A.S.' },
    { id: 2, nombre: 'Adecco Colombia S.A.' },
    { id: 3, nombre: 'ManpowerGroup Colombia' },
  ],

  /* ── Empleados ──────────────────────────────────────────── */
  empleados: [
    {
      id: 1, cc: '10234567', nombre: 'Carlos Alberto Rodríguez Mora',
      fechaNacimiento: '1985-03-14', telefono: '3104567890', correo: 'c.rodriguez@empresa.com',
      direccion: 'Cra 15 #45-32', ciudad: 'Bogotá', departamento: 'Cundinamarca',
      contactoEmergenciaNombre: 'María Rodríguez', contactoEmergenciaTel: '3115678901',
      escolaridad: 'Profesional',
      eps: 'Sura EPS', arl: 'Sura ARL',
      sedeId: 1, cargoId: 1, rol: 'jefe',
      tipoVinculacion: 'directo', jefeInmediatoId: null,
      fechaIngreso: '2019-01-15', diasVacacionesTomados: 30,
      estado: 'activo', motivoRetiro: null, fechaDesvinculacion: null,
      correoAcceso: 'c.rodriguez@empresa.com',
    },
    {
      id: 2, cc: '20345678', nombre: 'Laura Patricia Sánchez Gómez',
      fechaNacimiento: '1990-07-22', telefono: '3123456789', correo: 'l.sanchez@empresa.com',
      direccion: 'Cll 100 #18-50', ciudad: 'Bogotá', departamento: 'Cundinamarca',
      contactoEmergenciaNombre: 'Juan Sánchez', contactoEmergenciaTel: '3134567890',
      escolaridad: 'Profesional',
      eps: 'Nueva EPS', arl: 'Bolívar ARL',
      sedeId: 1, cargoId: 2, rol: 'regente',
      tipoVinculacion: 'directo', jefeInmediatoId: 1,
      fechaIngreso: '2020-03-01', diasVacacionesTomados: 15,
      estado: 'activo', motivoRetiro: null, fechaDesvinculacion: null,
      correoAcceso: 'l.sanchez@empresa.com',
    },
    {
      id: 3, cc: '30456789', nombre: 'Andrés Felipe Torres Ruiz',
      fechaNacimiento: '1995-11-05', telefono: '3156789012', correo: 'a.torres@empresa.com',
      direccion: 'Av Caracas #32-10', ciudad: 'Bogotá', departamento: 'Cundinamarca',
      contactoEmergenciaNombre: 'Clara Torres', contactoEmergenciaTel: '3167890123',
      escolaridad: 'Técnico',
      eps: 'Compensar', arl: 'Sura ARL',
      sedeId: 1, cargoId: 3, rol: 'auxiliar',
      tipoVinculacion: 'temporal', jefeInmediatoId: 2,
      empresaTemporalId: 1, fechaInicioContrato: '2024-01-01', fechaFinContrato: '2024-12-31',
      fechaIngreso: '2024-01-01', diasVacacionesTomados: 0,
      estado: 'activo', motivoRetiro: null, fechaDesvinculacion: null,
      correoAcceso: 'a.torres@empresa.com',
    },
    {
      id: 4, cc: '40567890', nombre: 'Diana Marcela Vargas López',
      fechaNacimiento: '1992-06-18', telefono: '3178901234', correo: 'd.vargas@empresa.com',
      direccion: 'Cra 50 #80-25', ciudad: 'Bogotá', departamento: 'Cundinamarca',
      contactoEmergenciaNombre: 'Pedro Vargas', contactoEmergenciaTel: '3189012345',
      escolaridad: 'Bachillerato',
      eps: 'Famisanar', arl: 'Positiva',
      sedeId: 1, cargoId: 5, rol: 'operario',
      tipoVinculacion: 'directo', jefeInmediatoId: 2,
      fechaIngreso: '2021-07-01', diasVacacionesTomados: 10,
      estado: 'activo', motivoRetiro: null, fechaDesvinculacion: null,
      correoAcceso: 'd.vargas@empresa.com',
    },
    {
      id: 5, cc: '50678901', nombre: 'Hernán David Castillo Mejía',
      fechaNacimiento: '1988-09-30', telefono: '3190123456', correo: 'h.castillo@empresa.com',
      direccion: 'Cll 50 #80 #50-11', ciudad: 'Medellín', departamento: 'Antioquia',
      contactoEmergenciaNombre: 'Rosa Castillo', contactoEmergenciaTel: '3201234567',
      escolaridad: 'Profesional',
      eps: 'Sura EPS', arl: 'Sura ARL',
      sedeId: 2, cargoId: 1, rol: 'jefe',
      tipoVinculacion: 'directo', jefeInmediatoId: null,
      fechaIngreso: '2018-06-15', diasVacacionesTomados: 45,
      estado: 'activo', motivoRetiro: null, fechaDesvinculacion: null,
      correoAcceso: 'h.castillo@empresa.com',
    },
    {
      id: 6, cc: '60789012', nombre: 'Valentina Ospina Restrepo',
      fechaNacimiento: '1993-04-12', telefono: '3212345678', correo: 'v.ospina@empresa.com',
      direccion: 'Cll 10 Sur #43-25', ciudad: 'Medellín', departamento: 'Antioquia',
      contactoEmergenciaNombre: 'Luis Ospina', contactoEmergenciaTel: '3223456789',
      escolaridad: 'Tecnológico',
      eps: 'Comfama', arl: 'AXA Colpatria',
      sedeId: 2, cargoId: 3, rol: 'auxiliar',
      tipoVinculacion: 'temporal', jefeInmediatoId: 5,
      empresaTemporalId: 2, fechaInicioContrato: '2024-06-01', fechaFinContrato: '2025-05-31',
      fechaIngreso: '2024-06-01', diasVacacionesTomados: 5,
      estado: 'activo', motivoRetiro: null, fechaDesvinculacion: null,
      correoAcceso: 'v.ospina@empresa.com',
    },
    {
      id: 7, cc: '70890123', nombre: 'Miguel Ángel Herrera Díaz',
      fechaNacimiento: '1980-01-25', telefono: '3234567890', correo: 'm.herrera@empresa.com',
      direccion: 'Av 6N #23-45', ciudad: 'Cali', departamento: 'Valle del Cauca',
      contactoEmergenciaNombre: 'Carmen Herrera', contactoEmergenciaTel: '3245678901',
      escolaridad: 'Profesional',
      eps: 'Coomeva', arl: 'Sura ARL',
      sedeId: 3, cargoId: 1, rol: 'jefe',
      tipoVinculacion: 'directo', jefeInmediatoId: null,
      fechaIngreso: '2017-03-01', diasVacacionesTomados: 60,
      estado: 'activo', motivoRetiro: null, fechaDesvinculacion: null,
      correoAcceso: 'm.herrera@empresa.com',
    },
    {
      id: 8, cc: '80901234', nombre: 'Natalia Bermúdez Salazar',
      fechaNacimiento: '1994-08-07', telefono: '3256789012', correo: 'n.bermudez@empresa.com',
      direccion: 'Cll 9 #43B-10', ciudad: 'Cali', departamento: 'Valle del Cauca',
      contactoEmergenciaNombre: 'Jorge Bermúdez', contactoEmergenciaTel: '3267890123',
      escolaridad: 'Profesional',
      eps: 'Coomeva', arl: 'Bolívar ARL',
      sedeId: 3, cargoId: 2, rol: 'regente',
      tipoVinculacion: 'directo', jefeInmediatoId: 7,
      fechaIngreso: '2021-02-15', diasVacacionesTomados: 8,
      estado: 'activo', motivoRetiro: null, fechaDesvinculacion: null,
      correoAcceso: 'n.bermudez@empresa.com',
    },
    {
      id: 9, cc: '91012345', nombre: 'Sebastián Moreno Parra',
      fechaNacimiento: '1998-12-03', telefono: '3278901234', correo: 's.moreno@empresa.com',
      direccion: 'Cra 28 #12-60', ciudad: 'Cali', departamento: 'Valle del Cauca',
      contactoEmergenciaNombre: 'Ana Moreno', contactoEmergenciaTel: '3289012345',
      escolaridad: 'Bachillerato',
      eps: 'Coomeva', arl: 'Positiva',
      sedeId: 3, cargoId: 7, rol: 'operario',
      tipoVinculacion: 'directo', jefeInmediatoId: 8,
      fechaIngreso: '2023-04-01', diasVacacionesTomados: 0,
      estado: 'activo', motivoRetiro: null, fechaDesvinculacion: null,
      correoAcceso: 's.moreno@empresa.com',
    },
    {
      id: 10, cc: '12345670', nombre: 'Jorge Enrique Pineda Castro',
      fechaNacimiento: '1986-05-17', telefono: '3290123456', correo: 'j.pineda@empresa.com',
      direccion: 'Cra 7 #35-80', ciudad: 'Bogotá', departamento: 'Cundinamarca',
      contactoEmergenciaNombre: 'Patricia Pineda', contactoEmergenciaTel: '3201234568',
      escolaridad: 'Técnico',
      eps: 'Sura EPS', arl: 'Sura ARL',
      sedeId: 1, cargoId: 4, rol: 'auxiliar',
      tipoVinculacion: 'directo', jefeInmediatoId: 1,
      fechaIngreso: '2022-08-01', diasVacacionesTomados: 3,
      estado: 'inactivo',
      motivoRetiro: 'Renuncia voluntaria — traslado a otra ciudad',
      fechaDesvinculacion: '2024-11-30',
      correoAcceso: 'j.pineda@empresa.com',
    },
    {
      id: 11, cc: '23456701', nombre: 'Paula Andrea Ríos Acosta',
      fechaNacimiento: '1996-02-28', telefono: '3212345679', correo: 'p.rios@empresa.com',
      direccion: 'Cll 45 #22-15', ciudad: 'Bogotá', departamento: 'Cundinamarca',
      contactoEmergenciaNombre: 'Sandra Ríos', contactoEmergenciaTel: '3223456780',
      escolaridad: 'Tecnológico',
      eps: 'Nueva EPS', arl: 'Bolívar ARL',
      sedeId: 1, cargoId: 3, rol: 'auxiliar',
      tipoVinculacion: 'temporal', jefeInmediatoId: 2,
      empresaTemporalId: 3, fechaInicioContrato: '2025-01-01', fechaFinContrato: '2025-06-30',
      fechaIngreso: '2025-01-01', diasVacacionesTomados: 0,
      estado: 'activo', motivoRetiro: null, fechaDesvinculacion: null,
      correoAcceso: 'p.rios@empresa.com',
    },
  ],

  /* ── Plantillas de Turno ────────────────────────────────── */
  turnos: [
    {
      id: 1,
      nombre: 'Turno Mañana L–V',
      dias: {
        lunes:    { entrada: '07:00', salida: '15:00', labora: true },
        martes:   { entrada: '07:00', salida: '15:00', labora: true },
        miercoles:{ entrada: '07:00', salida: '15:00', labora: true },
        jueves:   { entrada: '07:00', salida: '15:00', labora: true },
        viernes:  { entrada: '07:00', salida: '15:00', labora: true },
        sabado:   { entrada: null,    salida: null,    labora: false },
        domingo:  { entrada: null,    salida: null,    labora: false },
      },
    },
    {
      id: 2,
      nombre: 'Turno Tarde L–V',
      dias: {
        lunes:    { entrada: '14:00', salida: '22:00', labora: true },
        martes:   { entrada: '14:00', salida: '22:00', labora: true },
        miercoles:{ entrada: '14:00', salida: '22:00', labora: true },
        jueves:   { entrada: '14:00', salida: '22:00', labora: true },
        viernes:  { entrada: '14:00', salida: '22:00', labora: true },
        sabado:   { entrada: null,    salida: null,    labora: false },
        domingo:  { entrada: null,    salida: null,    labora: false },
      },
    },
    {
      id: 3,
      nombre: 'Turno Completo 6×1',
      dias: {
        lunes:    { entrada: '08:00', salida: '18:00', labora: true },
        martes:   { entrada: '08:00', salida: '18:00', labora: true },
        miercoles:{ entrada: '08:00', salida: '18:00', labora: true },
        jueves:   { entrada: '08:00', salida: '18:00', labora: true },
        viernes:  { entrada: '08:00', salida: '18:00', labora: true },
        sabado:   { entrada: '08:00', salida: '14:00', labora: true },
        domingo:  { entrada: null,    salida: null,    labora: false },
      },
    },
    {
      id: 4,
      nombre: 'Turno Fin de Semana',
      dias: {
        lunes:    { entrada: null,    salida: null,    labora: false },
        martes:   { entrada: null,    salida: null,    labora: false },
        miercoles:{ entrada: null,    salida: null,    labora: false },
        jueves:   { entrada: null,    salida: null,    labora: false },
        viernes:  { entrada: '14:00', salida: '22:00', labora: true },
        sabado:   { entrada: '08:00', salida: '18:00', labora: true },
        domingo:  { entrada: '08:00', salida: '16:00', labora: true },
      },
    },
  ],

  /* ── Asignaciones de Turno ──────────────────────────────── */
  asignacionesTurno: [
    { id: 1, empleadoId: 1,  turnoId: 1, vigenciaDesde: '2024-01-01', programadoPor: 'Carlos A. Rodríguez' },
    { id: 2, empleadoId: 2,  turnoId: 3, vigenciaDesde: '2024-03-01', programadoPor: 'Carlos A. Rodríguez' },
    { id: 3, empleadoId: 3,  turnoId: 1, vigenciaDesde: '2024-01-01', programadoPor: 'Laura P. Sánchez' },
    { id: 4, empleadoId: 4,  turnoId: 4, vigenciaDesde: '2024-06-01', programadoPor: 'Laura P. Sánchez' },
    { id: 5, empleadoId: 11, turnoId: 2, vigenciaDesde: '2025-01-01', programadoPor: 'Carlos A. Rodríguez' },
  ],

  /* ── Eventos Laborales ──────────────────────────────────── */
  eventos: [
    {
      id: 1, empleadoId: 2, tipo: 'vacaciones',
      fechaInicio: '2026-04-14', fechaFin: '2026-04-25',
      autorizadoPor: 'Carlos A. Rodríguez',
      diasSolicitados: 8, estado: 'activo',
      documento: 'solicitud_vacaciones_apr26.pdf',
    },
    {
      id: 2, empleadoId: 3, tipo: 'incapacidad',
      fechaInicio: '2026-04-10', fechaFin: '2026-04-17',
      tipoIncapacidad: 'Enfermedad general',
      entidadExpide: 'Compensar EPS',
      autorizadoPor: 'Laura P. Sánchez',
      estado: 'activo',
      documento: 'incapacidad_torres_abr26.pdf',
    },
    {
      id: 3, empleadoId: 4, tipo: 'permiso',
      fechaInicio: '2026-04-18', fechaFin: '2026-04-18',
      descripcion: 'Cita médica de control — medicina general',
      autorizadoPor: 'Laura P. Sánchez',
      estado: 'activo',
      documento: null,
    },
    {
      id: 4, empleadoId: 11, tipo: 'vacaciones',
      fechaInicio: '2026-03-03', fechaFin: '2026-03-14',
      autorizadoPor: 'Carlos A. Rodríguez',
      diasSolicitados: 8, estado: 'finalizado',
      documento: 'vac_rios_mar26.pdf',
    },
    {
      id: 5, empleadoId: 6, tipo: 'incapacidad',
      fechaInicio: '2026-04-20', fechaFin: '2026-04-26',
      tipoIncapacidad: 'Accidente de trabajo',
      entidadExpide: 'AXA Colpatria ARL',
      autorizadoPor: 'Hernán D. Castillo',
      estado: 'activo',
      documento: 'at_ospina_abr26.pdf',
    },
    {
      id: 6, empleadoId: 1, tipo: 'permiso',
      fechaInicio: '2026-02-10', fechaFin: '2026-02-10',
      descripcion: 'Diligencia personal — trámite notarial',
      autorizadoPor: 'Gerencia General',
      estado: 'finalizado',
      documento: null,
    },
    {
      id: 7, empleadoId: 8, tipo: 'vacaciones',
      fechaInicio: '2026-05-05', fechaFin: '2026-05-16',
      autorizadoPor: 'Miguel Á. Herrera',
      diasSolicitados: 8, estado: 'activo',
      documento: 'vac_bermudez_may26.pdf',
    },
    {
      id: 8, empleadoId: 9, tipo: 'permiso',
      fechaInicio: '2026-04-15', fechaFin: '2026-04-15',
      descripcion: 'Grado universitario familiar',
      autorizadoPor: 'Natalia Bermúdez',
      estado: 'anulado',
      motivoAnulacion: 'Duplicado — se registró dos veces',
      documento: null,
    },
  ],

  /* ── Horas Extras ───────────────────────────────────────── */
  horasExtras: [
    {
      id: 1, empleadoId: 2, fecha: '2026-04-08',
      horas: 3.0, motivo: 'Inventario de fin de mes — cierre contable',
      estado: 'aprobado',
      aprobadoPor: 'Carlos A. Rodríguez', fechaAprobacion: '2026-04-09',
      motivoRechazo: null,
    },
    {
      id: 2, empleadoId: 3, fecha: '2026-04-10',
      horas: 2.5, motivo: 'Recepción de pedido urgente de medicamentos',
      estado: 'pendiente',
      aprobadoPor: null, fechaAprobacion: null, motivoRechazo: null,
    },
    {
      id: 3, empleadoId: 4, fecha: '2026-04-12',
      horas: 1.5, motivo: 'Cubrimiento de turno por ausencia de compañero',
      estado: 'pendiente',
      aprobadoPor: null, fechaAprobacion: null, motivoRechazo: null,
    },
    {
      id: 4, empleadoId: 1, fecha: '2026-04-05',
      horas: 4.0, motivo: 'Reunión regional de coordinadores de sedes',
      estado: 'pendiente',
      aprobadoPor: null, fechaAprobacion: null, motivoRechazo: null,
      esJefePropiasSolicitud: true,
    },
    {
      id: 5, empleadoId: 11, fecha: '2026-03-28',
      horas: 2.0, motivo: 'Atención a cliente con pedido especial',
      estado: 'rechazado',
      aprobadoPor: null, fechaAprobacion: null,
      motivoRechazo: 'No hay soporte del pedido especial en el sistema',
    },
    {
      id: 6, empleadoId: 2, fecha: '2026-04-15',
      horas: 1.0, motivo: 'Cargue de planilla mensual',
      estado: 'pendiente',
      aprobadoPor: null, fechaAprobacion: null, motivoRechazo: null,
    },
    {
      id: 7, empleadoId: 6, fecha: '2026-04-16',
      horas: 3.5, motivo: 'Inventario de auditoría — sede norte',
      estado: 'aprobado',
      aprobadoPor: 'Hernán D. Castillo', fechaAprobacion: '2026-04-17',
      motivoRechazo: null,
    },
    {
      id: 8, empleadoId: 9, fecha: '2026-04-11',
      horas: 2.0, motivo: 'Reorganización de bodega de insumos',
      estado: 'pendiente',
      aprobadoPor: null, fechaAprobacion: null, motivoRechazo: null,
      anuladoPor: null, fechaAnulacion: null, motivoAnulacion: null,
    },
    {
      id: 9, empleadoId: 5, fecha: '2026-03-15',
      horas: 2.0, motivo: 'Asistencia a capacitación regional — sede norte',
      estado: 'anulado',
      aprobadoPor: 'Hernán D. Castillo', fechaAprobacion: '2026-03-16',
      motivoRechazo: null,
      anuladoPor: 'Carlos A. Rodríguez', fechaAnulacion: '2026-03-22',
      motivoAnulacion: 'La capacitación fue cancelada — no aplica reconocimiento de hora extra',
    },
  ],

  /* ── Historial Empleado (para prototipo) ────────────────── */
  /* Combinado de eventos + horas extras + turnos */
  getHistorial(empleadoId) {
    const eventos = this.eventos
      .filter(e => e.empleadoId === empleadoId)
      .map(e => ({ ...e, _tipo: 'evento' }));
    const horas = this.horasExtras
      .filter(h => h.empleadoId === empleadoId)
      .map(h => ({ ...h, _tipo: 'horaExtra' }));
    const asig = this.asignacionesTurno
      .filter(a => a.empleadoId === empleadoId)
      .map(a => ({ ...a, _tipo: 'turno' }));
    return [...eventos, ...horas, ...asig]
      .sort((a, b) => {
        const da = a.fechaInicio || a.fecha || a.vigenciaDesde || '';
        const db = b.fechaInicio || b.fecha || b.vigenciaDesde || '';
        return db.localeCompare(da);
      });
  },

  /* ── Helpers ────────────────────────────────────────────── */
  getSede(id)     { return this.sedes.find(s => s.id === id); },
  getCargo(id)    { return this.cargos.find(c => c.id === id); },
  getEmpleado(id) { return this.empleados.find(e => e.id === id); },
  getTurno(id)    { return this.turnos.find(t => t.id === id); },
  getEmpresaTemporal(id) { return this.empresasTemporales.find(e => e.id === id); },

  getEmpleadosPorSede(sedeId) {
    return this.empleados.filter(e => e.sedeId === sedeId);
  },

  countActivos() { return this.empleados.filter(e => e.estado === 'activo').length; },
  countJefes()   { return this.empleados.filter(e => e.estado === 'activo' && e.rol === 'jefe').length; },
  countNoDisponiblesHoy() {
    const hoy = new Date().toISOString().split('T')[0];
    const empleadosEnNovedad = new Set(
      this.eventos
        .filter(e => e.estado === 'activo' && e.fechaInicio <= hoy && e.fechaFin >= hoy)
        .map(e => e.empleadoId)
    );
    return empleadosEnNovedad.size;
  },
};
