using GestionPersonal.Models.DTOs.Empleado;

namespace GestionPersonal.Web.ViewModels.Sedes;

public class SedeDetalleViewModel
{
    public int SedeId { get; init; }
    public string Nombre { get; init; } = string.Empty;
    public string Ciudad { get; init; } = string.Empty;
    public string Direccion { get; init; } = string.Empty;

    public string ResponsableNombre { get; init; } = "Sin responsable";
    public string ResponsableCargo { get; init; } = "Sin responsable";

    public int TotalUsuarios { get; init; }
    public int Activos { get; init; }
    public int NoDisponibles { get; init; }
    public int Inactivos { get; init; }

    public IReadOnlyList<EmpleadoListaDto> Usuarios { get; init; } = [];

    public string? Buscar { get; init; }
    public string? Estado { get; init; }
    public string? TipoVinculacion { get; init; }
    public string? Rol { get; init; }
}
