from sqlalchemy_service import BaseService as BaseRepository

from app.db.tables import Mailing, MailingTemplate


class MailingRepository[Table: Mailing, int](BaseRepository):
    base_table = Mailing

    async def create(self, model: Mailing) -> Mailing:
        self.session.add(model)
        await self._commit()
        await self.session.refresh(model)
        self.response.status_code = 201
        return await self.get(model.id)

    async def list(self, text: str | None = None, page=None, count=None) -> list[Mailing]:
        query = self._get_list_query(page=page, count=count)
        if text:
            query = self._query_like_filter(query, text=text)
        query = query.order_by(Mailing.created_at.desc())
        return list(await self.session.scalars(query))

    async def get(self, model_id: int) -> Mailing:
        return await self._get_one(
            id=model_id,
            select_in_load=[
                Mailing.tariffs,
                {"parent": Mailing.template, "children": [MailingTemplate.tariffs]},
                Mailing.buttons
            ]
        )

    async def update(self, model_id: int, **fields) -> Mailing:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: int):
        await self._delete(model_id)

