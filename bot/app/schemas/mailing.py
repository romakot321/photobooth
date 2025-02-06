from pydantic import BaseModel


class MailingButtonData(BaseModel):
    text: str
    callback_data: str | None = None
    url: str | None = None


class MailingTestData(BaseModel):
    chat_id: int
    text: str
    buttons: list[MailingButtonData] | None = None

