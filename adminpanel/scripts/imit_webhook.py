"""Скрипт для рассылки через основное API бота, используя симуляцию нажатий на inline кнопки.
Для запуска необходимо указать env-ы для подключения к продовой базе данных
"""

import asyncio
import json
import copy
import aiohttp
import os
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_service.base_db.base import async_session, Base
from sqlalchemy import column, select
from loguru import logger


class User(Base):
    __tablename__ = "bot_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int]
    gender: Mapped[str | None]
    name: Mapped[str]
    login: Mapped[str | None]
    tariff_id: Mapped[int | None]


url = os.getenv("BOT_WEBHOOK_URL")
if url is None:
    raise EnvironmentError("Invalid BOT_WEBHOOK_URL environment")

webhook_data = {
    "chatId": '',
    "firstName": None,
    "lastName": None,
    "username": "",
    "name": "",
    "message": None,
    "isDocument": False,
    "documentId": None,
    "documentName": None,
    "command": "",
    "photo": False,
    "mediaGroupId": False,
    "referralCode": None,
    "partnerCode": None,
    "appHudUserId": None,
    "gender": "",
    "source": "bot"
}


def pack_webhook_data(chat_id: int, username: str | None, name: str, gender: str | None, callback_query_data: str) -> dict:
    data = copy.deepcopy(webhook_data)
    data["chatId"] = str(chat_id)
    data['username'] = username
    data['name'] = name
    data['gender'] = gender
    data['command'] = callback_query_data
    return data


async def send(webhook_data: dict):
    async with aiohttp.ClientSession() as session:
        resp = await session.post(url + json.dumps(webhook_data), headers={"Content-Type": "application/json"})
        assert resp.status == 200, resp.text


async def list_users(tariff_ids: list[int] = None, with_tariff: bool | None = None, offset: int = 0, count: int = 100000, from_user_id: int | None = None) -> list[User]:
    """
    :param count: For all specify 18446744073709551615
    """
    query = select(User)
    if tariff_ids:
        query = query.filter(User.tariff_id.in_(tariff_ids))
    if with_tariff is True:
        query = query.filter_by(tariff_id=None)
    if with_tariff is False:
        query = query.filter(User.tariff_id != None)
    if from_user_id is not None:
        query = query.filter(User.id > from_user_id)
    query = query.limit(count).offset(offset)
    async with async_session() as session:
        return list(await session.scalars(query))


async def send_for_users(command: str, from_user_id: int | None = None, tariff_ids: list[int] | None = None, with_tariff: bool | None = None):
    offset = 0
    while True:
        users = await list_users(from_user_id=from_user_id, tariff_ids=tariff_ids, with_tariff=with_tariff, offset=offset)
        if len(users) == 0:
            break
        offset += len(users)

        for user in users:
            if user.chat_id is None:
                continue
            data = pack_webhook_data(user.chat_id, user.login, user.name, user.gender, command)
            try:
                await send(data)
            except Exception as e:
                logger.info(e)
            logger.debug(f"Sended for {user.id=} {user.chat_id=} {command=}")
            await asyncio.sleep(0.1)


async def main():
    await send_for_users("/services23", with_tariff=True)
    await send_for_users("/subscription23", with_tariff=False)


asyncio.run(main())
