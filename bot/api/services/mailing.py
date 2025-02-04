from fastapi import Depends

from app.controller import BotController


class MailingService:
    def __init__(self, bot_controller: BotController = Depends()):
        self.bot_controller = bot_controller

    async def start(self, mailing_id: int):
        await self.bot_controller.start_mailing(mailing_id)

