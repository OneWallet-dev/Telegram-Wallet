from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from api.database.models.associations_tables import address_tokens
from api.database.postgres import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_Id = Column(String, nullable=True)
    token_name = Column(String)

    algorithm_name = Column(String, ForeignKey('algorithms.name', onupdate="CASCADE", ondelete="CASCADE"))
    network_id = Column(Integer, ForeignKey('networks.id', onupdate="CASCADE", ondelete="CASCADE"))

    addresses = relationship(
        "Address", secondary=address_tokens, back_populates="tokens", lazy="joined"
    )
    algorithm = relationship('Algorithm', lazy="joined", back_populates="tokens")
    network = relationship('Network', lazy="joined", back_populates="tokens")
