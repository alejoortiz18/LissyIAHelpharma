using FluentAssertions;
using GestionPersonal.Application.Interfaces;
using GestionPersonal.Application.Services;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using GestionPersonal.Models.Models;
using Moq;

namespace GestionPersonal.Tests.Services;

public class EmpleadoServiceContratoTemporalTests
{
    private readonly Mock<IEmpleadoRepository>                _repoMock       = new();
    private readonly Mock<ICatalogoService>                   _catalogoSvcMock = new();
    private readonly Mock<IUsuarioService>                    _usuarioSvcMock = new();
    private readonly Mock<IHistorialDesvinculacionRepository> _historialMock  = new();
    private readonly Mock<IEventoLaboralRepository>           _eventoRepoMock = new();

    private EmpleadoService CrearSut()
    {
        _catalogoSvcMock
            .Setup(c => c.ObtenerCargosParaSelectAsync(It.IsAny<int?>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<Cargo>
            {
                new() { Id = 1, Nombre = "Analista de Servicios Farmacéuticos", Estado = "Activo" }
            });

        return new EmpleadoService(
            _repoMock.Object,
            _catalogoSvcMock.Object,
            _usuarioSvcMock.Object,
            _historialMock.Object,
            _eventoRepoMock.Object);
    }

    [Fact]
    public async Task CrearAsync_TemporalSinFechaFin_AsignaSeisMesesDespuesDeIngreso()
    {
        Empleado? capturado = null;
        _repoMock.Setup(r => r.ExisteCedulaAsync(It.IsAny<string>(), null, default)).ReturnsAsync(false);
        _repoMock.Setup(r => r.ExisteCorreoAsync(It.IsAny<string>(), null, default)).ReturnsAsync(false);
        _usuarioSvcMock.Setup(u => u.CrearParaEmpleadoAsync(
                It.IsAny<string>(), It.IsAny<RolUsuario>(), It.IsAny<int>(), null, default))
            .ReturnsAsync(ResultadoOperacion<int>.Ok(10));
        _repoMock.Setup(r => r.Agregar(It.IsAny<Empleado>())).Callback<Empleado>(e => capturado = e);

        var dto = DtoCrearTemporal();
        dto.FechaIngreso     = new DateOnly(2026, 1, 15);
        dto.FechaFinContrato = null;

        var sut = CrearSut();
        var resultado = await sut.CrearAsync(dto, creadoPorUsuarioId: 1);

        resultado.Exito.Should().BeTrue();
        capturado.Should().NotBeNull();
        capturado!.TipoVinculacion.Should().Be(TipoVinculacion.Temporal);
        capturado.FechaFinContrato.Should().Be(new DateOnly(2026, 7, 15));
        capturado.FechaInicioContrato.Should().BeNull();
    }

    [Fact]
    public async Task CrearAsync_TemporalConFechaFinExplicita_RespetaLaFechaIndicada()
    {
        Empleado? capturado = null;
        _repoMock.Setup(r => r.ExisteCedulaAsync(It.IsAny<string>(), null, default)).ReturnsAsync(false);
        _repoMock.Setup(r => r.ExisteCorreoAsync(It.IsAny<string>(), null, default)).ReturnsAsync(false);
        _usuarioSvcMock.Setup(u => u.CrearParaEmpleadoAsync(
                It.IsAny<string>(), It.IsAny<RolUsuario>(), It.IsAny<int>(), null, default))
            .ReturnsAsync(ResultadoOperacion<int>.Ok(10));
        _repoMock.Setup(r => r.Agregar(It.IsAny<Empleado>())).Callback<Empleado>(e => capturado = e);

        var dto = DtoCrearTemporal();
        dto.FechaFinContrato = new DateOnly(2027, 12, 31);

        var sut = CrearSut();
        var resultado = await sut.CrearAsync(dto, creadoPorUsuarioId: 1);

        resultado.Exito.Should().BeTrue();
        capturado!.FechaFinContrato.Should().Be(new DateOnly(2027, 12, 31));
    }

    [Fact]
    public async Task EditarAsync_TemporalSinFechaFin_AsignaSeisMesesDespuesDeIngreso()
    {
        var empleado = new Empleado
        {
            Id              = 5,
            NombreCompleto  = "Temporal Prueba",
            Cedula          = "99887766",
            CorreoElectronico = "temporal.prueba@yopmail.com",
            SedeId          = 1,
            CargoId         = 1,
            FechaIngreso    = new DateOnly(2026, 3, 1),
            TipoVinculacion = TipoVinculacion.Temporal,
            EmpresaTemporalId = 1,
            FechaFinContrato  = new DateOnly(2026, 9, 1),
            Estado          = EstadoEmpleado.Activo
        };

        _repoMock.Setup(r => r.ObtenerPorIdConDetallesAsync(5, default)).ReturnsAsync(empleado);

        var dto = new EditarEmpleadoDto
        {
            Id               = 5,
            NombreCompleto   = empleado.NombreCompleto,
            Telefono         = "3001112233",
            CorreoElectronico = empleado.CorreoElectronico,
            Direccion        = "Calle 1",
            Ciudad           = "Bogotá",
            Departamento     = "Cundinamarca",
            SedeId           = 1,
            CargoId          = 1,
            TipoVinculacion  = "Temporal",
            EmpresaTemporalId = 1,
            FechaFinContrato = null
        };

        var sut = CrearSut();
        var resultado = await sut.EditarAsync(dto, modificadoPorUsuarioId: 2);

        resultado.Exito.Should().BeTrue();
        empleado.FechaFinContrato.Should().Be(new DateOnly(2026, 9, 1));
    }

    private static CrearEmpleadoDto DtoCrearTemporal() => new()
    {
        NombreCompleto    = "Empleado Temporal",
        Cedula            = "11223344",
        Telefono          = "3009998877",
        CorreoElectronico = "empleado.temporal@yopmail.com",
        Direccion         = "Cra 10",
        Ciudad            = "Medellín",
        Departamento      = "Antioquia",
        SedeId            = 1,
        CargoId           = 1,
        Rol               = RolUsuario.Operario,
        TipoVinculacion   = TipoVinculacion.Temporal,
        FechaIngreso      = new DateOnly(2026, 1, 15),
        EmpresaTemporalId = 1
    };
}
