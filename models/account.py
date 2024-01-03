from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import declarative_base, relationship

from enum import Enum

Base = declarative_base()


class BankAccount(Base):
    __tablename__ = 'bank_accounts'

    id = Column(Integer, primary_key=True)
    account_number = Column(String(20), unique=True, nullable=False)
    balance = Column(Numeric(precision=10, scale=2), default=0)
    account_type = Column(String(20), nullable=False)

    owner_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    owner = relationship('Customer', back_populates='accounts')
    transactions = relationship('Transaction', back_populates='account')

