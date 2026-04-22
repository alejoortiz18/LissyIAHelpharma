using GestionPersonal.Models.DTOs.Cuenta;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Interfaces;

public interface ICuentaService
{
    Task<ResultadoOperacion<UsuarioSesionDto>> LoginAsync(LoginDto dto, CancellationToken ct = default);
    Task<ResultadoOperacion> SolicitarRecuperacionAsync(SolicitarRecuperacionDto dto, CancellationToken ct = default);
    Task<ResultadoOperacion> RestablecerPasswordAsync(RestablecerPasswordDto dto, CancellationToken ct = default);
    Task<ResultadoOperacion> CambiarPasswordAsync(int usuarioId, CambiarPasswordDto dto, CancellationToken ct = default);
}
