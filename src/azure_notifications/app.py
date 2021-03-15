import asyncio
import functools

from azure_notifications.config import SMTP_SERVER_PORT
from azure_notifications.smtpd import SMTP as MailServer
from azure_notifications.worker import dispatch_email


async def consume(queue: asyncio.Queue):
    while True:
        msg = await queue.get()
        event = dispatch_email(msg)
        print(event)


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
