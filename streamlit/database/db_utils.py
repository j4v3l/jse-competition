import sqlite3
import pandas as pd


def fetch_stock_data():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM stock_participants", conn)
    preferred_stocks = pd.read_sql_query("SELECT symbol FROM preference", conn)
    ordinary_stocks = pd.read_sql_query("SELECT symbol FROM ordinary", conn)
    df = df[df['symbol'].isin(preferred_stocks['symbol'])
            | df['symbol'].isin(ordinary_stocks['symbol'])]
    conn.close()
    return df


def update_closing_price():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch all symbols from the 'stock_participants' table
    cur.execute("SELECT DISTINCT symbol FROM stock_participants")
    symbols = [row[0] for row in cur.fetchall()]

    for symbol in symbols:
        # Fetch the closing price from the 'preference' or 'ordinary' database
        cur.execute(
            f"SELECT closing_price FROM preference WHERE symbol = '{symbol}' UNION SELECT closing_price FROM ordinary WHERE symbol = '{symbol}'"
        )
        closing_price = cur.fetchone()

        if closing_price is not None:
            # Update the 'closing_price' column in the 'stock_participants' table
            cur.execute(
                f"UPDATE stock_participants SET closing_price = {closing_price[0]} WHERE symbol = '{symbol}'"
            )

    conn.commit()
    conn.close()


def insert_stock_data(first_name, last_name, symbol, shares, purchase_price,
                      date_purchased):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        '''INSERT INTO stock_participants (first_name, last_name, symbol, shares, purchase_price, date_purchased) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
        (first_name, last_name, symbol, shares, purchase_price,
         date_purchased))
    conn.commit()
    conn.close()


def add_date_purchased_column():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''ALTER TABLE stock_participants 
           ADD COLUMN date_purchased DATE''')
    conn.commit()
    conn.close()


def insert_admin_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        '''INSERT INTO admin (username, password) 
                   VALUES (?, ?)''', (username, password))
    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('../jse_data.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# Create the 'stock_participants' table
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS stock_participants 
           (first_name TEXT, last_name TEXT, symbol TEXT, shares INTEGER, purchase_price REAL, closing_price REAL)'''
                )
    conn.commit()
    conn.close()


def create_admin_table(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS admin 
           (username TEXT PRIMARY KEY, password TEXT)''')
    cur.execute(
        '''INSERT INTO admin (username, password) 
                   VALUES (?, ?)''', (username, password))
    conn.commit()
    conn.close()


def create_stock_participants_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_participants (
            id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            symbol TEXT NOT NULL,
            shares INTEGER NOT NULL,
            purchase_price REAL NOT NULL,
            date_purchased DATE NOT NULL
        )
    """)
    conn.commit()
    conn.close()
