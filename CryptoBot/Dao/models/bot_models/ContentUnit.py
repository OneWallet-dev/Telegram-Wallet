from sqlalchemy import String, Column

from Dao.models.bot_models.bot_base import BotBase


class ContentUnit(BotBase):
    __tablename__ = "content"

    tag = Column(String, primary_key=True)
    text = Column(String)
    media_id = Column(String)
    media_type = Column(String)

