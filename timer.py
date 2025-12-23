import asyncio
from datetime import timedelta

from aiogram.types import Message

from main import simple_inline
import datetime
from dotenv import load_dotenv
from os import getenv
from aiogram import Bot, Dispatcher
from aiogram import F

load_dotenv('.env')
TOKEN = getenv("TOKEN")
bot = Bot(token=getenv('TOKEN'))
dp = Dispatcher(bot=bot)
global_time = (datetime.datetime(year=2025, day=28, month=12) - datetime.datetime.now())
@dp.message(F.text == '/start')
async def start(message: Message):
    global global_time
    global_time = (datetime.datetime(year=2025, day=28, month=12) - datetime.datetime.now())
    a = await message.answer('Отсчёт уже пошёл...', reply_markup=await simple_inline([[[str(global_time).replace('days,', 'дня').split('.')[0], 'city_selection']]]))

async def main() -> None:
    print(await bot.get_me())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
