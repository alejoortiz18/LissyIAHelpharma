using GestionPersonal.Models.Enums;

namespace GestionPersonal.Models.DTOs.Empleado;

/// <summary>DTO de solo lectura para mostrar en la tabla de empleados.</summary>
public class EmpleadoListaDto
{
    public int Id { get; init; }
    public string NombreCompleto { get; init; } = null!;
    public string Cedula { get; init; } = null!;
    public string CargoNombre { get; init; } = null!;
    public string SedeNombre { get; init; } = null!;
    public string TipoVinculacion { get; init; } = null!;
    public string Rol { get; init; } = null!;
    public string Estado { get; init; } = null!;
    public string FechaIngreso { get; init; } = null!;
}
