using GestionPersonal.Models.DTOs.Empleado;

namespace GestionPersonal.Web.ViewModels.Sedes;

public class SedesIndexViewModel
{
    public IReadOnlyList<SedeCardViewModel> Sedes { get; init; } = [];
}

public class SedeCardViewModel
{
    public int SedeId { get; init; }
    public string Nombre { get; init; } = string.Empty;
    public string Ciudad { get; init; } = string.Empty;
    public string Direccion { get; init; } = string.Empty;
    public int CantidadUsuarios { get; init; }
    public string ResponsableNombre { get; init; } = "Sin responsable";
    public string ResponsableCargo { get; init; } = "Sin responsable";
    public IReadOnlyList<EmpleadoListaDto> Usuarios { get; init; } = [];
}
