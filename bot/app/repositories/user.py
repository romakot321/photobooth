from db.tables import User
from sqlalchemy_service import BaseService as BaseRepository
from sqlalchemy_service.base_db.base import Base as BaseTable
from sqlalchemy_service.base_db.base import get_session

from typing import TypedDict, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram3_di import Depends


class UserRepository[Table: User, int](BaseRepository):
    base_table = User

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
        **filters
    ):
        query = self._get_list_query(
            page=page,
            count=count,
            select_in_load=select_in_load,
            **filters
        )
        return await self.session.scalars(query)

    async def create(self, model: User) -> User:
        self.session.add(model)
        await self._commit()
        await self.session.refresh(model)
        self.response.status_code = 201
        return await self.get(model.id)

    async def list(self, gender=None, tariff_id=None) -> list[User]:
        filters = {k: v for k, v in (('gender', gender), ('tariff_id', tariff_id)) if v is not None}
        return list(await self._get_list(count=1000000, **filters))

