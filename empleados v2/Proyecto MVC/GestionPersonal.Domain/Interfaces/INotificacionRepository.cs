using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Domain.Interfaces;

public interface INotificacionRepository
{
    void Agregar(RegistroNotificacion registro);
    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}
