using GestionPersonal.Models.Enums;

namespace GestionPersonal.Models.DTOs.Empleado;

/// <summary>DTO completo para la vista de perfil del empleado.</summary>
public class EmpleadoDto
{
    // Identificación
    public int Id { get; init; }
    public string NombreCompleto { get; init; } = null!;
    public string Cedula { get; init; } = null!;
    public string? FechaNacimiento { get; init; }

    // Contacto
    public string? Telefono { get; init; }
    public string? CorreoElectronico { get; init; }

    // Residencia
    public string? Direccion { get; init; }
    public string? Ciudad { get; init; }
    public string? Departamento { get; init; }

    // Formación y seguridad social
    public string? NivelEscolaridad { get; init; }
    public string? Eps { get; init; }
    public string? Arl { get; init; }

    // Contacto de emergencia
    public string? ContactoEmergenciaNombre { get; init; }
    public string? ContactoEmergenciaTelefono { get; init; }

    // Vinculación laboral
    public int SedeId { get; init; }
    public string SedeNombre { get; init; } = null!;
    public int CargoId { get; init; }
    public string CargoNombre { get; init; } = null!;
    public string TipoVinculacion { get; init; } = null!;
    public string Rol { get; init; } = null!;
    public int? JefeInmediatoId { get; init; }
    public string? JefeInmediatoNombre { get; init; }
    public string FechaIngreso { get; init; } = null!;
    public decimal DiasVacacionesPrevios { get; init; }

    // Contrato temporal
    public string? EmpresaTemporalNombre { get; init; }
    public string? FechaInicioContrato { get; init; }
    public string? FechaFinContrato { get; init; }

    // Estado
    public string Estado { get; init; } = null!;

    // Turno activo (resumen)
    public string? PlantillaTurnoActualNombre { get; init; }
}
