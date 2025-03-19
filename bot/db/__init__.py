from sqlalchemy_service.base_db.db_configure import MySQLDBConfiguration
from sqlalchemy_service.base_db.base import ServiceEngine

engine = ServiceEngine(MySQLDBConfiguration().get_url())
