using GestionPersonal.Application.Interfaces;
using GestionPersonal.Models.DTOs.EventoLaboral;
using GestionPersonal.Models.Enums;
using GestionPersonal.Web.Helpers;
using GestionPersonal.Web.ViewModels.Solicitud;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc;

namespace GestionPersonal.Web.Controllers;

[Authorize(Roles = "Operario,Direccionador")]
public class SolicitudController : Controller
{
    private readonly ISolicitudService _solicitudService;
    private readonly IWebHostEnvironment _env;

    private static readonly HashSet<string> _extensionesPermitidas =
        new(StringComparer.OrdinalIgnoreCase) { ".pdf", ".jpg", ".jpeg", ".png" };
    private const long _maxTamanoBytes = 5 * 1024 * 1024; // 5 MB

    public SolicitudController(ISolicitudService solicitudService, IWebHostEnvironment env)
    {
        _solicitudService = solicitudService;
        _env = env;
    }

    // GET /Solicitud
    [HttpGet]
    public async Task<IActionResult> Index(string? tipo, string? estado, int pagina = 1)
    {
        const int tam = 15;

        var empId = SesionHelper.GetEmpleadoId(User);
        if (!empId.HasValue)
            return Forbid();

        ViewBag.EmpleadoId = empId.Value;

        var todas = await _solicitudService.ObtenerPropiosAsync(empId.Value);

        var q = todas.AsEnumerable();
        if (!string.IsNullOrEmpty(tipo))
            q = q.Where(s => s.TipoEvento.Equals(tipo, StringComparison.OrdinalIgnoreCase));
        if (!string.IsNullOrEmpty(estado))
            q = q.Where(s => s.Estado.Equals(estado, StringComparison.OrdinalIgnoreCase));

        var lista   = q.ToList();
        var total   = lista.Count;
        var paginas = (int)Math.Ceiling(total / (double)tam);
        pagina      = Math.Clamp(pagina, 1, Math.Max(1, paginas));
        var paginado = lista.Skip((pagina - 1) * tam).Take(tam).ToList();

        var vm = new SolicitudesViewModel
        {
            Solicitudes    = paginado,
            Tipo           = tipo,
            Estado         = estado,
            Pagina         = pagina,
            TotalPaginas   = paginas,
            TotalRegistros = total
        };

        return View(vm);
    }

    // POST /Solicitud/Crear
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Crear(
        string tipoEvento,
        string fechaInicio,
        string fechaFin,
        string? descripcion,
        string? observaciones,
        int? diasDisfrutar,
        IFormFile? Documento = null)
    {
        var empId      = SesionHelper.GetEmpleadoId(User);
        var usuarioId  = SesionHelper.GetUsuarioId(User);

        if (!empId.HasValue)
            return Forbid();

        if (!Enum.TryParse<TipoEvento>(tipoEvento, ignoreCase: true, out var tipo))
        {
            TempData["Error"] = "El tipo de solicitud seleccionado no es válido.";
            return RedirectToAction(nameof(Index));
        }

        if (!DateOnly.TryParse(fechaInicio, out var inicio) ||
            !DateOnly.TryParse(fechaFin,    out var fin))
        {
            TempData["Error"] = "Las fechas ingresadas no son válidas.";
            return RedirectToAction(nameof(Index));
        }

        if (fin < inicio)
        {
            TempData["Error"] = "La fecha de fin no puede ser anterior a la fecha de inicio.";
            return RedirectToAction(nameof(Index));
        }

        var dto = new CrearEventoLaboralDto
        {
            EmpleadoId    = empId.Value,
            TipoEvento    = tipo,
            FechaInicio   = inicio,
            FechaFin      = fin,
            Descripcion   = CombinarDescripcion(descripcion, observaciones),
            DiasDisfrutar = (tipo == TipoEvento.Vacaciones && diasDisfrutar.HasValue && diasDisfrutar > 0)
                            ? diasDisfrutar
                            : null,
            // AutorizadoPor y EstadoInicial son forzados por SolicitudService
            AutorizadoPor = string.Empty
        };

        // Guardar archivo adjunto si se proporcionó
        if (Documento is { Length: > 0 })
        {
            if (Documento.Length > _maxTamanoBytes)
            {
                TempData["Error"] = "El archivo no puede superar 5 MB.";
                return RedirectToAction(nameof(Index));
            }

            var ext = Path.GetExtension(Documento.FileName);
            if (!_extensionesPermitidas.Contains(ext))
            {
                TempData["Error"] = "Solo se permiten archivos PDF, JPG o PNG.";
                return RedirectToAction(nameof(Index));
            }

            var carpeta = Path.Combine(_env.WebRootPath, "uploads", "eventos");
            Directory.CreateDirectory(carpeta);

            var nombreGuardado = $"{Guid.NewGuid()}{ext}";
            var rutaFisica     = Path.Combine(carpeta, nombreGuardado);

            using (var stream = new FileStream(rutaFisica, FileMode.Create))
                await Documento.CopyToAsync(stream);

            dto.RutaDocumento   = rutaFisica;
            dto.NombreDocumento = Documento.FileName;
        }

        var resultado = await _solicitudService.CrearSolicitudAsync(dto, usuarioId);

        if (!resultado.Exito)
        {
            TempData["Error"] = resultado.Mensaje;
            return RedirectToAction(nameof(Index));
        }

        TempData["Exito"] = "Tu solicitud fue enviada correctamente y está pendiente de aprobación.";
        return RedirectToAction(nameof(Index));
    }

    // ── Helpers privados ─────────────────────────────────────────────

    private static string? CombinarDescripcion(string? motivo, string? observaciones)
    {
        var partes = new[] { motivo?.Trim(), observaciones?.Trim() }
            .Where(p => !string.IsNullOrEmpty(p));
        var texto = string.Join(" | Observaciones: ", partes);
        return string.IsNullOrEmpty(texto) ? null : texto;
    }
}
