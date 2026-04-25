namespace GestionPersonal.Models.Enums;

/// <summary>
/// Coincide con CK_Eventos_Estado.
/// Valores originales: 'Activo' | 'Finalizado' | 'Anulado'
/// Valores de autogestión (Solicitud): 'Pendiente' | 'Aprobado' | 'Rechazado' | 'Cancelado' | 'EnRevision'
/// </summary>
public enum EstadoEvento
{
    // ── Estados del flujo existente de eventos laborales ──────────────
    Activo,
    Finalizado,
    Anulado,

    // ── Estados del flujo de autogestión (Mis Solicitudes) ────────────
    Pendiente,
    Aprobado,
    Rechazado,
    Cancelado,
    EnRevision
}
