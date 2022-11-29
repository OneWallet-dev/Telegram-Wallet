from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Base_api = 'https://rest.cryptoapis.io'
# API_version = "/v2"
# Base_api = Base_api + API_version

association_table = Table(
    "address_tokens",
    Base.metadata,
    Column("address_id", ForeignKey("addresses.address"), primary_key=True),
    Column("contract_Id", ForeignKey("tokens.contract_Id"), primary_key=True),
)


