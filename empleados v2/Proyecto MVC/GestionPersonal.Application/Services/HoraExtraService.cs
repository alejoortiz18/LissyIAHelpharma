using GestionPersonal.Application.Interfaces;
using GestionPersonal.Constants.Messages;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.DTOs.HoraExtra;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Services;

public class HoraExtraService : IHoraExtraService
{
    private readonly IHoraExtraRepository _repo;

    public HoraExtraService(IHoraExtraRepository repo) => _repo = repo;

    public async Task<IReadOnlyList<HoraExtraDto>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default)
    {
        var lista = await _repo.ObtenerPorSedeAsync(sedeId, ct);
        return lista.Select(MapToDto).ToList();
    }

    public async Task<IReadOnlyList<HoraExtraDto>> ObtenerPorEmpleadoAsync(int empleadoId, CancellationToken ct = default)
    {
        var lista = await _repo.ObtenerPorEmpleadoAsync(empleadoId, ct);
        return lista.Select(MapToDto).ToList();
    }

    public async Task<IReadOnlyList<HoraExtraDto>> ObtenerPendientesPorSedeAsync(int sedeId, CancellationToken ct = default)
    {
        var lista = await _repo.ObtenerPendientesPorSedeAsync(sedeId, ct);
        return lista.Select(MapToDto).ToList();
    }

    public async Task<ResultadoOperacion> CrearAsync(CrearHoraExtraDto dto, int creadoPorUsuarioId, CancellationToken ct = default)
    {
        var horaExtra = new HoraExtra
        {
            EmpleadoId     = dto.EmpleadoId,
            FechaTrabajada = dto.FechaTrabajada,
            CantidadHoras  = dto.CantidadHoras,
            Motivo         = dto.Motivo,
            Estado         = EstadoHoraExtra.Pendiente,
            CreadoPor      = creadoPorUsuarioId,
            FechaCreacion  = DateTime.UtcNow
        };

        _repo.Agregar(horaExtra);
        await _repo.GuardarCambiosAsync(ct);

        return ResultadoOperacion.Ok(HoraExtraConstant.HoraExtraCreada);
    }

    public async Task<ResultadoOperacion> AprobarAsync(int horaExtraId, int aprobadoPorUsuarioId, CancellationToken ct = default)
    {
        var he = await _repo.ObtenerPorIdAsync(horaExtraId, ct);
        if (he is null)
            return ResultadoOperacion.Fail(HoraExtraConstant.HoraExtraNoEncontrada);

        he.Estado                    = EstadoHoraExtra.Aprobado;
        he.AprobadoRechazadoPor      = aprobadoPorUsuarioId;
        he.FechaAprobacion           = DateTime.UtcNow;

        _repo.Actualizar(he);
        await _repo.GuardarCambiosAsync(ct);

        return ResultadoOperacion.Ok(HoraExtraConstant.HoraExtraAprobada);
    }

    public async Task<ResultadoOperacion> RechazarAsync(int horaExtraId, string motivoRechazo, int rechazadoPorUsuarioId, CancellationToken ct = default)
    {
        var he = await _repo.ObtenerPorIdAsync(horaExtraId, ct);
        if (he is null)
            return ResultadoOperacion.Fail(HoraExtraConstant.HoraExtraNoEncontrada);

        he.Estado               = EstadoHoraExtra.Rechazado;
        he.MotivoRechazo        = motivoRechazo;
        he.AprobadoRechazadoPor = rechazadoPorUsuarioId;
        he.FechaAprobacion      = DateTime.UtcNow;

        _repo.Actualizar(he);
        await _repo.GuardarCambiosAsync(ct);

        return ResultadoOperacion.Ok(HoraExtraConstant.HoraExtraRechazada);
    }

    public async Task<ResultadoOperacion> AnularAsync(int horaExtraId, string motivoAnulacion, int anuladoPorUsuarioId, CancellationToken ct = default)
    {
        var he = await _repo.ObtenerPorIdAsync(horaExtraId, ct);
        if (he is null)
            return ResultadoOperacion.Fail(HoraExtraConstant.HoraExtraNoEncontrada);

        he.Estado          = EstadoHoraExtra.Anulado;
        he.MotivoAnulacion = motivoAnulacion;
        he.AnuladoPor      = anuladoPorUsuarioId;
        he.FechaAnulacion  = DateTime.UtcNow;

        _repo.Actualizar(he);
        await _repo.GuardarCambiosAsync(ct);

        return ResultadoOperacion.Ok("La hora extra fue anulada exitosamente.");
    }

    private static HoraExtraDto MapToDto(HoraExtra h) => new()
    {
        Id             = h.Id,
        EmpleadoId     = h.EmpleadoId,
        EmpleadoNombre = h.Empleado?.NombreCompleto     ?? string.Empty,
        SedeNombre     = h.Empleado?.Sede?.Nombre       ?? string.Empty,
        FechaTrabajada = h.FechaTrabajada.ToString("dd/MM/yyyy"),
        CantidadHoras  = h.CantidadHoras,
        Motivo         = h.Motivo,
        Estado         = h.Estado.ToString(),
        MotivoRechazo  = h.MotivoRechazo,
        MotivoAnulacion = h.MotivoAnulacion,
        FechaAprobacion = h.FechaAprobacion?.ToString("dd/MM/yyyy HH:mm")
    };
}
