from sqlalchemy_service import BaseService as BaseRepository

from app.db.tables import MailingImage


class ImageRepository[Table: MailingImage, int](BaseRepository):
    base_table = MailingImage

    async def create(self, model: MailingImage) -> MailingImage:
        self.session.add(model)
        await self._commit()
        await self.session.refresh(model)
        self.response.status_code = 201
        return await self.get(model.id)

    async def list(self, page=None, count=None) -> list[MailingImage]:
        query = self._get_list_query(page=page, count=count)
        query = query.order_by(MailingImage.created_at.desc())
        return list(await self.session.scalars(query))

    async def get(self, model_id: int) -> MailingImage:
        return await self._get_one(id=model_id)

    async def update(self, filename: str, **fields) -> MailingImage:
        return await self._update({"filename": filename}, **fields)

    async def delete(self, model_id: int):
        await self._delete(model_id)

