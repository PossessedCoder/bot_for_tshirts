from sqlalchemy import create_engine
import pandas as pd
import datetime

# Замените на ваши данные для подключения к базе данных
engine = create_engine('sqlite:///db///database.db')


# Выполните запрос к вашей таблице
def create_excel_orders():
    query = "SELECT * FROM orders"
    df = pd.read_sql(query, engine)
    a = f"tables/Orders{str(datetime.datetime.now()).replace(':', '-')}.xlsx"
    df.to_excel(a, index=False)
    return a


def create_excel_products():
    query = "SELECT * FROM products"
    df = pd.read_sql(query, engine)
    a = f"tables/Products{str(datetime.datetime.now()).replace(':', '-')}.xlsx"
    df.to_excel(a, index=False)
    return a


def create_excel_all_products():
    query = "SELECT * FROM all_products"
    df = pd.read_sql(query, engine)
    a = f"tables/AllProducts{str(datetime.datetime.now()).replace(':', '-')}.xlsx"
    df.to_excel(a, index=False)
    return a


def create_excel_events():
    query = "SELECT * FROM events"
    df = pd.read_sql(query, engine)
    a = f"tables/Events{str(datetime.datetime.now()).replace(':', '-')}.xlsx"
    df.to_excel(a, index=False)
    return a


def create_excel_users():
    query = "SELECT * FROM users"
    df = pd.read_sql(query, engine)
    a = f"tables/Users{str(datetime.datetime.now()).replace(':', '-')}.xlsx"
    df.to_excel(a, index=False)
    return a
