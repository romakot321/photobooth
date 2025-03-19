from db.tables import Mailing, MailingTemplate

from app.repositories.base import BaseRepository


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


class MailingRepository[Table: Mailing, int](BaseRepository):
    base_table = Mailing

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
        return await self._get_one(id=model_id, select_in_load=[Mailing.tariffs, {"parent": Mailing.template, "children": [MailingTemplate.tariffs]}])

    async def create(self, model: Mailing) -> Mailing:
        return await self._create(model)

    async def list(self, **filters) -> list[Mailing]:
        return list(await self._get_list(count=1000000, **filters))

