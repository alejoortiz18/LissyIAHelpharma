namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class ContactoEmergencia
{
    public int Id { get; set; }
    public int EmpleadoId { get; set; }
    public string NombreContacto { get; set; } = null!;
    public string TelefonoContacto { get; set; } = null!;

    public virtual Empleado Empleado { get; set; } = null!;
}
