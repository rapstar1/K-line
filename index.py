from flask import Flask, request, render_template, json
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'aasdfasdfasdgsryukjytresdgjgjhrtd'

# SQLite database connection
mydb = sqlite3.connect('webdata.db', check_same_thread=False)
cursor = mydb.cursor()

# Create the order_book and bitcoin_trade tables if they don't already exist
cursor.execute('''CREATE TABLE IF NOT EXISTS order_book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    order_price REAL,
    order_amount REAL,
    type TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS bitcoin_trade (
    trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_price REAL,
    trade_amount REAL,
    trade_timestamp DATETIME
)''')

mydb.commit()

@app.route('/')
def index():
    return render_template('exchange.html')

@app.route('/order', methods=['POST', 'GET'])
def order():
    user_id = 1  # 示例用户 ID
    price = request.form['price']
    amount = request.form['amount']
    order_type = request.form['type']

    # Insert the order into the SQLite database
    sql = "INSERT INTO order_book (user_id, order_price, order_amount, type) VALUES (?, ?, ?, ?)"
    values = (user_id, price, amount, order_type)
    cursor.execute(sql, values)
    mydb.commit()

    return 'Order placed successfully'

@app.route('/order_list', methods=['GET'])
def order_list():
    order_type = request.args.get('order_type')

    buy_sql = "SELECT user_id, order_price, order_amount, type from order_book WHERE type = 'buy' limit 20"
    sell_sql = "SELECT user_id, order_price, order_amount, type from order_book WHERE type = 'sell' limit 20"

    if order_type == 'buy':
        cursor.execute(buy_sql)
    else:
        cursor.execute(sell_sql)

    rows = cursor.fetchall()
    result = [{'user_id': row[0], 'order_price': float(row[1]), 'order_amount': float(row[2]), 'type': row[3]} for row in rows]

    return json.dumps(result)

@app.route('/trade_list', methods=['GET'])
def trade_list():
    trade_sql = "SELECT trade_id, trade_price, trade_amount, trade_timestamp FROM bitcoin_trade LIMIT 20"
    cursor.execute(trade_sql)
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            'trade_id': row[0],
            'trade_price': float(row[1]),
            'trade_amount': float(row[2]),
            'trade_timestamp': row[3]  # SQLite doesn't support .isoformat() natively
        })

    return json.dumps(result)

@app.route('/trade_period', methods=['GET'])
def trade_period():
    trade_sql = """
    SELECT 
        strftime('%s', MIN(trade_timestamp)) * 1000 AS timestamp,
        (SELECT trade_price FROM bitcoin_trade WHERE trade_timestamp = MIN(bt.trade_timestamp)) AS open,
        (SELECT trade_price FROM bitcoin_trade WHERE trade_timestamp = MAX(bt.trade_timestamp)) AS close,
        MAX(trade_price) AS high,
        MIN(trade_price) AS low,
        SUM(trade_amount) AS volume
    FROM bitcoin_trade bt
    GROUP BY strftime('%Y-%m-%d %H', trade_timestamp)
    ORDER BY timestamp ASC LIMIT 20;
    """
    cursor.execute(trade_sql)
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            'timestamp': int(row[0]),
            'open': float(row[1]),
            'close': float(row[2]),
            'high': float(row[3]),
            'low': float(row[4]),
            'volume': float(row[5])
        })

    return json.dumps(result)

if __name__ == '__main__':
    app.run('0.0.0.0', 8081, debug=False)
