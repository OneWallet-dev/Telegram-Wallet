import asyncio

from bata import Data

bot = Data.main_bot


async def loader(chat_id, text: str = '', time: int = 5, reply_markup: bool = None):
    loader_bar = ['🟩', '⬜', '⬜', '⬜', '⬜', '⬜️']
    new_text = text + '\n\n' + ''.join(loader_bar)
    if time > 2:
        count = 0
        message = await bot.send_message(chat_id=chat_id, text=new_text, reply_markup=reply_markup)
        message_id = message.message_id
        for load in loader_bar:
            count += 1
            loader_bar[count] = "🟩"
            edit_text = text + '\n\n' + ''.join(loader_bar)
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=edit_text)
            await asyncio.sleep(len(loader_bar)/time)
            if count == len(loader_bar) - 1:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
                return True
    else:
        raise ValueError("Loading cannot be faster than 2 seconds")



