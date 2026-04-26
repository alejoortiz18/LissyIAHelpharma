using GestionPersonal.Application.Interfaces;
using GestionPersonal.Constants.Messages;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.DTOs.EventoLaboral;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Services;

public class EventoLaboralService : IEventoLaboralService
{
    private readonly IEventoLaboralRepository _repo;
    private readonly IEmpleadoRepository _empleadoRepo;

    public EventoLaboralService(IEventoLaboralRepository repo, IEmpleadoRepository empleadoRepo)
    {
        _repo         = repo;
        _empleadoRepo = empleadoRepo;
    }

    public async Task<IReadOnlyList<EventoLaboralDto>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default)
    {
        var lista = await _repo.ObtenerPorSedeAsync(sedeId, ct);
        return lista.Select(MapToDto).ToList();
    }

    public async Task<IReadOnlyList<EventoLaboralDto>> ObtenerTodosAsync(CancellationToken ct = default)
    {
        var lista = await _repo.ObtenerTodosAsync(ct);
        return lista.Select(MapToDto).ToList();
    }

    public async Task<IReadOnlyList<EventoLaboralDto>> ObtenerPorEmpleadoAsync(int empleadoId, CancellationToken ct = default)
    {
        var lista = await _repo.ObtenerPorEmpleadoAsync(empleadoId, ct);
        return lista.Select(MapToDto).ToList();
    }

    public async Task<IReadOnlyList<EventoLaboralDto>> ObtenerPorEmpleadoConFiltroAsync(
        int empleadoId, DateOnly? desde, DateOnly? hasta, CancellationToken ct = default)
    {
        var lista = await _repo.ObtenerPorEmpleadoConFiltroAsync(empleadoId, desde, hasta, ct);
        return lista.Select(MapToDto).ToList();
    }

    public async Task<ResultadoOperacion> CrearAsync(CrearEventoLaboralDto dto, int creadoPorUsuarioId, CancellationToken ct = default)
    {
        // Verificar solapamiento
        var solapados = await _repo.ObtenerActivosEnFechaAsync(dto.EmpleadoId, dto.FechaInicio, ct);
        if (solapados.Any())
            return ResultadoOperacion.Fail(EventoLaboralConstant.SolapamientoFechas);

        // Validación de saldo de vacaciones
        if (dto.TipoEvento == TipoEvento.Vacaciones && dto.DiasDisfrutar.HasValue)
        {
            var saldo = await ObtenerSaldoVacacionesAsync(dto.EmpleadoId, ct);
            if (saldo is null)
                return ResultadoOperacion.Fail("No se pudo calcular el saldo de vacaciones del empleado.");

            if (saldo.Disponibles <= 0)
                return ResultadoOperacion.Fail("El empleado no cuenta con días disponibles de vacaciones.");

            if (dto.DiasDisfrutar.Value > saldo.Disponibles)
                return ResultadoOperacion.Fail(
                    $"Los días a disfrutar ({dto.DiasDisfrutar.Value}) superan el saldo disponible ({saldo.Disponibles} días).");
        }

        var evento = new EventoLaboral
        {
            EmpleadoId      = dto.EmpleadoId,
            TipoEvento      = dto.TipoEvento,
            Estado          = dto.EstadoInicial,
            FechaInicio     = dto.FechaInicio,
            FechaFin        = dto.FechaFin,
            TipoIncapacidad = dto.TipoIncapacidad,
            EntidadExpide   = dto.EntidadExpide,
            Descripcion     = dto.Descripcion,
            DiasDisfrutar   = dto.TipoEvento == TipoEvento.Vacaciones ? dto.DiasDisfrutar : null,
            AutorizadoPor   = dto.AutorizadoPor,
            RutaDocumento   = dto.RutaDocumento,
            NombreDocumento = dto.NombreDocumento,
            CreadoPor       = creadoPorUsuarioId,
            FechaCreacion   = DateTime.UtcNow
        };

        _repo.Agregar(evento);
        await _repo.GuardarCambiosAsync(ct);

        return ResultadoOperacion.Ok(EventoLaboralConstant.EventoCreado);
    }

    public async Task<ResultadoOperacion> AnularAsync(int eventoId, string motivoAnulacion, int anuladoPorUsuarioId, CancellationToken ct = default)
    {
        var evento = await _repo.ObtenerPorIdAsync(eventoId, ct);
        if (evento is null)
            return ResultadoOperacion.Fail(EventoLaboralConstant.EventoNoEncontrado);

        evento.Estado           = EstadoEvento.Anulado;
        evento.MotivoAnulacion  = motivoAnulacion;
        evento.AnuladoPor       = anuladoPorUsuarioId;
        evento.FechaModificacion = DateTime.UtcNow;

        _repo.Actualizar(evento);
        await _repo.GuardarCambiosAsync(ct);

        return ResultadoOperacion.Ok("El evento fue anulado exitosamente.");
    }

    /// <summary>
    /// Devuelve el conjunto de IDs de todos los empleados que están bajo el jefe
    /// en la jerarquía (descendientes directos e indirectos, BFS).
    /// </summary>
    public async Task<IReadOnlySet<int>> ObtenerDescendientesAsync(int jefeId, CancellationToken ct = default)
    {
        // Necesitamos el mapeo completo jefe->subordinados de TODA la plataforma
        var todos = await _empleadoRepo.ObtenerTodosAsync(ct);
        var porJefe = todos
            .Where(e => e.JefeInmediatoId.HasValue)
            .GroupBy(e => e.JefeInmediatoId!.Value)
            .ToDictionary(g => g.Key, g => g.Select(e => e.Id).ToList());

        var resultado = new HashSet<int>();
        var cola = new Queue<int>();
        cola.Enqueue(jefeId);

        while (cola.Count > 0)
        {
            var actual = cola.Dequeue();
            if (!porJefe.TryGetValue(actual, out var hijos)) continue;
            foreach (var hijo in hijos)
            {
                if (resultado.Add(hijo))
                    cola.Enqueue(hijo);
            }
        }
        return resultado;
    }

    public async Task<ResultadoOperacion> CambiarEstadoAsync(
        int eventoId,
        EstadoEvento nuevoEstado,
        string nombreResponsable,
        string? observacion,
        CancellationToken ct = default)
    {
        var evento = await _repo.ObtenerPorIdAsync(eventoId, ct);
        if (evento is null)
            return ResultadoOperacion.Fail(EventoLaboralConstant.EventoNoEncontrado);

        // El estado Anulado solo se maneja por AnularAsync
        if (nuevoEstado == EstadoEvento.Anulado)
            return ResultadoOperacion.Fail("Usa la acción Anular para anular un evento.");

        var estadoAnterior = evento.Estado;

        // Observación obligatoria al rechazar o al reversar (cambiar desde Aprobado o Rechazado)
        bool esRechazo   = nuevoEstado == EstadoEvento.Rechazado;
        bool esReversion = estadoAnterior == EstadoEvento.Aprobado || estadoAnterior == EstadoEvento.Rechazado;

        if ((esRechazo || esReversion) && string.IsNullOrWhiteSpace(observacion))
            return ResultadoOperacion.Fail("La observación es obligatoria al rechazar o reversar una decisión.");

        evento.Estado            = nuevoEstado;
        evento.AutorizadoPor     = nombreResponsable;
        evento.MotivoAnulacion   = string.IsNullOrWhiteSpace(observacion) ? evento.MotivoAnulacion : observacion;
        evento.FechaModificacion = DateTime.UtcNow;

        _repo.Actualizar(evento);
        await _repo.GuardarCambiosAsync(ct);

        var etiqueta = nuevoEstado switch
        {
            EstadoEvento.Aprobado  => "aprobada",
            EstadoEvento.Rechazado => "rechazada",
            EstadoEvento.Pendiente => "devuelta a Pendiente",
            _                      => nuevoEstado.ToString().ToLower()
        };

        return ResultadoOperacion.Ok($"La solicitud fue {etiqueta} correctamente.");
    }

    public async Task<SaldoVacacionesDto?> ObtenerSaldoVacacionesAsync(int empleadoId, CancellationToken ct = default)
    {
        var empleado = await _empleadoRepo.ObtenerPorIdAsync(empleadoId, ct);
        if (empleado is null) return null;

        // Sin contrato directo no se puede calcular vacaciones causadas
        if (empleado.FechaInicioContrato is null)
            return new SaldoVacacionesDto { Acumulados = 0, Tomados = 0, Disponibles = 0 };

        var hoy    = DateOnly.FromDateTime(DateTime.Today);
        var inicio = empleado.FechaInicioContrato.Value;

        // Meses laborados con calendario real
        var meses = ((hoy.Year - inicio.Year) * 12) + hoy.Month - inicio.Month;
        if (hoy.Day < inicio.Day) meses--;
        if (meses < 0) meses = 0;

        var causadas = (int)(meses * 1.25m);

        var vacaciones = await _repo.ObtenerPorEmpleadoYTipoAsync(empleadoId, TipoEvento.Vacaciones, ct);
        var tomados = vacaciones
            .Where(e => e.Estado != EstadoEvento.Anulado && e.FechaInicio >= inicio)
            .Sum(e => e.FechaFin.DayNumber - e.FechaInicio.DayNumber + 1);

        return new SaldoVacacionesDto
        {
            Acumulados  = causadas,
            Tomados     = tomados,
            Disponibles = Math.Max(0, causadas - tomados),
        };
    }

    private static int ContarDiasHabiles(DateOnly inicio, DateOnly fin)
    {
        var count = 0;
        var d = inicio;
        while (d <= fin)
        {
            if (d.DayOfWeek != DayOfWeek.Sunday) count++;
            d = d.AddDays(1);
        }
        return count;
    }

    private static EventoLaboralDto MapToDto(EventoLaboral e) => new()
    {
        Id              = e.Id,
        EmpleadoId      = e.EmpleadoId,
        JefeInmediatoId = e.Empleado?.JefeInmediatoId,
        EmpleadoNombre  = e.Empleado?.NombreCompleto ?? string.Empty,
        SedeNombre      = e.Empleado?.Sede?.Nombre   ?? string.Empty,
        TipoEvento      = e.TipoEvento.ToString(),
        FechaInicio     = e.FechaInicio.ToString("dd/MM/yyyy"),
        FechaFin        = e.FechaFin.ToString("dd/MM/yyyy"),
        DiasSolicitados = e.FechaInicio.DayNumber > e.FechaFin.DayNumber
                          ? 0
                          : e.FechaFin.DayNumber - e.FechaInicio.DayNumber + 1,
        TipoIncapacidad = e.TipoIncapacidad?.ToString(),
        EntidadExpide   = e.EntidadExpide,
        Descripcion     = e.Descripcion,
        AutorizadoPor   = e.AutorizadoPor,
        Estado          = e.Estado.ToString(),
        MotivoAnulacion = e.MotivoAnulacion,
        RutaDocumento   = e.RutaDocumento,
        NombreDocumento = e.NombreDocumento,
        DiasDisfrutar   = e.DiasDisfrutar
    };
}
