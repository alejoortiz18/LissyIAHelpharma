namespace GestionPersonal.Models.DTOs.Catalogos;

public class RolSistemaDetalleDto
{
    public int Id { get; init; }
    public string Codigo { get; init; } = string.Empty;
    public string Nombre { get; init; } = string.Empty;
    public string? Descripcion { get; init; }
    public bool EsRolSistema { get; init; }
    public string Estado { get; init; } = string.Empty;
    public IReadOnlyList<int> PermisoIds { get; init; } = [];
}
