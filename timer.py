import asyncio
from datetime import timedelta

from aiogram.types import Message, BufferedInputFile

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
    a = await bot.send_photo(message.from_user.id,
                             photo=BufferedInputFile(bytes(open(f'photos/timer.jpg', 'rb').read()), 'Candle'),
                             reply_markup=await simple_inline(
                                 [[['ОТСЧЁТ УЖЕ ПОШЁЛ', 'https://t.me/renaissanceoutfit|url']]]))
    b = await message.answer('<b>ОСТАЛОСЬ           </b>', parse_mode='HTML', reply_markup=await simple_inline(
        [[[str(global_time).replace('days,', 'дня').split('.')[0], 'https://t.me/renaissanceoutfit|url']]]))


async def main() -> None:
    print(await bot.get_me())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
