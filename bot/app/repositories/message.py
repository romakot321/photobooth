from loguru import logger
import aiogram
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.input_file import FSInputFile
import asyncio
import os
import re
import pathlib
from redis import exceptions
from dataclasses import dataclass

from app.repositories.user import UserRepository
from db.tables import Mailing, User
from app.schemas.mailing import MailingButtonData
from app.repositories.redis import RedisRepository
from sqlalchemy_service.base_db.base import async_session


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
                [
                    InlineKeyboardButton(text=b.text, callback_data=b.callback_data, url=b.url)
                    for b in buttons
                ]
            ]
        )
        return keyboard

    def _escape_markdown(self, text: str) -> str:
        escape_characters = [
            '_', '*', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'
        ]
        for char in escape_characters:
            text = text.replace(char, f'\\{char}')
        return text

    async def _send_message(
            self,
            chat_id: int,
            text: str,
            keyboard: InlineKeyboardMarkup | None,
            image_path: str | None,
            video_path: str | None
    ):
        # text = self._escape_markdown(text)
        try:
            if image_path is not None:
                await self.bot.send_photo(chat_id=chat_id, caption=text, photo=FSInputFile(image_path), reply_markup=keyboard, parse_mode="HTML")
            elif video_path is not None:
                await self.bot.send_video(chat_id=chat_id, caption=text, video=FSInputFile(video_path), reply_markup=keyboard, parse_mode="HTML")
            else:
                await self.bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")
        except (aiogram.exceptions.TelegramBadRequest, aiogram.exceptions.TelegramForbiddenError, aiogram.exceptions.TelegramNetworkError) as e:
            pass
        except aiogram.exceptions.TelegramRetryAfter as e:
            logger.info("Rate limit exceed")

    async def send(self, chat_ids: list[int | str | None], text: str, buttons: list[_Button], image_path: str | None, video_path: str | None):
        while self.is_locked:
            await asyncio.sleep(1)
        keyboard = self._build_keyboard(buttons)

        self.is_locked = True
        for chat_id in chat_ids:
            await asyncio.sleep(3)
            if chat_id is None:
                continue
            await asyncio.sleep(0.1)
            await self._send_message(int(chat_id), text, keyboard, image_path, video_path)
        self.is_locked = False


class _MailingHandler:
    storage_path = pathlib.Path(os.getenv("IMAGE_STORAGE_PATH", "images"))

    def __init__(self, mailing: Mailing, users_count: int, sender: _Sender, db: RedisRepository):
        self.mailing = mailing
        self.users_count = users_count
        self.sender = sender
        self.message_count = 0
        self.sended_chat_ids = []
        self.is_finished = False
        self._pause = False
        self.db = db

    def _get_image_path(self) -> str | None:
        if not self.mailing.images or self.mailing.images[0].is_video:
            return None
        return str(self.storage_path / self.mailing.images[0].filename)

    def _get_video_path(self) -> str | None:
        if not self.mailing.images or not self.mailing.images[0].is_video:
            return None
        return str(self.storage_path / self.mailing.images[0].filename)

    async def _list_users(self, offset: int, count: int = 100000) -> list[User]:
        async with async_session() as db_session:
            user_repository = UserRepository(session=db_session)
            last_user_id = await self.db.get_mailing_last_user_id(self.mailing.id)
            users = await user_repository.list_from_mailing(
                self.mailing,
                from_user_id=last_user_id,
                offset=offset,
                count=count
            )
        return users

    async def set_pause(self, value: bool):
        self._pause = value
        await self.db.set_mailing_status(self.mailing.id, ("pause" if value else "running"))

    async def start(self):
        text = self.mailing.text or ('' if self.mailing.template is None else self.mailing.template.text)
        if not self._pause:
            await self.db.set_mailing_status(self.mailing.id, "running")

        for offset in range(0, self.users_count, 100000):
            users = await self._list_users(offset)

            for i in range(0, len(users), 3):
                while self._pause:
                    await asyncio.sleep(1)
                if self.is_finished:
                    break
                chat_ids = [u.chat_id for u in users[i:i + 3]]

                await self.sender.send(chat_ids, text, self.mailing.buttons, self._get_image_path(), self._get_video_path())
                await self.db.add_mailing_user_ids(self.mailing.id, *[u.id for u in users[i:i + 3]])

                self.sended_chat_ids += chat_ids
                self.message_count += len(chat_ids)

            try:
                await self.db.save()
            except exceptions.ResponseError:
                pass

        await self.db.set_mailing_status(self.mailing.id, "finished")
        await self.db.close()
        self.is_finished = True
        logger.debug(f"Mailing {self.mailing.id=} finished")


class _TestHandler:
    storage_path = pathlib.Path(os.getenv("IMAGE_STORAGE_PATH", "images"))

    def __init__(self, text: str, chat_ids: list[int], image_filename: str | None, video_filename: str | None, buttons: list[_Button], sender: _Sender):
        self.text = text
        self.chat_ids = chat_ids
        self.sender = sender
        self.message_count = 0
        self.buttons = buttons
        self.image_filename = image_filename
        self.video_filename = video_filename

    def _get_image_path(self) -> str | None:
        if not self.image_filename:
            return None
        return str(self.storage_path / self.image_filename)

    def _get_video_path(self) -> str | None:
        if not self.video_filename:
            return None
        return str(self.storage_path / self.video_filename)

    async def start(self):
        for i in range(0, len(self.chat_ids), 5):
            chat_ids = self.chat_ids[i:i + 5]
            await self.sender.send(chat_ids, self.text, self.buttons, self._get_image_path(), self._get_video_path())
            self.message_count += len(chat_ids)


sender = _Sender()
handlers: list[_MailingHandler] = []


def create_test_handler(text: str, buttons: list[MailingButtonData], image_filename: str | None, video_filename: str | None, *chat_ids: int) -> _TestHandler:
    global handlers, sender
    return _TestHandler(text, chat_ids, image_filename, video_filename, buttons, sender)


def create_mailing_handler(mailing: Mailing, users_count: int) -> _MailingHandler:
    global handlers, sender
    redis_service = RedisRepository()
    handler = _MailingHandler(mailing, users_count, sender, redis_service)
    handlers.append(handler)
    return handler


def get_mailing_messages_count(mailing_id: int) -> int | None:
    for handler in handlers:
        if handler.mailing.id == mailing_id:
            return handler.message_count
    return None


def get_sended_chat_ids(mailing_id: int) -> list[int] | None:
    for handler in handlers:
        if handler.mailing.id == mailing_id:
            return handler.sended_chat_ids
    return None


async def set_mailing_pause(mailing_id: int, value: bool):
    for handler in handlers:
        if handler.mailing.id == mailing_id:
            await handler.set_pause(value)
            break

