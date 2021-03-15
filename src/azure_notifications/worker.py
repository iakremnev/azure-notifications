from email.message import Message

from .parse.email import extract_event_headers, decode_payload
from .parse.html import parse_payload
from .config import Event
from .parse.html import *


def dispatch_email(email: Message):
    event_info = extract_event_headers(email)
    payload = decode_payload(email)

    if event_info["type"] == Event.WORK_ITEM_CHANGED.value:
        payload = WorkItemHtml(payload)
        return parse_payload(
            payload, changed_by=event_info["initiator"], trigger=event_info["trigger"]
        )

    elif event_info["type"] == Event.PR_COMMENT.value:
        payload = PullRequestCommentHtml(payload)
        return parse_payload(
            payload, commentator=event_info["initiator"], trigger=event_info["trigger"]
        )

    elif event_info["type"] == Event.BUILD_COMPLETED.value:
        payload = BuildCompletedHtml(payload)
        return parse_payload(payload, trigger=event_info["trigger"])

    elif event_info["type"] == Event.PULL_REQUEST.value:
        payload = PullRequestHtml(payload)
        return parse_payload(
            payload, initiator=event_info["initiator"], trigger=event_info["trigger"]
        )

    else:
        raise NotImplementedError
