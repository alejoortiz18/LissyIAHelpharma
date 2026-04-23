using GestionPersonal.Application.Interfaces;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.DTOs.Catalogos;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Services;

public class CatalogoService : ICatalogoService
{
    private readonly ICatalogoRepository _repo;

    public CatalogoService(ICatalogoRepository repo) => _repo = repo;

    public Task<IReadOnlyList<Sede>> ObtenerSedesActivasAsync(CancellationToken ct = default)
        => _repo.ObtenerSedesActivasAsync(ct);

    public Task<IReadOnlyList<Cargo>> ObtenerCargosActivosAsync(CancellationToken ct = default)
        => _repo.ObtenerCargosActivosAsync(ct);

    public Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesActivasAsync(CancellationToken ct = default)
        => _repo.ObtenerEmpresasTemporalesActivasAsync(ct);

    public async Task<ResultadoOperacion> CrearSedeAsync(CrearSedeDto dto)
    {
        try
        {
            var sede = new Sede
            {
                Nombre        = dto.Nombre.Trim(),
                Ciudad        = dto.Ciudad.Trim(),
                Direccion     = dto.Direccion.Trim(),
                Estado        = "Activa",
                FechaCreacion = DateTime.UtcNow,
            };
            _repo.AgregarSede(sede);
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Sede creada correctamente.");
        }
        catch (Exception ex) when (ex.Message.Contains("UX_Sedes_Nombre") ||
                                   (ex.InnerException?.Message.Contains("UX_Sedes_Nombre") ?? false))
        {
            return ResultadoOperacion.Fail("Ya existe una sede con ese nombre.");
        }
        catch
        {
            return ResultadoOperacion.Fail("No se pudo crear la sede. Verifique los datos e intente nuevamente.");
        }
    }

    public async Task<ResultadoOperacion> CrearCargoAsync(CrearCargoDto dto)
    {
        try
        {
            var cargo = new Cargo
            {
                Nombre        = dto.Nombre.Trim(),
                Estado        = "Activo",
                FechaCreacion = DateTime.UtcNow,
            };
            _repo.AgregarCargo(cargo);
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Cargo creado correctamente.");
        }
        catch (Exception ex) when (ex.Message.Contains("UX_Cargos_Nombre") ||
                                   (ex.InnerException?.Message.Contains("UX_Cargos_Nombre") ?? false))
        {
            return ResultadoOperacion.Fail("Ya existe un cargo con ese nombre.");
        }
        catch
        {
            return ResultadoOperacion.Fail("No se pudo crear el cargo. Verifique los datos e intente nuevamente.");
        }
    }

    public async Task<ResultadoOperacion> CrearEmpresaTemporalAsync(CrearEmpresaTemporalDto dto)
    {
        try
        {
            var empresa = new EmpresaTemporal
            {
                Nombre        = dto.Nombre.Trim(),
                Estado        = "Activa",
                FechaCreacion = DateTime.UtcNow,
            };
            _repo.AgregarEmpresaTemporal(empresa);
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Empresa temporal creada correctamente.");
        }
        catch (Exception ex) when (ex.Message.Contains("UX_EmpresasTemporales_Nombre") ||
                                   (ex.InnerException?.Message.Contains("UX_EmpresasTemporales_Nombre") ?? false))
        {
            return ResultadoOperacion.Fail("Ya existe una empresa temporal con ese nombre.");
        }
        catch
        {
            return ResultadoOperacion.Fail("No se pudo crear la empresa temporal. Verifique los datos e intente nuevamente.");
        }
    }

    public async Task<ResultadoOperacion> EditarSedeAsync(EditarSedeDto dto)
    {
        var sede = await _repo.ObtenerSedePorIdAsync(dto.Id);
        if (sede is null) return ResultadoOperacion.Fail("Sede no encontrada.");

        try
        {
            sede.Nombre            = dto.Nombre.Trim();
            sede.Ciudad            = dto.Ciudad.Trim();
            sede.Direccion         = dto.Direccion.Trim();
            sede.FechaModificacion = DateTime.UtcNow;
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Sede actualizada correctamente.");
        }
        catch (Exception ex) when (ex.Message.Contains("UX_Sedes_Nombre") ||
                                   (ex.InnerException?.Message.Contains("UX_Sedes_Nombre") ?? false))
        {
            return ResultadoOperacion.Fail("Ya existe otra sede con ese nombre.");
        }
        catch
        {
            return ResultadoOperacion.Fail("No se pudo actualizar la sede. Verifique los datos e intente nuevamente.");
        }
    }

    public async Task<ResultadoOperacion> EditarCargoAsync(EditarCargoDto dto)
    {
        var cargo = await _repo.ObtenerCargoPorIdAsync(dto.Id);
        if (cargo is null) return ResultadoOperacion.Fail("Cargo no encontrado.");

        try
        {
            cargo.Nombre            = dto.Nombre.Trim();
            cargo.FechaModificacion = DateTime.UtcNow;
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Cargo actualizado correctamente.");
        }
        catch (Exception ex) when (ex.Message.Contains("UX_Cargos_Nombre") ||
                                   (ex.InnerException?.Message.Contains("UX_Cargos_Nombre") ?? false))
        {
            return ResultadoOperacion.Fail("Ya existe otro cargo con ese nombre.");
        }
        catch
        {
            return ResultadoOperacion.Fail("No se pudo actualizar el cargo. Verifique los datos e intente nuevamente.");
        }
    }

    public async Task<ResultadoOperacion> EditarEmpresaTemporalAsync(EditarEmpresaTemporalDto dto)
    {
        var empresa = await _repo.ObtenerEmpresaTemporalPorIdAsync(dto.Id);
        if (empresa is null) return ResultadoOperacion.Fail("Empresa temporal no encontrada.");

        try
        {
            empresa.Nombre            = dto.Nombre.Trim();
            empresa.FechaModificacion = DateTime.UtcNow;
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Empresa temporal actualizada correctamente.");
        }
        catch (Exception ex) when (ex.Message.Contains("UX_EmpresasTemporales_Nombre") ||
                                   (ex.InnerException?.Message.Contains("UX_EmpresasTemporales_Nombre") ?? false))
        {
            return ResultadoOperacion.Fail("Ya existe otra empresa temporal con ese nombre.");
        }
        catch
        {
            return ResultadoOperacion.Fail("No se pudo actualizar la empresa temporal. Verifique los datos e intente nuevamente.");
        }
    }
}
