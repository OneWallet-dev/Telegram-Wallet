from pydantic import BaseModel
from datetime import datetime


class CreateWallet(BaseModel):
    owner_id: str
    blockchain: str


class WalletOut(BaseModel):
    id: str
    blockchain: str
    owner_id: str
    mnemonic: str


class CurrentWallet(BaseModel):
    wallet: WalletOut

