from email.message import EmailMessage

from .config import Event
from .parse.email import decode_payload, extract_event_headers
from .parse.html import *
from .parse.html import parse_payload


def dispatch_email(email: EmailMessage):
    event_info = extract_event_headers(email, decode_utf=False)
    payload = decode_payload(email)

    if event_info["type"] == Event.WORK_ITEM_CHANGED.value:
        payload = WorkItemHtml(payload)
        return parse_payload(
            payload, changed_by=event_info["initiator"], trigger=event_info["trigger"]
        )

    elif event_info["type"] == Event.PR_COMMENT.value:
        payload = PullRequestCommentHtml(payload)
        return parse_payload(
            payload, commenter=event_info["initiator"], trigger=event_info["trigger"]
        )

    elif event_info["type"] == Event.BUILD_COMPLETED.value:
        payload = BuildCompletedHtml(payload)
        return parse_payload(payload, trigger=event_info["trigger"])

    elif event_info["type"] == Event.PULL_REQUEST.value:
        payload = PullRequestHtml(payload)

        return parse_payload(
            payload,
            initiator=event_info["initiator"],
            subject=event_info["subject"],
            trigger=event_info["trigger"],
        )

    else:
        raise NotImplementedError
