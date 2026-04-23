using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Domain.Interfaces;

public interface ICatalogoRepository
{
    // Sedes
    Task<IReadOnlyList<Sede>> ObtenerSedesActivasAsync(CancellationToken ct = default);
    Task<Sede?> ObtenerSedePorIdAsync(int id, CancellationToken ct = default);

    // Cargos
    Task<IReadOnlyList<Cargo>> ObtenerCargosActivosAsync(CancellationToken ct = default);
    Task<Cargo?> ObtenerCargoPorIdAsync(int id, CancellationToken ct = default);

    // Empresas Temporales
    Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesActivasAsync(CancellationToken ct = default);
    Task<EmpresaTemporal?> ObtenerEmpresaTemporalPorIdAsync(int id, CancellationToken ct = default);

    // Creación
    void AgregarSede(Sede sede);
    void AgregarCargo(Cargo cargo);
    void AgregarEmpresaTemporal(EmpresaTemporal empresa);

    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}
