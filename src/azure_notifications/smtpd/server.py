import asyncio


class Handler:

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        pass

    async def handle_DATA(self, server, session, envelope):
        pass