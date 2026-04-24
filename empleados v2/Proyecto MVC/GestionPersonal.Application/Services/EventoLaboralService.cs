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

        var evento = new EventoLaboral
        {
            EmpleadoId      = dto.EmpleadoId,
            TipoEvento      = dto.TipoEvento,
            Estado          = EstadoEvento.Activo,
            FechaInicio     = dto.FechaInicio,
            FechaFin        = dto.FechaFin,
            TipoIncapacidad = dto.TipoIncapacidad,
            EntidadExpide   = dto.EntidadExpide,
            Descripcion     = dto.Descripcion,
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
        NombreDocumento = e.NombreDocumento
    };
}
