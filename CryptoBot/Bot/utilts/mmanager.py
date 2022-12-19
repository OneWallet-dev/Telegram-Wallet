import asyncio
import inspect
from contextlib import suppress

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message, \
    Update, CallbackQuery, InputMedia

from AllLogs.bot_logger import main_logger
from Bot.utilts.ContentService import ContentService
from Dao.models.bot_models import ContentUnit


# TODO: Все же раскидать на два разных класса
class MManager:
    _garbagekey = 'garbage'
    _stickerkey = 'sticker'

    @classmethod
    async def sticker_surf(cls, state: FSMContext, bot: Bot, chat_id: str | int, new_text: str | None = None,
                           keyboard: InlineKeyboardMarkup | None = None,
                           store_sticker: bool = True, keep_old: bool = False):
        sticker_data: dict = (await state.get_data()).get(cls._stickerkey)
        msg_id = sticker_data.get("id")
        text = new_text if new_text else sticker_data.get("text")
        n_msg = await bot.send_message(chat_id, text, reply_markup=keyboard)
        if not keep_old:
            with suppress(TelegramBadRequest):
                await bot.delete_message(chat_id, msg_id)
        else:
            await bot.edit_message_reply_markup(chat_id, msg_id)
        if store_sticker:
            await MManager.sticker_store(state, n_msg)

    @classmethod
    async def content_surf(cls,
                           event: Message | CallbackQuery,
                           state: FSMContext,
                           bot: Bot,
                           content_unit: ContentUnit,
                           keyboard: InlineKeyboardMarkup | None = None,
                           placeholder_text: str | None = None):
        sticker_data: dict = (await state.get_data()).get(cls._stickerkey, dict())
        chat_id = event.chat.id if isinstance(event, Message) else event.message.chat.id
        msg_id = sticker_data.get("id")

        if isinstance(event, CallbackQuery) and msg_id:
            n_msg = await ContentService.edit(content=content_unit, bot=bot, chat_id=chat_id,
                                              keyboard=keyboard, target_msg_id=msg_id,
                                              placeholder_text=placeholder_text)
        else:
            n_msg = await ContentService.send(content=content_unit, bot=bot, chat_id=chat_id, keyboard=keyboard,
                                              placeholder_text=placeholder_text)
            if msg_id:
                with suppress(TelegramBadRequest):
                    await bot.delete_message(chat_id, msg_id)
                    await bot.delete_message(chat_id, event.message_id)
        await MManager.sticker_store(state, n_msg)

    @classmethod
    async def sticker_store(cls, state: FSMContext, sticker_message: Message):
        await state.update_data({cls._stickerkey: {"id": sticker_message.message_id,
                                                   "text": sticker_message.html_text}})

    @classmethod
    async def sticker_text(cls, state: FSMContext) -> str:
        data = await state.get_data()
        sticky_dict = data.get(cls._stickerkey)
        return sticky_dict.get('text')

    @classmethod
    async def sticker_free(cls, state: FSMContext):
        await state.update_data({cls._stickerkey: None})

    @classmethod
    async def sticker_delete(cls, state: FSMContext, bot: Bot, chat_id: int):
        mid = (await state.get_data()).get(cls._stickerkey).get("id")
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id, mid)

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
        corutines = [bot.delete_message(chat_id, message_id) for message_id in msg_list[::-1]]
        try:
            await asyncio.gather(*corutines, return_exceptions=True)
        except TelegramBadRequest:
            pass
        await state.update_data({cls._garbagekey: []})

    @classmethod
    async def purge_chat(cls, bot: Bot, message_id: int, chat_id: int):
        corutines = [bot.delete_message(chat_id, msg_id) for msg_id in range(message_id, message_id - 50, -1)]
        try:
            await asyncio.gather(*corutines, return_exceptions=True)
        except TelegramBadRequest:
            pass
