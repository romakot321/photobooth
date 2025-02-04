from aiogram.filters.callback_data import CallbackData
from pydantic import Field, AliasChoices


class ActionCallback(CallbackData, prefix='action'):
    """
    :param action: str, action_name from Action enum
    """
    action: str

    @classmethod
    def copy(cls):
        return cls(**cls.__dict__)

    def replace(self, **values):
        """Return new object with replaced values"""
        new_state = self.__dict__ | values
        return self.__class__(**new_state)


class MailingData(CallbackData, prefix='mailing'):
    mailing_id: int
