using FluentAssertions;
using GestionPersonal.Application.Interfaces;
using GestionPersonal.Application.Services;
using GestionPersonal.Constants.Messages;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using Moq;

namespace GestionPersonal.Tests.Services;

public class EmpleadoServiceDesvinculacionTests
{
    // ── Mocks ─────────────────────────────────────────────────────────
    private readonly Mock<IEmpleadoRepository>                _repoMock        = new();
    private readonly Mock<ICatalogoService>                   _catalogoSvcMock = new();
    private readonly Mock<IUsuarioService>                    _usuarioSvcMock  = new();
    private readonly Mock<IHistorialDesvinculacionRepository> _historialMock   = new();
    private readonly Mock<IEventoLaboralRepository>           _eventoRepoMock  = new();

    private EmpleadoService CrearSut() =>
        new(_repoMock.Object, _catalogoSvcMock.Object, _usuarioSvcMock.Object,
            _historialMock.Object, _eventoRepoMock.Object);

    /// <summary>Crea un <see cref="Empleado"/> activo con datos mínimos.</summary>
    private static Empleado EmpleadoActivo(int id = 1) => new()
    {
        Id             = id,
        NombreCompleto = "Carlos Ortiz",
        Cedula         = "12345678",
        Estado         = EstadoEmpleado.Activo,
        FechaIngreso   = new DateOnly(2024, 1, 15),
        TipoVinculacion = TipoVinculacion.Directo
    };

    private static DesvincularEmpleadoDto DtoValido(int empleadoId = 1) => new()
    {
        EmpleadoId          = empleadoId,
        FechaDesvinculacion = DateOnly.FromDateTime(DateTime.Today),
        MotivoRetiro        = "Renuncia voluntaria"
    };

    // ─────────────────────────────────────────────────────────────────
    // 1. Éxito
    // ─────────────────────────────────────────────────────────────────

    [Fact]
    public async Task DesvincularAsync_EmpleadoExisteYMotivoValido_RetornaExito()
    {
        // Arrange
        var empleado = EmpleadoActivo();
        _repoMock.Setup(r => r.ObtenerPorIdAsync(1, default))
                 .ReturnsAsync(empleado);

        var sut = CrearSut();

        // Act
        var resultado = await sut.DesvincularAsync(DtoValido(), registradoPorUsuarioId: 99);

        // Assert
        resultado.Exito.Should().BeTrue();
        resultado.Mensaje.Should().Be(EmpleadoConstant.EmpleadoDesactivado);
    }

    [Fact]
    public async Task DesvincularAsync_EmpleadoExisteYMotivoValido_PonEstadoInactivo()
    {
        // Arrange
        var empleado = EmpleadoActivo();
        _repoMock.Setup(r => r.ObtenerPorIdAsync(1, default))
                 .ReturnsAsync(empleado);

        var sut = CrearSut();

        // Act
        await sut.DesvincularAsync(DtoValido(), registradoPorUsuarioId: 99);

        // Assert
        empleado.Estado.Should().Be(EstadoEmpleado.Inactivo);
    }

    [Fact]
    public async Task DesvincularAsync_EmpleadoExisteYMotivoValido_GuardaHistorialDesvinculacion()
    {
        // Arrange
        var empleado = EmpleadoActivo();
        _repoMock.Setup(r => r.ObtenerPorIdAsync(1, default))
                 .ReturnsAsync(empleado);

        var sut = CrearSut();

        // Act
        await sut.DesvincularAsync(DtoValido(), registradoPorUsuarioId: 99);

        // Assert – se agregó exactamente un registro al historial
        _historialMock.Verify(h => h.Agregar(It.Is<HistorialDesvinculacion>(hd =>
            hd.EmpleadoId   == 1 &&
            hd.MotivoRetiro == "Renuncia voluntaria" &&
            hd.RegistradoPor == 99
        )), Times.Once);
    }

    [Fact]
    public async Task DesvincularAsync_EmpleadoExisteYMotivoValido_LlamaGuardarCambios()
    {
        // Arrange
        var empleado = EmpleadoActivo();
        _repoMock.Setup(r => r.ObtenerPorIdAsync(1, default))
                 .ReturnsAsync(empleado);

        var sut = CrearSut();

        // Act
        await sut.DesvincularAsync(DtoValido(), registradoPorUsuarioId: 99);

        // Assert
        _repoMock.Verify(r => r.GuardarCambiosAsync(It.IsAny<CancellationToken>()), Times.Once);
    }

    // ─────────────────────────────────────────────────────────────────
    // 2. Validaciones de entrada
    // ─────────────────────────────────────────────────────────────────

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData(null)]
    public async Task DesvincularAsync_MotivoVacioONulo_RetornaFallo(string? motivo)
    {
        // Arrange
        var dto = DtoValido();
        dto.MotivoRetiro = motivo!;

        var sut = CrearSut();

        // Act
        var resultado = await sut.DesvincularAsync(dto, registradoPorUsuarioId: 1);

        // Assert
        resultado.Exito.Should().BeFalse();
        resultado.Mensaje.Should().Be(EmpleadoConstant.MotivoRetiroObligatorio);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData(null)]
    public async Task DesvincularAsync_MotivoVacioONulo_NoTocaRepositorio(string? motivo)
    {
        // Arrange
        var dto = DtoValido();
        dto.MotivoRetiro = motivo!;

        var sut = CrearSut();

        // Act
        await sut.DesvincularAsync(dto, registradoPorUsuarioId: 1);

        // Assert
        _repoMock.Verify(r => r.ObtenerPorIdAsync(It.IsAny<int>(), It.IsAny<CancellationToken>()), Times.Never);
        _repoMock.Verify(r => r.GuardarCambiosAsync(It.IsAny<CancellationToken>()), Times.Never);
    }

    // ─────────────────────────────────────────────────────────────────
    // 3. Empleado no encontrado
    // ─────────────────────────────────────────────────────────────────

    [Fact]
    public async Task DesvincularAsync_EmpleadoNoExiste_RetornaFallo()
    {
        // Arrange
        _repoMock.Setup(r => r.ObtenerPorIdAsync(99, default))
                 .ReturnsAsync((Empleado?)null);

        var dto = DtoValido(empleadoId: 99);
        var sut = CrearSut();

        // Act
        var resultado = await sut.DesvincularAsync(dto, registradoPorUsuarioId: 1);

        // Assert
        resultado.Exito.Should().BeFalse();
        resultado.Mensaje.Should().Be(EmpleadoConstant.EmpleadoNoEncontrado);
    }

    [Fact]
    public async Task DesvincularAsync_EmpleadoNoExiste_NoGuardaHistorial()
    {
        // Arrange
        _repoMock.Setup(r => r.ObtenerPorIdAsync(99, default))
                 .ReturnsAsync((Empleado?)null);

        var dto = DtoValido(empleadoId: 99);
        var sut = CrearSut();

        // Act
        await sut.DesvincularAsync(dto, registradoPorUsuarioId: 1);

        // Assert
        _historialMock.Verify(h => h.Agregar(It.IsAny<HistorialDesvinculacion>()), Times.Never);
        _repoMock.Verify(r => r.GuardarCambiosAsync(It.IsAny<CancellationToken>()), Times.Never);
    }

    // ─────────────────────────────────────────────────────────────────
    // 4. Datos guardados correctamente
    // ─────────────────────────────────────────────────────────────────

    [Fact]
    public async Task DesvincularAsync_Exito_GuardaFechaDesvinculacionCorrecta()
    {
        // Arrange
        var empleado          = EmpleadoActivo();
        var fechaEsperada     = new DateOnly(2026, 4, 28);
        var dto               = DtoValido();
        dto.FechaDesvinculacion = fechaEsperada;

        _repoMock.Setup(r => r.ObtenerPorIdAsync(1, default))
                 .ReturnsAsync(empleado);

        var sut = CrearSut();

        // Act
        await sut.DesvincularAsync(dto, registradoPorUsuarioId: 5);

        // Assert
        _historialMock.Verify(h => h.Agregar(It.Is<HistorialDesvinculacion>(hd =>
            hd.FechaDesvinculacion == fechaEsperada
        )), Times.Once);
    }

    [Fact]
    public async Task DesvincularAsync_Exito_MarcaFechaModificacionEnEmpleado()
    {
        // Arrange
        var empleado = EmpleadoActivo();
        _repoMock.Setup(r => r.ObtenerPorIdAsync(1, default))
                 .ReturnsAsync(empleado);

        var sut = CrearSut();

        // Act
        await sut.DesvincularAsync(DtoValido(), registradoPorUsuarioId: 7);

        // Assert
        empleado.FechaModificacion.Should().NotBeNull();
        empleado.ModificadoPor.Should().Be(7);
    }
}
