from sqlalchemy_service import BaseService as BaseRepository

from app.db.tables import MailingTemplate


class MailingTemplateRepository[Table: MailingTemplate, int](BaseRepository):
    base_table = MailingTemplate

    async def create(self, model: MailingTemplate) -> MailingTemplate:
        self.session.add(model)
        await self._commit()
        await self.session.refresh(model)
        self.response.status_code = 201
        return await self.get(model.id)

    async def list(self, text: str = None, page=None, count=None) -> list[MailingTemplate]:
        query = self._get_list_query(page=page, count=count)
        if text:
            query = self._query_like_filter(query, text=text)
        return list(await self.session.scalars(query))

    async def get(self, model_id: int) -> MailingTemplate:
        return await self._get_one(id=model_id, select_in_load=MailingTemplate.tariffs)

    async def update(self, model_id: int, **fields) -> MailingTemplate:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: int):
        await self._delete(model_id)

