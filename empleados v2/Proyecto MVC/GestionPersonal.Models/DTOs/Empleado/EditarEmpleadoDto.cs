using System.ComponentModel.DataAnnotations;
using GestionPersonal.Models.Enums;

namespace GestionPersonal.Models.DTOs.Empleado;

/// <summary>DTO de entrada para editar un empleado existente.</summary>
public class EditarEmpleadoDto
{
    public int Id { get; set; }

    // Datos personales
    [Required(ErrorMessage = "El nombre completo es obligatorio.")]
    [StringLength(200)]
    public string NombreCompleto { get; set; } = null!;

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
    [Required(ErrorMessage = "El nombre del contacto de emergencia es obligatorio.")]
    [StringLength(200)]
    public string ContactoEmergenciaNombre { get; set; } = null!;

    [Required(ErrorMessage = "El teléfono del contacto de emergencia es obligatorio.")]
    [StringLength(20)]
    public string ContactoEmergenciaTelefono { get; set; } = null!;

    // Formación y seguridad social
    public NivelEscolaridad? NivelEscolaridad { get; set; }

    [Required(ErrorMessage = "La EPS es obligatoria.")]
    [StringLength(200)]
    public string Eps { get; set; } = null!;

    [StringLength(200)]
    public string? Arl { get; set; }

    // Vinculación laboral (Jefe puede cambiar sede/cargo/rol)
    [Required(ErrorMessage = "La sede es obligatoria.")]
    [Range(1, int.MaxValue, ErrorMessage = "Selecciona una sede válida.")]
    public int SedeId { get; set; }

    [Required(ErrorMessage = "El cargo es obligatorio.")]
    [Range(1, int.MaxValue, ErrorMessage = "Selecciona un cargo válido.")]
    public int CargoId { get; set; }

    public int? JefeInmediatoId { get; set; }

    [Range(0, 9999.9, ErrorMessage = "Los días deben ser un valor positivo.")]
    public decimal DiasVacacionesPrevios { get; set; }

    // Contrato temporal
    public int? EmpresaTemporalId { get; set; }
    public DateOnly? FechaInicioContrato { get; set; }
    public DateOnly? FechaFinContrato { get; set; }
}
