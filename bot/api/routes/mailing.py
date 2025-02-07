from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.services.mailing import MailingService


router = APIRouter(prefix="/api/mailing", tags=["Mailing"])


class MailingTestSchema(BaseModel):
    class Button(BaseModel):
        text: str
        callback_data: str | None = None
        url: str | None = None

    chat_id: int
    text: str
    buttons: list[Button] | None = None
    image_filename: str | None = None


@router.post("/test")
async def test_mailing(
        schema: MailingTestSchema,
        service: MailingService = Depends()
):
    return await service.test(schema)


@router.post("/{mailing_id}")
async def start_mailing(
        mailing_id: int,
        service: MailingService = Depends()
):
    return await service.start(mailing_id)


@router.get("/{mailing_id}/progress")
async def get_mailing_messages_count(
        mailing_id: int,
        service: MailingService = Depends()
) -> int:
    return await service.get_mailing_messages_count(mailing_id)
