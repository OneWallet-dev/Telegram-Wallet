from pydantic import BaseModel
from datetime import datetime

class CreateUser(BaseModel):
    password: str


class UserOut(BaseModel):
    id: str
    created_at: datetime


class CurrentUser(BaseModel):
    user: UserOut
