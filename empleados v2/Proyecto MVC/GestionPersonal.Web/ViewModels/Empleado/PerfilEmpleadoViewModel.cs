using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.DTOs.EventoLaboral;
using GestionPersonal.Models.DTOs.HoraExtra;
using GestionPersonal.Models.DTOs.Turno;

namespace GestionPersonal.Web.ViewModels.Empleado;

public class PerfilEmpleadoViewModel
{
    public EmpleadoDto Empleado { get; init; } = null!;
    public IReadOnlyList<EventoLaboralDto> Eventos { get; init; } = [];
    public IReadOnlyList<HoraExtraDto> HorasExtras { get; init; } = [];
    public PlantillaTurnoDto? TurnoActual { get; init; }
    public IReadOnlyList<PlantillaTurnoDto> Plantillas { get; init; } = [];
    public IReadOnlyList<AsignacionTurnoDto> HistorialTurnos { get; init; } = [];

    /// <summary>Tab activo: "datos" | "historial" | "horario" | "personal-a-cargo"</summary>
    public string Tab { get; init; } = "datos";

    /// <summary>Resumen de días totalizados por tipo de evento (respeta los filtros de fecha).</summary>
    public IReadOnlyList<ResumenEventoDto> ResumenEventos { get; init; } = [];

    /// <summary>Vacaciones disponibles calculadas: causadas por mes × 1.25 − disfrutadas desde FechaInicioContrato.</summary>
    public decimal? VacacionesDisponibles { get; init; }

    /// <summary>Valor del filtro Desde en formato yyyy-MM-dd (para el input type=date).</summary>
    public string? FiltroDesde { get; init; }

    /// <summary>Valor del filtro Hasta en formato yyyy-MM-dd (para el input type=date).</summary>
    public string? FiltroHasta { get; init; }

    /// <summary>True si el empleado está en la jerarquía (directa o indirecta) del usuario en sesión.</summary>
    public bool EsSubordinadoDelJefeEnSesion { get; init; }

    /// <summary>True si el cargo del empleado del perfil puede tener personal a cargo.</summary>
    public bool EsJefeConPersonalACargo { get; init; }

    public IReadOnlyList<EmpleadoListaDto> PersonalACargo { get; init; } = [];

    public string? FiltroBuscarPersonal { get; init; }
    public string? FiltroEstadoPersonal { get; init; }
    public string? FiltroTipoVinculacionPersonal { get; init; }
}
