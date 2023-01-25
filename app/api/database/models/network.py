from sqlalchemy import Column, String, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship

from api.database.postgres import Base


class Network(Base):  # Arbitrum/Polygon
    __tablename__ = "networks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    base_token = Column(String)
    mainnet = Column(Boolean)
