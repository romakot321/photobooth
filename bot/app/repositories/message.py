from loguru import logger
from aiogram import Bot
import asyncio

import app
from db.tables import Mailing, User


class _Sender:
    def __init__(self, bot: Bot):
        self.is_locked = False
        self.bot = bot

    async def send(self, chat_ids: list[int], text: str):
        while self.is_locked:
            await asyncio.sleep(0.1)

        self.is_locked = True
        for chat_id in chat_ids:
            await asyncio.sleep(0.2)
            await self.bot.send_message(chat_id, text)
        self.is_locked = False


class _MailingHandler:
    def __init__(self, mailing: Mailing, users: list[User], sender: _Sender):
        self.mailing = mailing
        self.users = users
        self.sender = sender
        self.message_count = 0

    async def start(self):
        text = self.mailing.text or self.mailing.template.text

        for i in range(0, len(self.users), 5):
            chat_ids = [u.chat_id for u in self.users[i:i + 5]]
            await self.sender.send(chat_ids, text)
            self.message_count += len(chat_ids)


sender = _Sender(app.bot_instance)
handlers = []


def create_mailing_handler(mailing: Mailing, users: list[User]) -> _MailingHandler:
    global handlers, sender
    handler = _MailingHandler(mailing, users, sender)
    handlers.append(handler)
    return handler


def get_messages_count(mailing: Mailing) -> int | None:
    for handler in handlers:
        if handler.mailing.id == mailing.id:
            return handler.message_count
    return None

