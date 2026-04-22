namespace GestionPersonal.Models.Models;

public class PaginacionModel
{
    public int Pagina        { get; set; } = 1;
    public int TamanioPagina { get; set; } = 10;

    public static readonly int[] OpcionesTamanio = [10, 25, 50, 100];
}
