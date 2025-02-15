import os
import sys
import asyncio
from dotenv import load_dotenv
import logging

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import sqlite3

from validation import validate

# .\env environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

dp = Dispatcher()


db = sqlite3.connect("users.db")
cursor = db.cursor()
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS users(
id INGETER PRIMARY KEY,
user_id INTEGER,
incomes REAL,
expenses REAL
)
"""
)
db.commit()

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📈 Доход"),
            KeyboardButton(text="📉 Расход"),
        ],
        [KeyboardButton(text="📊 Статистика")],
    ],
    resize_keyboard=True,
)


class Income(StatesGroup):
    income = State()


class Expense(StatesGroup):
    expense = State()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    user_id = message.from_user.id
    cursor.execute(
        """
        SELECT rowid FROM users WHERE user_id = ?
        """,
        (user_id,),
    )
    if not cursor.fetchall():
        cursor.execute(
            """
            INSERT INTO users (user_id, incomes, expenses) VALUES (?, ?, ?)
            """,
            (
                user_id,
                0,
                0,
            ),
        )
        db.commit()

    await message.reply(text="Добрый день!", reply_markup=main_menu_keyboard)


@dp.message(F.text == "📈 Доход")
async def income(message: Message, state: FSMContext) -> None:
    await state.set_state(Income.income)
    await message.reply("Введите доход: ")


@dp.message(F.text == "📉 Расход")
async def income(message: Message, state: FSMContext) -> None:
    await state.set_state(Expense.expense)
    await message.reply("Введите расход: ")


@dp.message(F.text == "📊 Статистика")
async def statistics(message: Message) -> None:
    cursor.execute(
        """
        SELECT incomes, expenses FROM users WHERE user_id = ?
        """,
        (message.from_user.id,),
    )
    data = cursor.fetchone()
    await message.reply(f"💳\nВаши доходы: `{data[0]}`\nВаши расходы: `{data[1]}`")


@dp.message(Income.income)
async def _income(message: Message, state: FSMContext) -> None:
    is_valid = await validate(message.text)
    if is_valid:
        user_id = message.from_user.id
        await state.update_data(income=message.text)
        data = await state.get_data()
        await state.clear()
        cursor.execute(
            """
            SELECT incomes FROM users WHERE user_id = ?
            """,
            (user_id,),
        )
        incomes = float(cursor.fetchone()[0]) + float(data["income"])
        cursor.execute(
            """
            UPDATE users SET incomes = ? WHERE user_id = ?
            """,
            (
                incomes,
                user_id,
            ),
        )
        db.commit()
    else:
        await message.reply("Вы ввели не число, или оно было отрицательное")


@dp.message(Expense.expense)
async def _expense(message: Message, state: FSMContext) -> None:
    is_valid = await validate(message.text)
    if is_valid:
        user_id = message.from_user.id
        await state.update_data(expense=message.text)
        data = await state.get_data()
        await state.clear()
        cursor.execute(
            """
            SELECT expenses FROM users WHERE user_id = ?
            """,
            (user_id,),
        )
        expenses = float(cursor.fetchone()[0]) + float(data["expense"])
        cursor.execute(
            """
            UPDATE users SET expenses = ? WHERE user_id = ?
            """,
            (
                expenses,
                user_id,
            ),
        )
        db.commit()
    else:
        await message.reply("Вы ввели не число, или оно было отрицательное")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    db.close()
