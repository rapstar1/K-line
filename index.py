from flask import Flask, request, render_template
from flask_cors import CORS
import json

app = Flask(__name__)
app.secret_key = 'aasdfasdfasdgsryukjytresdgjgjhrtd'

import mysql.connector

#CORS(app)

# Create a MySQL connector
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="webdata"
)

# Check if the connection is successful
if mydb.is_connected():
    print("Connected to MySQL database")

# Create a cursor object
    cursor = mydb.cursor()


@app.route('/')
def index():
    return render_template('exchange.html')

@app.route('/order',methods = ['POST', 'GET'])
def order():
    # Add your code here to handle the order route
    user_id = 1
    
    price = request.form['price']
    amount = request.form['amount']
    order_type = request.form['type']
    # Generate SQL string to insert data into "order_book" table
    sql = "INSERT INTO order_book (user_id, order_price, order_amount, type) VALUES (%s, %s, %s, %s)"
    values = (user_id, price, amount,order_type)

    # Execute the SQL query
    cursor.execute(sql, values)

    # Commit the changes to the database
    mydb.commit()

    # Close the cursor and database connection
    return 'Place your order here'

@app.route('/order_list', methods=['GET'])
def order_list():
    order_type = request.args.get('order_type')
    # Add your code here to process the order type
    # ...
    # Generate SQL string to read buy orders from "order_book" table
    #buy_sql = "SELECT user_id,type,order_price,SUM(order_amount) FROM order_book WHERE type = 'buy' GROUP BY order_price ORDER BY order_price DESC LIMIT 20"
    buy_sql = "SELECT user_id, order_price, order_amount, type from order_book WHERE type = 'buy' limit 20;"
    # Generate SQL string to read sell orders from "order_book" table
    sell_sql = "SELECT user_id, order_price, order_amount, type from order_book WHERE type = 'sell' limit 20;"
    if order_type == 'buy':
        # Execute the buy SQL query
        cursor.execute(buy_sql)
    else:
        # Execute the sell SQL query
        cursor.execute(sell_sql)

    # Fetch all the rows from the result
    rows = cursor.fetchall()

    # Convert the rows to a list of dictionaries
    result = []
    for row in rows:
        result.append({
            'user_id': row[0],
            'order_price': float(row[1]),
            'order_amount': float(row[2]),
            'type': row[3]
        })

    # Convert the result to JSON
    json_result = json.dumps(result)

    # Return the JSON response
    return json_result

@app.route('/trade_list', methods=['GET'])
def trade_list():
    trade_sql = "SELECT trade_id,trade_price,trade_amount,trade_timestamp from bitcoin_trade limit 20;"
    cursor.execute(trade_sql)
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            'trade_id': row[0],  # order_id
            'trade_price': float(row[1]),  # order_price is a decimal/float value
            'trade_amount': float(row[2]),  # order_amount is also a decimal/float value
            'trade_timestamp': row[3].isoformat()  # Format datetime to a string (ISO 8601 format)
        })

    # Convert the result to JSON
    json_result = json.dumps(result)

    return json_result

@app.route('/trade_period', methods=['GET'])
def trade_period():
    trade_sql = """
    SELECT
    UNIX_TIMESTAMP(MIN(trade_timestamp)) * 1000 AS timestamp,  -- Timestamp in milliseconds for each minute
    SUBSTRING_INDEX(GROUP_CONCAT(trade_price ORDER BY trade_timestamp ASC), ',', 1) AS open,  -- First price in each minute
    SUBSTRING_INDEX(GROUP_CONCAT(trade_price ORDER BY trade_timestamp DESC), ',', 1) AS close,   -- Last price in each minute
    MAX(trade_price) AS high,                  -- Maximum price in each minute
    MIN(trade_price) AS low,                   -- Minimum price in each minute
    SUM(trade_amount) AS volume                -- Total amount of orders in each minute
FROM
    bitcoin_trade
GROUP BY
    UNIX_TIMESTAMP(trade_timestamp) DIV 36000               -- Group by each minute
ORDER BY
    timestamp ASC limit 20;
"""
    cursor.execute(trade_sql)
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            'timestamp': int(row[0]),  # 'minute' is a datetime, converting it to ISO 8601 format
            'open': float(row[1]),         # 'open' is the first price in each minute
            'close': float(row[2]),        # 'close' is the last price in each minute
            'high': float(row[3]),         # 'high' is the maximum price in each minute
            'low': float(row[4]),          # 'low' is the minimum price in each minute
            'volume': float(row[5])        # 'volume' is the total order amount (sum)
        })

    # Convert the result to JSON
    json_result = json.dumps(result)

    return json_result

if __name__ == '__main__':
    app.run('0.0.0.0', 8080, debug=False)
