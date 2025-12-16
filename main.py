import asyncio
from io import BytesIO
from os import getenv

from utils import *
import aiogram.types
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StatesGroup, State, StateFilter
from aiogram.types import Message, CallbackQuery, InputFile, BufferedInputFile
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from aiogram.filters import *
from base import Base, User, Order, Product, AllProducts, Event, City
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from aiogram.utils.markdown import hlink, link
import logging
from typing import *
import datetime
import time
from math import log, floor
from dotenv import load_dotenv
# logging
# logging.basicConfig(level=logging.INFO)

engine = create_engine("sqlite:///db/database.db", echo=True)
load_dotenv('.env')
TOKEN = getenv("TOKEN")
bot = Bot(token=getenv('TOKEN'))
dp = Dispatcher(bot=bot)


class Form(StatesGroup):
    new_product_title = State()
    status = State()
    new_event = State()
    event_id = State()
    all_product_id = State()
    address = State()
    new_address = State()
    order_delete_id = State()
    new_city = State()
    delete_city_id = State()

def create_db_and_tables() -> None:
    Base.metadata.create_all(engine)


async def add_product(product):
    with Session(engine) as session:
        session.add(product)
        session.commit()


async def update_order_status_by_id(i, status):
    with Session(engine) as session:
        od: Order = session.scalars(select(Order).where(Order.id == i)).first()
        od.status = status
        od.data = str(datetime.datetime.now())[:50]
        session.commit()


async def search_user_by_id(i):
    with Session(engine) as session:
        stmt = select(User).where(User.id.in_([i]))
        return session.scalars(stmt).first()


async def update_user_orders_statisticts(i, a, b):
    with Session(engine) as session:
        stmt = select(User).where(User.id.in_([i]))
        user: User = session.scalars(stmt).first()
        user.all_orders_sum += a
        user.all_orders_count += b
        session.commit()


async def add_event(event: Event):
    with Session(engine) as session:
        session.add(event)
        session.commit()

async def add_city(city: City):
    with Session(engine) as session:
        session.add(city)
        session.commit()
        return city.id

async def delete_event(i):
    with Session(engine) as session:
        stmt = select(Event).where(Event.id == i)
        event = session.scalars(stmt).first()
        session.delete(event)
        session.commit()

async def delete_city(i):
    with Session(engine) as session:
        stmt = select(City).where(City.id == i)
        city = session.scalars(stmt).first()
        session.delete(city)
        session.commit()

async def get_all_products():
    with Session(engine) as session:
        return session.scalars(select(AllProducts)).fetchall()


async def delete_all_product_by_id(i):
    with Session(engine) as session:
        stmt = select(AllProducts).where(AllProducts.id == i)
        product = session.scalars(stmt).first()
        session.delete(product)
        session.commit()


async def get_all_events():
    with Session(engine) as session:
        return session.scalars(select(Event)).fetchall()

async def get_all_cities():
    with Session(engine) as session:
        return session.scalars(select(City)).fetchall()


async def get_all_products_same_type(type, city) -> Sequence[AllProducts]:
    with Session(engine) as session:
        return session.scalars(select(AllProducts).where(AllProducts.type == type and AllProducts.city_id == city)).fetchall()


async def change_status_order_by_id(id_, status):
    with Session(engine) as session:
        stmt = select(Order).where(Order.id == id_)
        od = session.scalars(stmt).first()
        od.status = status
        session.commit()

async def address_update(id_, address):
    with Session(engine) as session:
        stmt = select(Order).where(Order.id == id_)
        od = session.scalars(stmt).first()
        od.address = address
        session.commit()

async def delete_order_by_id(id_):
    with Session(engine) as session:
        stmt = select(Order).where(Order.id == id_)
        od: Order = session.scalars(stmt).first()
        session.delete(od)
        session.commit()



async def generate_user_status(status):
    if status == 'payed':
        return "оплачено"
    elif status == 'awaiting_delivery':
        return "ожидает доставки"
    elif status == 'delivered':
        return "доставлено"
    else:
        return 'неизвестный статус'


async def add_to_cart_by_username(product: Product, username, size=None):
    with Session(engine) as session:
        user = await search_user_by_tag(username)
        cart: Order = await search_cart(user)
        if cart:
            product.order = cart
            await add_product(product)
        else:
            a = Order(data=str(datetime.datetime.now())[:50], status='in_cart', user=user)
            session.add(a)
            product.order = a
            session.add(product)
        session.commit()


async def search_cart(user: User):
    try:
        return list(filter(lambda x: x.status == 'in_cart', user.orders))[0]
    except:
        return None


async def search_orders(user: User):
    try:
        return list(filter(lambda x: x.status != 'in_cart' and x.status != 'taken_away', user.orders))
    except:
        return None


async def get_all_products_by_id(i):
    with Session(engine) as session:
        stmt = select(AllProducts).where(AllProducts.id == i)
        return session.scalars(stmt).first()


async def get_product_by_id(i) -> AllProducts:
    with Session(engine) as session:
        return session.scalars(select(AllProducts).where(AllProducts.id == i)).first()


async def create_user(user: User) -> None:
    with Session(engine) as session:
        stmt = select(User).where(User.phone_number.in_([user.phone_number]))
        if not session.scalars(stmt).fetchall():
            session.add(user)
        else:
            session.scalars(stmt).first().tag = user.tag
        session.commit()


async def delete_product_by_id(product_id):
    with Session(engine) as session:
        stmt = select(Product).where(Product.id == product_id)
        product = session.scalars(stmt)
        session.delete(product)
        session.commit()


async def delete_product(product):
    with Session(engine) as session:
        session.delete(product)
        session.commit()


async def search_order_by_id(i):
    with Session(engine) as session:
        stmt = select(Order).where(Order.id == i)
        return session.scalars(stmt).first()

async def search_city_by_id(i):
    with Session(engine) as session:
        stmt = select(City).where(City.id == i)
        return session.scalars(stmt).first()

async def is_user(tag):
    stmt = select(User).where(User.tag.in_([tag]))
    with Session(engine) as session:
        a = session.scalars(stmt).first()
        if not session.scalars(stmt).fetchall():
            return False
        else:
            return True


async def get_product_id_by_title(title):
    with Session(engine) as session:
        stmt = select(AllProducts).where(AllProducts.name == title)
        return session.scalars(stmt).first()


async def add_product_to_all_products(a: AllProducts):
    with Session(engine) as session:
        stmt = select(AllProducts).where(AllProducts.name.in_([a.name]))
        if not session.scalars(stmt).fetchall():
            session.add(a)
        session.commit()


async def search_user_by_tag(tag) -> User:
    with Session(engine) as session:
        stmt = select(User).where(User.tag.in_([tag]))
        return session.scalars(stmt).first()


async def simple_inline(lst):
    b = InlineKeyboardBuilder()
    a = []
    for i in lst:
        a = []
        for el in i:
            if el[1].split('|')[-1] != 'url':
                a.append(InlineKeyboardButton(text=el[0], callback_data=el[1]))
            else:
                a.append(InlineKeyboardButton(text=el[0], url=el[1].split('|')[0]))

        b.row(*a)
    return b.as_markup()


async def contact_keyboard():
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📱 Отправить", request_contact=True)]],
                                 resize_keyboard=True)
    return markup


# Command handler
@dp.message(F.text == '/start')
async def command_start_handler(message: Message) -> None:
    if await is_user(message.from_user.username):
        await home(message)
    else:
        await message.answer('''Нажмите кнопку 
«Отправить номер телефона». 

Бот будет знать номер на которой ЗАРЕГЕСТРИРОВАН ваш аккаует в телеграме

🌸 Так вы будете в нашей базе данных 🌸''',
                             reply_markup=await contact_keyboard())


@dp.message(F.text.startswith('/start'))
async def get_product(message: Message):
    type_, id_ = message.text.split()[-1].split('_')
    ap = await get_product_by_id(id_)
    await message.delete()
    a = await bot.send_photo(message.from_user.id,
                         BufferedInputFile(bytes(open(f'photos/{type_}_{id_}.jpg', 'rb').read()), 'Candle'),
                         caption=f'{ap.name}\n{ap.description}\n{ap.price}',
                         reply_markup=await simple_inline([[['Добавить товар в корзину', f'to_cart_{type_}_{id_}']]]))


@dp.message(F.text == 'Домой')
async def home_button(message: Message):
    await message.answer(text='''Итак, с чего начнём?

👀 Увидеть все коллекции (Каталог) — Полная коллекция RO с актуальными ценами и наличием. Чтобы ничего не упустить.

🎁 Выгодно (Акции и дропы) — Ограниченные серии и специальные условия. Успей занять свою позицию.

❓ Нужна помощь? (Менеджер) — Команда RO на связи! Любые вопросы по заказу, размеру или доставке — поможем с выбором.

Выбирай, что тебе ближе 👇''',
                         reply_markup=await simple_inline(
                             [[['Прайс лист', 'city_selection']], [['Акции', 'event']],
                              [['менеджер', 'tg://resolve?domain=project_manager_Y|url']]]))
    await message.delete()


@dp.message(F.contact)
async def home(message: Message):
    print(message.from_user.id)
    a = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Корзина'), KeyboardButton(text='Профиль'), KeyboardButton(text='Заказы'),
                   KeyboardButton(text='Домой')]],
        resize_keyboard=True)
    if not await is_user(message.from_user.username):
        await create_user(User(phone_number=message.contact.phone_number, tag=message.from_user.username, ))
    await message.answer(text='''💫🏙 Привет и добро пожаловать в официальный бот Renaissance Outfit! 🏙

Очень рады видеть тебя здесь! ✨

Это — твой прямой проводник в мир стиля, который возрождает локальную идентичность. Здесь мы создаём не просто одежду, а аутфиты, объединяющие людей и города.

В этом боте всё устроено просто и по делу:
✨ Сразу увидеть всю коллекцию — актуальные модели, наличие и цены.
✨ Узнать про коллаборации и дропы — эксклюзивы и ограниченные серии.
✨ Моментально оформить заказ — без лишних переходов и сложностей.

За каждым заказом следит наша команда, поэтому всё пройдёт гладко и чётко)

Готовы выбрать вещь, которая станет частью твоего стиля и твоего города? Жми на кнопку ниже! 👇''',
                         reply_markup=a)
    await message.answer(text='''Итак, с чего начнём?

👀 Увидеть все коллекции (Каталог) — Полная коллекция RO с актуальными ценами и наличием. Чтобы ничего не упустить.

🎁 Выгодно (Акции и дропы) — Ограниченные серии и специальные условия. Успей занять свою позицию.

❓ Нужна помощь? (Менеджер) — Команда RO на связи! Любые вопросы по заказу, размеру или доставке — поможем с выбором.

Выбирай, что тебе ближе 👇''',
                         reply_markup=await simple_inline(
                             [[['Прайс лист', 'city_selection']], [['Акции', 'event']],
                              [['менеджер', 'tg://resolve?domain=IneY_project_manager|url']]]))


@dp.message(Command('admin'))
async def admin(message: Message):
    if message.from_user.id == 7077870371 or message.from_user.id == 1295888314 or message.from_user.id == 1241466637:
        await message.answer(text=f"Здравствуйте {message.from_user.first_name}! Что вы хотите сделать?",
                             reply_markup=await simple_inline(
                                 [[['добавить товар', 'add_product']], [['посмотреть заказы', 'print_orders']],
                                  [['обновить статус по id', 'update_status']], [['добавить акцию', 'add_events']], [['добавить город', 'add_city']], [['удалить город', 'delete_city']],
                                  [['удалить акцию', 'delete_events']], [['удалить товар', 'delete_all_product']], [['изменить адрес доставки', 'update_address_delivery']], [['Удалить доставленный заказ', 'delete_order']]]))


@dp.message(Command('cancel'))
async def cancel_handler(message: Message, state: FSMContext):
    """

    Allow user to cancel any action

    """

    current_state = await state.get_state()

    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)

    # Cancel state and inform user about it

    await state.clear()

    # And remove keyboard (just in case)

    await message.answer('Отменено', reply_markup=ReplyKeyboardRemove())


@dp.callback_query(F.data == 'add_product')
async def add_product_(message: CallbackQuery, state: FSMContext):
    await state.set_state(Form.new_product_title)
    await bot.send_message(chat_id=message.from_user.id,
                           text='Скиньте фото с описанием в формате название /// цена /// тип (tshort, hat, hoodie, patch, pants) /// описание /// айди города')


@dp.message(Form.new_product_title)
async def add_product1(message: Message, state: FSMContext):
    data = message.caption.split('///')
    await add_product_to_all_products(
        AllProducts(name=data[0], price=data[1].replace(' ', ''), type=data[2].replace(' ', ''), description=data[3], city_id=int(data[4].replace(' ', ''))))
    id_ = await get_product_id_by_title(data[0])
    await bot.download_file((await bot.get_file(message.photo[-1].file_id)).file_path,
                            f'photos/{id_.type}_{id_.id}.jpg')
    await message.answer('Успешно')
    await state.clear()

@dp.callback_query(F.data == 'return_to_price_list')
@dp.callback_query(F.data == 'city_selection')
async def city_selection(message: CallbackQuery):
    lst = []
    for el in await get_all_cities():
        lst.append([[str(el.name), 'price_list_' + str(el.id)]])
    lst.sort(key=lambda x: x[0][0])
    print(lst)
    await bot.send_message(message.from_user.id, text='Выберите город', reply_markup=await simple_inline(lst))

@dp.callback_query(F.data.startswith('price_list_'))
async def get_price_list(message: CallbackQuery):
    await message.message.delete()
    p1, p2, city_id = message.data.split('_')
    await bot.send_message(chat_id=message.from_user.id, text='''Чтобы тебе было удобнее
мы разделили прайс-лист по категориям)

👇 Выбери то что тебе по душе👇''',
                           reply_markup=await simple_inline(
                               [[['Худи', f'hoodie_{city_id}']], [['Футболки', f'tshort_{city_id}']],
                                [['Патчи', f'patch_{city_id}']]]))

@dp.callback_query(F.data == 'update_address_delivery')
async def update_address_delivery(message: CallbackQuery, state: FSMContext):
    await state.set_state(Form.new_address)
    await bot.send_message(message.from_user.id, text='Введите новый адрес в формате айди заказа///новый адрес(точка)')

@dp.message(Form.new_address)
async def update_address_delivery(message: CallbackQuery, state: FSMContext):
    data = message.text.split('///')
    await address_update(int(data[0]), data[-1])
    await message.answer(text='Успешно изменено!')
    await state.clear()

@dp.callback_query(F.data == 'event')
async def events(message: Message):
    s = '🎁 <b>АКЦИИ</b> 🎁\n\n'
    for el in await get_all_events():
        a = el.description + '\n\n'
        s += a
    if len(s) > 4096:
        for x in range(0, len(s), 4096):
            await bot.send_message(chat_id=message.from_user.id, text=s[x:x + 4096], parse_mode='HTML')
    else:
        await bot.send_message(chat_id=message.from_user.id, text=s, parse_mode='HTML')


@dp.callback_query(F.data.startswith('hoodie_'))
async def hoodie(message: CallbackQuery):
    await message.message.delete()
    t, city_id = message.data.split('_')
    s = '''ХУДИ

'''
    print(await get_all_products())
    if await get_all_products_same_type('hoodie', city_id):
        for el in await get_all_products_same_type('hoodie', city_id):
            s += hlink(str(el.name), f'tg://resolve?domain=Test123123213123123123123_bot&start={el.type}_{el.id}') + ' Цена: ' + str(
                el.price) + ' ₽' + '\n'
        await bot.send_message(chat_id=message.from_user.id, text=s, parse_mode='HTML',
                               reply_markup=await simple_inline([[['Назад', 'return_to_price_list']]]))
    else:
        a = await bot.send_message(chat_id=message.from_user.id, text='Ещё нет товара выбранного типа')
        await asyncio.sleep(5)
        await a.delete()


@dp.callback_query(F.data == 'back_products_tshort')
@dp.callback_query(F.data.startswith('tshort_'))
async def tshort(message: CallbackQuery):
    await message.message.delete()
    t, city_id = message.data.split('_')
    s = '''ФУТБОЛКИ

'''
    print(await get_all_products())
    if await get_all_products_same_type('tshort', city_id):
        for el in await get_all_products_same_type('tshort', city_id):
            s += hlink(str(el.name), f'tg://resolve?domain=Test123123213123123123123_bot&start={el.type}_{el.id}') + ' Цена: ' + str(
                el.price) + ' ₽' + '\n'
        await bot.send_message(chat_id=message.from_user.id, text=s, parse_mode='HTML',
                               reply_markup=await simple_inline([[['Назад', 'return_to_price_list']]]))
    else:
        a = await bot.send_message(chat_id=message.from_user.id, text='Ещё нет товара выбранного типа')
        await asyncio.sleep(5)
        await a.delete()


@dp.callback_query(F.data == 'back_products_hat')
@dp.callback_query(F.data.startswith('hat_'))
async def hoodie(message: CallbackQuery):
    await message.message.delete()
    t, city_id = message.data.split('_')
    s = '''🎆 ПОСТЕРЫ 🎆

'''
    print(await get_all_products())
    if await get_all_products_same_type('hat_', city_id):
        for el in await get_all_products_same_type('hat', city_id):
            s += hlink(str(el.name), f'tg://resolve?domain=Test123123213123123123123_bot&start={el.type}_{el.id}') + ' Цена: ' + str(
                el.price) + ' ₽' + '\n'
        await bot.send_message(chat_id=message.from_user.id, text=s, parse_mode='HTML',
                               reply_markup=await simple_inline([[['Назад', 'return_to_price_list']]]))
    else:
        a = await bot.send_message(chat_id=message.from_user.id, text='Ещё нет товара выбранного типа')
        await asyncio.sleep(5)
        await a.delete()


@dp.callback_query(F.data == 'back_products_pants')
@dp.callback_query(F.data.startswith('pants_'))
async def hoodie(message: CallbackQuery):
    await message.message.delete()
    t, city_id = message.data.split('_')
    s = '''🧷 ЗНАЧКИ 🧷

'''
    print(await get_all_products())
    if await get_all_products_same_type('pants', city_id):
        for el in await get_all_products_same_type('pants', city_id):
            s += hlink(str(el.name), f'tg://resolve?domain=Renaissance_Outfit_bot&start={el.type}_{el.id}') + ' Цена: ' + str(
                el.price) + ' ₽' + '\n'
        await bot.send_message(chat_id=message.from_user.id, text=s, parse_mode='HTML',
                               reply_markup=await simple_inline([[['Назад', 'return_to_price_list']]]))
    else:
        a = await bot.send_message(chat_id=message.from_user.id, text='Ещё нет товара выбранного типа')
        await asyncio.sleep(5)
        await a.delete()


@dp.callback_query(F.data == 'back_products_patch')
@dp.callback_query(F.data.startswith('patch_'))
async def hoodie(message: CallbackQuery):
    await message.message.delete()
    t, city_id = message.data.split('_')
    s = 'ПАТЧИ\n\n'
    print(await get_all_products())
    if await get_all_products_same_type('patch', city_id):
        for el in await get_all_products_same_type('patch', city_id):
            s += hlink(str(el.name), f'tg://resolve?domain=Test123123213123123123123_bot&start={el.type}_{el.id}') + ' Цена: ' + str(
                el.price) + ' ₽' + '\n'
        await bot.send_message(chat_id=message.from_user.id, text=s, parse_mode='HTML',
                               reply_markup=await simple_inline([[['Назад', 'return_to_price_list']]]))
    else:
        a = await bot.send_message(chat_id=message.from_user.id, text='Ещё нет товара выбранного типа')
        await asyncio.sleep(5)
        await a.delete()


@dp.message(F.text == 'Корзина')
async def show_cart(message: Message):
    cart: Order = await search_cart(await search_user_by_tag(message.from_user.username))
    s = '''
🛒 КОРЗИНА 🛒

Товары:
'''
    c = 0
    if cart and cart.products:
        for el in cart.products:
            s += f'{el.name} Цена: {el.price} Размер: {el.size}\n\n'
            c += el.price
        s += f'Общая сумма - {c}₽'
        await message.answer(s, reply_markup=await simple_inline(
            [[['Оплатить', f'pay_{cart.id}']], [['Очистить корзину', 'clean_cart']]]))
    else:
        await message.answer('Вы ещё ничего не добавили в корзину')
    await message.delete()


@dp.message(F.text == 'Домой')
async def show_cart(message: Message):
    await home(message)
    await message.delete()


@dp.callback_query(F.data.startswith('to_cart_'))
async def add_to_cart(message: CallbackQuery):
    _1, _2, t, i = str(message.data).split('_')
    if await is_user(message.from_user.username):
        await bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message.message_id, reply_markup=await simple_inline([[['XS', f'add_to_cart_{t}_{i}_XS'], ['S', f'add_to_cart_{t}_{i}_S']],
                                                                                                                                                   [['M', f'add_to_cart_{t}_{i}_M'], ['L', f'add_to_cart_{t}_{i}_L']],
                                                                                                                                                   [['XL', f'add_to_cart_{t}_{i}_XL']]]))

    else:
        await bot.send_message(message.from_user.id, text='Сначала зарегестрируйтесь в боте! Для этого введите /start')

@dp.callback_query(F.data.startswith('add_to_cart_'))
async def to_cart_add_with_size(message: CallbackQuery):
    print(message.data)
    _1, _2, _3, t, i, s = str(message.data).split('_')
    apr = await get_all_products_by_id(i)
    a = Product(name=apr.name, price=apr.price, size=s)
    await add_to_cart_by_username(a, message.from_user.username)
    a = await bot.send_message(chat_id=message.from_user.id, text='Добавлено в корзину')
    await asyncio.sleep(5)
    await a.delete()
    await message.message.delete()

@dp.callback_query(F.data == 'update_status')
async def admin_update_status(message: CallbackQuery, state: FSMContext):
    await state.set_state(Form.status)
    await bot.send_message(chat_id=message.from_user.id, text='id///status(awaiting_delivery, delivered, taken_away))')


@dp.message(Form.status)
async def admin_update_status1(message: Message, state: FSMContext):
    data = message.text.replace(' ', '').split('///')
    await update_order_status_by_id(int(data[0]), data[1])
    await state.clear()
    await bot.send_message(chat_id=message.from_user.id, text='Успешно')


@dp.message(F.text == 'Заказы')
async def get_orders(message: Message):
    user = await search_user_by_tag(message.from_user.username)
    orders = await search_orders(user)
    s = ''
    if orders:
        for el in orders:
            a = str((datetime.datetime.strptime(el.data, '%Y-%m-%d %H:%M:%S.%f') + datetime.timedelta(days=7)).date()).replace('-', '\-')
            s += f'id Заказа: {el.id}\nСтатус заказа: {await generate_user_status(el.status)}\n{"Примерная дата доставки " + a}\nТочка доставки: `{el.address}`\n'
            for i in el.products:
                s += f'   {i.name} Размер: {i.size}\n'
        if len(s) > 4096:
            for x in range(0, len(s), 4096):
                await message.answer(s[x:x + 4096])
        else:
            await message.answer(s, parse_mode='MarkdownV2')
        await message.delete()
    else:
        await message.answer('Вы ещё ничего не заказали')
        await message.delete()


@dp.callback_query(F.data == 'print_orders')
async def print_orders(message: CallbackQuery):
    a = create_excel_orders()
    b = create_excel_products()
    c = create_excel_users()
    d = create_excel_all_products()
    e = create_excel_events()
    f = create_excel_cities()
    await bot.send_message(chat_id=message.from_user.id, text='Пришлю в течении 5 минут')
    await bot.send_document(chat_id=message.from_user.id, document=BufferedInputFile(bytes(open(a, 'rb').read()), a))
    await bot.send_document(chat_id=message.from_user.id, document=BufferedInputFile(bytes(open(b, 'rb').read()), b))
    await bot.send_document(chat_id=message.from_user.id, document=BufferedInputFile(bytes(open(c, 'rb').read()), c))
    await bot.send_document(chat_id=message.from_user.id, document=BufferedInputFile(bytes(open(d, 'rb').read()), d))
    await bot.send_document(chat_id=message.from_user.id, document=BufferedInputFile(bytes(open(e, 'rb').read()), e))
    await bot.send_document(chat_id=message.from_user.id, document=BufferedInputFile(bytes(open(f, 'rb').read()), f))

@dp.message(F.text == 'Профиль')
async def profile(message: Message):
    user = await search_user_by_tag(message.from_user.username)
    await message.answer(f'''👤 ПРОФИЛЬ 👤

Имя: {user.tag}
Телефон: {user.phone_number}
ID профиля: {user.id} (для поддержки)

Уровень: {floor(log(int(user.all_orders_sum) // 100, 2)) if user.all_orders_sum != 0 else 0}
XP до следующего уровня:
{int(user.all_orders_sum) // 100}/{round(2 ** (log(int(user.all_orders_sum) // 100, 2))) if user.all_orders_sum != 0 else 2}

Кол-во заказов: {user.all_orders_count}
Общая сумма заказов: {user.all_orders_sum}
Персональная скидка: {user.discount}
''')
    await message.delete()


@dp.callback_query(F.data == 'clean_cart')
async def clean_cart(message: CallbackQuery):
    user = await search_user_by_tag(message.from_user.username)
    cart: Order = await search_cart(user)
    for el in cart.products:
        await delete_product(el)
    await message.message.delete()


@dp.callback_query(F.data == 'add_events')
async def add_events(message: CallbackQuery, state: FSMContext):
    await state.set_state(Form.new_event)
    await bot.send_message(chat_id=message.from_user.id, text='Отправьте акцию')

@dp.callback_query(F.data == 'add_city')
async def add_cities(message: CallbackQuery, state: FSMContext):
    await state.set_state(Form.new_city)
    await bot.send_message(chat_id=message.from_user.id, text='Отправьте название города')


@dp.message(Form.new_event)
async def add_events1(message: Message, state: FSMContext):
    await state.clear()
    a = Event()
    a.description = message.text
    await add_event(a)
    await message.answer('Успешно')

@dp.message(Form.new_city)
async def add_events1(message: Message, state: FSMContext):
    await state.clear()
    a = City()
    a.name = message.text
    b = await add_city(a)
    await message.answer(f'Успешно. ID города: {b}')


@dp.callback_query(F.data == 'delete_events')
async def delete_events(message: CallbackQuery, state: FSMContext):
    await state.set_state(Form.event_id)
    await bot.send_message(chat_id=message.from_user.id, text='Отправьте id акции')

@dp.callback_query(F.data == 'delete_city')
async def delete_events(message: CallbackQuery, state: FSMContext):
    await state.set_state(Form.delete_city_id)
    await bot.send_message(chat_id=message.from_user.id, text='Отправьте id города')


@dp.message(Form.event_id)
async def delete_events(message: Message, state: FSMContext):
    await state.clear()
    await delete_event(int(message.text))
    await message.answer('Успешно')

@dp.message(Form.delete_city_id)
async def delete_events(message: Message, state: FSMContext):
    await state.clear()
    await delete_city(int(message.text))
    await message.answer('Успешно')

@dp.callback_query(F.data == 'delete_all_product')
async def delete_all_product(message: CallbackQuery, state: FSMContext):
    await state.set_state(Form.all_product_id)
    await bot.send_message(chat_id=message.from_user.id, text='Отправьте id товара')


@dp.message(Form.all_product_id)
async def delete_all_product1(message: Message, state: FSMContext):
    await state.clear()
    await delete_all_product_by_id(int(message.text))
    await message.answer('Успешно')


@dp.callback_query(F.data.startswith('pay_'))
async def pay_id(message: CallbackQuery, state: FSMContext):
    i = message.data.split('_')[1]
    c = 0
    order: Order = await search_order_by_id(i)
    for el in order.products:
        c += el.price
    b = len(order.products)
    print(c, b)
    await update_user_orders_statisticts(order.user_id, c, b)
    # user.discount = user.discount
    await update_order_status_by_id(i, 'payed')
    a = await bot.send_message(message.from_user.id, text='Успешно оплачено!')
    await bot.send_message(message.from_user.id,text='Отправьте адрес Яндекс маркета удобным для вас способом',
                         reply_markup=await simple_inline([[['Прислать геолокацию', f'sendaddressgeo_{i}']], [['Связаться с менеджером', 'tg://resolve?domain=project_manager_Y|url']], [['Прислать адрес', f'sendaddresstext_{i}']]]))
    await message.message.delete()
    await asyncio.sleep(5)
    await a.delete()


@dp.callback_query(F.data.startswith('sendaddressgeo'))
async def address(message: CallbackQuery, state: FSMContext):
    await message.message.delete()
    await state.set_state(Form.address)
    await state.update_data(address=message.data.split('_')[-1])
    a = await bot.send_message(message.from_user.id, text="Отправьте геолокацию(нажмите на иконку скрепки в поле отправки сообщения и выберите пункт геопозиция. Найдите на карте здание Яндекс маркета и нажмите \"Отправить выбранную геопозицию\")")
    await asyncio.sleep(60)
    await a.delete()

@dp.callback_query(F.data.startswith('sendaddresstext'))
async def address(message: CallbackQuery, state: FSMContext):
    await message.message.delete()
    await state.set_state(Form.address)
    await state.update_data(address=message.data.split('_')[-1])
    a = await bot.send_message(message.from_user.id, text="Отправьте адрес")
    await asyncio.sleep(60)
    await a.delete()

@dp.message(F.location, StateFilter(Form.address))
async def address_collect(message: Message, state: FSMContext):
    d = await state.get_data()
    await address_update(int(d['address']), f'{message.location.latitude}, {message.location.longitude}')
    await state.clear()
    a = await bot.send_message(message.from_user.id, text='Успешно получен адрес!')
    await bot.send_message(7077870371, text=f'Новый заказ! Адрес: {message.location.latitude}, {message.location.longitude}; юзернейм: @{message.from_user.username}')
    await message.delete()
    await asyncio.sleep(5)
    await a.delete()

@dp.message(Form.address)
async def address_collect(message: Message, state: FSMContext):
    d = await state.get_data()
    await address_update(int(d['address']), message.text)
    await state.clear()
    a = await bot.send_message(message.from_user.id, text='Успешно получен адрес!')
    await bot.send_message(7077870371, text=f'Новый заказ! Адрес: {message.text}, юзернейм: @{message.from_user.username}', )
    await message.delete()
    await asyncio.sleep(5)
    await a.delete()

@dp.callback_query(F.data == 'delete_order')
async def delete_order(message: Message, state: FSMContext):
    await state.set_state(Form.order_delete_id)
    await bot.send_message(message.from_user.id, text='Пришлите айди заказа')

@dp.message(Form.order_delete_id)
async def id_order_delete(message: Message, state: FSMContext):
    await delete_order_by_id(int(message.text))
    await state.clear()
    await message.answer('Успешно')

# Run the bot
async def main() -> None:
    print(await bot.get_me())
    await dp.start_polling(bot)


if __name__ == "__main__":
    create_db_and_tables()
    asyncio.run(main())
