from class_Player import *
from aiogram import Bot, Dispatcher, executor, types
import os


bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot)

# Кэш игроков
players: dict = {}


# TODO Как бот работает с группами


# START
@dp.message_handler(commands="start")
async def start_message(message: types.Message):
    p = await get_player(message)
    await p.start_game(message)


@dp.callback_query_handler(text="new_game")
async def new_game_button(call: types.CallbackQuery):
    await start_message(call.message)


# RULES
@dp.message_handler(commands="rules")
async def rules_message(m):
    await m.answer(
        f"""\
{CORRECT} - Цифра верная и стоит на своём месте (не известно, какая)
{WRONG_PLACE} - Цифра верная, но на неправильном месте
{INCORRECT} - Цифры нет в пароле
\nНАПРИМЕР
Пароль - 9872
Догадка - 7012 (2 - угадана, 7 - не на своём месте, 0 и 1 - мимо)
Результат {CORRECT}{WRONG_PLACE}{INCORRECT}{INCORRECT}""",
    )


@dp.callback_query_handler(text="rules")
async def rules_callback(call: types.CallbackQuery):
    await rules_message(call.message)


# CASH PLAYERS
async def get_player(message: types.Message) -> Player:
    """
    Get player from dictionary if exists
    Create player if not exist
    :param message: source message
    :return: class Player object
    """

    if (
        message.chat.id not in players.keys()
    ):  # Если игрок не играл в текущей сессии, добавляем в словарь
        players[message.chat.id] = Player(message.chat)

    return players.get(message.chat.id, False)


# BEST
@dp.callback_query_handler(text="myBest")
async def send_self_top_button(call: types.CallbackQuery):
    p = await get_player(call.message)
    await p.show_my_top(call.message)


@dp.callback_query_handler(text="allBest")
async def all_top_button(call: types.CallbackQuery):
    p = await get_player(call.message)
    await p.show_best_top(call.message)


# GAME
@dp.message_handler()
async def any_text_message(m: types.Message):
    p = await get_player(m)
    await p.hack_password(m)


if __name__ == "__main__":
    logging.info(f"Bot started working")
    executor.start_polling(dp, skip_updates=True)
