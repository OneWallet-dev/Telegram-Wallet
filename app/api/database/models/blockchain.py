from sqlalchemy import Column, String

from api.database.postgres import Base


class Blockchain(Base):
    __tablename__ = "blockchains"

    name = Column(String, primary_key=True)
