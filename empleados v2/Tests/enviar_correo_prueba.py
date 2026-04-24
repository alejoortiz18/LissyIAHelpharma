"""
Script puntual: envía un correo de prueba a alejo@yopmail.com
para verificar que la configuración SMTP de Office 365 está correcta.

Uso:
  python Tests/enviar_correo_prueba.py
"""
import smtplib
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── Configuración SMTP (igual que EmailSettings en appsettings.json + user-secrets) ──
SMTP_HOST    = "smtp.office365.com"
SMTP_PORT    = 587
SMTP_USER    = "sistemas.helpharma@zentria.com.co"
SMTP_PASS    = "H3lph42023**"
FROM_ADDRESS = "notificacion.sf@zentria.com.co"  # Requiere permiso "Send As" en Exchange Admin
FROM_NAME    = "Notificaciones GestionPersonal"

DESTINATARIO = "alejo@yopmail.com"

HTML_CUERPO = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:32px;">
  <div style="max-width:520px;margin:auto;background:#fff;border-radius:8px;
              padding:32px;box-shadow:0 2px 8px rgba(0,0,0,.1);">
    <h2 style="color:#1a7f3c;margin-top:0;">✅ Prueba de configuración SMTP</h2>
    <p>Si estás leyendo este mensaje, el servidor de correo está correctamente configurado.</p>
    <table style="width:100%;border-collapse:collapse;margin-top:16px;">
      <tr style="background:#f0f0f0;">
        <td style="padding:8px 12px;font-weight:bold;">Host SMTP</td>
        <td style="padding:8px 12px;">smtp.office365.com</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;font-weight:bold;">Puerto</td>
        <td style="padding:8px 12px;">587 (STARTTLS)</td>
      </tr>
      <tr style="background:#f0f0f0;">
        <td style="padding:8px 12px;font-weight:bold;">Cuenta de autenticación</td>
        <td style="padding:8px 12px;">sistemas.helpharma@zentria.com.co</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;font-weight:bold;">Remitente (Send As)</td>
        <td style="padding:8px 12px;">notificacion.sf@zentria.com.co</td>
      </tr>
      <tr style="background:#f0f0f0;">
        <td style="padding:8px 12px;font-weight:bold;">Destinatario</td>
        <td style="padding:8px 12px;">alejo@yopmail.com</td>
      </tr>
    </table>
    <p style="margin-top:24px;font-size:12px;color:#888;">
      Generado por el script de prueba de GestiónRH · 2026
    </p>
  </div>
</body>
</html>"""

def main() -> int:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "[GestiónRH] Prueba de configuración SMTP"
    msg["From"]    = f"{FROM_NAME} <{FROM_ADDRESS}>"
    msg["To"]      = DESTINATARIO
    msg.attach(MIMEText(HTML_CUERPO, "html", "utf-8"))

    print(f"  Conectando a {SMTP_HOST}:{SMTP_PORT} (STARTTLS)...")
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()
            print(f"  Autenticando como {SMTP_USER}...")
            smtp.login(SMTP_USER, SMTP_PASS)
            print(f"  Enviando a {DESTINATARIO}...")
            smtp.sendmail(FROM_ADDRESS, [DESTINATARIO], msg.as_bytes())

        print(f"\n  ✅ ÉXITO — Correo enviado correctamente.")
        print(f"  Verifica la bandeja en: https://yopmail.com/en/?login=alejo")
        return 0

    except smtplib.SMTPAuthenticationError as e:
        print(f"\n  ❌ ERROR DE AUTENTICACIÓN: {e}")
        print("  → Verificar: credenciales en user-secrets, cuenta activa en M365")
        return 1
    except smtplib.SMTPSenderRefused as e:
        print(f"\n  ❌ REMITENTE RECHAZADO: {e}")
        print(f"  → '{FROM_ADDRESS}' necesita permiso 'Send As' en Exchange Admin")
        return 1
    except smtplib.SMTPConnectError as e:
        print(f"\n  ❌ ERROR DE CONEXIÓN: {e}")
        print(f"  → Verificar acceso a {SMTP_HOST}:{SMTP_PORT} (firewall, proxy)")
        return 1
    except TimeoutError:
        print(f"\n  ❌ TIMEOUT conectando a {SMTP_HOST}:{SMTP_PORT}")
        print("  → Verificar conectividad de red y que el puerto 587 no está bloqueado")
        return 1
    except Exception as e:
        print(f"\n  ❌ ERROR INESPERADO: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
