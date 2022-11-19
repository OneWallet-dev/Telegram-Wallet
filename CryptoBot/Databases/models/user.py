import datetime

from sqlalchemy import Column, BigInteger, String, DateTime

from Databases.DB_Postgres import Base


class Users(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    username = Column(String)
    first_name = Column(String)
    datetime_come = Column(DateTime, default=datetime.datetime.now())
    password = Column(String)
