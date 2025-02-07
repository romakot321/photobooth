from sqlalchemy_service import BaseService as BaseRepository
from sqlalchemy_service.base_db.base import Base as BaseTable
from sqlalchemy_service.base_db.base import get_session
from sqlalchemy import not_, or_, func, select

from app.db.tables import Generation, User


class UserRepository[Table: User, int](BaseRepository):
    base_table = User

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

    async def list(
            self,
            gender: str | None = None,
            without_tariff: bool | None = None,
            tariff_ids: list[int] | None = None,
            god_mode: bool | None = None
    ) -> list[User]:
        query = self._get_list_query(count=10000000)
        if gender is not None:
            query = query.filter_by(gender=gender)
        if tariff_ids is not None and tariff_ids:
            if without_tariff is True:
                query = query.filter(or_(User.tariff_id.in_(tariff_ids), User.tariff_id == None))
            else:
                query = query.filter(User.tariff_id.in_(tariff_ids))
        elif without_tariff:
            query = query.filter_by(tariff_id=None)
        if god_mode is not None:
            if god_mode:
                query = query.filter(User.generations.any(Generation.is_god_mode == True))
            else:
                query = query.filter(not_(User.generations.any(Generation.is_god_mode == True)))
        return list(await self.session.scalars(query))

    async def count(
            self,
            gender: str | None = None,
            without_tariff: bool | None = None,
            tariff_ids=None,
            god_mode: bool | None = None
    ) -> int:
        query = select(func.count("*")).select_from(User)
        if gender is not None:
            query = query.filter_by(gender=gender)
        if tariff_ids is not None and tariff_ids:
            if without_tariff is True:
                query = query.filter(or_(User.tariff_id.in_(tariff_ids), User.tariff_id == None))
            else:
                query = query.filter(User.tariff_id.in_(tariff_ids))
        elif without_tariff:
            query = query.filter_by(tariff_id=None)
        if god_mode is not None:
            if god_mode:
                query = query.filter(User.generations.any(Generation.is_god_mode == True))
            else:
                query = query.filter(not_(User.generations.any(Generation.is_god_mode == True)))
        return await self.session.scalar(query)

