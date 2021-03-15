import asyncio
import aiosmtpd.smtp
import email


class EnqueueHandler:
    """SMTP commands handler that forwards emails to a specified queue"""

    def __init__(self, queue: asyncio.Queue):
        self.msg_queue = queue

    async def handle_DATA(self, server, session, envelope):
        print("handle data")
        msg = email.message_from_bytes(envelope.original_content)
        self.msg_queue.put_nowait(msg)
        return "250 OK"


class SMTP(aiosmtpd.smtp.SMTP):
    def __init__(self, message_queue, loop=None):
        print("init")
        handler = EnqueueHandler(message_queue)
        super().__init__(handler, loop=loop)
