import asyncio
import email
import email.policy
import logging

import aiosmtpd.smtp


class EnqueueHandler:
    """SMTP commands handler that forwards emails to a specified queue"""

    def __init__(self, queue: asyncio.Queue):
        self.msg_queue = queue

    async def handle_DATA(self, server, session, envelope):
        logging.debug(f"Handle data from {session.peer[0]}:{session.peer[1]}")
        msg = email.message_from_bytes(
            envelope.original_content, policy=email.policy.default
        )
        self.msg_queue.put_nowait(msg)
        return "250 OK"


class SMTP(aiosmtpd.smtp.SMTP):
    def __init__(self, message_queue, loop=None):
        logging.debug("Start SMTP server")
        handler = EnqueueHandler(message_queue)
        super().__init__(handler, loop=loop)
