from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from app.services.mailing import MailingService
from app.schemas.mailing import MailingImageSchema, MailingMessagesCountSchema, MailingProgressSchema, MailingSearchSchema, MailingSendedUserIds, MailingUpdateSchema
from app.schemas.mailing import MailingSchema, MailingCreateSchema
from app.schemas.mailing import MailingTestSchema

router = APIRouter(prefix="/api/mailing", tags=["Mailing"])


@router.get("", response_model=list[MailingSchema])
async def list_mailings(
        schema: MailingSearchSchema = Depends(),
        service: MailingService = Depends()
):
    return await service.list(schema)


@router.get("/messages", response_model=int)
async def calculate_messages_to_send_count(
        tariff_ids: list[int] | None = Query(None),
        schema: MailingMessagesCountSchema = Depends(),
        service: MailingService = Depends()
):
    print(tariff_ids)
    schema.tariff_ids = tariff_ids
    return await service.count_messages_to_send(schema)


@router.get("/{mailing_id}", response_model=MailingSchema)
async def get_mailing(
        mailing_id: int,
        service: MailingService = Depends()
):
    return await service.get(mailing_id)


@router.post("/image", response_model=MailingImageSchema)
async def store_mailing_file(
        file: UploadFile = File(...),
        service: MailingService = Depends()
):
    if not file.content_type.startswith("video/") and not file.content_type.startswith("image/"):
        raise HTTPException(400, detail="Invalid file type")
    return await service.store_image(file)


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


@router.get("/{mailing_id}/progress", response_model=MailingProgressSchema)
async def get_mailing_progress(
        mailing_id: int,
        service: MailingService = Depends()
):
    return await service.get_mailing_progress(mailing_id)


@router.get("/{mailing_id}/chats", response_model=MailingSendedUserIds)
async def get_mailing_sended_user_ids(
        mailing_id: int,
        service: MailingService = Depends()
):
    return await service.get_mailing_sended_user_ids(mailing_id)


@router.post("/{mailing_id}/pause", status_code=200)
async def set_mailing_pause(
        mailing_id: int,
        value: bool = Query(),
        service: MailingService = Depends()
):
    return await service.pause_sending(mailing_id, value)

