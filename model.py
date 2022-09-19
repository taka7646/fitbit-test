
from db import Base
import secrets
import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN

SQLITE3_NAME = "./db.sqlite3"

class User(Base):
    __tablename__ = 'user'
    id = Column('id', INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    fitbit_id = Column('fitbit_id', String(64), index=True)
    access_token = Column('access_token', String(256))
    refresh_token = Column('refresh_token', String(256))
    session_id = Column('session_id', String(256), index=True)
    api_key = Column('api_key', String(256), index=True)
    expires_in = Column('expires_in', INTEGER())
    expires_at = Column('expires_at', INTEGER())

    def __init__(self, params: dict) -> None:
        self.fitbit_id = params['user_id']
        self.access_token = params['access_token']
        self.refresh_token = params['refresh_token']
        self.expires_in = params['expires_in']
        if 'expires_at' in params:
            self.expires_at = params['expires_at']
        else:
            self.expires_at = datetime.datetime.now().timestamp() + self.expires_in
        self.api_key = secrets.token_urlsafe(64)
        self.update_session()

    def update(self, params: dict) -> None:
        self.access_token = params['access_token']
        self.refresh_token = params['refresh_token']
        self.expires_in = params['expires_in']
        if 'expires_at' in params:
            self.expires_at = params['expires_at']
        else:
            self.expires_at = datetime.datetime.now().timestamp() + self.expires_in

    def update_session(self):
        self.session_id = secrets.token_urlsafe(16)

    def __str__(self) -> str:
        return "id: {0}, fitbit_id: {1}, api_key:{2}".format(self.id, self.fitbit_id, self.api_key)


