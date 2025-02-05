from fastapi import APIRouter, Depends

from app.services.mailing import MailingService
from app.schemas.mailing import MailingSearchSchema, MailingUpdateSchema
from app.schemas.mailing import MailingSchema, MailingCreateSchema
from app.schemas.mailing import MailingTestSchema

router = APIRouter(prefix="/api/mailing", tags=["Mailing"])


@router.get("", response_model=list[MailingSchema])
async def list_mailings(
        schema: MailingSearchSchema = Depends(),
        service: MailingService = Depends()
):
    return await service.list(schema)


@router.get("/{mailing_id}", response_model=MailingSchema)
async def get_mailing(
        mailing_id: int,
        service: MailingService = Depends()
):
    return await service.get(mailing_id)


@router.post("/test", status_code=200)
async def test_mailing(
        schema: MailingTestSchema,
        service: MailingService = Depends()
):
    return await service.test(schema)


@router.post("", response_model=MailingSchema)
async def create_and_run_mailing(
        schema: MailingCreateSchema,
        service: MailingService = Depends()
):
    return await service.create_and_run(schema)


@router.patch("/{mailing_id}", response_model=MailingSchema)
async def update_mailing(
        mailing_id: int,
        schema: MailingUpdateSchema,
        service: MailingService = Depends()
):
    return await service.update(mailing_id, schema)


@router.delete("/{mailing_id}", status_code=204)
async def delete_mailing(
        mailing_id: int,
        service: MailingService = Depends()
):
    return await service.delete(mailing_id)

