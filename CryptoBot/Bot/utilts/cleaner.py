from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext


class Cleaner:
    storekey = 'tech_msgs'

    @classmethod
    async def store(cls, state: FSMContext, tech_msg_id: str | int):
        msg_list = (await state.get_data()).get(cls.storekey, [])
        msg_list.append(tech_msg_id)
        await state.update_data({cls.storekey: msg_list})

    @classmethod
    async def clean(cls, state: FSMContext, bot: Bot, chat_id: str | int):
        msg_list = (await state.get_data()).get(cls.storekey, [])
        for msg_id in msg_list:
            try:
                await bot.delete_message(chat_id, msg_id)
            except TelegramBadRequest:
                pass
        await state.update_data({cls.storekey: []})
