using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Domain.Interfaces;

public interface ICatalogoRepository
{
    Task<IReadOnlyList<Sede>> ObtenerSedesActivasAsync(CancellationToken ct = default);
    Task<IReadOnlyList<Sede>> ObtenerTodasSedesAsync(CancellationToken ct = default);
    Task<IReadOnlyList<Sede>> ObtenerSedesParaSelectAsync(int? incluirId, CancellationToken ct = default);
    Task<Sede?> ObtenerSedePorIdAsync(int id, CancellationToken ct = default);
    Task<(int Usuarios, int Empleados)> ContarUsoSedeAsync(int sedeId, CancellationToken ct = default);

    Task<IReadOnlyList<Cargo>> ObtenerCargosActivosAsync(CancellationToken ct = default);
    Task<IReadOnlyList<Cargo>> ObtenerTodosCargosAsync(CancellationToken ct = default);
    Task<IReadOnlyList<Cargo>> ObtenerCargosParaSelectAsync(int? incluirId, CancellationToken ct = default);
    Task<Cargo?> ObtenerCargoPorIdAsync(int id, CancellationToken ct = default);
    Task<int> ContarUsoCargoAsync(int cargoId, CancellationToken ct = default);

    Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesActivasAsync(CancellationToken ct = default);
    Task<IReadOnlyList<EmpresaTemporal>> ObtenerTodasEmpresasTemporalesAsync(CancellationToken ct = default);
    Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesParaSelectAsync(int? incluirId, CancellationToken ct = default);
    Task<EmpresaTemporal?> ObtenerEmpresaTemporalPorIdAsync(int id, CancellationToken ct = default);
    Task<int> ContarUsoEmpresaTemporalAsync(int empresaId, CancellationToken ct = default);

    void AgregarSede(Sede sede);
    void AgregarCargo(Cargo cargo);
    void AgregarEmpresaTemporal(EmpresaTemporal empresa);
    void EliminarSede(Sede sede);
    void EliminarCargo(Cargo cargo);
    void EliminarEmpresaTemporal(EmpresaTemporal empresa);

    Task<IReadOnlyList<TipoSolicitud>> ObtenerTiposSolicitudActivosAsync(CancellationToken ct = default);
    Task<IReadOnlyList<TipoSolicitud>> ObtenerTodosTiposSolicitudAsync(CancellationToken ct = default);
    Task<TipoSolicitud?> ObtenerTipoSolicitudPorIdAsync(int id, CancellationToken ct = default);
    Task<TipoSolicitud?> ObtenerTipoSolicitudActivoPorCodigoAsync(string codigo, CancellationToken ct = default);
    Task<int> ContarUsoTipoSolicitudAsync(string codigo, CancellationToken ct = default);

    void AgregarTipoSolicitud(TipoSolicitud tipo);
    void EliminarTipoSolicitud(TipoSolicitud tipo);

    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}
