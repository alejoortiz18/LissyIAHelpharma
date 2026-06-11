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

    public Task<IReadOnlyList<Sede>> ObtenerTodasSedesAsync(CancellationToken ct = default)
        => _repo.ObtenerTodasSedesAsync(ct);

    public Task<IReadOnlyList<Sede>> ObtenerSedesParaSelectAsync(int? incluirId, CancellationToken ct = default)
        => _repo.ObtenerSedesParaSelectAsync(incluirId, ct);

    public Task<IReadOnlyList<Cargo>> ObtenerCargosActivosAsync(CancellationToken ct = default)
        => _repo.ObtenerCargosActivosAsync(ct);

    public Task<IReadOnlyList<Cargo>> ObtenerTodosCargosAsync(CancellationToken ct = default)
        => _repo.ObtenerTodosCargosAsync(ct);

    public Task<IReadOnlyList<Cargo>> ObtenerCargosParaSelectAsync(int? incluirId, CancellationToken ct = default)
        => _repo.ObtenerCargosParaSelectAsync(incluirId, ct);

    public Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesActivasAsync(CancellationToken ct = default)
        => _repo.ObtenerEmpresasTemporalesActivasAsync(ct);

    public Task<IReadOnlyList<EmpresaTemporal>> ObtenerTodasEmpresasTemporalesAsync(CancellationToken ct = default)
        => _repo.ObtenerTodasEmpresasTemporalesAsync(ct);

    public Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesParaSelectAsync(int? incluirId, CancellationToken ct = default)
        => _repo.ObtenerEmpresasTemporalesParaSelectAsync(incluirId, ct);

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

    public async Task<ResultadoOperacion> DarDeBajaSedeAsync(int id)
    {
        var sede = await _repo.ObtenerSedePorIdAsync(id);
        if (sede is null) return ResultadoOperacion.Fail("Sede no encontrada.");
        if (sede.Estado == "Inactiva")
            return ResultadoOperacion.Fail("La sede ya está inactiva.");

        var (usuarios, empleados) = await _repo.ContarUsoSedeAsync(id);
        var enUso = usuarios + empleados;
        if (enUso == 0)
        {
            _repo.EliminarSede(sede);
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Sede eliminada correctamente.");
        }

        sede.Estado = "Inactiva";
        sede.FechaModificacion = DateTime.UtcNow;
        await _repo.GuardarCambiosAsync();
        return ResultadoOperacion.Ok(
            $"La sede está asignada a {enUso} usuario(s) o empleado(s). Se inactivó y ya no aparecerá en los listados de asignación.");
    }

    public async Task<ResultadoOperacion> ActivarSedeAsync(int id)
    {
        var sede = await _repo.ObtenerSedePorIdAsync(id);
        if (sede is null) return ResultadoOperacion.Fail("Sede no encontrada.");
        sede.Estado = "Activa";
        sede.FechaModificacion = DateTime.UtcNow;
        await _repo.GuardarCambiosAsync();
        return ResultadoOperacion.Ok("Sede activada correctamente.");
    }

    public async Task<ResultadoOperacion> DarDeBajaCargoAsync(int id)
    {
        var cargo = await _repo.ObtenerCargoPorIdAsync(id);
        if (cargo is null) return ResultadoOperacion.Fail("Cargo no encontrado.");
        if (cargo.Estado == "Inactivo")
            return ResultadoOperacion.Fail("El cargo ya está inactivo.");

        var enUso = await _repo.ContarUsoCargoAsync(id);
        if (enUso == 0)
        {
            _repo.EliminarCargo(cargo);
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Cargo eliminado correctamente.");
        }

        cargo.Estado = "Inactivo";
        cargo.FechaModificacion = DateTime.UtcNow;
        await _repo.GuardarCambiosAsync();
        return ResultadoOperacion.Ok(
            $"El cargo está asignado a {enUso} empleado(s). Se inactivó y ya no aparecerá en los listados de asignación.");
    }

    public async Task<ResultadoOperacion> ActivarCargoAsync(int id)
    {
        var cargo = await _repo.ObtenerCargoPorIdAsync(id);
        if (cargo is null) return ResultadoOperacion.Fail("Cargo no encontrado.");
        cargo.Estado = "Activo";
        cargo.FechaModificacion = DateTime.UtcNow;
        await _repo.GuardarCambiosAsync();
        return ResultadoOperacion.Ok("Cargo activado correctamente.");
    }

    public async Task<ResultadoOperacion> DarDeBajaEmpresaTemporalAsync(int id)
    {
        var empresa = await _repo.ObtenerEmpresaTemporalPorIdAsync(id);
        if (empresa is null) return ResultadoOperacion.Fail("Empresa temporal no encontrada.");
        if (empresa.Estado == "Inactiva")
            return ResultadoOperacion.Fail("La empresa ya está inactiva.");

        var enUso = await _repo.ContarUsoEmpresaTemporalAsync(id);
        if (enUso == 0)
        {
            _repo.EliminarEmpresaTemporal(empresa);
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Empresa temporal eliminada correctamente.");
        }

        empresa.Estado = "Inactiva";
        empresa.FechaModificacion = DateTime.UtcNow;
        await _repo.GuardarCambiosAsync();
        return ResultadoOperacion.Ok(
            $"La empresa está asignada a {enUso} empleado(s). Se inactivó y ya no aparecerá en los listados de asignación.");
    }

    public async Task<ResultadoOperacion> ActivarEmpresaTemporalAsync(int id)
    {
        var empresa = await _repo.ObtenerEmpresaTemporalPorIdAsync(id);
        if (empresa is null) return ResultadoOperacion.Fail("Empresa temporal no encontrada.");
        empresa.Estado = "Activa";
        empresa.FechaModificacion = DateTime.UtcNow;
        await _repo.GuardarCambiosAsync();
        return ResultadoOperacion.Ok("Empresa temporal activada correctamente.");
    }

    public Task<IReadOnlyList<TipoSolicitud>> ObtenerTiposSolicitudActivosAsync(CancellationToken ct = default)
        => _repo.ObtenerTiposSolicitudActivosAsync(ct);

    public Task<IReadOnlyList<TipoSolicitud>> ObtenerTodosTiposSolicitudAsync(CancellationToken ct = default)
        => _repo.ObtenerTodosTiposSolicitudAsync(ct);

    public Task<TipoSolicitud?> ObtenerTipoSolicitudActivoPorCodigoAsync(string codigo, CancellationToken ct = default)
        => _repo.ObtenerTipoSolicitudActivoPorCodigoAsync(codigo.Trim(), ct);

    public async Task<ResultadoOperacion> CrearTipoSolicitudAsync(CrearTipoSolicitudDto dto)
    {
        try
        {
            var codigo = dto.Codigo.Trim();
            var tipo = new TipoSolicitud
            {
                Nombre        = dto.Nombre.Trim(),
                Codigo        = codigo,
                EsVacaciones  = dto.EsVacaciones,
                Estado        = "Activo",
                FechaCreacion = DateTime.UtcNow,
            };
            _repo.AgregarTipoSolicitud(tipo);
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Tipo de solicitud creado correctamente.");
        }
        catch (Exception ex) when (ex.Message.Contains("UX_TiposSolicitud_Codigo") ||
                                   (ex.InnerException?.Message.Contains("UX_TiposSolicitud_Codigo") ?? false))
        {
            return ResultadoOperacion.Fail("Ya existe un tipo de solicitud con ese código.");
        }
        catch
        {
            return ResultadoOperacion.Fail("No se pudo crear el tipo de solicitud. Verifique los datos e intente nuevamente.");
        }
    }

    public async Task<ResultadoOperacion> EditarTipoSolicitudAsync(EditarTipoSolicitudDto dto)
    {
        var tipo = await _repo.ObtenerTipoSolicitudPorIdAsync(dto.Id);
        if (tipo is null) return ResultadoOperacion.Fail("Tipo de solicitud no encontrado.");

        try
        {
            tipo.Nombre            = dto.Nombre.Trim();
            tipo.EsVacaciones      = dto.EsVacaciones;
            tipo.FechaModificacion = DateTime.UtcNow;
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Tipo de solicitud actualizado correctamente.");
        }
        catch
        {
            return ResultadoOperacion.Fail("No se pudo actualizar el tipo de solicitud.");
        }
    }

    public async Task<ResultadoOperacion> DarDeBajaTipoSolicitudAsync(int id)
    {
        var tipo = await _repo.ObtenerTipoSolicitudPorIdAsync(id);
        if (tipo is null) return ResultadoOperacion.Fail("Tipo de solicitud no encontrado.");
        if (tipo.Estado == "Inactivo")
            return ResultadoOperacion.Fail("El tipo ya está inactivo.");

        var enUso = await _repo.ContarUsoTipoSolicitudAsync(tipo.Codigo);
        if (enUso == 0)
        {
            _repo.EliminarTipoSolicitud(tipo);
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Tipo de solicitud eliminado correctamente.");
        }

        tipo.Estado = "Inactivo";
        tipo.FechaModificacion = DateTime.UtcNow;
        await _repo.GuardarCambiosAsync();
        return ResultadoOperacion.Ok(
            $"El tipo está en {enUso} solicitud(es) registrada(s). Se inactivó y ya no aparecerá al crear nuevas solicitudes.");
    }

    public async Task<ResultadoOperacion> ActivarTipoSolicitudAsync(int id)
    {
        var tipo = await _repo.ObtenerTipoSolicitudPorIdAsync(id);
        if (tipo is null) return ResultadoOperacion.Fail("Tipo de solicitud no encontrado.");
        tipo.Estado = "Activo";
        tipo.FechaModificacion = DateTime.UtcNow;
        await _repo.GuardarCambiosAsync();
        return ResultadoOperacion.Ok("Tipo de solicitud activado correctamente.");
    }
}
