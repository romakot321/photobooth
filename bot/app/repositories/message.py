from loguru import logger
import aiogram
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os
from dataclasses import dataclass

from db.tables import Mailing, User
from app.schemas.mailing import MailingButtonData


@dataclass
class _Button:
    text: str
    callback_data: str | None = None
    url: str | None = None


class _Sender:
    def __init__(self):
        self.is_locked = False
        self.bot = aiogram.Bot(token=os.getenv("BOT_TOKEN"))

    @classmethod
    def _build_keyboard(cls, buttons: list[_Button]) -> InlineKeyboardMarkup | None:
        if not buttons:
            return None
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=b.text, callback_data=b.callback_data, url=b.url) for b in buttons]
            ]
        )
        return keyboard

    async def send(self, chat_ids: list[int | str | None], text: str, buttons: list[_Button]):
        while self.is_locked:
            await asyncio.sleep(0.1)
        keyboard = self._build_keyboard(buttons)

        self.is_locked = True
        for chat_id in chat_ids:
            if chat_id is None:
                continue
            await asyncio.sleep(0.2)
            try:
                await self.bot.send_message(int(chat_id), text, reply_markup=keyboard)
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
            await self.sender.send(chat_ids, text, self.mailing.buttons)
            self.message_count += len(chat_ids)


class _TestHandler:
    def __init__(self, text: str, chat_ids: list[int], buttons: list[_Button], sender: _Sender):
        self.text = text
        self.chat_ids = chat_ids
        self.sender = sender
        self.message_count = 0
        self.buttons = buttons

    async def start(self):
        for i in range(0, len(self.chat_ids), 5):
            chat_ids = self.chat_ids[i:i + 5]
            await self.sender.send(chat_ids, self.text, self.buttons)
            self.message_count += len(chat_ids)


sender = _Sender()
handlers: list[_MailingHandler] = []


def create_test_handler(text: str, buttons: list[MailingButtonData], *chat_ids: int) -> _TestHandler:
    global handlers, sender
    return _TestHandler(text, chat_ids, buttons, sender)


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

