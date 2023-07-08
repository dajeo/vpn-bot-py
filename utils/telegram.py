import asyncio

import telegram
from telegram.constants import ParseMode

import conf


async def _send_message(chat_id: int, message: str, parse_mode: ParseMode = None):
    await telegram.Bot(conf.get()["bot"]["token"]).send_message(chat_id, message, parse_mode=parse_mode)


def send_message(chat_id: int, message: str, parse_mode: ParseMode = None):
    asyncio.run(_send_message(chat_id, message, parse_mode))
