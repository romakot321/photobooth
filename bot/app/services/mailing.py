from typing import Annotated
from loguru import logger
from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram3_di import Depends

from app.repositories.mailing import MailingRepository
from app.repositories.user import UserRepository
from app.schemas.action import MailingData


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
        users = await self.user_repository.list()
        logger.debug(users)

        for user in users:
            if mailing.gender and user.gender != mailing.gender:
                continue
            if mailing.tariff_id and (mailing.tariff_id == -1 and user.tariff_id is None or mailing.tariff_id != user.tariff_id):
                continue
            await bot.send_message(user.chat_id, mailing.text)

