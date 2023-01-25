from pydantic import BaseModel
from datetime import datetime


class CreateAddress(BaseModel):
    address: str
    wallet_id: str

    custom_name: str
    private_key: str


class AddressOut(BaseModel):
    address: str
    wallet_id: str

    custom_name: str
    private_key: str


class CurrentAddress(BaseModel):
    address: AddressOut
