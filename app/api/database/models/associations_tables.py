from sqlalchemy import Column, ForeignKey, Table

from api.database.postgres import Base

address_tokens = Table(
    "address_tokens",
    Base.metadata,
    Column("address_id", ForeignKey("addresses.address", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column("token_id", ForeignKey("tokens.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
)


