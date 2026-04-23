using GestionPersonal.Application.Interfaces;
using GestionPersonal.Constants.Messages;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.DTOs.Turno;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Services;

public class TurnoService : ITurnoService
{
    private readonly ITurnoRepository _repo;

    public TurnoService(ITurnoRepository repo) => _repo = repo;

    public async Task<IReadOnlyList<PlantillaTurnoDto>> ObtenerPlantillasActivasAsync(CancellationToken ct = default)
    {
        var lista = await _repo.ObtenerActivasAsync(ct);
        return lista.Select(MapToDto).ToList();
    }

    public async Task<ResultadoOperacion<PlantillaTurnoDto>> ObtenerPlantillaConDetallesAsync(int id, CancellationToken ct = default)
    {
        var plantilla = await _repo.ObtenerPorIdConDetallesAsync(id, ct);
        if (plantilla is null)
            return new ResultadoOperacion<PlantillaTurnoDto> { Exito = false, Mensaje = TurnoConstant.TurnoNoEncontrado };

        return ResultadoOperacion<PlantillaTurnoDto>.Ok(MapToDto(plantilla));
    }

    public async Task<ResultadoOperacion> EditarPlantillaAsync(int id, CrearPlantillaTurnoDto dto, CancellationToken ct = default)
    {
        var plantilla = await _repo.ObtenerPorIdConDetallesAsync(id, ct);
        if (plantilla is null)
            return ResultadoOperacion.Fail(TurnoConstant.TurnoNoEncontrado);

        if (await _repo.ExisteNombreAsync(dto.Nombre, excluirId: id, ct: ct))
            return ResultadoOperacion.Fail("Ya existe una plantilla con ese nombre.");

        plantilla.Nombre = dto.Nombre;
        plantilla.FechaModificacion = DateTime.UtcNow;

        _repo.EliminarDetalles(plantilla.PlantillaTurnoDetalles);
        plantilla.PlantillaTurnoDetalles = dto.Detalles.Select(d => new PlantillaTurnoDetalle
        {
            DiaSemana   = d.DiaSemana,
            HoraEntrada = d.HoraEntrada,
            HoraSalida  = d.HoraSalida
        }).ToList();

        await _repo.GuardarCambiosAsync(ct);
        return ResultadoOperacion.Ok("Plantilla actualizada correctamente.");
    }

    public async Task<IReadOnlyList<AsignacionTurnoDto>> ObtenerAsignacionesPorSedeAsync(int sedeId, CancellationToken ct = default)
    {
        var lista = await _repo.ObtenerAsignacionesActivasPorSedeAsync(sedeId, ct);
        return lista
            .GroupBy(a => a.EmpleadoId)
            .Select(g => g.OrderByDescending(a => a.FechaVigencia).First())
            .Select(a => new AsignacionTurnoDto
            {
                EmpleadoId      = a.EmpleadoId,
                EmpleadoNombre  = a.Empleado.NombreCompleto,
                SedeNombre      = a.Empleado.Sede.Nombre,
                PlantillaTurnoId = a.PlantillaTurnoId,
                PlantillaNombre = a.PlantillaTurno.Nombre,
                FechaVigencia   = a.FechaVigencia.ToString("dd/MM/yyyy"),
                AsignadoPor     = a.ProgramadoPorNavigation.CorreoAcceso,
            })
            .OrderBy(r => r.EmpleadoNombre)
            .ToList();
    }

    public async Task<ResultadoOperacion> CrearPlantillaAsync(CrearPlantillaTurnoDto dto, CancellationToken ct = default)
    {
        if (await _repo.ExisteNombreAsync(dto.Nombre, ct: ct))
            return ResultadoOperacion.Fail("Ya existe una plantilla con ese nombre.");

        var plantilla = new PlantillaTurno
        {
            Nombre        = dto.Nombre,
            Estado        = "Activa",
            FechaCreacion = DateTime.UtcNow,
            PlantillaTurnoDetalles = dto.Detalles.Select(d => new PlantillaTurnoDetalle
            {
                DiaSemana  = d.DiaSemana,
                HoraEntrada = d.HoraEntrada,
                HoraSalida  = d.HoraSalida
            }).ToList()
        };

        _repo.AgregarPlantilla(plantilla);
        await _repo.GuardarCambiosAsync(ct);

        return ResultadoOperacion.Ok(TurnoConstant.TurnoCreado);
    }

    public async Task<ResultadoOperacion> AsignarTurnoAsync(AsignarTurnoDto dto, int programadoPorUsuarioId, CancellationToken ct = default)
    {
        var plantilla = await _repo.ObtenerPorIdAsync(dto.PlantillaTurnoId, ct);
        if (plantilla is null)
            return ResultadoOperacion.Fail(TurnoConstant.TurnoNoEncontrado);

        var asignacion = new AsignacionTurno
        {
            EmpleadoId      = dto.EmpleadoId,
            PlantillaTurnoId = dto.PlantillaTurnoId,
            FechaVigencia   = dto.FechaVigencia,
            ProgramadoPor   = programadoPorUsuarioId,
            FechaCreacion   = DateTime.UtcNow
        };

        _repo.AgregarAsignacion(asignacion);
        await _repo.GuardarCambiosAsync(ct);

        return ResultadoOperacion.Ok("Turno asignado exitosamente.");
    }

    public async Task<IReadOnlyList<AsignacionTurnoDto>> ObtenerHistorialPorEmpleadoAsync(
        int empleadoId, CancellationToken ct = default)
    {
        var lista = await _repo.ObtenerHistorialPorEmpleadoAsync(empleadoId, ct);
        return lista.Select(a => new AsignacionTurnoDto
        {
            Id               = a.Id,
            EmpleadoId       = a.EmpleadoId,
            EmpleadoNombre   = string.Empty,
            SedeNombre       = string.Empty,
            PlantillaTurnoId = a.PlantillaTurnoId,
            PlantillaNombre  = a.PlantillaTurno.Nombre,
            FechaVigencia    = a.FechaVigencia.ToString("dd/MM/yyyy"),
            AsignadoPor      = a.ProgramadoPorNavigation.CorreoAcceso,
        }).ToList();
    }

    public async Task<ResultadoOperacion> EditarAsignacionAsync(
        EditarAsignacionDto dto, int usuarioId, CancellationToken ct = default)
    {
        var asignacion = await _repo.ObtenerAsignacionPorIdAsync(dto.Id, ct);
        if (asignacion is null)
            return ResultadoOperacion.Fail("Asignación no encontrada.");

        var plantilla = await _repo.ObtenerPorIdAsync(dto.PlantillaTurnoId, ct);
        if (plantilla is null)
            return ResultadoOperacion.Fail(TurnoConstant.TurnoNoEncontrado);

        asignacion.PlantillaTurnoId = dto.PlantillaTurnoId;
        asignacion.FechaVigencia    = dto.FechaVigencia;
        asignacion.ProgramadoPor    = usuarioId;

        await _repo.GuardarCambiosAsync(ct);
        return ResultadoOperacion.Ok("Asignación actualizada exitosamente.");
    }

    private static PlantillaTurnoDto MapToDto(PlantillaTurno p) => new()
    {
        Id     = p.Id,
        Nombre = p.Nombre,
        Estado = p.Estado,
        Detalles = p.PlantillaTurnoDetalles
            .OrderBy(d => d.DiaSemana)
            .Select(d => new PlantillaTurnoDetalleDto
            {
                DiaSemana  = d.DiaSemana,
                HoraEntrada = d.HoraEntrada?.ToString("HH:mm"),
                HoraSalida  = d.HoraSalida?.ToString("HH:mm")
            }).ToList()
    };
}
