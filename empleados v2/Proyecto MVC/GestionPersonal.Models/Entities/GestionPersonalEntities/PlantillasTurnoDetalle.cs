namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class PlantillaTurnoDetalle
{
    public int Id { get; set; }
    public int PlantillaTurnoId { get; set; }
    public byte DiaSemana { get; set; }
    public TimeOnly? HoraEntrada { get; set; }
    public TimeOnly? HoraSalida { get; set; }

    public virtual PlantillaTurno PlantillaTurno { get; set; } = null!;
}
