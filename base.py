from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship, Session


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String(60))
    phone_number: Mapped[str] = mapped_column(String(11))
    orders: Mapped[List["Order"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy='subquery')
    all_orders_count: Mapped[int] = mapped_column(Integer, default=0)
    all_orders_sum: Mapped[int] = mapped_column(Integer, default=0)
    discount: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, tag={self.tag!r}, phone_number={self.phone_number!r})"


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    data: Mapped[String] = mapped_column(String(50))
    user: Mapped[User] = relationship(back_populates="orders")
    products: Mapped[List["Product"]] = relationship(back_populates="order", cascade="all, delete-orphan",
                                                     lazy='subquery')
    status: Mapped[String] = mapped_column(String(20))
    address: Mapped[String] = mapped_column(String(100), nullable=True)


class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[String] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    order: Mapped[Order] = relationship(back_populates="products")
    size: Mapped[String] = mapped_column(String(3))


class AllProducts(Base):
    __tablename__ = 'all_products'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[String] = mapped_column(String(100))
    description: Mapped[String] = mapped_column(String(1000))
    type: Mapped[String] = mapped_column(String(20))
    price: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"AllProducts(id={self.id}, name={self.name}, type={self.type})"


class Event(Base):
    __tablename__ = 'events'
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[String] = mapped_column(String(200))
