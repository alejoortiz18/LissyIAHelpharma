using GestionPersonal.Application.Interfaces;
using GestionPersonal.Constants;
using GestionPersonal.Constants.Messages;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.DTOs.HoraExtra;
using GestionPersonal.Models.DTOs.Notificaciones;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using GestionPersonal.Models.Models;
using Microsoft.Extensions.Logging;

namespace GestionPersonal.Application.Services;

public class HoraExtraService : IHoraExtraService
{
    private readonly IHoraExtraRepository _repo;
    private readonly IEmpleadoRepository _empleadoRepo;
    private readonly INotificationService _notificationService;
    private readonly ILogger<HoraExtraService> _logger;

    public HoraExtraService(
        IHoraExtraRepository repo,
        IEmpleadoRepository empleadoRepo,
        INotificationService notificationService,
        ILogger<HoraExtraService> logger)
    {
        _repo                = repo;
        _empleadoRepo        = empleadoRepo;
        _notificationService = notificationService;
        _logger              = logger;
    }

    public async Task<IReadOnlyList<HoraExtraDto>> ObtenerTodosAsync(CancellationToken ct = default)
    {
        var lista = await _repo.ObtenerTodosAsync(ct);
        return lista.Select(MapToDto).ToList();
    }

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

        try
        {
            await EnviarNotificacionHoraExtraCreadaAsync(horaExtra, dto.EmpleadoId, ct);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex,
                "Error al notificar nueva hora extra para empleado {EmpleadoId}", dto.EmpleadoId);
        }

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

    private async Task EnviarNotificacionHoraExtraCreadaAsync(
        HoraExtra horaExtra,
        int solicitanteEmpleadoId,
        CancellationToken ct)
    {
        var solicitante = await _empleadoRepo.ObtenerPorIdConDetallesAsync(solicitanteEmpleadoId, ct);
        if (solicitante is null || !solicitante.JefeInmediatoId.HasValue)
            return;

        var visitados    = new HashSet<int> { solicitanteEmpleadoId };
        var jefeActualId = solicitante.JefeInmediatoId;
        var destinatariosJerarquia = new List<DestinatarioJerarquiaSolicitud>();
        var correosJerarquia = new List<string>();
        string? nombreJefeInmediatoSolicitante = null;
        string? correoJefeInmediato = null;
        var esPrimerJefeEnCadena = true;

        while (jefeActualId.HasValue && visitados.Add(jefeActualId.Value))
        {
            var jefe = await _empleadoRepo.ObtenerPorIdConDetallesAsync(jefeActualId.Value, ct);
            if (jefe is null) break;

            var correoJefe = ResolverCorreo(jefe);
            if (!string.IsNullOrWhiteSpace(correoJefe))
            {
                var esJefeInmediato = esPrimerJefeEnCadena;
                if (esJefeInmediato)
                {
                    nombreJefeInmediatoSolicitante = jefe.NombreCompleto;
                    correoJefeInmediato = correoJefe;
                    esPrimerJefeEnCadena = false;
                }

                if (!correosJerarquia.Any(c => c.Equals(correoJefe, StringComparison.OrdinalIgnoreCase)))
                {
                    correosJerarquia.Add(correoJefe);
                    destinatariosJerarquia.Add(new DestinatarioJerarquiaSolicitud(
                        correoJefe,
                        jefe.NombreCompleto,
                        esJefeInmediato,
                        CargoJefeSede.EsCargoAnalistaServiciosFarmaceuticos(jefe.Cargo?.Nombre)));
                }
            }

            jefeActualId = jefe.JefeInmediatoId;
        }

        if (destinatariosJerarquia.Count == 0 || string.IsNullOrWhiteSpace(correoJefeInmediato))
            return;

        var descripcion = $"{horaExtra.CantidadHoras} hora(s). {horaExtra.Motivo}".Trim();

        var dto = new NotificacionSolicitudDto(
            TipoEvento                : "HoraExtra",
            TipoSolicitud             : "Hora extra",
            FechaEvento               : horaExtra.FechaTrabajada.ToString("dd/MM/yyyy"),
            NombreEmpleadoSolicitante : solicitante.NombreCompleto,
            CorreoEmpleadoSolicitante : ResolverCorreo(solicitante) ?? "",
            NombreJefeInmediato       : nombreJefeInmediatoSolicitante ?? "Jefe inmediato",
            CorreoJefeInmediato       : correoJefeInmediato,
            NombreJefeApoyo           : null,
            CorreoJefeApoyo           : null,
            NombreAprobador           : null,
            Observacion               : null,
            NombreQuienGenera         : solicitante.NombreCompleto,
            FechaFin                  : null,
            Descripcion               : descripcion,
            RutaDocumentoAdjunto      : null,
            NombreDocumentoAdjunto    : null,
            CorreosLineaJerarquica    : correosJerarquia,
            DestinatariosJerarquia    : destinatariosJerarquia);

        await _notificationService.NotificarSolicitudCreadaAsync(dto, ct);
    }

    private static string? ResolverCorreo(Empleado emp) =>
        !string.IsNullOrWhiteSpace(emp.CorreoElectronico)
            ? emp.CorreoElectronico
            : emp.Usuario?.CorreoAcceso;

    private static HoraExtraDto MapToDto(HoraExtra h) => new()
    {
        Id              = h.Id,
        EmpleadoId      = h.EmpleadoId,
        JefeInmediatoId = h.Empleado?.JefeInmediatoId,
        EmpleadoNombre  = h.Empleado?.NombreCompleto     ?? string.Empty,
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
