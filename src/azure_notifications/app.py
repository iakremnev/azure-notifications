import asyncio
import logging
import os
from email.message import EmailMessage

from azure_notifications.config import SERVER_PORT
from azure_notifications.slack import send_error_to_slack, send_to_slack
from azure_notifications.worker import dispatch_email
from slack_bolt.async_app import AsyncApp


logging.basicConfig(level=os.getenv("LOG_LEVEL") or logging.INFO)

slack = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


async def consume(queue: asyncio.Queue):
    while True:
        msg: EmailMessage = await queue.get()
        try:
            event = dispatch_email(msg)
            logging.info(event)
            await send_to_slack(event)
        except NotImplementedError:
            logging.error(
                "Couldn't handle message:\n"
                f"X-VSS-Event-Type:\t{msg['X-VSS-Event-Type']}\n"
                f"X-VSS-Event-Trigger:\t{msg['X-VSS-Event-Trigger']}"
            )
            await send_error_to_slack(msg)


if __name__ == "__main__":
    slack.start(SERVER_PORT)
