using GestionPersonal.Models.DTOs.Catalogos;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Interfaces;

/// <summary>Provee las listas de catálogos (sedes, cargos, empresas temporales) para los dropdowns.</summary>
public interface ICatalogoService
{
    Task<IReadOnlyList<Sede>> ObtenerSedesActivasAsync(CancellationToken ct = default);
    Task<IReadOnlyList<Cargo>> ObtenerCargosActivosAsync(CancellationToken ct = default);
    Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesActivasAsync(CancellationToken ct = default);

    Task<ResultadoOperacion> CrearSedeAsync(CrearSedeDto dto);
    Task<ResultadoOperacion> CrearCargoAsync(CrearCargoDto dto);
    Task<ResultadoOperacion> CrearEmpresaTemporalAsync(CrearEmpresaTemporalDto dto);

    Task<ResultadoOperacion> EditarSedeAsync(EditarSedeDto dto);
    Task<ResultadoOperacion> EditarCargoAsync(EditarCargoDto dto);
    Task<ResultadoOperacion> EditarEmpresaTemporalAsync(EditarEmpresaTemporalDto dto);
}
