using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Interfaces;

public interface IEmpleadoService
{
    Task<IReadOnlyList<EmpleadoListaDto>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default);
    Task<IReadOnlyList<EmpleadoListaDto>> ObtenerTodosAsync(CancellationToken ct = default);
    Task<ResultadoOperacion<EmpleadoDto>> ObtenerPerfilAsync(int id, CancellationToken ct = default);
    Task<ResultadoOperacion<EmpleadoDto>> ObtenerParaEditarAsync(int id, CancellationToken ct = default);
    Task<ResultadoOperacion> CrearAsync(CrearEmpleadoDto dto, int creadoPorUsuarioId, CancellationToken ct = default);
    Task<ResultadoOperacion> EditarAsync(EditarEmpleadoDto dto, int modificadoPorUsuarioId, CancellationToken ct = default);
    Task<ResultadoOperacion> DesvincularAsync(DesvincularEmpleadoDto dto, int registradoPorUsuarioId, CancellationToken ct = default);
}
