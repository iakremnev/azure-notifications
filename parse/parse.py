from __future__ import annotations

import argparse
import email
from email.message import Message
import base64
import quopri
import re
from pathlib import Path
# from bs4 import BeautifulSoup
from functools import singledispatch

# from html import Html, WorkItemHtml


def decode_word(encoded_words):
    """Decode encoded-word syntax.
    
    Can work with multiline encodings.
    See https://dmorgan.info/posts/encoded-word-syntax/
    """
    pattern = r'=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}='
    encoded = ""
    for match in re.findall(pattern, encoded_words):
        charset, encoding, text_fragment = match
        encoded += text_fragment
    if encoding == 'B':
        byte_string = base64.b64decode(encoded)
    elif encoding == 'Q':
        byte_string = quopri.decodestring(encoded)
    return byte_string.decode(charset)


def extract_event(email: Message) -> dict[str, str]:
    """Extract headers of interest descring notification event"""
    event = {
        "type": email["X-VSS-Event-Type"],
        "initiator": decode_word(email["X-VSS-Event-Initiator"]),
        # "initiator-ascii": msg["X-VSS-Event-Initiator-Ascii"],  # This is broken
        "trigger": email["X-VSS-Event-Trigger"]
    }
    return event


def extract_payload(email: Message) -> Html:
    """Extract payload content from email file
    """
    payload = email.get_payload(decode=True).decode()
    return payload.strip().replace("\r\n", "\n")


@singledispatch
def parse_payload(html):
    raise NotImplementedError


# @parse_payload.register
# def _(html: WorkItemHtml):
#     print("Yo man")
    # soup = BeautifulSoup(payload, features="lxml")
    # core_fields = soup.find_all("tr", id=lambda s: s and "coreFields" in s)
    # name = soup.find_all("span", class_="active")
    # print("core fields", [field.text.strip() for field in core_fields])
    # print("name", [field.text.strip() for field in name])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read and parse email payload")
    parser.add_argument("email", type=Path, help="Email text file")
    args = parser.parse_args()

    with open(args.email) as f:
        email_msg = email.message_from_file(f)
    
    event = extract_event(email_msg)
    payload = extract_payload(email_msg)

    if event["type"] == "ms.vss-work.workitem-changed-event":
        # payload = WorkItemHtml(payload)

    