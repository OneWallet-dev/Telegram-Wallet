from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

BotBase = declarative_base(metadata=MetaData(schema="bot"))
