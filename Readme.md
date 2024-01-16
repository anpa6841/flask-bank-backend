## Flask Bank Backend

### Setup 

### Create virtual env and install depdendencies

- python3 -m venv myvenv
- source myvenv/bin/activate
- pip3 install -r requirements.txt

### Create database

- mysql -u root
- create database bankdb

### Flask shell

- export FLASK_APP=app
- flask shell
<pre>

       from app import db
       db.drop_all()
       db.create_all()
       exit()

</pre>

### Launch flask server and make it available on all interfaces.

- flask run --host=0.0.0.0 --port 5001 (to run over http)

To configure https on flask server

- Update the openssl.cnf file with your flask server's ip address

- Create a self-signed certificate

    - openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout private_key.pem -out cert.pem -extensions v3_req -config openssl.cnf

- flask run --host=[IP Address] --port 5001 --cert=[cert.pem] --key=[private_key.pem]

- Copy the cert.pem to the /app/src/main/res/raw/ folder in the Android Project

### Generate test data

- Hit the endpoint `/generate_test_data`

- curl localhost:5001/generate_test_data

{"sucess": true}

### Verify tables created in db with test data

- use bankdb;
- show tables;
- select * from customers;
- describe bank_accounts;


### Run API Tests

- Set the variables is in the BankAPI.postman_collection.json

    - base_url - https://Flask IP:Port
    - customer_id
    - account_id

- Install Newman

    - npm install -g newman

- Run the collection

    - newman run BankAPI.postman_collection.json --insecure


### Test endpoints 

1. Customer Login
<pre>
curl -X POST "localhost:5001/login" -d '{"username": "sa-1", "password": "sa-1"}' -H "Content-Type: application/json" | jq .

{
  "id": 1,
  "name": "sa-1"
}

</pre>


2. Get Customer Accounts  `/customer/<customer_id>/accounts`
<pre>
curl "localhost:5001/customer/1/accounts" | jq . 

[
  {
    "account_balance": 31.606,
    "account_id": 1,
    "account_number": "2506772706",
    "account_type": "checking"
  },
  {
    "account_balance": 27.2923,
    "account_id": 2,
    "account_number": "7724681514",
    "account_type": "savings"
  }
]


</pre>

3. Get Account Transactions `/account/<account_id>/transactions`

<pre>
curl "localhost:5001/account/1/transactions" | jq .


[
  {
    "amount": 91.5208,
    "current_balance": 2.96719,
    "desc": "Utility Bill Payment",
    "id": 4,
    "timestamp": "Fri, 22 Dec 2023 15:28:43 GMT",
    "type": "debit"
  },
  {
    "amount": 73.4854,
    "current_balance": 94.488,
    "desc": "Salary Deposit",
    "id": 3,
    "timestamp": "Thu, 21 Dec 2023 15:28:43 GMT",
    "type": "credit"
  },
  {
    "amount": 16.1776,
    "current_balance": 21.0026,
    "desc": "Withdrawal",
    "id": 2,
    "timestamp": "Thu, 21 Dec 2023 15:28:43 GMT",
    "type": "debit"
  },
  {
    "amount": 37.1802,
    "current_balance": 37.1802,
    "desc": "Initial Balance",
    "id": 1,
    "timestamp": "Wed, 20 Dec 2023 15:28:43 GMT",
    "type": "credit"
  }
]


</pre>

4. Filter Transactions by date, amount or keyword  `/account/<account_id>/transfer_amount?min_date=&max_date=&min_amount=&max_amount=&keyword=`

Filter by amount : 
<pre>
curl "localhost:5001/account/1/transactions?min_amount=35&max_amount=75" | jq .

[
  {
    "amount": 73.4854,
    "current_balance": 94.488,
    "desc": "Salary Deposit",
    "id": 3,
    "timestamp": "Thu, 21 Dec 2023 15:28:43 GMT",
    "type": "credit"
  },
  {
    "amount": 37.1802,
    "current_balance": 37.1802,
    "desc": "Initial Balance",
    "id": 1,
    "timestamp": "Wed, 20 Dec 2023 15:28:43 GMT",
    "type": "credit"
  }
]

### Response contains Transactions within the inclusive range (min_amount, max_amount)
</pre>
Filter by date :
<pre>
curl "localhost:5001/account/2/transactions?min_date=2023/12/21&max_date=2023/12/24" | jq .

[
  {
    "amount": 12.1784,
    "current_balance": 112.278,
    "desc": "Refund",
    "id": 7,
    "timestamp": "Sat, 23 Dec 2023 15:28:43 GMT",
    "type": "credit"
  },
  {
    "amount": 59.3084,
    "current_balance": 100.1,
    "desc": "Salary Deposit",
    "id": 6,
    "timestamp": "Sat, 23 Dec 2023 15:28:43 GMT",
    "type": "credit"
  },
  {
    "amount": 40.7916,
    "current_balance": 40.7916,
    "desc": "Initial Balance",
    "id": 5,
    "timestamp": "Fri, 22 Dec 2023 15:28:43 GMT",
    "type": "credit"
  }
]

### Response contains Transations within the range (min_date, max_date-1)

</pre>

Filter by keyword :
<pre>
curl "localhost:5001/account/2/transactions?keyword=online" | jq .

[
  {
    "amount": 32.6742,
    "current_balance": 94.8978,
    "desc": "Online Purchase",
    "id": 9,
    "timestamp": "Sun, 24 Dec 2023 15:28:43 GMT",
    "type": "debit"
  }
]


</pre>

5. Make Transfer `/transfer`

<pre>
curl -H "Content-Type: application/json" -X POST localhost:5001/transfer -d '{"from_account_number": "6973332720" ,"to_account_number": "3119971489", "amount": "50"}' | jq .


{
  "from_account_balance": 87.693,
  "message": "Transfer successful",
  "to_account_balance": 145.438
}

### Check db records. A transaction entry will be logged for transfer to each account.

`select * from transactions;`

<pre>
| 20 |      50 | debit            | Deposit to Acc. Checking-1489  | 2024-01-08 15:45:18 |          87.693 |          3 |
| 21 |      50 | credit           | Deposit from Acc. Savings-2720 | 2024-01-08 15:45:18 |         145.438 |          4 |
+----+---------+------------------+--------------------------------+---------------------+-----------------+------------+
</pre>


curl -H "Content-Type: application/json" -X POST localhost:5001/transfer -d '{"from_account_number": "1541050381" ,"to_account_number": "3119971489", "amount": "50"}' | jq .


{
  "message": "Insufficient funds for transfer"
}


curl -H "Content-Type: application/json" -X POST localhost:5001/transfer -d '{"from_account_number": "1541050381" ,"to_account_number": "1234", "amount": "50"}' | jq .


{
  "message": "One or both accounts not found"
}

</pre>

6. Return 10 Transactions per page

<pre>

curl -k "https://192.168.0.3:5001/account/1/transactions?keyword=bonus" | jq .[].timestamp

</pre>
