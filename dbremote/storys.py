import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Story(SqlAlchemyBase):
    __tablename__ = 'stories'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    channel_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("authorchannels.id"))
    channel = orm.relationship("Authorchannel", back_populates="stories")
    template_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)