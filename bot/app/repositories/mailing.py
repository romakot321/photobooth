from db.tables import Mailing

from sqlalchemy_service import BaseService as BaseRepository
from sqlalchemy_service.base_db.base import Base as BaseTable
from sqlalchemy_service.base_db.base import get_session

from typing import TypedDict, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram3_di import Depends


class MailingRepository[Table: Mailing, int](BaseRepository):
    base_table = Mailing

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

    async def get(self, model_id: int) -> Mailing:
        return await self._get_one(id=model_id, select_in_load=Mailing.template)

    async def create(self, model: Mailing) -> Mailing:
        return await self._create(model)

    async def list(self, **filters) -> list[Mailing]:
        return list(await self._get_list(count=1000000, **filters))

