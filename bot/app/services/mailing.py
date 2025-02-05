from typing import Annotated
from loguru import logger
from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram3_di import Depends
import asyncio

import app
from app.repositories.mailing import MailingRepository
from app.repositories.user import UserRepository
from app.repositories.message import create_mailing_handler
from app.schemas.action import MailingData
from db.tables import Mailing, User


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

    async def handle_start_mailing(self, data: MailingData, query: CallbackQuery, bot: Bot):
        mailing = await self.mailing_repository.get(data.mailing_id)
        users = await self.user_repository.list(
            tariff_id=mailing.tariff_id or mailing.template.tariff_id,
            gender=mailing.gender or mailing.template.gender
        )

        handler = create_mailing_handler(mailing, users)
        asyncio.create_task(handler.start())

