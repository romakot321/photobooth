import datetime as dt

from sqlalchemy_service import Base

from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as column
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import ForeignKey
from sqlalchemy import text
from sqlalchemy import VARCHAR

sql_utcnow = text('(now() at time zone \'utc\')')


class BaseMixin:
    @declared_attr.directive
    def __tablename__(cls):
        letters = ['_' + i.lower() if i.isupper() else i for i in cls.__name__]
        return ''.join(letters).lstrip('_') + 's'

    created_at: M[dt.datetime] = column(server_default=sql_utcnow)
    updated_at: M[dt.datetime | None] = column(nullable=True, onupdate=sql_utcnow)
    id: M[int] = column(primary_key=True, index=True)


class Mailing(BaseMixin, Base):
    text: M[str | None] = column(VARCHAR(4096), nullable=True)
    gender: M[str | None] = column(VARCHAR(10), nullable=True)
    tariff_id: M[int | None] = column(nullable=True)
    template_id: M[int] = column(ForeignKey("mailing_templates.id", ondelete="CASCADE"))

    template: M['MailingTemplate'] = relationship(back_populates='mailings', lazy='selectin')



class MailingTemplate(BaseMixin, Base):
    title: M[str] = column(VARCHAR(256))
    text: M[str] = column(VARCHAR(4096))
    gender: M[str | None] = column(VARCHAR(10), nullable=True)
    tariff_id: M[int | None] = column(nullable=True)

    mailings: M[list['Mailing']] = relationship(back_populates='template', lazy='noload')


class User(Base):
    __tablename__ = "bot_users"

    id: M[int] = column(primary_key=True, index=True)
    chat_id: M[str | None] = column(VARCHAR(40), nullable=True)
    name: M[str | None] = column(VARCHAR(150), nullable=True)
    gender: M[str | None] = column(VARCHAR(10), nullable=True)
    tariff_id: M[int | None] = column(nullable=True)

