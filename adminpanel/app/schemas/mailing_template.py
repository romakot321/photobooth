from pydantic import BaseModel, computed_field, ConfigDict


class MailingTemplateSchema(BaseModel):
    id: int
    title: str
    text: str
    gender: str | None = None
    tariff_id: int | None = None

    @computed_field
    @property
    def gender_display(self) -> str:
        return {'f': "Женский", 'm': "Мужской"}.get(self.gender, "-")

    @computed_field
    @property
    def tariff_display(self) -> str:
        return "Есть" if self.tariff_id is not None else "-"

    model_config = ConfigDict(from_attributes=True)


class MailingTemplateCreateSchema(BaseModel):
    title: str
    text: str
    gender: str | None = None
    tariff_id: int | None = None


class MailingTemplateSearchSchema(BaseModel):
    text: str | None = None
    page: int = 0
    count: int = 50


class MailingTemplateUpdateSchema(BaseModel):
    title: str | None = None
    text: str | None = None
    gender: str | None = None
    tariff_id: int | None = None

