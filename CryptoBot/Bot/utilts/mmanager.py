import asyncio
import functools
import inspect
import json

from aiogram import Bot
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, Message, \
    CallbackQuery, Update, Chat
from sqlalchemy.ext.asyncio import AsyncSession


# TODO: Все же раскидать на два разных класса
class MManager:
    _garbagekey = 'garbage'
    _stickerkey = 'sticker'

    @classmethod
    async def sticker_surf(cls,
                           new_text: str,
                           state: FSMContext,
                           bot: Bot,
                           chat_id: str | int,
                           keyboard: InlineKeyboardMarkup):
        msg_id = int(((await state.get_data()).get(cls._stickerkey)).get("id"))
        n_msg = await bot.send_message(chat_id, new_text, reply_markup=keyboard)
        await bot.delete_message(chat_id, msg_id)
        await MManager.sticker_store(state, n_msg)

    @classmethod
    async def sticker_store(cls, state: FSMContext, sticker_message: Message):
        await state.update_data({cls._stickerkey: {"id": sticker_message.message_id,
                                                   "text": sticker_message.text}})

    @classmethod
    async def sticker_text(cls, state: FSMContext):
        data = await state.get_data()
        sticky_dict = data.get(cls._stickerkey)
        return sticky_dict.get('text')

    @classmethod
    def garbage_manage(cls, *, store: bool = True, clean: bool = False):
        def garbage_decor(some_handler):
            """
            Decorator for messages and callbacks.
            At default will store any marked message from user (if used at message handler)
            or message from which callback was sent.

            :param some_handler: function for decoration
            :param store: mark True if you want to store user message in garbage
            :param clean: mark True if you want to delete all garbage messages AFTER handler
            """

            async def wrap(*args, **kwargs):
                update: Update = kwargs.get("event_update")
                state: FSMContext = kwargs.get("state")
                tg_obj = None
                if update:
                    if update.message:
                        tg_obj = update.message
                    elif update.callback_query:
                        tg_obj = update.callback_query
                if tg_obj:
                    message_id = tg_obj.message_id if isinstance(tg_obj, Message) else tg_obj.message.message_id
                    if store:
                        await MManager.garbage_store(state, message_id)
                prepared_kwargs = {k: v for k, v in kwargs.items() if k in inspect.getfullargspec(some_handler).args}
                # print(prepared_kwargs)
                # partal = functools.partial(some_handler, tg_object, **prepared_kwargs)
                await some_handler(*args, **prepared_kwargs)
                if clean and tg_obj:
                    bot: Bot = kwargs.get("bot")
                    chat_id = tg_obj.chat.id if isinstance(tg_obj, Message) else tg_obj.message.chat.id
                    await MManager.clean(state, bot, chat_id)

            return wrap

        return garbage_decor

    @classmethod
    async def garbage_store(cls, state: FSMContext, tech_msg_id: str | int):
        msg_list = list(set((await state.get_data()).get(cls._garbagekey, [])))
        msg_list.append(tech_msg_id)
        await state.update_data({cls._garbagekey: msg_list})

    @classmethod
    async def clean(cls, state: FSMContext, bot: Bot, chat_id: str | int):
        msg_list = (await state.get_data()).get(cls._garbagekey, [])
        for msg_id in msg_list:
            try:
                await asyncio.create_task(bot.delete_message(chat_id, msg_id))
            except TelegramBadRequest:
                pass
        await state.update_data({cls._garbagekey: []})
