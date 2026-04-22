using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Domain.Interfaces;

public interface IUsuarioRepository
{
    Task<Usuario?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<Usuario?> ObtenerPorCorreoAsync(string correo, CancellationToken ct = default);
    Task<bool> ExisteCorreoAsync(string correo, int? excluirId = null, CancellationToken ct = default);

    void Agregar(Usuario usuario);
    void Actualizar(Usuario usuario);

    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}
