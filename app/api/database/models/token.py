from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from api.database.postgres import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_Id = Column(String, nullable=True)
    token_name = Column(String)
