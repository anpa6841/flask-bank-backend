from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    accounts = relationship('BankAccount', back_populates='owner')
