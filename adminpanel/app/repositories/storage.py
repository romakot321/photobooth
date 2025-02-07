import pathlib
import os
import uuid


class StorageRepository:
    storage_path = pathlib.Path(os.getenv("IMAGE_STORAGE_PATH", "images"))

    @classmethod
    def generate_image_filename(cls) -> str:
        return str(uuid.uuid4())

    @classmethod
    def store_image(cls, filename: str, body: bytes):
        with open(cls.storage_path / filename, 'wb') as f:
            f.write(body)

    @classmethod
    def read_image(cls, filename: str) -> bytes:
        with open(cls.storage_path / filename, 'rb') as f:
            return f.read()

