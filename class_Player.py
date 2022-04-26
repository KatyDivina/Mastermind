import os

from settings import *
from aiogram import types
import psycopg2

from random import shuffle
from datetime import datetime, timedelta
import pytz


# POSTGRESQL
user = os.getenv('PG_USER')
password = os.getenv('PG_PASSWORD')
host = os.getenv('PG_HOST')
port = os.getenv('PG_PORT')
database = os.getenv('PG_DATABASE')



db = psycopg2.connect(user=user,
                      password=password,
                      host=host,
                      port=port,
                      database=database)
cur = db.cursor()


def now_time():
    updated_time = datetime.now(pytz.timezone("Europe/Moscow"))
    return updated_time.strftime("%Y-%m-%d %H:%M:%S")


def att_ending(attempts_counter, case="Р"):

    if attempts_counter % 10 == 1 and attempts_counter != 11:
        if case == "Р":  # Если в родительном падеже
            return "попытку"
        if case == "И":  # Если в именительном падеже
            return "попыткa"
    elif attempts_counter % 10 in [2, 3, 4] and attempts_counter not in [12, 13, 14]:
        return "попытки"
    else:
        return "попыток"


class Player:
    def __init__(self, chat):
        #    ---DATABASE---
        cur.execute(f"""SELECT * FROM users WHERE user_id = {chat.id};""")
        if not cur.fetchone():  # Если игрока нет в бд, то добавляем туда
            cur.execute(
                f"""INSERT INTO users VALUES
                ({chat.id},
                '{chat.first_name}',
                '{chat.last_name}',
                '{chat.username}',
                '{now_time()}',
                1000);"""
            )
            db.commit()

        #    ---USER---
        self.id = chat.id
        self.first_name = chat.first_name
        self.username = chat.username
        self.last_name = chat.last_name

        #    ---GAME---
        self.password = ""
        self.attempts_counter = 0
        self.game_id = None

        #    ---SCORE---
        cur.execute(
            f"""SELECT best_score FROM users WHERE user_id = {self.id};""")
        self.best_score = cur.fetchone()[0]

    async def start_game(self, m):
        await self._passw_generator()

        cur.execute(
            f"""INSERT INTO games(user_id, pass )
                VALUES
                ({self.id},
                '{self.password}')
                RETURNING game_id;"""
        )
        self.game_id = cur.fetchone()[0]
        db.commit()

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton(
                text="Помощь",
                callback_data="rules"))

        await m.answer("😈")
        await m.answer(
            f"😈ХА-ХА-ХА! Я захватил твою систему и поменял пароль, тебе его ни за что не угадать!{LOCK}",
            reply_markup=keyboard,
        )

        await m.answer("🖥Введите пароль: ")

    async def _passw_generator(self):
        self.password = ""
        nums = list("0123456789")
        shuffle(nums)
        self.password = "".join(nums[:4])

        logging.info(
            f"{self.first_name} , {self.username}, {self.last_name} set password: {self.password}"
        )
        self.attempts_counter = 0

    async def hack_password(self, m):

        if self.game_id is None:  # Если была игра до перезапуска
            cur.execute(
                f"""SELECT game_id, pass
                            FROM games
                            WHERE user_id = {self.id}
                            AND games.end_game IS NULL
                            ORDER BY start_game DESC;"""
            )

            try:
                self.game_id, self.password = cur.fetchone()

                cur.execute(
                    f"""SELECT count(attempt_id) FROM attempts
                    WHERE game_id = {self.game_id};"""
                )

                self.attempts_counter = cur.fetchone()[0]

            except BaseException:

                await m.answer("Для запуска новой игры нажмите /start")
                logging.info(f"message without game: {m.text}")
                return

        if not m.text.isdigit():
            await m.answer("🖥Пароль состоит только из цифр")
            logging.info(
                f"{self.first_name} , {self.username}, {self.last_name} "
                f"try invalid pass, not digits only: {m.text}"
            )
            return
        if len(m.text) != 4:
            await m.answer("🖥В пароле ровно 4 цифры")
            logging.info(
                f"{self.first_name} , {self.username}, {self.last_name} "
                f"try invalid pass, not 4 digits: {m.text}"
            )
            return
        if len(set(m.text)) != 4:
            await m.answer("🖥В пароле все цифры должны быть разными")
            logging.info(
                f"{self.first_name} , {self.username}, {self.last_name} "
                f"try invalid pass, not unique nums: {m.text}"
            )
            return

        cur.execute(
            f"""INSERT INTO attempts (game_id, password, data) VALUES
                        ({self.game_id},
                        '{m.text}',
                        '{now_time()}');"""
        )
        db.commit()

        correct = 0
        wrong_place = 0
        incorrect = 0

        for i in range(4):
            if m.text[i] == self.password[i]:
                correct += 1
            elif m.text[i] not in self.password:
                incorrect += 1
            else:
                wrong_place += 1

        self.attempts_counter += 1
        await m.answer(
            f"{correct * str(CORRECT)}{wrong_place * WRONG_PLACE}{incorrect * INCORRECT}"
        )

        #    ---END GAME---
        if correct == 4:
            logging.info(
                f"{self.first_name} , {self.username}, {self.last_name}, "
                f"пароль: {self.password}, "
                f"попыток: {self.attempts_counter}"
            )

            # ---DATABASE---
            cur.execute(
                f"""UPDATE
                        games
                    SET
                        end_game = '{now_time()}',
                        attempts_counter = '{self.attempts_counter}'
                    WHERE
                        game_id = {self.game_id};"""
            )
            db.commit()

            self.game_id = None

            if self.attempts_counter < self.best_score:
                self.best_score = self.attempts_counter
                cur.execute(
                    f"""UPDATE
                            users
                        SET
                            best_score = {self.best_score}
                        WHERE
                            user_id = {self.id};"""
                )

                db.commit()

            buttons = [
                types.InlineKeyboardButton(text="Новая игра", callback_data="new_game"),
                types.InlineKeyboardButton(
                    text="Топ 10 моих игр", callback_data="myBest"
                ),
                types.InlineKeyboardButton(
                    text="Топ 10 лучших игр", callback_data="allBest"
                ),
            ]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)

            await m.answer("🔐")
            await m.answer(
                f"{UNLOCK}ДОСТУП РАЗРЕШЁН! "
                f"Пароль угадан за {self.attempts_counter} {att_ending(self.attempts_counter)}!"
                f" Ваш лучший результат - {self.best_score} {att_ending(self.best_score, case='И')}",
                reply_markup=keyboard,
            )

    async def show_my_top(self, m):
        cur.execute(
            f"""SELECT attempts_counter, pass FROM games
            WHERE attempts_counter >0 AND user_id = {self.id}
            ORDER BY attempts_counter LIMIT 10;"""
        )

        # sorted_tuples = sorted(self.best_games.items(), key=lambda item: item[1])
        # best_games = {k: v for k, v in sorted_tuples}

        message = f"🏆 TOP {self.first_name} 🏆\n"

        i = 0
        for attempt, passw in cur.fetchall():
            message += f"{emoji[i]} {passw} - {attempt} {att_ending(attempt)}\n"
            i += 1

        if i == 0:
            message += "Игры не найдены"
        await m.answer(message)

    async def show_best_top(self, m):

        cur.execute(
            f"""SELECT users.first_name, games.attempts_counter, games.pass, games.start_game, games.end_game
                FROM games INNER JOIN users
                ON games.user_id = users.user_id
                WHERE games.end_game IS NOT NULL
                ORDER BY attempts_counter
                LIMIT 10;""")

        message = "🏆 TOP 🏆\n"

        i = 0
        for name, best_attempt, passw, start_game, end_game in cur.fetchall():
            time = end_game - start_game

            # TODO Время с нулями в начале
            # TODO Поменять часы и никнейм местами
            # TODO Удалить SQLITE

            message += f"{emoji[i]} {passw}  -  ⏱{str(time)} | {best_attempt} {att_ending(best_attempt).ljust(9, ' ')} -  {name.ljust(12, ' ')}  \n"
            i += 1

        if i == 0:
            message += "Игры не найдены"

        await m.answer(message)
