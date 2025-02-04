from fastapi import Depends

from app.schemas.mailing_template import MailingTemplateSchema
from app.schemas.mailing_template import MailingTemplateSearchSchema
from app.schemas.mailing_template import MailingTemplateCreateSchema
from app.schemas.mailing_template import MailingTemplateUpdateSchema
from app.db.tables import MailingTemplate
from app.repositories.mailing_template import MailingTemplateRepository


class MailingTemplateService:
    def __init__(
            self,
            template_repository: MailingTemplateRepository = Depends()
    ):
        self.template_repository = template_repository

    async def list(self, schema: MailingTemplateSearchSchema = None) -> list[MailingTemplateSchema]:
        models = await self.template_repository.list(**schema.model_dump(exclude_none=True))
        return [MailingTemplateSchema.model_validate(model) for model in models]

    async def get(self, template_id: int) -> MailingTemplateSchema:
        model = await self.template_repository.get(template_id)
        return MailingTemplateSchema.model_validate(model)

    async def create(self, schema: MailingTemplateCreateSchema) -> MailingTemplateSchema:
        model = MailingTemplate(**schema.model_dump(exclude_none=True))
        model = await self.template_repository.create(model)
        return MailingTemplateSchema.model_validate(model)

    async def update(self, model_id: int, schema: MailingTemplateUpdateSchema) -> MailingTemplateSchema:
        model = await self.template_repository.update(model_id, **schema.model_dump())
        return MailingTemplateSchema.model_validate(model)

    async def delete(self, model_id: int):
        await self.template_repository.delete(model_id)

