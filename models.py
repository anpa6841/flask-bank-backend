from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import declarative_base, relationship
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

db = SQLAlchemy()


class Customer(db.Model):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    username = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    accounts = relationship('BankAccount', back_populates='customer')


class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'

    id = Column(Integer, primary_key=True)
    account_number = Column(String(20), unique=True, nullable=False)
    balance = Column(db.Float(precision=2), default=0)
    account_type = Column(String(20), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    customer = relationship('Customer', back_populates='accounts')
    transactions = relationship('Transaction', back_populates='account')


    def __init__(self, account_number, account_type, account_balance, customer_id):
        self.account_number = account_number
        self.account_type = account_type
        self.balance = account_balance
        self.customer_id = customer_id


    def deposit(self, amount, transaction_desc):
        self.balance += amount
        transaction = Transaction(amount=amount, transaction_type='credit', transaction_desc=transaction_desc, current_balance=self.balance, account_id=self.id)
        db.session.add(transaction)
        db.session.commit()
        return f'Transaction successful. New balance: {self.balance}'


    def withdraw(self, amount, transaction_desc):
        if amount > self.balance:
            return 'Insufficient funds. Withdrawal unsuccessful.'
        else:
            self.balance -= amount
            transaction = Transaction(amount=amount, transaction_type='debit', transaction_desc=transaction_desc, current_balance=self.balance, account_id=self.id)
            db.session.add(transaction)
            db.session.commit()
            return f'Transaction successful. New balance: {self.balance}'


    def generate_random_account_number():
        return ''.join(str(random.randint(0, 9)) for _ in range(10))


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    amount = Column(db.Float(precision=2), nullable=False)
    transaction_type = Column(String(20), nullable=False)
    transaction_desc = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=db.func.current_timestamp(), nullable=False)
    current_balance = Column(db.Float(precision=2), default=0)
    account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False)
    account = relationship('BankAccount', back_populates='transactions')
