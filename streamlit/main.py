import streamlit as st
import sqlite3
import pandas as pd

# Assuming you have created the 'stock_participants' table as previously described


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


#create_table()


def create_admin_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS admin 
           (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()


#create_admin_table()


def insert_admin_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        '''INSERT INTO admin (username, password) 
                   VALUES (?, ?)''', (username, password))
    conn.commit()
    conn.close()


#insert_admin_user('jager', 'password')

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Admin credentials (Hardcoded for demonstration)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'  # Warning: Hardcoding passwords is not secure for real applications


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


#update_closing_price()


def fetch_stock_data():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM stock_participants", conn)
    preferred_stocks = pd.read_sql_query("SELECT symbol FROM preference", conn)
    ordinary_stocks = pd.read_sql_query("SELECT symbol FROM ordinary", conn)
    df = df[df['symbol'].isin(preferred_stocks['symbol'])
            | df['symbol'].isin(ordinary_stocks['symbol'])]
    conn.close()
    return df


def login_form():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT password FROM admin WHERE username = ?",
                        (username, ))
            result = cur.fetchone()
            conn.close()

            if result is not None and result[0] == password:
                st.session_state['logged_in'] = True
                st.experimental_rerun()  # Add this line
            else:
                st.error("Invalid username or password")


# Call this function once to add the new column to the table
#add_date_purchased_column()


def admin_input_form():

    with st.form("stock_data_form"):
        st.write("### Add New Stock Data")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        share_type = st.selectbox("Share Type", ["ordinary", "preference"])
        conn = get_db_connection()
        if share_type == "ordinary":
            symbols = pd.read_sql_query("SELECT symbol FROM ordinary",
                                        conn)['symbol'].tolist()
        else:
            symbols = pd.read_sql_query("SELECT symbol FROM preference",
                                        conn)['symbol'].tolist()
        conn.close()
        symbol = st.selectbox("Symbol", symbols)
        shares = st.number_input("Shares", min_value=1)
        purchase_price = st.number_input("Purchase Price", min_value=0.01)
        date_purchased = st.date_input("Date Purchased")
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            insert_stock_data(first_name, last_name, symbol, shares,
                              purchase_price, date_purchased)
            st.success("Stock Data Added Successfully")


def layout(df):
    st.title('Stock Competition Leaderboard')

    # Login / Logout
    if st.session_state.get('logged_in', False):
        admin_dashboard(df)  # Call the admin dashboard function
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.experimental_rerun()
    else:
        with st.sidebar:
            if 'login_button' not in st.session_state:
                st.session_state['login_button'] = False
            login_form()
            if st.session_state['login_button']:
                st.session_state['logged_in'] = True

    if not st.session_state.get('logged_in', False):
        normal_dashboard(df)  # Call the normal dashboard function

    return df


def admin_dashboard(df):
    st.write("### Admin Dashboard")
    admin_input_form()


def normal_dashboard(df):
    st.write("### Normal Dashboard")

    # ... rest of your code ...

    # Calculate the height and width based on the size of the dataframe
    height = min(50 + len(df) * 20,
                 1000)  # 25 for the header, 20 per row, max 800
    width = min(100 + len(df.columns) * 500, 1000)  # 100 per column, max 800

    st.dataframe(df, hide_index=True, width=width, height=height)


def main():
    # Fetch the stock data
    df = fetch_stock_data()

    # Call the layout function
    df = layout(df)


if __name__ == "__main__":
    main()
