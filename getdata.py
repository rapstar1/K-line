import requests
import mysql.connector
from datetime import datetime, timedelta

# Database connection
db = mysql.connector.connect(
    host="localhost",      # Replace with your DB host
    user="root",           # Replace with your DB username
    password="password",   # Replace with your DB password
    database="webdata"  # Replace with your DB name
)

cursor = db.cursor()

# Function to fetch historical Bitcoin prices
def get_historical_bitcoin_prices(start_date, end_date):
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
    params = {
        'vs_currency': 'usd',
        'from': int(start_date.timestamp()),
        'to': int(end_date.timestamp())
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an error for bad responses
    data = response.json()
    return data['prices']  # Returns a list of [timestamp, price]

# Function to insert the fetched data into the new table
def insert_bitcoin_trade(trade_price, trade_amount, trade_timestamp):
    sql = """
    INSERT INTO bitcoin_trade (trade_price, trade_amount, trade_timestamp)
    VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (trade_price, trade_amount, trade_timestamp))
    db.commit()

# Main function
def main():
    end_date = datetime.now()  # Current date and time
    start_date = end_date - timedelta(days=30)  # Example: last 30 days

    print(f"Fetching Bitcoin prices from {start_date} to {end_date}")
    prices = get_historical_bitcoin_prices(start_date, end_date)

    # Insert each historical price into the database
    for price in prices:
        trade_timestamp = datetime.fromtimestamp(price[0] / 1000)  # Convert from milliseconds
        trade_price = price[1]
        trade_amount = 0.01  # Example trade amount
        print(f"Inserting Bitcoin price: {trade_price}, Trade amount: {trade_amount}, Timestamp: {trade_timestamp}")
        insert_bitcoin_trade(trade_price, trade_amount, trade_timestamp)

if __name__ == '__main__':
    main()
    cursor.close()
    db.close()
