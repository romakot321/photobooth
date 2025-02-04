from fastapi import APIRouter, Depends

from api.services.mailing import MailingService


router = APIRouter(prefix="/api/mailing", tags=["Mailing"])


@router.post("/{mailing_id}")
async def start_mailing(
        mailing_id: int,
        service: MailingService = Depends()
):
    return await service.start(mailing_id)

