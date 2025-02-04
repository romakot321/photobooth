from fastapi import Depends
from aiogram.filters.callback_data import CallbackData
import app
import copy
import json

from app.schemas.action import MailingData


class BotController:
    __webhook_data = {
        'update_id': 0,
        'callback_query': {
            'id': '1',
            'from': {
                'id': None,
                'is_bot': False,
                'first_name': '.'
            },
            'message': {
                'message_id': 1,
                'from': {
                    'id': 1,
                    'is_bot': True,
                    'first_name': "bot"
                },
                'chat': {
                    'id': None,
                    'first_name': '.',
                    'type': 'private'
                },
                'date': 1,
                'text': '.'
            },
            'data': 'action:history',
            'chat_instance': '1'
        }
    }

    @staticmethod
    def _parse_mailing(mailing_id: int) -> str:
        return MailingData(mailing_id=mailing_id).pack()

    @classmethod
    def _pack_webhook_data(cls, chat_id: int, data: str) -> str:
        webhookdata = copy.deepcopy(cls.__webhook_data)
        webhookdata['callback_query']['from']['id'] = chat_id
        webhookdata['callback_query']['message']['chat']['id'] = chat_id
        webhookdata['callback_query']['data'] = data
        return json.dumps(webhookdata)

    @classmethod
    async def start_mailing(cls, mailing_id: int):
        mailing_data = cls._parse_mailing(mailing_id)
        webhook_data = cls._pack_webhook_data(0, mailing_data)

        await app.dispatcher_instance.feed_webhook_update(
            app.bot_instance, app.bot_instance.session.json_loads(webhook_data)
        )

