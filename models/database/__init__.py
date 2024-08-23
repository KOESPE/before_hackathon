from sqlalchemy import Column, ForeignKey
from sqlalchemy import SmallInteger, ARRAY, Integer, BigInteger, String, Date, Time, Boolean, DateTime
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String)
    password = Column(String)
    role = Column(String)
    access_token = Column(String)


class PurchaseHistory(Base):
    __tablename__ = "purchase_history"

    order_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer)
    order_date = Column(DateTime(timezone=True))
    product_quantity = Column(Integer)
    order_sum = Column(Integer)