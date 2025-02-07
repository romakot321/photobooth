from fastapi import Depends

from app.repositories.user import UserRepository
from app.schemas.mailing_template import MailingTemplateSchema
from app.schemas.mailing_template import MailingTemplateSearchSchema
from app.schemas.mailing_template import MailingTemplateCreateSchema
from app.schemas.mailing_template import MailingTemplateUpdateSchema
from app.schemas.tariff import TariffSchema
from app.db.tables import MailingTemplate, Tariff
from app.repositories.mailing_template import MailingTemplateRepository
from app.repositories.tariff import TariffRepository


class MailingTemplateService:
    def __init__(
            self,
            template_repository: MailingTemplateRepository = Depends(),
            tariff_repository: TariffRepository = Depends(),
            user_repository: UserRepository = Depends()
    ):
        self.template_repository = template_repository
        self.tariff_repository = tariff_repository
        self.user_repository = user_repository

        self._tariffs_cache: list[TariffSchema] = []

    async def list_tariffs(self) -> list[TariffSchema]:
        if self._tariffs_cache:
            return self._tariffs_cache
        models = await self.tariff_repository.list()
        schemas = [TariffSchema.model_validate(model) for model in models]
        self._tariffs_cache = schemas
        return schemas

    async def list(self, schema: MailingTemplateSearchSchema | None = None) -> list[MailingTemplateSchema]:
        filters = schema.model_dump(exclude_none=True) if schema else {}
        models = await self.template_repository.list(**filters)
        return [MailingTemplateSchema.model_validate(model) for model in models]

    async def get(self, template_id: int) -> MailingTemplateSchema:
        model = await self.template_repository.get(template_id)
        return MailingTemplateSchema.model_validate(model)

    async def create(self, schema: MailingTemplateCreateSchema) -> MailingTemplateSchema:
        state = schema.model_dump(exclude_none=True)
        tariffs = []
        if schema.tariff_ids:
            for tariff_id in state.pop("tariff_ids"):
                tariffs.append(await self.tariff_repository.get(tariff_id))
        model = MailingTemplate(**state)
        model.tariffs = tariffs
        model = await self.template_repository.create(model)
        return MailingTemplateSchema.model_validate(model)

    async def update(self, model_id: int, schema: MailingTemplateUpdateSchema) -> MailingTemplateSchema:
        model = await self.template_repository.update(model_id, **schema.model_dump())
        return MailingTemplateSchema.model_validate(model)

    async def delete(self, model_id: int):
        await self.template_repository.delete(model_id)

    async def get_messages_to_send_count(self, template_id) -> int:
        model = await self.template_repository.get(template_id)
        return await self.user_repository.count(
            tariff_ids=[m.id for m in model.tariffs],
            god_mode=model.god_mode,
            # without_tariff=model.without_tariff,
            gender=model.gender
        )

