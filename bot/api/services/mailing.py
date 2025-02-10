from fastapi import Depends

from app.controller import BotController


class MailingService:
    def __init__(self, bot_controller: BotController = Depends()):
        self.bot_controller = bot_controller

    async def start(self, mailing_id: int):
        await self.bot_controller.start_mailing(mailing_id)

    async def test(self, schema):
        await self.bot_controller.test_mailing(**schema.model_dump())

    async def get_mailing_messages_count(self, mailing_id: int) -> int:
        return await self.bot_controller.get_mailing_messages_count(mailing_id)

    async def get_mailing_sended_chat_ids(self, mailing_id: int) -> list[int]:
        return await self.bot_controller.get_mailing_sended_chat_ids(mailing_id)

    async def pause_mailing_sending(self, mailing_id: int, value: bool):
        await self.bot_controller.pause_mailing_sending(mailing_id, value)

