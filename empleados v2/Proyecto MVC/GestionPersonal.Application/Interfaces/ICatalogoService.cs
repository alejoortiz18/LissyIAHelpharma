using GestionPersonal.Models.DTOs.Catalogos;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Interfaces;

/// <summary>Provee las listas de catálogos (sedes, cargos, empresas temporales) para los dropdowns.</summary>
public interface ICatalogoService
{
    Task<IReadOnlyList<Sede>> ObtenerSedesActivasAsync(CancellationToken ct = default);
    Task<IReadOnlyList<Sede>> ObtenerTodasSedesAsync(CancellationToken ct = default);
    Task<IReadOnlyList<Sede>> ObtenerSedesParaSelectAsync(int? incluirId, CancellationToken ct = default);

    Task<IReadOnlyList<Cargo>> ObtenerCargosActivosAsync(CancellationToken ct = default);
    Task<IReadOnlyList<Cargo>> ObtenerTodosCargosAsync(CancellationToken ct = default);
    Task<IReadOnlyList<Cargo>> ObtenerCargosParaSelectAsync(int? incluirId, CancellationToken ct = default);

    Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesActivasAsync(CancellationToken ct = default);
    Task<IReadOnlyList<EmpresaTemporal>> ObtenerTodasEmpresasTemporalesAsync(CancellationToken ct = default);
    Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesParaSelectAsync(int? incluirId, CancellationToken ct = default);

    Task<ResultadoOperacion> CrearSedeAsync(CrearSedeDto dto);
    Task<ResultadoOperacion> CrearCargoAsync(CrearCargoDto dto);
    Task<ResultadoOperacion> CrearEmpresaTemporalAsync(CrearEmpresaTemporalDto dto);

    Task<ResultadoOperacion> EditarSedeAsync(EditarSedeDto dto);
    Task<ResultadoOperacion> EditarCargoAsync(EditarCargoDto dto);
    Task<ResultadoOperacion> EditarEmpresaTemporalAsync(EditarEmpresaTemporalDto dto);

    Task<ResultadoOperacion> DarDeBajaSedeAsync(int id);
    Task<ResultadoOperacion> ActivarSedeAsync(int id);
    Task<ResultadoOperacion> DarDeBajaCargoAsync(int id);
    Task<ResultadoOperacion> ActivarCargoAsync(int id);
    Task<ResultadoOperacion> DarDeBajaEmpresaTemporalAsync(int id);
    Task<ResultadoOperacion> ActivarEmpresaTemporalAsync(int id);

    Task<IReadOnlyList<TipoSolicitud>> ObtenerTiposSolicitudActivosAsync(CancellationToken ct = default);
    Task<IReadOnlyList<TipoSolicitud>> ObtenerTodosTiposSolicitudAsync(CancellationToken ct = default);
    Task<TipoSolicitud?> ObtenerTipoSolicitudActivoPorCodigoAsync(string codigo, CancellationToken ct = default);

    Task<ResultadoOperacion> CrearTipoSolicitudAsync(CrearTipoSolicitudDto dto);
    Task<ResultadoOperacion> EditarTipoSolicitudAsync(EditarTipoSolicitudDto dto);
    Task<ResultadoOperacion> DarDeBajaTipoSolicitudAsync(int id);
    Task<ResultadoOperacion> ActivarTipoSolicitudAsync(int id);
}
