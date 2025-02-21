from pydantic import BaseModel, ConfigDict


class TariffSchema(BaseModel):
    id: int
    title: str
    is_start: bool

    model_config = ConfigDict(from_attributes=True)

