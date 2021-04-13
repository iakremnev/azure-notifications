import asyncio
import logging
import os
import json
from typing import Any

from azure_notifications.config import SERVER_PORT, BOT_SERVICE_CHANNEL
from azure_notifications.worker import preprocess_slack_event, work
from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient


logging.basicConfig(level=os.getenv("LOG_LEVEL") or logging.INFO)
save_events = True

slack = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)


@slack.event(
    {
        "type": "message",
        "channel": BOT_SERVICE_CHANNEL,
        "subtype": "file_share",
        "user": "USLACKBOT",
    }
)
async def process_azure_email(client: AsyncWebClient, event: dict[str, Any]):
    if save_events:
        with open(f"data/json/{event['event_ts']}.json", "w") as f:
            json.dump(event, f, indent=4, ensure_ascii=False)
        return

    headers, plain_text, file_url = preprocess_slack_event(event)
    asyncio.create_task(work(client, headers, plain_text, file_url))


if __name__ == "__main__":
    slack.start(SERVER_PORT)
