"""Worker is an email dispatcher that is tightly coupled with event classes"""
from email.header import decode_header
from typing import Any
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import re

from .event_classes import *
from slack_sdk.web.async_client import AsyncWebClient
from .config import slack_users, slack_ims


async def get_fields_from_html(html: asyncio.Task[str]) -> dict[str, str]:
    bs = BeautifulSoup(await html)

    fields = {}
    fields["url"] = bs.find("a", text=lambda s: "View" in s).get("href")

    comment_text = bs.find("td", class_="comment")
    if comment_text:
        fields["text"] = comment_text.text.strip()

    return fields


async def dispatch_text(headers: dict[str, str], plain_text: str, html: asyncio.Task[str]) -> TFSEvent:

    # 1. Extract common TFSEvent headers
    fields = {}
    html_fields = asyncio.create_task(get_fields_from_html(html))

    subscriber, enc = decode_header(headers["reply_to"])[0]
    subscriber = subscriber.decode(enc or "utf-8")
    fields["subscriber"] = subscriber

    message_id = headers["message_id"]
    trigger = re.match(r"<.*\d+\.(?P<trigger>[\w.]+)\.[a-z0-9]", message_id).group("trigger")
    fields["trigger"] = trigger

    fields.update(await html_fields)

    # 2. Dispatch by trigger
    event = {
        "Successfully_Completed": BuildCompletedEvent,
        "Failed": BuildCompletedEvent,
        "FieldChanged.AssignedToChanged": WorkItemEvent,
        "CommentNotification": PullRequestCommentEvent,
        "PushNotification": PullRequestPushEvent,
        "ReviewersUpdateNotification": PullRequestReviewerAddedEvent,
        "ReviewerVoteNotification": PullRequestVoteEvent,
        "StatusUpdateNotification": PullRequestStatusUpdateEvent,
    }[trigger].from_text(plain_text, **fields)

    return event


async def get_user_im(client: AsyncWebClient, user_id: str, cache: dict) -> str:
    # NOTE: this is the easiest way to implement LRU cache with coroutines
    if user_id not in cache:
        response = await client.conversations_list(exclude_archived=True, types="im")
        for channel in response["channels"]:
            cache[channel["user"]] = channel["id"]
    return cache[user_id]


async def download_email_html(url: str, auth_token: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"Authorization": f"Bearer {auth_token}"}) as response:
            html = await response.text()
    return html


def preprocess_slack_event(event: dict[str, Any]):
    file = event["files"].pop()
    assert file["mode"] == "email"
    assert file["from"][0]["address"] == "tfs@astralnalog.ru"

    headers = file["headers"]
    plain_text = file["plain_text"]
    file_url = file["url_private"]  # file["preview"] is not sufficient for every case
    return headers, plain_text, file_url


async def work(slack_client: AsyncWebClient, headers: dict[str, str], plain_text: str, html_url: str):
    """Parse event and send notification through the client"""
    html = asyncio.create_task(download_email_html(html_url, slack_client.token))
    event: TFSEvent = await dispatch_text(headers, plain_text, html)

    user_id = slack_users[event.subscriber]
    try:
        channel = await get_user_im(slack_client, user_id, slack_ims)
    except KeyError:
        raise KeyError(f"Looks like {event.subscriber} hasn't added app to their DM")
    markdown_text = event.to_markdown()

    response = await slack_client.chat_postMessage(
        channel=channel,
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

    return event, response
