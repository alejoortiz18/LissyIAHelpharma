using System.ComponentModel.DataAnnotations;
using GestionPersonal.Models.Enums;

namespace GestionPersonal.Models.DTOs.Empleado;

/// <summary>DTO de entrada para registrar un nuevo empleado.</summary>
public class CrearEmpleadoDto
{
    // Datos personales
    [Required(ErrorMessage = "El nombre completo es obligatorio.")]
    [StringLength(200)]
    public string NombreCompleto { get; set; } = null!;

    [Required(ErrorMessage = "La cédula es obligatoria.")]
    [StringLength(20)]
    public string Cedula { get; set; } = null!;

    public DateOnly? FechaNacimiento { get; set; }

    [Required(ErrorMessage = "El teléfono es obligatorio.")]
    [StringLength(20)]
    public string Telefono { get; set; } = null!;

    [Required(ErrorMessage = "El correo es obligatorio.")]
    [EmailAddress(ErrorMessage = "Correo no válido.")]
    [StringLength(256)]
    public string CorreoElectronico { get; set; } = null!;

    // Residencia
    [Required(ErrorMessage = "La dirección es obligatoria.")]
    [StringLength(300)]
    public string Direccion { get; set; } = null!;

    [Required(ErrorMessage = "La ciudad es obligatoria.")]
    [StringLength(100)]
    public string Ciudad { get; set; } = null!;

    [Required(ErrorMessage = "El departamento es obligatorio.")]
    [StringLength(100)]
    public string Departamento { get; set; } = null!;

    // Contacto de emergencia
    [StringLength(200)]
    public string? ContactoEmergenciaNombre { get; set; }

    [StringLength(20)]
    public string? ContactoEmergenciaTelefono { get; set; }

    // Formación y seguridad social
    public NivelEscolaridad? NivelEscolaridad { get; set; }

    [StringLength(200)]
    public string? Eps { get; set; }

    [StringLength(200)]
    public string? Arl { get; set; }

    // Vinculación laboral
    [Required(ErrorMessage = "La sede es obligatoria.")]
    [Range(1, int.MaxValue, ErrorMessage = "Selecciona una sede válida.")]
    public int SedeId { get; set; }

    [Required(ErrorMessage = "El cargo es obligatorio.")]
    [Range(1, int.MaxValue, ErrorMessage = "Selecciona un cargo válido.")]
    public int CargoId { get; set; }

    [Required(ErrorMessage = "El rol en el sistema es obligatorio.")]
    public RolUsuario Rol { get; set; }

    [Required(ErrorMessage = "El tipo de vinculación es obligatorio.")]
    public TipoVinculacion TipoVinculacion { get; set; }

    public int? JefeInmediatoId { get; set; }

    public DateOnly? FechaIngreso { get; set; }

    [Range(0, 9999.9, ErrorMessage = "Los días deben ser un valor positivo.")]
    public decimal DiasVacacionesPrevios { get; set; }

    // Contrato temporal (obligatorio solo si TipoVinculacion == Temporal)
    public int? EmpresaTemporalId { get; set; }
    public DateOnly? FechaInicioContrato { get; set; }
    public DateOnly? FechaFinContrato { get; set; }
}
