namespace GestionPersonal.Models.DTOs.Notificaciones;

/// <summary>Destinatario en la cadena jerárquica al crear una solicitud/evento.</summary>
public record DestinatarioJerarquiaSolicitud(
    string Correo,
    string Nombre,
    bool EsJefeInmediatoDelSolicitante,
    bool EsAnalistaServiciosFarmaceuticos);
