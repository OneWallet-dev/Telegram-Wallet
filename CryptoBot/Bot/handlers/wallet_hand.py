from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from Bot.filters.wallet_filters import ChainOwned
from Bot.keyboards.wallet_keys import create_wallet_kb, currency_kb, use_wallet_kb, send_money_kb, send_money_confirm_kb
from Bot.states.main_states import MainState
from Bot.states.wallet_states import WalletStates, WalletSendMoney
from Bot.utilts.cleaner import Cleaner
from Bot.utilts.currency_helper import currencies
from Bot.utilts.pretty_texts import pretty_balance
from Databases.DB_Postgres.models import Owner, Wallet

router = Router()
router.message.filter(StateFilter(MainState.welcome_state, WalletStates, WalletSendMoney))


@router.message(F.text == "💹 Кошельки", StateFilter(MainState.welcome_state))
async def choose_currency(message: Message, state: FSMContext):
    await message.answer('Выберите криптовалюту, с которой вы хотите совершать операции:',
                         reply_markup=currency_kb())


@router.callback_query(ChainOwned(), (F.data.in_(set(currencies.values()))))
async def use_wallet(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    await state.set_state(WalletStates.use_wallet)
    owner: Owner = await Owner.get(session, callback.from_user)

    wallet: Wallet = owner.wallets.get(callback.data)
    if wallet:
        msg = await callback.message.answer(f'Вы владеете кошельком в сети <b>{callback.data}</b>.\n\n'
                                            f'Публичный адрес:\n <code>{wallet.wallet_address}</code>',
                                            reply_markup=use_wallet_kb())
        await state.update_data(wallet_chain=wallet.blockchain, wallet_message=msg.message_id)
        await Cleaner.store(state, msg.message_id)
    else:
        await do_you_want_it(callback, state)


@router.callback_query(~ChainOwned(), (F.data.in_(set(currencies.values()))))
async def do_you_want_it(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(WalletStates.create_wallet)
    msg = await callback.message.answer(f'У вас нет кошелька в сети <b>{callback.data}</b>. Хотите завести?\n\n',
                                        reply_markup=create_wallet_kb(callback.data))
    await Cleaner.store(state, msg.message_id)


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
        msg = await message.answer(f'Создан кошелек:\n\nПубличный адрес:\n <code>{str(wallet.wallet_address)}</code>',
                                   reply_markup=use_wallet_kb())
        await Cleaner.store(state, msg.message_id)


@router.message(F.text == "💸 Отправить деньги 💸", StateFilter(WalletStates.use_wallet, WalletSendMoney))
async def send_money_start(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    await Cleaner.store(state, message.message_id)
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
    await Cleaner.store(state, message.message_id)
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

    await Cleaner.store(state, message.message_id)
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
    await Cleaner.clean(state, bot, callback.message.chat.id)
