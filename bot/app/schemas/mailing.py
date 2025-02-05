from pydantic import BaseModel


class MailingTestData(BaseModel):
    chat_id: int
    text: str
