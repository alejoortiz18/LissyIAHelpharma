namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class TokenRecuperacion
{
    public int Id { get; set; }
    public int UsuarioId { get; set; }
    public string Token { get; set; } = null!;
    public DateTime FechaExpiracion { get; set; }
    public bool Usado { get; set; }
    public DateTime FechaCreacion { get; set; }

    public virtual Usuario Usuario { get; set; } = null!;
}
