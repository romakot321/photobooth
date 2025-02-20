import datetime as dt

from sqlalchemy.sql.compiler import FK_ON_DELETE

from sqlalchemy_service import Base

from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as column
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import ForeignKey, false
from sqlalchemy import text

sql_utcnow = text('now()')


class BaseMixin:
    @declared_attr.directive
    def __tablename__(cls):
        letters = ['_' + i.lower() if i.isupper() else i for i in cls.__name__]
        return ''.join(letters).lstrip('_') + 's'

    created_at: M[dt.datetime] = column(server_default=sql_utcnow)
    updated_at: M[dt.datetime | None] = column(nullable=True, onupdate=sql_utcnow)
    id: M[int] = column(primary_key=True, index=True, autoincrement=True)


class MailingTariff(Base):
    __tablename__ = "mailings_tariffs"

    id: M[int] = column(primary_key=True)
    mailing_id: M[int] = column(ForeignKey("mailings.id", ondelete="CASCADE"))
    tariff_id: M[int] = column(ForeignKey("tariffs.id", ondelete="CASCADE"))


class MailingTemplateTariff(Base):
    __tablename__ = "mailing_templates_tariffs"

    id: M[int] = column(primary_key=True)
    mailing_template_id: M[int] = column(ForeignKey("mailing_templates.id", ondelete="CASCADE"))
    tariff_id: M[int] = column(ForeignKey("tariffs.id", ondelete="CASCADE"))


class Mailing(BaseMixin, Base):
    text: M[str | None] = column(nullable=True)
    gender: M[str | None] = column(nullable=True)
    template_id: M[int] = column(ForeignKey("mailing_templates.id", ondelete="CASCADE"))
    god_mode: M[bool | None] = column(nullable=True)
    without_tariff: M[bool | None] = column(nullable=True)
    created_from: M[dt.datetime | None] = column(nullable=True)
    created_to: M[dt.datetime | None] = column(nullable=True)
    limit_messages: M[int | None] = column(nullable=True)
    offset_messages: M[int | None] = column(nullable=True)
    next_payment_date: M[dt.date | None] = column(nullable=True)
    messages_count: M[int]

    template: M['MailingTemplate'] = relationship(back_populates='mailings', lazy='selectin')
    tariffs: M[list['Tariff']] = relationship(secondary="mailings_tariffs", back_populates="mailings", lazy="selectin")
    buttons: M[list['MailingButton']] = relationship(back_populates="mailing", lazy="selectin")
    images: M[list['MailingImage']] = relationship(back_populates="mailing", lazy="selectin")


class MailingButton(Base):
    __tablename__ = "mailing_buttons"

    id: M[int] = column(primary_key=True)
    text: M[str]
    callback_data: M[str | None] = column(nullable=True)
    url: M[str | None] = column(nullable=True)
    mailing_id: M[int] = column(ForeignKey('mailings.id', ondelete="CASCADE"))

    mailing: M['Mailing'] = relationship(back_populates="buttons", lazy="noload")


class MailingTemplate(BaseMixin, Base):
    title: M[str]
    text: M[str]
    gender: M[str | None] = column(nullable=True)
    god_mode: M[bool | None] = column(nullable=True)

    mailings: M[list['Mailing']] = relationship(back_populates='template', lazy='noload')
    tariffs: M[list['Tariff']] = relationship(secondary="mailing_templates_tariffs", back_populates="mailing_templates", lazy="selectin")


class MailingImage(BaseMixin, Base):
    filename: M[str]
    is_video: M[bool] = column(server_default=false())
    mailing_id: M[int | None] = column(ForeignKey('mailings.id', ondelete="CASCADE"), nullable=True)

    mailing: M['Mailing'] = relationship(back_populates="images", lazy="noload")


class Tariff(Base):
    __tablename__ = "tariffs"

    id: M[int] = column(primary_key=True)
    title: M[str]

    mailings: M[list['Mailing']] = relationship(secondary="mailings_tariffs", back_populates="tariffs")
    mailing_templates: M[list['MailingTemplate']] = relationship(secondary="mailing_templates_tariffs", back_populates="tariffs")


class Order(Base):
    __tablename__ = "orders"

    id: M[int] = column(primary_key=True)
    user_id: M[int] = column(ForeignKey("bot_users.id"))
    system_id: M[bool]
    paid_at: M[dt.datetime | None]
    is_paid: M[bool | None]

    user: M['User'] = relationship(back_populates="orders", lazy="selectin")


class User(Base):
    __tablename__ = "bot_users"

    id: M[int] = column(primary_key=True, index=True)
    chat_id: M[str | None] = column(nullable=True)
    name: M[str | None] = column(nullable=True)
    gender: M[str | None] = column(nullable=True)
    tariff_id: M[int | None] = column(nullable=True)
    created_at: M[dt.datetime]

    generations: M[list['Generation']] = relationship(back_populates='user', lazy='noload')
    orders: M[list['Order']] = relationship(back_populates='user', lazy='noload')


class Generation(Base):
    __tablename__ = "generations"

    id: M[int] = column(primary_key=True)
    user_id: M[int] = column(ForeignKey("bot_users.id", ondelete="CASCADE"))
    is_god_mode: M[bool]

    user: M['User'] = relationship(back_populates="generations", lazy="noload")

