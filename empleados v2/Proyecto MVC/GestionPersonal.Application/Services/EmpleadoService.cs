using GestionPersonal.Application.Interfaces;
using GestionPersonal.Constants.Messages;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Services;

public class EmpleadoService : IEmpleadoService
{
    private readonly IEmpleadoRepository _repo;
    private readonly IUsuarioService _usuarioService;
    private readonly IHistorialDesvinculacionRepository _historialRepo;

    public EmpleadoService(
        IEmpleadoRepository repo,
        IUsuarioService usuarioService,
        IHistorialDesvinculacionRepository historialRepo)
    {
        _repo            = repo;
        _usuarioService  = usuarioService;
        _historialRepo   = historialRepo;
    }

    public async Task<IReadOnlyList<EmpleadoListaDto>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default)
    {
        var lista = await _repo.ObtenerPorSedeAsync(sedeId, ct);
        return lista.Select(MapToListaDto).ToList();
    }

    public async Task<IReadOnlyList<EmpleadoListaDto>> ObtenerTodosAsync(CancellationToken ct = default)
    {
        var lista = await _repo.ObtenerTodosAsync(ct);
        return lista.Select(MapToListaDto).ToList();
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

        // Crear usuario de acceso
        var resultadoUsuario = await _usuarioService.CrearParaEmpleadoAsync(
            dto.CorreoElectronico, dto.Rol, dto.SedeId, ct);

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
            FechaFinContrato       = dto.FechaFinContrato,
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
            // Contrato temporal: FechaInicioContrato siempre null
            emp.EmpresaTemporalId   = dto.EmpresaTemporalId;
            emp.FechaInicioContrato = null;
            emp.FechaFinContrato    = dto.FechaFinContrato;
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

    // ── Mappers privados ──────────────────────────────────────────
    private static EmpleadoListaDto MapToListaDto(Empleado e) => new()
    {
        Id              = e.Id,
        JefeInmediatoId = e.JefeInmediatoId,
        NombreCompleto  = e.NombreCompleto,
        Cedula          = e.Cedula,
        CargoNombre     = e.Cargo?.Nombre ?? string.Empty,
        SedeNombre      = e.Sede?.Nombre  ?? string.Empty,
        TipoVinculacion = e.TipoVinculacion.ToString(),
        Rol             = e.Usuario?.Rol.ToString() ?? string.Empty,
        Estado          = e.Estado.ToString(),
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
        EmpresaTemporalNombre      = e.EmpresaTemporal?.Nombre,
        FechaInicioContrato        = e.FechaInicioContrato?.ToString("dd/MM/yyyy"),
        FechaFinContrato           = e.FechaFinContrato?.ToString("dd/MM/yyyy"),
        Estado                     = e.Estado.ToString()
    };
}
