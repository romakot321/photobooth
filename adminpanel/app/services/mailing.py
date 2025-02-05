from fastapi import Depends
from loguru import logger

from app.schemas.mailing import MailingSchema
from app.schemas.mailing import MailingSearchSchema
from app.schemas.mailing import MailingCreateSchema
from app.schemas.mailing import MailingUpdateSchema
from app.schemas.mailing import MailingTestSchema
from app.db.tables import Mailing
from app.repositories.mailing import MailingRepository
from app.repositories.bot import BotRepository
from app.repositories.tariff import TariffRepository


class MailingService:
    def __init__(
            self,
            mailing_repository: MailingRepository = Depends(),
            bot_repository: BotRepository = Depends(),
            tariff_repository: TariffRepository = Depends()
    ):
        self.mailing_repository = mailing_repository
        self.bot_repository = bot_repository
        self.tariff_repository = tariff_repository

    async def list(self, schema: MailingSearchSchema = None) -> list[MailingSchema]:
        models = await self.mailing_repository.list(**schema.model_dump(exclude_none=True))
        return [MailingSchema.model_validate(model) for model in models]

    async def get(self, mailing_id: int) -> MailingSchema:
        model = await self.mailing_repository.get(mailing_id)
        logger.debug(model.__dict__)
        return MailingSchema.model_validate(model)

    async def create_and_run(self, schema: MailingCreateSchema) -> MailingSchema:
        state = schema.model_dump(exclude_none=True)
        tariffs = []
        if schema.tariff_ids is not None:
            for tariff_id in state.pop("tariff_ids"):
                tariffs.append(await self.tariff_repository.get(tariff_id))
        model = Mailing(**state)
        model.tariffs = tariffs
        model = await self.mailing_repository.create(model)
        logger.debug(model.__dict__)
        await self.bot_repository.trigger_mailing_run(model.id)
        return MailingSchema.model_validate(model)

    async def update(self, model_id: int, schema: MailingUpdateSchema) -> MailingSchema:
        model = await self.mailing_repository.update(model_id, **schema.model_dump())
        return MailingSchema.model_validate(model)

    async def delete(self, model_id: int):
        await self.mailing_repository.delete(model_id)

    async def test(self, schema: MailingTestSchema):
        await self.bot_repository.trigger_mailing_test(schema.chat_id, schema.text)

