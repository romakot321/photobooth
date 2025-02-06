from db.tables import Generation, User
from sqlalchemy_service import BaseService as BaseRepository
from sqlalchemy_service.base_db.base import Base as BaseTable
from sqlalchemy_service.base_db.base import get_session
from sqlalchemy import not_

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

    async def list(self, gender=None, without_tariff: bool = None, tariff_ids: list[int] = None, god_mode: bool = None) -> list[User]:
        query = self._get_list_query(count=10000000)
        if gender is not None:
            query = query.filter_by(gender=gender)
        if without_tariff:
            tariff_ids = [None] if tariff_ids is None else tariff_ids + [None]
        if tariff_ids is not None and tariff_ids:
            query = query.filter(User.tariff_id.in_(tariff_ids))
        if god_mode is not None:
            if god_mode:
                query = query.filter(User.generations.any(Generation.is_god_mode == True))
            else:
                query = query.filter(not_(User.generations.any(Generation.is_god_mode == True)))
        print(query)
        return list(await self.session.scalars(query))

