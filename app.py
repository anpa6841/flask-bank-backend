from flask import Flask, request, redirect, jsonify

from flask_bcrypt import Bcrypt
from flask_cors import CORS

from flask_sqlalchemy import SQLAlchemy
from models import db
from models import Customer, BankAccount, Transaction

from datetime import datetime, timedelta
from itertools import groupby
from pprint import pprint
import random
import time

app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root@localhost/bankdb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def generate_password_hash(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_data = request.get_json()
        name = user_data.get('name')
        email = user_data.get('email')
        username = user_data.get('username')
        password = user_data.get('password')
        hashed_passwd = generate_password_hash(password)
       
        user = Customer(name=name, email=email, username=username, password_hash=hashed_passwd)
        db.session.add(user)
        db.session.commit()

    return jsonify({'success': True})


@app.route("/", methods=['GET'])
def index():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_data = request.get_json()
        username = user_data.get('username')
        password = user_data.get('password')

        user = Customer.query.filter_by(username=username).first()

        if not user:
            return jsonify({'error': 'User not found'})

        else: 
            if bcrypt.check_password_hash(user.password_hash, password):
                return jsonify({'id': user.id,'name': user.name})
            else:
                return jsonify({'error': 'Invalid Credentials', 'customer_id': 0})

    return jsonify({"msg": "login page"})


@app.route("/customer/<int:customer_id>/accounts", methods=['GET'])
def get_customer_accounts(customer_id):
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'message': 'Customer not found'})

    accounts = [
                {
                'account_id': account.id,
                'account_type': account.account_type,
                'account_number': account.account_number,
                'account_balance': account.balance
                } 
                for account in customer.accounts
            ]

    group_by_account_type = [
                        list(group)[0]
                        for key, group in groupby(
                                            accounts,
                                            key=lambda acc: acc['account_type']
                                            )
                        ]

    return jsonify(group_by_account_type)


@app.route("/account/<account_id>/transactions", methods=['GET'])
def get_transactions(account_id):
    # Get optional query parameters for filtering
    min_amount = request.args.get('min_amount', type=float)
    max_amount = request.args.get('max_amount', type=float)

    min_date = request.args.get('min_date', type=lambda x: datetime.strptime(x, '%Y/%m/%d'))
    max_date = request.args.get('max_date', type=lambda x: datetime.strptime(x, '%Y/%m/%d'))


    keyword = request.args.get('keyword', type=str)

    account = BankAccount.query.get(account_id)

    filtered_transactions = []

    if not account:
        return jsonify({'message': 'Account not found'})

    db_transactions = Transaction.query.filter_by(account_id=account_id).all()

    filtered_transactions = [
        {
            'id': transaction.id,
            'amount': transaction.amount,
            'current_balance': transaction.current_balance,
            'type': transaction.transaction_type,
            'desc': transaction.transaction_desc,
            'timestamp': transaction.timestamp
        }
        for transaction in db_transactions
            if (
                (min_date is None or transaction.timestamp >= min_date) and
                (max_date is None or transaction.timestamp <= max_date) and
                (min_amount is None or transaction.amount >= min_amount) and
                (max_amount is None or transaction.amount <= max_amount) and
                (keyword is None or keyword.lower() in transaction.transaction_desc.lower())
            )
    ]

    return jsonify(sorted(filtered_transactions, key=lambda t: t['id'], reverse=True))


@app.route('/transfer', methods=['POST'])
def transfer_amount():
    data = request.get_json()

    from_account_number = data.get('from_account_number')
    to_account_number = data.get('to_account_number')
    amount = float(data.get('amount'))

    # Retrieve accounts from the database
    from_account = BankAccount.query.filter_by(account_number=from_account_number).first()
    to_account = BankAccount.query.filter_by(account_number=to_account_number).first()


    if not from_account or not to_account:
        return jsonify({'message': 'One or both accounts not found'})

    if from_account.balance < amount:
        return jsonify({'message': 'Insufficient funds for transfer'})

    # Perform the transfer
    from_account.balance -= amount
    to_account.balance += amount

    # Record transactions for both accounts
    from_transaction = Transaction(
                                amount=amount,
                                transaction_type='debit',
                                transaction_desc=f"Deposit to Acc. {from_account.account_type.capitalize()}-{to_account_number[-4:]}",
                                current_balance=from_account.balance,
                                account_id=from_account.id
                                )

    to_transaction = Transaction(
                            amount=amount,
                            transaction_type='credit',
                            transaction_desc=f"Deposit from Acc. {to_account.account_type.capitalize()}-{from_account_number[-4:]}",
                            current_balance=to_account.balance,
                            account_id=to_account.id
                            )

    db.session.add_all([from_transaction, to_transaction])
    db.session.commit()

    return jsonify({
                'message': 'Transfer successful',
                'from_account_balance': from_account.balance,
                'to_account_balance': to_account.balance
                })


@app.route("/generate_test_data", methods=['GET'])
def generate_test_data():
    acc_type = ['checking', 'savings']
    customer_name = ['John Mayo', 'Lynn Loring']

    for idx in range(1, 3):
        name = customer_name[idx-1]
        email = f"{'.'.join(name.split(' '))}@test.com"
        username = f'sa-{idx}'
        password = f'sa-{idx}'

        transaction_type_desc = {
                    "debit": ["Online Purchase", "Grocery Shopping", "Utility Bill Payment", "Withdrawal"],
                    "credit": ["Salary Deposit", "Refund", "Bonus"]
                }

        password_hash = generate_password_hash(password)
        customer = Customer(name=name, email=email, username=username, password_hash=password_hash)
        db.session.add(customer)
        db.session.commit()

        for idx in range(2):
            account_number = BankAccount.generate_random_account_number()
            balance = random.uniform(20, 50)
            account = BankAccount(
                            account_number=account_number,
                            account_type=acc_type[idx],
                            account_balance=balance,
                            customer_id=customer.id
                            )

            db.session.add(account)
            db.session.commit()

            transaction = Transaction(
                    amount=balance,
                    transaction_type='credit',
                    transaction_desc='Initial Balance',
                    current_balance=balance,
                    account_id=account.id
                    )

            db.session.add(transaction)

            # Generate random transactions
            for idx in range(5):
                amount = random.uniform(1, 100)

                transaction_type = list(transaction_type_desc.keys())[random.randint(0, 1)]

                transaction_type_count =len(transaction_type_desc[transaction_type]) - 1

                transaction_desc = transaction_type_desc[transaction_type][random.randint(0, transaction_type_count)]

                if transaction_type == 'credit':
                    account.deposit(amount, transaction_desc)

                if transaction_type == 'debit':
                    account.withdraw(amount, transaction_desc)

    # Update time for transactions to past dates for testing purposes
    transactions = Transaction.query.all()

    time_travel = len(transactions)

    for idx, transaction in enumerate(transactions):
        timestamp = datetime.now() - timedelta(days=time_travel)
        transaction.timestamp = timestamp
        if idx % 2 == 0:
            time_travel -= 1

    db.session.commit()
    return jsonify({"success": True})


if __name__ == '__main__':
    app.run(debug=True)
