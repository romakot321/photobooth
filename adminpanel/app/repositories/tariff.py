from sqlalchemy_service import BaseService as BaseRepository

from app.db.tables import Tariff


class TariffRepository[Table: Tariff, int](BaseRepository):
    base_table = Tariff

    async def list(self, text: str = None, page=None, count=None) -> list[Tariff]:
        query = self._get_list_query(page=page, count=count)
        if text:
            query = self._query_like_filter(query, text=text)
        return list(await self.session.scalars(query))

    async def get(self, model_id: int) -> Tariff:
        return await self._get_one(id=model_id)

