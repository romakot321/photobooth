from db.tables import MailingTemplate

from sqlalchemy_service import BaseService as BaseRepository
from sqlalchemy_service.base_db.base import Base as BaseTable
from sqlalchemy_service.base_db.base import get_session

from typing import TypedDict, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram3_di import Depends


operation_comments = [
    "Покупка новой модели",
    "Основной тариф 1390 руб / 50 фото",
    "Основной тариф 1390 руб / 100 фото",
    "Покупка новых генераций: +10",
    "Покупка новых генераций: +50",
    "Покупка новых генераций: +100",
    "Начисление партнеру доп. генераций",
    "Спец предложение 390 руб за 10 фото",
    "Основной тариф 990 руб / 50 фото",
    "Спец предложение 490 руб за 10 фото"
]


class MailingTemplateRepository[Table: MailingTemplate, int](BaseRepository):
    base_table = MailingTemplate

    @classmethod
    def init(
            cls,
            session: Annotated[AsyncSession, Depends(get_session)]
    ):
        return cls(session=session)

    async def _get_list(
        self,
        page: int | None = None,
        count: int | None = None,
        select_in_load = None,
        none_as_values: bool = False,
        **filters
    ):
        query = self._get_list_query(
            page=page,
            count=count,
            select_in_load=select_in_load,
            none_as_values=none_as_values,
            **filters
        )
        return await self.session.scalars(query)

    async def get(self, model_id: int) -> MailingTemplate:
        return await self._get_one(id=model_id)

    async def list(self, **filters) -> list[MailingTemplate]:
        return list(await self._get_list(count=1000000, **filters))

