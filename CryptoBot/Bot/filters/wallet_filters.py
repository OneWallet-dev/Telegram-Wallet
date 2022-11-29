from typing import Dict, Any

from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from Databases.DB_Postgres.models import Owner
from Databases.DB_Postgres.session import create_session
from Databases.DB_Redis import RedRedis


