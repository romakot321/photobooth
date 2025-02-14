from typing import Annotated
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram3_di import Depends
import asyncio

import app
from app.repositories import redis
from app.repositories.mailing import MailingRepository
from app.repositories.mailing_template import MailingTemplateRepository
from app.repositories.user import UserRepository
from app.repositories.message import create_mailing_handler, create_test_handler, get_mailing_messages_count, get_sended_chat_ids
from app.repositories.redis import RedisRepository
from app.repositories.message import set_mailing_pause
from app.schemas.action import MailingData
from app.schemas.mailing import MailingTestData
from db.tables import Mailing, User
from sqlalchemy_service.base_db.base import get_session


class MailingService:
    def __init__(self, mailing_repository, user_repository):
        self.mailing_repository = mailing_repository
        self.user_repository = user_repository

    @classmethod
    def init(
            cls,
            mailing_repository: Annotated[
                MailingRepository, Depends(MailingRepository.init)],
            user_repository: Annotated[
                UserRepository, Depends(UserRepository.init)],
    ):
        return cls(mailing_repository, user_repository)

    async def _get_users_for_mailing(self, mailing: Mailing, from_user_id: int | None = None) -> list[User]:
        tariff_ids = []
        if mailing.tariffs:
            tariff_ids = [t.id for t in mailing.tariffs]
        elif mailing.template and mailing.template.tariffs:
            tariff_ids = [t.id for t in mailing.template.tariffs]

        users = await self.user_repository.list(
            tariff_ids=tariff_ids,
            god_mode=mailing.god_mode or (mailing.god_mode if mailing.template is None else mailing.template.god_mode),
            without_tariff=mailing.without_tariff or (mailing.without_tariff if mailing.template is None else mailing.template.without_tariff),
            gender=mailing.gender or (None if mailing.template is None else mailing.template.gender),
            created_from=mailing.created_from,
            created_to=mailing.created_to,
            limit=mailing.limit_messages,
            offset=mailing.offset_messages,
            from_user_id=from_user_id
        )
        return users

    async def handle_start_mailing(
            self,
            data: MailingData,
            query: CallbackQuery,
            bot: Bot
    ):
        mailing: Mailing = await self.mailing_repository.get(data.mailing_id)
        users = await self._get_users_for_mailing(mailing)
        logger.debug(f"Starting mailing({mailing.id=}) for {len(users)} users")

        handler = create_mailing_handler(mailing, users)
        asyncio.create_task(handler.start())

    @classmethod
    async def restore_mailings(cls):
        sessionmaker = get_session()
        db_session: AsyncSession = await anext(sessionmaker)
        mailing_repository = MailingRepository(session=db_session)
        user_repository = UserRepository(session=db_session)
        redis_repository = RedisRepository()
        self = cls(mailing_repository=mailing_repository, user_repository=user_repository)

        mailings_statuses = await redis_repository.list_mailings_statuses()
        for mailing_id, status in mailings_statuses.items():
            if status == "finished":
                continue
            mailing = await mailing_repository.get(mailing_id)
            last_user_id = await redis_repository.get_mailing_last_user_id(mailing_id)
            users = await self._get_users_for_mailing(mailing, from_user_id=last_user_id)
            handler = create_mailing_handler(mailing, users)
            if status == "pause":
                await handler.set_pause(True)
            asyncio.create_task(handler.start())
            logger.debug(f"Restarted mailing({mailing.id=}) for {len(users)} users")

        try:
            await db_session.close()
            await anext(sessionmaker)
        except StopAsyncIteration:
            pass

    @classmethod
    async def get_mailing_messages_sent(cls, mailing_id) -> int:
        count = get_mailing_messages_count(mailing_id)
        return count or 0

    @classmethod
    async def get_mailing_sended_chat_ids(cls, mailing_id) -> list[int]:
        chat_ids = get_sended_chat_ids(mailing_id)
        return chat_ids or []

    @classmethod
    async def pause_sending(cls, mailing_id: int, value: bool):
        await set_mailing_pause(mailing_id, value)

    @classmethod
    async def test_mailing(cls, data: MailingTestData):
        handler = create_test_handler(data.text, data.buttons or [], data.image_filename, data.chat_id)
        asyncio.create_task(handler.start())

