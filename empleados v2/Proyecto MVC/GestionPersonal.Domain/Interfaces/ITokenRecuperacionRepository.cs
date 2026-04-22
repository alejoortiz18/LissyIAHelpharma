using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Domain.Interfaces;

public interface ITokenRecuperacionRepository
{
    Task<TokenRecuperacion?> ObtenerTokenActivoAsync(string token, CancellationToken ct = default);

    void Agregar(TokenRecuperacion tokenRecuperacion);
    void Actualizar(TokenRecuperacion tokenRecuperacion);

    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}
