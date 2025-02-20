from db.tables import Generation, Order, User
from sqlalchemy_service import BaseService as BaseRepository
from sqlalchemy_service.base_db.base import Base as BaseTable
from sqlalchemy_service.base_db.base import get_session
from sqlalchemy import and_, not_, or_
import datetime as dt

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

    async def list(
            self,
            gender=None,
            without_tariff: bool = None,
            tariff_ids: list[int] = None,
            god_mode: bool = None,
            created_from: dt.datetime | None = None,
            created_to: dt.datetime | None = None,
            limit: int | None = None,
            offset: int | None = None,
            from_user_id: int | None = None,
            next_payment_date: dt.date | None = None
    ) -> list[User]:
        query = self._get_list_query(count=10000000)
        if gender is not None:
            query = query.filter_by(gender=gender)
        if tariff_ids is not None and tariff_ids:
            if without_tariff:
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
        if created_from is not None:
            query = query.filter(User.created_at >= created_from)
        if created_to is not None:
            query = query.filter(User.created_at <= created_to)
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
            if limit is None:
                query = query.limit(18446744073709551615)
        if from_user_id is not None:
            query = query.filter(User.id > from_user_id)
        if next_payment_date is not None:
            next_payment_date = next_payment_date - dt.timedelta(days=30)
            start_datetime = dt.datetime(hour=0, minute=0, second=0, day=next_payment_date.day, month=next_payment_date.month, year=next_payment_date.year)
            end_datetime = dt.datetime(hour=23, minute=59, second=59, day=next_payment_date.day, month=next_payment_date.month, year=next_payment_date.year)
            query = query.filter(User.orders.any(and_(Order.system_id == 1, Order.paid_at >= start_datetime, Order.paid_at <= end_datetime)))
        query = query.order_by(User.id)
        print(query)
        return list(await self.session.scalars(query))

