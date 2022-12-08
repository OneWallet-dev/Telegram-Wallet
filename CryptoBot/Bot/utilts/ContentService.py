from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InputMedia

from Dao.models.bot_models import ContentUnit


class ContentService:

    @staticmethod
    async def send(content: ContentUnit,
                   bot: Bot,
                   chat_id: int,
                   keyboard: InlineKeyboardMarkup):
        n_msg = None
        if content.media_id:
            if content.media_type == 'video':
                n_msg = await bot.send_video(chat_id=chat_id,
                                             video=content.media_id,
                                             caption=content.text,
                                             reply_markup=keyboard)
            elif content.media_type == 'photo':
                n_msg = await bot.send_photo(chat_id=chat_id,
                                             photo=content.media_id,
                                             caption=content.text,
                                             reply_markup=keyboard)
        else:
            n_msg = await bot.send_message(text=content.text,
                                           chat_id=chat_id,
                                           reply_markup=keyboard)
        return n_msg

    @staticmethod
    async def edit(content: ContentUnit,
                   bot: Bot,
                   chat_id: int,
                   target_msg_id: int,
                   keyboard: InlineKeyboardMarkup):
        if content.media_id:
            n_msg = await bot.edit_message_media(media=InputMedia(type=content.media_type,
                                                                  media=content.media_id,
                                                                  caption=content.text),
                                                 chat_id=chat_id,
                                                 message_id=target_msg_id,
                                                 reply_markup=keyboard)
        else:
            n_msg = await bot.edit_message_text(text=content.text,
                                                chat_id=chat_id,
                                                message_id=target_msg_id,
                                                reply_markup=keyboard)
        return n_msg
