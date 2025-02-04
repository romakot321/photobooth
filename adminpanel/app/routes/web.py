from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.mailing import MailingService
from app.services.mailing_template import MailingTemplateService
from app.services.user import UserService

from app.schemas.mailing_template import MailingTemplateSchema, MailingTemplateSearchSchema
from app.schemas.mailing import MailingSchema, MailingSearchSchema

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
async def index_page(
        request: Request,
        text: str | None = Query(None),
        template_service: MailingTemplateService = Depends()
):
    """Mailing templates page"""
    models: list[MailingTemplateSchema] = await template_service.list(MailingTemplateSearchSchema(text=text))
    return templates.TemplateResponse("index.html", {"request": request, "templates": models})


@router.get("/mailing", response_class=HTMLResponse)
async def mailings_page(
        request: Request,
        text: str | None = Query(None),
        mailing_service: MailingService = Depends()
):
    mailings: list[MailingSchema] = await mailing_service.list(MailingSearchSchema(text=text))
    return templates.TemplateResponse(
        "mailings.html",
        {"request": request, "mailings": mailings}
    )


@router.get("/mailing/create", response_class=HTMLResponse)
async def create_mailing_page(
        request: Request,
        template_id: int | None = Query(None),
        template_service: MailingTemplateService = Depends(),
        user_service: UserService = Depends()
):
    if template_id is not None:
        template = await template_service.get(template_id)
        messages_count = await user_service.count_messages_to_send(gender=template.gender, tariff_id=template.tariff_id)
    else:
        template = MailingTemplateSchema()
        messages_count = 0
    return templates.TemplateResponse(
        "mailing-create.html",
        {"request": request, "template": template, "messages_count": messages_count}
    )


@router.get("/mailing/{mailing_id}", response_class=HTMLResponse)
async def mailing_details_page(
        request: Request,
        mailing_id: int,
        mailing_service: MailingService = Depends()
):
    mailing: MailingSchema = await mailing_service.get(mailing_id)
    return templates.TemplateResponse("mailing.html", {"request": request, "mailing": mailing})

