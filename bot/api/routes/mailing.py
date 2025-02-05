from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.services.mailing import MailingService


router = APIRouter(prefix="/api/mailing", tags=["Mailing"])


class MailingTestSchema(BaseModel):
    chat_id: int
    text: str


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

