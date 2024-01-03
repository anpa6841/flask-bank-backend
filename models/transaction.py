from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import declarative_base, relationship

from enum import Enum
from datetime import datetime

Base = declarative_base()


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    transaction_type = Column(String(20), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False)
    account = relationship('BankAccount', back_populates='transactions')

