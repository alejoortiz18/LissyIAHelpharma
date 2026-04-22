using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Application.Interfaces;

/// <summary>Provee las listas de catálogos (sedes, cargos, empresas temporales) para los dropdowns.</summary>
public interface ICatalogoService
{
    Task<IReadOnlyList<Sede>> ObtenerSedesActivasAsync(CancellationToken ct = default);
    Task<IReadOnlyList<Cargo>> ObtenerCargosActivosAsync(CancellationToken ct = default);
    Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesActivasAsync(CancellationToken ct = default);
}
