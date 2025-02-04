from typing import Annotated

from aiogram import F
from aiogram import Router, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram3_di import Depends
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.mailing import MailingService
from app.schemas.action import MailingData

router = Router(name=__name__)


@router.callback_query(MailingData.filter())
async def start_mailing(
        query: CallbackQuery,
        callback_data: MailingData,
        bot: Bot,
        service: Annotated[
            MailingService, Depends(MailingService.init)]
):
    await service.handle_start_mailing(callback_data, query, bot)

