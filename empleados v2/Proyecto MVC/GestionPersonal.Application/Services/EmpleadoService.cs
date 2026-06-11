using GestionPersonal.Application.Interfaces;
using GestionPersonal.Constants;
using GestionPersonal.Constants.Messages;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Services;

public class EmpleadoService : IEmpleadoService
{
    private const int MesesFinContratoTemporalPorDefecto = 6;

    private readonly IEmpleadoRepository _repo;
    private readonly ICatalogoService _catalogoService;
    private readonly IUsuarioService _usuarioService;
    private readonly IHistorialDesvinculacionRepository _historialRepo;
    private readonly IEventoLaboralRepository _eventoRepo;

    public EmpleadoService(
        IEmpleadoRepository repo,
        ICatalogoService catalogoService,
        IUsuarioService usuarioService,
        IHistorialDesvinculacionRepository historialRepo,
        IEventoLaboralRepository eventoRepo)
    {
        _repo            = repo;
        _catalogoService = catalogoService;
        _usuarioService  = usuarioService;
        _historialRepo   = historialRepo;
        _eventoRepo      = eventoRepo;
    }

    public async Task<IReadOnlyList<EmpleadoListaDto>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default)
    {
        var hoy           = DateOnly.FromDateTime(DateTime.Today);
        var lista         = await _repo.ObtenerPorSedeAsync(sedeId, ct);
        var noDisponibles = (await _eventoRepo.ObtenerActivosHoyGlobalAsync(hoy, ct))
                                .Select(e => e.EmpleadoId).ToHashSet();
        return lista.Select(e => MapToListaDto(e, noDisponibles)).ToList();
    }

    public async Task<IReadOnlyList<EmpleadoListaDto>> ObtenerTodosAsync(CancellationToken ct = default)
    {
        var hoy           = DateOnly.FromDateTime(DateTime.Today);
        var lista         = await _repo.ObtenerTodosAsync(ct);
        var noDisponibles = (await _eventoRepo.ObtenerActivosHoyGlobalAsync(hoy, ct))
                                .Select(e => e.EmpleadoId).ToHashSet();
        return lista.Select(e => MapToListaDto(e, noDisponibles)).ToList();
    }

    public async Task<ResultadoOperacion<EmpleadoDto>> ObtenerPerfilAsync(int id, CancellationToken ct = default)
    {
        var emp = await _repo.ObtenerPorIdConDetallesAsync(id, ct);
        if (emp is null)
            return new ResultadoOperacion<EmpleadoDto> { Exito = false, Mensaje = EmpleadoConstant.EmpleadoNoEncontrado };

        return ResultadoOperacion<EmpleadoDto>.Ok(MapToDto(emp));
    }

    public async Task<ResultadoOperacion<EmpleadoDto>> ObtenerParaEditarAsync(int id, CancellationToken ct = default)
    {
        var emp = await _repo.ObtenerPorIdConDetallesAsync(id, ct);
        if (emp is null)
            return new ResultadoOperacion<EmpleadoDto> { Exito = false, Mensaje = EmpleadoConstant.EmpleadoNoEncontrado };

        return ResultadoOperacion<EmpleadoDto>.Ok(MapToDto(emp));
    }

    public async Task<ResultadoOperacion> CrearAsync(CrearEmpleadoDto dto, int creadoPorUsuarioId, CancellationToken ct = default)
    {
        if (await _repo.ExisteCedulaAsync(dto.Cedula, ct: ct))
            return ResultadoOperacion.Fail(EmpleadoConstant.CedulaDuplicada);

        if (await _repo.ExisteCorreoAsync(dto.CorreoElectronico, ct: ct))
            return ResultadoOperacion.Fail(EmpleadoConstant.CorreoElectronicoDuplicado);

        // FechaIngreso es obligatoria para cualquier tipo de vinculación
        if (dto.FechaIngreso is null)
            return ResultadoOperacion.Fail("La fecha de ingreso es obligatoria.");

        // Contrato directo: FechaInicioContrato obligatoria y >= FechaIngreso
        if (dto.TipoVinculacion == TipoVinculacion.Directo)
        {
            if (dto.FechaInicioContrato is null)
                return ResultadoOperacion.Fail("La fecha de inicio de contrato es obligatoria para contrato directo.");
            if (dto.FechaInicioContrato.Value < dto.FechaIngreso.Value)
                return ResultadoOperacion.Fail("La fecha de inicio de contrato no puede ser anterior a la fecha de ingreso.");
        }
        else if (dto.TipoVinculacion == TipoVinculacion.Temporal)
        {
            if (dto.EmpresaTemporalId is null or < 1)
                return ResultadoOperacion.Fail("La empresa temporal es obligatoria para contrato temporal.");
        }

        var fechaFinContrato = dto.TipoVinculacion == TipoVinculacion.Temporal
            ? ResolverFechaFinContratoTemporal(dto.FechaFinContrato, dto.FechaIngreso!.Value)
            : dto.FechaFinContrato;

        var cargoNombre = await ObtenerNombreCargoAsync(dto.CargoId, ct);
        var validacionJefe = await ValidarReglaJerarquiaJefeAsync(
            empleadoId: null,
            sedeId: dto.SedeId,
            cargoEmpleadoNombre: cargoNombre,
            jefeInmediatoId: dto.JefeInmediatoId,
            ct: ct);
        if (!validacionJefe.Exito) return validacionJefe;

        // Crear usuario de acceso
        var resultadoUsuario = await _usuarioService.CrearParaEmpleadoAsync(
            dto.CorreoElectronico, dto.Rol, dto.SedeId, dto.UrlBaseRestablecimiento, ct);

        if (!resultadoUsuario.Exito)
            return ResultadoOperacion.Fail(resultadoUsuario.Mensaje);

        var emp = new Empleado
        {
            NombreCompleto         = dto.NombreCompleto,
            Cedula                 = dto.Cedula,
            FechaNacimiento        = dto.FechaNacimiento,
            Telefono               = dto.Telefono,
            CorreoElectronico      = dto.CorreoElectronico,
            Direccion              = dto.Direccion,
            Ciudad                 = dto.Ciudad,
            Departamento           = dto.Departamento,
            NivelEscolaridad       = dto.NivelEscolaridad,
            Eps                    = dto.Eps,
            Arl                    = dto.Arl,
            SedeId                 = dto.SedeId,
            CargoId                = dto.CargoId,
            UsuarioId              = resultadoUsuario.Datos,
            JefeInmediatoId        = dto.JefeInmediatoId,
            TipoVinculacion        = dto.TipoVinculacion,
            FechaIngreso           = dto.FechaIngreso!.Value,
            DiasVacacionesPrevios  = dto.DiasVacacionesPrevios,
            EmpresaTemporalId      = dto.TipoVinculacion == TipoVinculacion.Temporal ? dto.EmpresaTemporalId : null,
            FechaInicioContrato    = dto.TipoVinculacion == TipoVinculacion.Directo ? dto.FechaInicioContrato : (DateOnly?)null,
            FechaFinContrato       = fechaFinContrato,
            Estado                 = EstadoEmpleado.Activo,
            FechaCreacion          = DateTime.UtcNow,
            CreadoPor              = creadoPorUsuarioId,
            ContactoEmergencia     = !string.IsNullOrWhiteSpace(dto.ContactoEmergenciaNombre)
                                     || !string.IsNullOrWhiteSpace(dto.ContactoEmergenciaTelefono)
                ? new ContactoEmergencia
                  {
                      NombreContacto   = dto.ContactoEmergenciaNombre ?? string.Empty,
                      TelefonoContacto = dto.ContactoEmergenciaTelefono ?? string.Empty
                  }
                : null
        };

        _repo.Agregar(emp);
        await _repo.GuardarCambiosAsync(ct);

        return ResultadoOperacion.Ok(EmpleadoConstant.EmpleadoCreado);
    }

    public async Task<ResultadoOperacion> EditarAsync(EditarEmpleadoDto dto, int modificadoPorUsuarioId, CancellationToken ct = default)
    {
        var emp = await _repo.ObtenerPorIdConDetallesAsync(dto.Id, ct);
        if (emp is null)
            return ResultadoOperacion.Fail(EmpleadoConstant.EmpleadoNoEncontrado);

        var cargoNombre = await ObtenerNombreCargoAsync(dto.CargoId, ct);
        var validacionJefe = await ValidarReglaJerarquiaJefeAsync(
            empleadoId: dto.Id,
            sedeId: dto.SedeId,
            cargoEmpleadoNombre: cargoNombre,
            jefeInmediatoId: dto.JefeInmediatoId,
            ct: ct);
        if (!validacionJefe.Exito) return validacionJefe;

        emp.NombreCompleto        = dto.NombreCompleto;
        emp.FechaNacimiento       = dto.FechaNacimiento;
        emp.Telefono              = dto.Telefono;
        emp.CorreoElectronico     = dto.CorreoElectronico;
        emp.Direccion             = dto.Direccion;
        emp.Ciudad                = dto.Ciudad;
        emp.Departamento          = dto.Departamento;
        emp.NivelEscolaridad      = dto.NivelEscolaridad;
        emp.Eps                   = dto.Eps;
        emp.Arl                   = dto.Arl;
        emp.SedeId                = dto.SedeId;
        emp.CargoId               = dto.CargoId;
        emp.JefeInmediatoId       = dto.JefeInmediatoId;
        emp.DiasVacacionesPrevios = dto.DiasVacacionesPrevios;
        emp.TipoVinculacion       = Enum.Parse<TipoVinculacion>(dto.TipoVinculacion);
        if (dto.TipoVinculacion == "Directo")
        {
            // Contrato directo: FechaInicioContrato obligatoria y >= FechaIngreso
            if (dto.FechaInicioContrato is null)
                return ResultadoOperacion.Fail("La fecha de inicio de contrato es obligatoria para contrato directo.");
            if (dto.FechaInicioContrato.Value < emp.FechaIngreso)
                return ResultadoOperacion.Fail("La fecha de inicio de contrato no puede ser anterior a la fecha de ingreso.");
            emp.EmpresaTemporalId   = null;
            emp.FechaInicioContrato = dto.FechaInicioContrato;
            emp.FechaFinContrato    = null;
        }
        else
        {
            if (dto.EmpresaTemporalId is null or < 1)
                return ResultadoOperacion.Fail("La empresa temporal es obligatoria para contrato temporal.");

            // Contrato temporal: FechaInicioContrato siempre null
            emp.EmpresaTemporalId   = dto.EmpresaTemporalId;
            emp.FechaInicioContrato = null;
            emp.FechaFinContrato    = ResolverFechaFinContratoTemporal(dto.FechaFinContrato, emp.FechaIngreso);
        }
        emp.FechaModificacion     = DateTime.UtcNow;
        emp.ModificadoPor         = modificadoPorUsuarioId;

        bool tieneContacto = !string.IsNullOrWhiteSpace(dto.ContactoEmergenciaNombre)
                             || !string.IsNullOrWhiteSpace(dto.ContactoEmergenciaTelefono);

        if (tieneContacto)
        {
            if (emp.ContactoEmergencia is not null)
            {
                emp.ContactoEmergencia.NombreContacto   = dto.ContactoEmergenciaNombre ?? string.Empty;
                emp.ContactoEmergencia.TelefonoContacto = dto.ContactoEmergenciaTelefono ?? string.Empty;
            }
            else
            {
                emp.ContactoEmergencia = new ContactoEmergencia
                {
                    EmpleadoId       = emp.Id,
                    NombreContacto   = dto.ContactoEmergenciaNombre ?? string.Empty,
                    TelefonoContacto = dto.ContactoEmergenciaTelefono ?? string.Empty
                };
            }
        }
        // Si ambos están vacíos, se preserva el contacto existente sin modificarlo

        if (emp.UsuarioId.HasValue)
        {
            var resUsuario = await _usuarioService.ActualizarParaEmpleadoAsync(
                emp.UsuarioId.Value, dto.CorreoElectronico, dto.Rol, dto.SedeId, ct);
            if (!resUsuario.Exito)
                return resUsuario;
        }

        _repo.Actualizar(emp);
        await _repo.GuardarCambiosAsync(ct);

        return ResultadoOperacion.Ok(EmpleadoConstant.EmpleadoActualizado);
    }

    public async Task<ResultadoOperacion> DesvincularAsync(DesvincularEmpleadoDto dto, int registradoPorUsuarioId, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(dto.MotivoRetiro))
            return ResultadoOperacion.Fail(EmpleadoConstant.MotivoRetiroObligatorio);

        var emp = await _repo.ObtenerPorIdAsync(dto.EmpleadoId, ct);
        if (emp is null)
            return ResultadoOperacion.Fail(EmpleadoConstant.EmpleadoNoEncontrado);

        emp.Estado            = EstadoEmpleado.Inactivo;
        emp.FechaModificacion = DateTime.UtcNow;
        emp.ModificadoPor     = registradoPorUsuarioId;

        var historial = new HistorialDesvinculacion
        {
            EmpleadoId          = emp.Id,
            MotivoRetiro        = dto.MotivoRetiro,
            FechaDesvinculacion = dto.FechaDesvinculacion,
            RegistradoPor       = registradoPorUsuarioId,
            FechaCreacion       = DateTime.UtcNow
        };

        _repo.Actualizar(emp);
        _historialRepo.Agregar(historial);
        await _repo.GuardarCambiosAsync(ct);

        return ResultadoOperacion.Ok(EmpleadoConstant.EmpleadoDesactivado);
    }

    public Task<bool> EsSubordinadoTransitivoAsync(
        int empleadoId, int jefeEmpleadoId, CancellationToken ct = default)
        => _repo.EsSubordinadoTransitivoAsync(empleadoId, jefeEmpleadoId, ct);

    public async Task<IReadOnlySet<int>> ObtenerDescendientesAsync(int jefeEmpleadoId, CancellationToken ct = default)
    {
        var todos = await _repo.ObtenerTodosAsync(ct);
        var porJefe = todos
            .Where(e => e.JefeInmediatoId.HasValue)
            .GroupBy(e => e.JefeInmediatoId!.Value)
            .ToDictionary(g => g.Key, g => g.Select(e => e.Id).ToList());

        var resultado = new HashSet<int>();
        var cola = new Queue<int>();
        cola.Enqueue(jefeEmpleadoId);

        while (cola.Count > 0)
        {
            var actual = cola.Dequeue();
            if (!porJefe.TryGetValue(actual, out var hijos)) continue;
            foreach (var hijo in hijos)
            {
                if (resultado.Add(hijo))
                    cola.Enqueue(hijo);
            }
        }

        return resultado;
    }

    public async Task<IReadOnlyList<EmpleadoListaDto>> ObtenerPersonalACargoAsync(
        int jefeEmpleadoId, CancellationToken ct = default)
    {
        var descendientes = await ObtenerDescendientesAsync(jefeEmpleadoId, ct);
        if (descendientes.Count == 0)
            return [];

        var hoy = DateOnly.FromDateTime(DateTime.Today);
        var todos = await _repo.ObtenerTodosAsync(ct);
        var noDisponibles = (await _eventoRepo.ObtenerActivosHoyGlobalAsync(hoy, ct))
            .Select(ev => ev.EmpleadoId).ToHashSet();

        return todos
            .Where(e => descendientes.Contains(e.Id))
            .Select(e => MapToListaDto(e, noDisponibles))
            .OrderBy(e => e.NombreCompleto)
            .ToList();
    }

    /// <summary>
    /// Si no se indica fin de contrato temporal, se asigna 6 meses después de la fecha de ingreso.
    /// </summary>
    private static DateOnly ResolverFechaFinContratoTemporal(DateOnly? fechaFin, DateOnly fechaIngreso)
        => fechaFin ?? fechaIngreso.AddMonths(MesesFinContratoTemporalPorDefecto);

    private async Task<string> ObtenerNombreCargoAsync(int cargoId, CancellationToken ct)
    {
        var cargos = await _catalogoService.ObtenerCargosParaSelectAsync(cargoId, ct);
        return cargos.FirstOrDefault(c => c.Id == cargoId)?.Nombre ?? string.Empty;
    }

    private async Task<ResultadoOperacion> ValidarReglaJerarquiaJefeAsync(
        int? empleadoId,
        int sedeId,
        string cargoEmpleadoNombre,
        int? jefeInmediatoId,
        CancellationToken ct)
    {
        var cargoEsAnalista = CargoJefeSede.EsCargoAnalistaServiciosFarmaceuticos(cargoEmpleadoNombre);
        if (cargoEsAnalista)
        {
            if (jefeInmediatoId.HasValue)
                return ResultadoOperacion.Fail("El cargo Analista de Servicios Farmacéuticos no debe tener jefe inmediato.");
            return ResultadoOperacion.Ok();
        }

        if (!jefeInmediatoId.HasValue)
            return ResultadoOperacion.Fail("Debe seleccionar un jefe inmediato válido según la jerarquía por cargo.");

        var jefesPermitidos = await ObtenerJefesPermitidosAsync(sedeId, cargoEmpleadoNombre, empleadoId, ct);
        if (jefesPermitidos.Count == 0)
            return ResultadoOperacion.Fail("No hay jefes configurados para ese cargo. Verifique Director, Regente o Analista de Servicios Farmacéuticos.");

        var jefe = jefesPermitidos.FirstOrDefault(x => x.Id == jefeInmediatoId.Value);
        if (jefe is null)
            return ResultadoOperacion.Fail("El jefe inmediato seleccionado no corresponde a la jerarquía definida para el cargo.");

        return ResultadoOperacion.Ok();
    }

    private async Task<List<Empleado>> ObtenerJefesPermitidosAsync(
        int sedeId,
        string cargoEmpleadoNombre,
        int? empleadoIdExcluir,
        CancellationToken ct)
    {
        var activos = (await _repo.ObtenerTodosAsync(ct))
            .Where(e => e.Estado == EstadoEmpleado.Activo)
            .Where(e => !empleadoIdExcluir.HasValue || e.Id != empleadoIdExcluir.Value)
            .ToList();

        var analistas = activos
            .Where(e => CargoJefeSede.EsCargoAnalistaServiciosFarmaceuticos(e.Cargo?.Nombre))
            .ToList();

        var directoresSede = activos
            .Where(e => e.SedeId == sedeId && CargoJefeSede.EsCargoDirector(e.Cargo?.Nombre))
            .ToList();

        var regentesSede = activos
            .Where(e => e.SedeId == sedeId && CargoJefeSede.EsCargoRegente(e.Cargo?.Nombre))
            .ToList();

        if (CargoJefeSede.EsCargoDirector(cargoEmpleadoNombre))
            return analistas;

        if (CargoJefeSede.EsCargoRegente(cargoEmpleadoNombre))
            return directoresSede.Count > 0 ? directoresSede : analistas;

        // Auxiliar, Direccionador y demás cargos:
        // Director -> Regente -> Analista de Servicios Farmacéuticos.
        if (directoresSede.Count > 0) return directoresSede;
        if (regentesSede.Count > 0) return regentesSede;
        return analistas;
    }

    // ── Mappers privados ──────────────────────────────────────────
    private static EmpleadoListaDto MapToListaDto(Empleado e, HashSet<int>? noDisponibles = null) => new()
    {
        Id              = e.Id,
        SedeId          = e.SedeId,
        JefeInmediatoId = e.JefeInmediatoId,
        NombreCompleto  = e.NombreCompleto,
        Cedula          = e.Cedula,
        CargoNombre     = e.Cargo?.Nombre ?? string.Empty,
        SedeNombre      = e.Sede?.Nombre  ?? string.Empty,
        TipoVinculacion = e.TipoVinculacion.ToString(),
        Rol             = e.Usuario?.Rol.ToString() ?? string.Empty,
        Estado          = (noDisponibles is not null
                           && noDisponibles.Contains(e.Id)
                           && e.Estado == EstadoEmpleado.Activo)
                          ? "NoDisponible"
                          : e.Estado.ToString(),
        FechaIngreso    = e.FechaIngreso.ToString("dd/MM/yyyy")
    };

    private static EmpleadoDto MapToDto(Empleado e) => new()
    {
        Id                         = e.Id,
        NombreCompleto             = e.NombreCompleto,
        Cedula                     = e.Cedula,
        FechaNacimiento            = e.FechaNacimiento?.ToString("dd/MM/yyyy"),
        Telefono                   = e.Telefono,
        CorreoElectronico          = e.CorreoElectronico,
        Direccion                  = e.Direccion,
        Ciudad                     = e.Ciudad,
        Departamento               = e.Departamento,
        NivelEscolaridad           = e.NivelEscolaridad?.ToString(),
        Eps                        = e.Eps,
        Arl                        = e.Arl,
        ContactoEmergenciaNombre   = e.ContactoEmergencia?.NombreContacto,
        ContactoEmergenciaTelefono = e.ContactoEmergencia?.TelefonoContacto,
        SedeId                     = e.SedeId,
        SedeNombre                 = e.Sede?.Nombre ?? string.Empty,
        CargoId                    = e.CargoId,
        CargoNombre                = e.Cargo?.Nombre ?? string.Empty,
        TipoVinculacion            = e.TipoVinculacion.ToString(),
        Rol                        = e.Usuario?.Rol.ToString() ?? string.Empty,
        JefeInmediatoId            = e.JefeInmediatoId,
        JefeInmediatoNombre        = e.JefeInmediato?.NombreCompleto,
        FechaIngreso               = e.FechaIngreso.ToString("dd/MM/yyyy"),
        DiasVacacionesPrevios      = e.DiasVacacionesPrevios,
        EmpresaTemporalId          = e.EmpresaTemporalId,
        EmpresaTemporalNombre      = e.EmpresaTemporal?.Nombre,
        FechaInicioContrato        = e.FechaInicioContrato?.ToString("dd/MM/yyyy"),
        FechaFinContrato           = e.FechaFinContrato?.ToString("dd/MM/yyyy"),
        Estado                     = e.Estado.ToString()
    };
}
