from fastapi import APIRouter, Depends

from app.services.mailing_template import MailingTemplateService
from app.schemas.mailing_template import MailingTemplateSearchSchema, MailingTemplateUpdateSchema
from app.schemas.mailing_template import MailingTemplateSchema, MailingTemplateCreateSchema

router = APIRouter(prefix="/api/mailing/template", tags=["Mailing Template"])


@router.get("", response_model=list[MailingTemplateSchema])
async def list_templates(
        schema: MailingTemplateSearchSchema = Depends(),
        service: MailingTemplateService = Depends()
):
    return await service.list(schema)


@router.get("/{template_id}", response_model=MailingTemplateSchema)
async def get_template(
        template_id: int,
        service: MailingTemplateService = Depends()
):
    return await service.get(template_id)


@router.post("", response_model=MailingTemplateSchema)
async def create_template(
        schema: MailingTemplateCreateSchema,
        service: MailingTemplateService = Depends()
):
    return await service.create(schema)


@router.patch("/{template_id}", response_model=MailingTemplateSchema)
async def update_template(
        template_id: int,
        schema: MailingTemplateUpdateSchema,
        service: MailingTemplateService = Depends()
):
    return await service.update(template_id, schema)


@router.delete("/{template_id}", status_code=204)
async def delete_template(
        template_id: int,
        service: MailingTemplateService = Depends()
):
    return await service.delete(template_id)

