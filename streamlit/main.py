import streamlit as st
import pandas as pd
from database.db_utils import create_stock_participants_table, get_db_connection, create_table, create_admin_table, insert_admin_user, insert_stock_data, add_date_purchased_column, update_closing_price, fetch_stock_data

# Initialize session state


def login_form():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            st.session_state['login_button'] = True
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT password FROM admin WHERE username = ?",
                        (username, ))
            result = cur.fetchone()
            conn.close()

            if result is not None and result[0] == password:
                st.session_state['logged_in'] = True
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
        else:
            st.session_state['login_button'] = False


def get_symbols(share_type):
    conn = get_db_connection()
    if share_type == "ordinary":
        symbols = pd.read_sql_query("SELECT symbol FROM ordinary",
                                    conn)['symbol'].tolist()
    elif share_type == "preference":
        symbols = pd.read_sql_query("SELECT symbol FROM preference",
                                    conn)['symbol'].tolist()
    conn.close()
    return symbols


def admin_input_form():
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

    with st.form("stock_data_form"):
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
            st.rerun()
    else:
        with st.sidebar:
            login_form()
            if st.session_state.get('login_button', False):
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

    # Drop the 'ID' column
    df = df.drop(columns=['id'])

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
