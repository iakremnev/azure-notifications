import asyncio
import functools
import logging
from email.message import EmailMessage

from azure_notifications.config import SMTP_SERVER_PORT
from azure_notifications.slack import send_error_to_slack, send_to_slack
from azure_notifications.smtpd import SMTP as MailServer
from azure_notifications.worker import dispatch_email


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


async def main():
    message_queue = asyncio.Queue()

    loop = asyncio.get_running_loop()
    smtp = await loop.create_server(
        functools.partial(MailServer, message_queue, loop), port=SMTP_SERVER_PORT
    )
    async with smtp:
        try:
            await consume(message_queue)
        except KeyboardInterrupt:
            pass


asyncio.run(main(), debug=True)
