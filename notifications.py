"""Apertura del cliente de correo predeterminado mediante enlace mailto."""

from email.utils import parseaddr
from typing import Tuple
import urllib.parse
import webbrowser

import validators


def build_mailto_url(recipient: str, subject: str, body: str) -> str:
    """Construye un enlace mailto: escapando correctamente asunto y cuerpo."""
    query_params = urllib.parse.urlencode({"subject": subject, "body": body}, quote_via=urllib.parse.quote)
    return f"mailto:{recipient}?{query_params}"


def send_email(recipient: str, subject: str, body: str) -> Tuple[bool, str]:
    """Abre el cliente de correo predeterminado del sistema con el mensaje precargado."""
    recipient = (recipient or "").strip()
    if not recipient or parseaddr(recipient)[1] != recipient or not validators.validate_email(recipient):
        return False, "La dirección de correo del destinatario no es válida."

    try:
        mailto_url = build_mailto_url(recipient, subject, body)
        opened = webbrowser.open(mailto_url)
        if opened:
            return True, "Cliente de correo abierto con la plantilla de mensaje."
        return True, "Enlace mailto generado para el cliente de correo."
    except Exception as error:
        return False, f"No se pudo abrir el cliente de correo: {error}"

