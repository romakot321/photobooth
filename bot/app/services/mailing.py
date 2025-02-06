from typing import Annotated
from loguru import logger
from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram3_di import Depends
import asyncio

import app
from app.repositories.mailing import MailingRepository
from app.repositories.mailing_template import MailingTemplateRepository
from app.repositories.user import UserRepository
from app.repositories.message import create_mailing_handler, create_test_handler
from app.schemas.action import MailingData
from app.schemas.mailing import MailingTestData
from db.tables import Mailing, User


class MailingService:
    def __init__(self, mailing_repository, user_repository, template_repository):
        self.mailing_repository = mailing_repository
        self.user_repository = user_repository
        self.template_repository = template_repository

    @classmethod
    def init(
            cls,
            mailing_repository: Annotated[
                MailingRepository, Depends(MailingRepository.init)],
            template_repository: Annotated[
                MailingTemplateRepository, Depends(MailingTemplateRepository.init)],
            user_repository: Annotated[
                UserRepository, Depends(UserRepository.init)],
    ):
        return cls(mailing_repository, user_repository, template_repository)

    async def handle_start_mailing(self, data: MailingData, query: CallbackQuery, bot: Bot):
        mailing = await self.mailing_repository.get(data.mailing_id)
        tariff_ids = []
        if mailing.tariffs:
            tariff_ids = [t.id for t in mailing.tariffs]
        elif mailing.template and mailing.template.tariffs:
            tariff_ids = [t.id for t in mailing.template.tariffs]

        users = await self.user_repository.list(
            tariff_ids=tariff_ids,
            god_mode=mailing.god_mode or (mailing.god_mode if mailing.template is None else mailing.template.god_mode),
            without_tariff=mailing.without_tariff or (mailing.without_tariff if mailing.template is None else mailing.template.without_tariff),
            gender=mailing.gender or (None if mailing.template is None else mailing.template.gender)
        )
        logger.debug(f"Starting mailing({mailing.id=}) for {len(users)} users")

        handler = create_mailing_handler(mailing, users)
        asyncio.create_task(handler.start())

    @classmethod
    async def test_mailing(cls, data: MailingTestData):
        handler = create_test_handler(data.text, data.buttons or [], data.chat_id)
        asyncio.create_task(handler.start())

