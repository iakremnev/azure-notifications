from email.message import EmailMessage
from functools import singledispatch

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from .config import SLACK_API_TOKEN, slack_user_ids
from .event_classes import *

slack = AsyncWebClient(token=SLACK_API_TOKEN)
CHANNEL = "D01R8L8TP0S"


@singledispatch
def to_markdown(event):
    raise NotImplementedError


@to_markdown.register
def work_item_to_markdown(event: WorkItemEvent):
    user_id = slack_user_ids.get(event.changed_by, event.changed_by)
    link = f"<{event.url}|{event.title}>"
    return f"<@{user_id}> назначил таску {link} :ya_v_ahue:"


@to_markdown.register
def pull_request_to_markdown(event: PullRequestEvent):
    user_id = slack_user_ids.get(event.initiator, event.initiator)
    link = f"<{event.url}|{event.title}>"

    if event.trigger == "PushNotification":
        return f"<@{user_id}> пушнул {event.commits} коммита в {link}"

    elif event.trigger == "ReviewerVoteNotification":
        if event.vote == "Approved":
            status = f"поставил аппрув к {link} :spinning_gorilla:"
        else:
            raise NotImplementedError
        return f"<@{user_id}> {status}"

    elif event.trigger == "ReviewersUpdateNotification":
        return f"<@{user_id}> повесил на тебя PR ревью {link} :eyes:"

    elif event.trigger == "StatusUpdateNotification":
        if event.status == "Completed":
            return f"Пиар {link} завершён :ronaldo:"
        else:
            raise NotImplementedError

    else:
        raise NotImplementedError


@to_markdown.register
def pr_comment_to_markdown(event: PullRequestCommentEvent):
    commenter_id = slack_user_ids.get(event.commenter, event.commenter)
    link = f"<{event.url}|{event.title}>"
    comment_escaped = ">" + event.text.replace("\n", "\n>")
    return f"<@{commenter_id}> оставил коммент в пиаре {link}:\n{comment_escaped}"


@to_markdown.register
def build_completed_to_markdown(event: BuildCompletedEvent):
    link = f"<{event.url}|{event.title}>"
    if event.trigger == "Successfully Completed":
        status = "собрался :white_check_mark:"
    elif event.trigger == "Failed":
        status = "не прошёл :x:"
    return f"Билд {link} {status}"


async def send_to_slack(event):
    markdown_text = to_markdown(event)
    try:
        await slack.chat_postMessage(
            channel=CHANNEL,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": markdown_text,
                    },
                }
            ],
        )
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")
        raise NotImplementedError


async def send_error_to_slack(msg: EmailMessage):
    await slack.files_upload(
        channels=CHANNEL,
        content=msg.as_string(),
        title="Fix me pls!",
        filename="error.eml",
        initial_comment="Миникачер нас предал!",
    )
