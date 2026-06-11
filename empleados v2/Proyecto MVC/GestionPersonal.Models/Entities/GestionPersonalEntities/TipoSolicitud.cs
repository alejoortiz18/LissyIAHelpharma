namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class TipoSolicitud
{
    public int Id { get; set; }
    public string Nombre { get; set; } = null!;
    /// <summary>Valor almacenado en EventosLaborales.TipoEvento.</summary>
    public string Codigo { get; set; } = null!;
    public bool EsVacaciones { get; set; }
    public string Estado { get; set; } = null!;
    public DateTime FechaCreacion { get; set; }
    public DateTime? FechaModificacion { get; set; }
}
