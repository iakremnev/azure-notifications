from __future__ import annotations

import base64
import quopri
import re
from email.message import EmailMessage


def decode_word(encoded_words: str):
    """Decode encoded-word syntax.

    Can work with multiline encodings.
    See https://dmorgan.info/posts/encoded-word-syntax/
    """
    pattern = r"=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}="
    encoded = ""
    for match in re.findall(pattern, encoded_words):
        charset, encoding, text_fragment = match
        encoded += text_fragment
    if encoding == "B":
        byte_string = base64.b64decode(encoded)
    elif encoding == "Q":
        byte_string = quopri.decodestring(encoded)
    return byte_string.decode(charset)


def extract_event_headers(email: EmailMessage, decode_utf=True) -> dict[str, str]:
    """Extract headers of interest descring notification event"""
    event = {
        "type": email["X-VSS-Event-Type"],
        "trigger": email["X-VSS-Event-Trigger"],
        "initiator": email.get("X-VSS-Event-Initiator"),
        "subject": email["Subject"],
    }

    if decode_utf:

        def decode_if_needed(s: str):
            try:
                return decode_word(s)
            except (ValueError, TypeError, UnboundLocalError):
                return s

        event = {header: decode_if_needed(value) for header, value in event.items()}

    return event


def decode_payload(email: EmailMessage) -> str:
    """Extract and decode payload from the email"""
    payload = email.get_content()
    return payload.strip().replace("\r\n", "\n")
