from pydantic import BaseModel, computed_field, ConfigDict

from app.schemas.tariff import TariffSchema

_operation_comments = {
    "newmodel": "Покупка новой модели",
    "tariff_1390_50": "Основной тариф 1390 руб / 50 фото",
    "tariff_1390_100": "Основной тариф 1390 руб / 100 фото",
    "tariff_990_50": "Основной тариф 990 руб / 50 фото",
    "gens_10": "Покупка новых генераций: +10",
    "gens_50": "Покупка новых генераций: +50",
    "gens_100": "Покупка новых генераций: +100",
    "partner": "Начисление партнеру доп. генераций",
    "spec_390_10": "Спец предложение 390 руб за 10 фото",
    "spec_490_10": "Спец предложение 490 руб за 10 фото"
}


class MailingTemplateSchema(BaseModel):
    id: int
    title: str
    text: str
    gender: str | None = None
    tariffs: list[TariffSchema] | None = None
    god_mode: bool | None = None

    @computed_field
    @property
    def gender_display(self) -> str:
        return {'f': "Женский", 'm': "Мужской"}.get(self.gender, "-")

    model_config = ConfigDict(from_attributes=True)


class MailingTemplateCreateSchema(BaseModel):
    title: str
    text: str
    gender: str | None = None
    tariff_ids: list[int] | None = None
    god_mode: bool | None = None


class MailingTemplateSearchSchema(BaseModel):
    text: str | None = None
    page: int = 0
    count: int = 50


class MailingTemplateUpdateSchema(BaseModel):
    title: str | None = None
    text: str | None = None
    gender: str | None = None
    tariff_ids: list[int] | None = None
    god_mode: bool | None = None

