from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from api.database.postgres import Base


class Algorithm(Base):
    __tablename__ = "algorithms"

    name = Column(String, primary_key=True)
    tokens = relationship('Token', lazy="joined", back_populates="algorithm")
