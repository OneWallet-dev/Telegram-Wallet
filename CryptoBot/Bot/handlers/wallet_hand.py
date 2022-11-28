from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.filters.wallet_filters import ChainOwned
from Bot.handlers.loading_handler import loader
from Bot.handlers.m_menu_hand import my_wallet_start
from Bot.keyboards.wallet_keys import create_wallet_kb, use_wallet_kb, send_money_kb, \
    send_money_confirm_kb, token_kb, network_kb
from Bot.states.main_states import MainState
from Bot.states.wallet_states import WalletStates, WalletSendMoney
from Bot.utilts.mmanager import MManager
from Bot.utilts.currency_helper import base_tokens
from Bot.utilts.pretty_texts import pretty_balance
from Bot.utilts.qr_code_generator import qr_code
from Dao.models.Owner import Owner
from Dao.models.Wallet import Wallet

router = Router()
router.message.filter(StateFilter(MainState.welcome_state, WalletStates, WalletSendMoney))


@router.callback_query(F.data == "add_token", StateFilter(WalletStates.create_token))
async def add_token(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await bot.edit_message_text('Выберите токен, который вы хотите добавить:',
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=token_kb())


@router.callback_query(F.data.startswith("new_t"), StateFilter(WalletStates.create_token))
async def add_network(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    token = callback.data.replace('new_t_', "")
    text = f"Токен: <code>{token}</code>\n\n"
    text += 'Выберите сеть из доступных для выбранного вами токена:'
    await state.update_data(token=token)
    await bot.edit_message_text(text=text,
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=network_kb(token=token))


@router.callback_query(F.data.startswith("new_n"), StateFilter(WalletStates.create_token))
async def complete_token(callback: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
    data = await state.get_data()
    token = data.get('token')
    network = callback.data.replace("new_n_", "")
    if network in base_tokens.get(token).get("network"):
        # Здесь установить соответствие сети и сохранить связь токен-сеть в нужный кошелек.
        await callback.answer('✅')
        text = f"Добавлен:\n\n" \
               f"Токен: <code>{token}</code>\n" \
               f"В сети:  <code>{network}</code>\n" \
               f"Баланс: <code>ВЫДАТЬ БАЛАНС</code>"
    else:
        await callback.answer('❌')
        text = "К сожалению, добавить токен в этой сети не удалось. Попробуйте позже."
    await bot.edit_message_text(text=text,
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id)
    await my_wallet_start(callback.message, state, session)


async def use_wallet(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    await state.set_state(WalletStates.use_wallet)
    owner: Owner = await Owner.get(session, callback.from_user)

    wallet: Wallet = owner.wallets.get(callback.data)
    if wallet:
        qr = await qr_code(wallet.wallet_address)
        img = BufferedInputFile(file=qr, filename=str(wallet.wallet_address) + ".PNG")

        await callback.message.answer_photo(
            photo=img, caption=f'Вы владеете кошельком в сети <b>{callback.data}</b>.\n\n'
                               f'Публичный адрес:\n <code>{wallet.wallet_address}</code>',
            reply_markup=use_wallet_kb()
        )
        await state.update_data(wallet_chain=wallet.blockchain)
    else:
        await do_you_want_it(callback, state)


@router.callback_query(~ChainOwned(), (F.data.in_(set(base_tokens.keys()))))
async def do_you_want_it(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(WalletStates.create_wallet)
    msg = await callback.message.answer(f'У вас нет кошелька в сети <b>{callback.data}</b>. Хотите завести?\n\n',
                                        reply_markup=create_wallet_kb(callback.data))
    await MManager.garbage_store(state, msg.message_id)


@router.message(F.text.startswith("🪙 Открыть кошелек в сети"), StateFilter(WalletStates.create_wallet))
async def choose_currency(message: Message, state: FSMContext, session: AsyncSession):
    try:
        owner: Owner = await session.get(Owner, message.from_user.id)
        wallet = await owner.createWallet(blockchain="tron", session=session)
    except Exception as ex:
        await message.answer(f'Произошла ошибка {ex}, перезапустите бота.', reply_markup=ReplyKeyboardRemove())
        return
    else:
        await state.set_state(WalletStates.use_wallet)
        qr = await qr_code(wallet.wallet_address)
        img = BufferedInputFile(file=qr, filename=str(wallet.wallet_address) + ".PNG")
        await loader(chat_id=message.from_user.id, text="Генерация кошелька", time=3)
        await message.answer_photo(
            photo=img,
            caption=f'<b>Кошелек успешно создан</b>\n\nПубличный адрес:\n<code>{str(wallet.wallet_address)}</code>',
            reply_markup=use_wallet_kb()
        )


@router.message(F.text == "💸 Отправить деньги 💸", StateFilter(WalletStates.use_wallet, WalletSendMoney))
async def send_money_start(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    await MManager.garbage_store(state, message.message_id)
    data = await state.get_data()
    chain = data.get('wallet_chain')
    owner: Owner = await session.get(Owner, message.from_user.id)
    wallet: Wallet = owner.wallets.get(chain)
    await state.set_state(WalletSendMoney.send_money_start)
    text = pretty_balance(await wallet.getBalance()) + "\nЧто именно вы хотите отправить?"
    msg = await message.answer(text, reply_markup=send_money_kb([token.upper() for token in await wallet.getBalance()]))
    await state.update_data(msg_sender=msg.message_id, send_text=text)


@router.callback_query(StateFilter(WalletSendMoney.send_money_start))
async def send_money_where(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    await state.set_state(WalletSendMoney.send_money_where)
    old_text = callback.message.text.replace("   \nЧто именно вы хотите отправить?", "")
    text = old_text + f"\nОтправляется: <code>{callback.data}</code>\n" + "\nТеперь введите целевой адрес:"
    await bot.edit_message_text(text,
                                callback.message.chat.id,
                                callback.message.message_id,
                                reply_markup=None)
    await state.update_data(send_text=text)


@router.message(StateFilter(WalletSendMoney.send_money_where))
async def send_money_how_many(message: Message, bot: Bot, state: FSMContext):
    await MManager.garbage_store(state, message.message_id)
    await state.set_state(WalletSendMoney.send_money_how_many)
    data = await state.get_data()
    await state.update_data(target_adress=message.text)
    old_text = data.get('send_text').replace("\nТеперь введите целевой адрес:", "")
    text = old_text + f"На адрес: <code>{message.text}</code>\n" + '\nСколько вы хотите отправить?'
    await state.update_data(send_text=text)
    await bot.edit_message_text(text,
                                message.chat.id,
                                data.get("msg_sender"),
                                reply_markup=None)


@router.message(StateFilter(WalletSendMoney.send_money_how_many))
async def send_money_confirm(message: Message, bot: Bot, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer('Пожалуйста, введите отправьте корректное число.')
        return

    await MManager.garbage_store(state, message.message_id)
    await state.set_state(WalletSendMoney.send_money_confirm)
    data = await state.get_data()
    old_text = data.get('send_text').replace('\nСколько вы хотите отправить?', "")
    text = old_text + f"Количество: <code>{amount}</code>\n" + "\nЕсли все верно, дважды подтвердите транзакцию:"
    await state.update_data(amount=amount, send_text=text)
    await bot.edit_message_text(text, message.chat.id, data.get("msg_sender"),
                                reply_markup=send_money_confirm_kb(confirm_push=0))


@router.callback_query(F.data == 'more_conf', StateFilter(WalletSendMoney.send_money_confirm))
async def send_money_confirm_pushs(callback: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    conf_push = data.get("confirm_push", 0)
    conf_push += 1
    await state.update_data(confirm_push=conf_push)
    await bot.edit_message_reply_markup(callback.message.chat.id, data.get("msg_sender"),
                                        reply_markup=send_money_confirm_kb(confirm_push=conf_push))


@router.callback_query(F.data == 'send_confirmed', StateFilter(WalletSendMoney.send_money_confirm))
async def send_money_really_end(callback: CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await bot.edit_message_reply_markup(callback.message.chat.id, data.get("msg_sender"),
                                        reply_markup=send_money_confirm_kb(confirm_push=2))
    try:
        owner: Owner = await session.get(Owner, callback.from_user.id)
        chain = data.get('wallet_chain')
        target_adress = (await state.get_data()).get('target_adress')
        amount = data.get('amount')
        wallet = owner.wallets.get(chain)
        text = await wallet.createTransaction(session, target_adress, float(amount))
        result_for_keyboard = 3
    except Exception as ex:
        text = str(ex)
        result_for_keyboard = 66
    await bot.edit_message_reply_markup(callback.message.chat.id, data.get("msg_sender"),
                                        reply_markup=send_money_confirm_kb(confirm_push=result_for_keyboard))
    await callback.message.answer(text)
    await state.set_state(WalletStates.use_wallet)
    await MManager.clean(state, bot, callback.message.chat.id)
