from pydantic import BaseModel, computed_field, ConfigDict
from loguru import logger
import datetime as dt
import locale

from app.schemas.mailing_template import MailingTemplateSchema
from app.schemas.tariff import TariffSchema

#locale.setlocale(
#    category=locale.LC_ALL,
#    locale="rus"
#)


class MailingButtonSchema(BaseModel):
    text: str
    callback_data: str | None = None
    url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MailingImageSchema(BaseModel):
    id: int
    filename: str
    is_video: bool

    model_config = ConfigDict(from_attributes=True)


class MailingSchema(BaseModel):
    id: int
    text: str | None = None
    gender: str | None = None
    tariffs: list[TariffSchema] | None = None
    buttons: list[MailingButtonSchema] | None = None
    messages_count: int | None = None
    messages_sent: int | None = None
    template: MailingTemplateSchema | None = None
    god_mode: bool | None = None
    without_tariff: bool | None = None
    created_at: dt.datetime
    images: list[MailingImageSchema] | None = None
    created_from: dt.datetime | None = None
    created_to: dt.datetime | None = None
    limit_messages: int | None = None
    offset_messages: int | None = None
    next_payment_date: dt.date | None = None

    @computed_field
    @property
    def text_display(self) -> str | None:
        return self.text or ('' if self.template is None else self.template.text)

    @computed_field
    @property
    def gender_display(self) -> str:
        gender = self.gender or (None if self.template is None else self.template.gender)
        return {'f': "Женский", 'm': "Мужской"}.get(gender, "-")

    @computed_field
    @property
    def god_mode_display(self) -> str:
        god_mode = self.god_mode or (self.god_mode if self.template is None else self.template.god_mode)
        return {True: "Да", False: "Нет", None: "-"}.get(god_mode)

    @computed_field
    @property
    def created_at_display(self) -> str:
        return self.created_at.strftime("%d %B %Y года в %H:%M")

    @computed_field
    @property
    def next_payment_display(self) -> str:
        if self.next_payment_date is None:
            return ''
        return self.next_payment_date.strftime("%d %M %Y")

    @computed_field
    @property
    def created_from_display(self) -> str:
        if self.created_from is None:
            return ''
        return self.created_from.strftime("%d %M %Y")

    @computed_field
    @property
    def created_to_display(self) -> str:
        if self.created_to is None:
            return ''
        return self.created_to.strftime("%d %M %Y")

    model_config = ConfigDict(from_attributes=True)


class MailingCreateSchema(BaseModel):
    text: str | None = None
    gender: str | None = None
    tariff_ids: list[int] | None = None
    template_id: int | None = None
    god_mode: bool | None = None
    without_tariff: bool | None = None
    buttons: list[MailingButtonSchema] | None = None
    images: list[str] | None = None
    created_from: dt.datetime | None = None
    created_to: dt.datetime | None = None
    limit_messages: int | None = None
    offset_messages: int | None = None
    next_payment_date: dt.date | None = None


class MailingUpdateSchema(BaseModel):
    text: str | None = None
    gender: str | None = None
    tariff_ids: list[int] | None = None
    template_id: int | None = None
    god_mode: bool | None = None
    without_tariff: bool | None = None
    buttons: list[MailingButtonSchema] | None = None
    images: list[str] | None = None


class MailingSearchSchema(BaseModel):
    text: str | None = None
    page: int = 0
    count: int = 50


class MailingTestSchema(BaseModel):
    chat_id: int
    text: str
    buttons: list[MailingButtonSchema] | None = None
    image_filename: str | None = None
    video_filename: str | None = None


class MailingProgressSchema(BaseModel):
    id: int
    messages_sent: int | None = None
    messages_count: int
    status: str | None = None


class MailingMessagesCountSchema(BaseModel):
    gender: str | None = None
    tariff_ids: list[int] | None = None
    god_mode: bool | None = None
    without_tariff: bool | None = None
    created_from: dt.datetime | None = None
    created_to: dt.datetime | None = None
    limit_messages: int | None = None
    offset_messages: int | None = None
    next_payment_date: dt.date | None = None


class MailingSendedUserIds(BaseModel):
    user_ids: list[int]

