from fastapi import Depends, File, UploadFile
from loguru import logger
from starlette import middleware

from app.repositories.user import UserRepository
from app.schemas.mailing import MailingImageSchema, MailingMessagesCountSchema, MailingProgressSchema, MailingSchema
from app.schemas.mailing import MailingSearchSchema
from app.schemas.mailing import MailingCreateSchema
from app.schemas.mailing import MailingUpdateSchema
from app.schemas.mailing import MailingTestSchema
from app.db.tables import Mailing, MailingButton, MailingImage
from app.repositories.mailing import MailingRepository
from app.repositories.mailing_button import MailingButtonRepository
from app.repositories.bot import BotRepository
from app.repositories.tariff import TariffRepository
from app.repositories.image import ImageRepository
from app.repositories.storage import StorageRepository


class MailingService:
    def __init__(
            self,
            mailing_repository: MailingRepository = Depends(),
            bot_repository: BotRepository = Depends(),
            tariff_repository: TariffRepository = Depends(),
            button_repository: MailingButtonRepository = Depends(),
            image_repository: ImageRepository = Depends(),
            storage_repository: StorageRepository = Depends(),
            user_repository: UserRepository = Depends()
    ):
        self.mailing_repository = mailing_repository
        self.bot_repository = bot_repository
        self.tariff_repository = tariff_repository
        self.button_repository = button_repository
        self.image_repository = image_repository
        self.storage_repository = storage_repository
        self.user_repository = user_repository

    async def list(self, schema: MailingSearchSchema = None) -> list[MailingSchema]:
        models = await self.mailing_repository.list(**schema.model_dump(exclude_none=True))
        return [MailingSchema.model_validate(model) for model in models]

    async def get(self, mailing_id: int) -> MailingSchema:
        model = await self.mailing_repository.get(mailing_id)
        return MailingSchema.model_validate(model)

    async def count_messages_to_send(self, schema: MailingMessagesCountSchema) -> int:
        return await self.user_repository.count(
            tariff_ids=schema.tariff_ids,
            god_mode=schema.god_mode,
            without_tariff=schema.without_tariff,
            gender=schema.gender
        )

    async def create_and_run(self, schema: MailingCreateSchema) -> MailingSchema:
        state = schema.model_dump(exclude_none=True)
        tariffs = []
        buttons_states = state.pop("buttons") if "buttons" in state else None
        images_filenames = state.pop("images") if "images" in state else None
        buttons_models = []
        messages_count = await self.count_messages_to_send(schema)

        if schema.tariff_ids is not None:
            for tariff_id in state.pop("tariff_ids"):
                tariffs.append(await self.tariff_repository.get(tariff_id))

        model = Mailing(messages_count=messages_count, **state)
        model.tariffs = tariffs
        model = await self.mailing_repository.create(model)

        if buttons_states:
            for button_state in buttons_states:
                button = await self.button_repository.create(MailingButton(**button_state, mailing_id=model.id))
                buttons_models.append(button)
            model.buttons = buttons_models
        if images_filenames:
            for image_filename in images_filenames:
                image = await self.image_repository.update(image_filename, mailing_id=model.id)
                model.images.append(image)

        logger.debug(f"Running mailing {model.id=}")
        await self.bot_repository.trigger_mailing_run(model.id)

        return MailingSchema.model_validate(model)

    async def update(self, model_id: int, schema: MailingUpdateSchema) -> MailingSchema:
        model = await self.mailing_repository.update(model_id, **schema.model_dump())
        return MailingSchema.model_validate(model)

    async def delete(self, model_id: int):
        await self.mailing_repository.delete(model_id)

    async def test(self, schema: MailingTestSchema):
        buttons = [i.model_dump() for i in schema.buttons] if schema.buttons else None
        await self.bot_repository.trigger_mailing_test(schema.chat_id, schema.text, buttons, schema.image_filename)

    async def store_image(self, file: UploadFile) -> MailingImageSchema:
        filename = self.storage_repository.generate_image_filename()
        model = MailingImage(filename=filename)
        self.storage_repository.store_image(filename, file.file.read())
        model = await self.image_repository.create(model)
        return MailingImageSchema.model_validate(model)

    async def get_mailing_progress(self, mailing_id: int) -> MailingProgressSchema:
        mailing = await self.mailing_repository.get(mailing_id)
        return MailingProgressSchema(
            id=mailing_id,
            messages_sent=await self.bot_repository.get_mailing_messages_count(mailing_id),
            messages_count=mailing.messages_count
        )

