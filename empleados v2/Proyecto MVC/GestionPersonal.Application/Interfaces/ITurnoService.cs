using GestionPersonal.Models.DTOs.Turno;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Interfaces;

public interface ITurnoService
{
    Task<IReadOnlyList<PlantillaTurnoDto>> ObtenerPlantillasActivasAsync(CancellationToken ct = default);
    Task<IReadOnlyList<PlantillaTurnoDto>> ObtenerPlantillasActivasPorCreadorAsync(int creadorEmpleadoId, CancellationToken ct = default);
    Task<ResultadoOperacion<PlantillaTurnoDto>> ObtenerPlantillaConDetallesAsync(int id, CancellationToken ct = default);
    Task<ResultadoOperacion> CrearPlantillaAsync(CrearPlantillaTurnoDto dto, int? creadoPorEmpleadoId = null, CancellationToken ct = default);
    Task<ResultadoOperacion> EditarPlantillaAsync(int id, CrearPlantillaTurnoDto dto, CancellationToken ct = default);
    Task<IReadOnlyList<AsignacionTurnoDto>> ObtenerAsignacionesPorSedeAsync(int sedeId, CancellationToken ct = default);
    Task<IReadOnlyList<AsignacionTurnoDto>> ObtenerHistorialPorEmpleadoAsync(int empleadoId, CancellationToken ct = default);
    Task<ResultadoOperacion> AsignarTurnoAsync(AsignarTurnoDto dto, int programadoPorUsuarioId, int? jefeEmpleadoId = null, CancellationToken ct = default);
    Task<ResultadoOperacion> EditarAsignacionAsync(EditarAsignacionDto dto, int usuarioId, CancellationToken ct = default);
    Task<ResultadoOperacion> EliminarAsignacionAsync(int asignacionId, int usuarioId, int? usuarioEmpleadoId, CancellationToken ct = default);
}
