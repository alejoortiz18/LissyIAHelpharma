namespace GestionPersonal.Constants.Messages.EmailTemplates;

/// <summary>
/// Proporciona el shell HTML base para todos los correos del sistema.
/// Ancho máximo 600px, compatible con Outlook, Gmail y clientes móviles.
/// Inline styles únicamente (sin CSS externo ni JavaScript).
/// </summary>
public static class EmailBase
{
    // ── Paleta de colores corporativos ────────────────────────────────────────
    private const string ColorPrimario   = "#1e3a8a";   // azul oscuro — cabecera
    private const string ColorSecundario = "#3b5bdb";   // azul medio  — acento
    private const string ColorFondo      = "#f1f5f9";   // gris muy claro
    private const string ColorTarjeta    = "#ffffff";
    private const string ColorTextoSuave = "#64748b";
    private const string ColorBorde      = "#e2e8f0";

    /// <summary>
    /// Construye el HTML completo del correo con cabecera degradada, cuerpo y pie.
    /// </summary>
    public static string Construir(
        string tituloVentana,
        string badgeColor,
        string badgeTexto,
        string tituloPrincipal,
        string cuerpoHtml,
        string generadoPor,
        string tipoEvento)
    {
        return $"""
        <!DOCTYPE html>
        <html lang="es" xmlns="http://www.w3.org/1999/xhtml">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <meta http-equiv="X-UA-Compatible" content="IE=edge" />
          <title>{EscapeHtml(tituloVentana)}</title>
        </head>
        <body style="margin:0;padding:0;background-color:{ColorFondo};font-family:Arial,Helvetica,sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;">
          <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color:{ColorFondo};padding:32px 16px;">
            <tr>
              <td align="center">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="max-width:600px;width:100%;background-color:{ColorTarjeta};border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,0.08);overflow:hidden;">

                  <!-- ── Cabecera con gradiente ── -->
                  <tr>
                    <td style="background:linear-gradient(135deg,{ColorPrimario} 0%,{ColorSecundario} 100%);padding:28px 32px;">
                      <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                        <tr>
                          <td>
                            <p style="margin:0;color:rgba(255,255,255,0.75);font-size:11px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;">{EscapeHtml(badgeTexto)}</p>
                            <h1 style="margin:6px 0 0;color:#ffffff;font-size:22px;font-weight:700;line-height:1.3;">{EscapeHtml(tituloPrincipal)}</h1>
                          </td>
                          <td align="right" style="vertical-align:top;">
                            <div style="display:inline-block;background-color:rgba(255,255,255,0.15);border-radius:20px;padding:4px 14px;">
                              <span style="color:#ffffff;font-size:12px;font-weight:600;">{EscapeHtml(badgeColor)}</span>
                            </div>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>

                  <!-- ── Cuerpo ── -->
                  <tr>
                    <td style="padding:32px;">
                      {cuerpoHtml}
                    </td>
                  </tr>

                  <!-- ── Pie ── -->
                  <tr>
                    <td style="background-color:{ColorFondo};padding:20px 32px;border-top:1px solid {ColorBorde};">
                      <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                        <tr>
                          <td>
                            <p style="margin:0;color:{ColorTextoSuave};font-size:12px;line-height:1.6;">
                              Este correo fue generado automáticamente por <strong>{EscapeHtml(generadoPor)}</strong>
                              como parte del proceso <em>{EscapeHtml(tipoEvento)}</em>.
                            </p>
                            <p style="margin:8px 0 0;color:{ColorTextoSuave};font-size:11px;">
                              Si tienes dudas, contacta a tu administrador. Por favor no respondas a este correo.
                            </p>
                          </td>
                          <td align="right" style="vertical-align:bottom;padding-left:16px;">
                            <p style="margin:0;color:{ColorPrimario};font-size:13px;font-weight:700;white-space:nowrap;">GestionPersonal</p>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>

                </table>
              </td>
            </tr>
          </table>
        </body>
        </html>
        """;
    }

    // ── Helpers compartidos ───────────────────────────────────────────────────

    /// <summary>Escapa caracteres HTML para evitar XSS en parámetros de usuario.</summary>
    public static string EscapeHtml(string? valor)
        => System.Net.WebUtility.HtmlEncode(valor ?? string.Empty);

    /// <summary>Genera una fila de datos para tablas de información.</summary>
    public static string FilaDato(string etiqueta, string valor, bool alternada = false)
    {
        var bg = alternada ? "#f8fafc" : "#ffffff";
        return $"""
            <tr>
              <td style="padding:10px 14px;background-color:{bg};border-bottom:1px solid #f1f5f9;font-size:13px;color:#64748b;font-weight:600;width:40%;">{EscapeHtml(etiqueta)}</td>
              <td style="padding:10px 14px;background-color:{bg};border-bottom:1px solid #f1f5f9;font-size:13px;color:#1e293b;">{EscapeHtml(valor)}</td>
            </tr>
            """;
    }

    /// <summary>Genera un banner de alerta coloreado según el tipo (info, exito, advertencia, peligro).</summary>
    public static string Banner(string mensaje, string tipo = "info")
    {
        var (bg, borde, icono) = tipo switch
        {
            "exito"       => ("#dcfce7", "#16a34a", "✓"),
            "advertencia" => ("#fef9c3", "#b45309", "⚠"),
            "peligro"     => ("#fee2e2", "#dc2626", "✗"),
            _             => ("#eff6ff", "#3b5bdb", "ℹ")
        };
        return $"""
           <div style="background-color:{bg};border-left:4px solid {borde};border-radius:0 8px 8px 0;padding:14px 18px;margin:20px 0;">
             <p style="margin:0;font-size:14px;color:#1e293b;"><strong style="margin-right:6px;">{icono}</strong>{EscapeHtml(mensaje)}</p>
           </div>
           """;
    }

    /// <summary>Tabla de información con borde redondeado y filas alternas.</summary>
    public static string TablaInfo(string filasHtml)
        => $"""
           <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%"
                  style="border-collapse:collapse;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin:20px 0;">
             <tbody>{filasHtml}</tbody>
           </table>
           """;

    // ── Colores expuestos para las subclases ──────────────────────────────────
    public const string Verde = "#16a34a";
    public const string Rojo  = "#dc2626";
    public const string Azul  = "#3b5bdb";
    public const string Ambar = "#b45309";
}
