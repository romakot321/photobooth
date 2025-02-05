from loguru import logger
import aiogram
import asyncio
import os

import app
from db.tables import Mailing, User


class _Sender:
    def __init__(self):
        self.is_locked = False
        self.bot = aiogram.Bot(token=os.getenv("BOT_TOKEN"))

    async def send(self, chat_ids: list[int | str | None], text: str):
        while self.is_locked:
            await asyncio.sleep(0.1)

        self.is_locked = True
        for chat_id in chat_ids:
            if chat_id is None:
                continue
            await asyncio.sleep(0.2)
            try:
                await self.bot.send_message(int(chat_id), text)
            except aiogram.exceptions.TelegramBadRequest:
                continue
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


class _TestHandler:
    def __init__(self, text: str, chat_ids: list[int], sender: _Sender):
        self.text = text
        self.chat_ids = chat_ids
        self.sender = sender
        self.message_count = 0

    async def start(self):
        for i in range(0, len(self.chat_ids), 5):
            chat_ids = self.chat_ids[i:i + 5]
            await self.sender.send(chat_ids, self.text)
            self.message_count += len(chat_ids)


sender = _Sender()
handlers: list[_MailingHandler] = []


def create_test_handler(text: str, *chat_ids: list[int]) -> _TestHandler:
    global handlers, sender
    return _TestHandler(text, chat_ids, sender)


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

