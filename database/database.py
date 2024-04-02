import sqlite3


def create_connection():
    """
    Creates a new connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: The SQLite connection.
    """
    conn = sqlite3.connect('jse_data.db')
    create_tables(conn)
    return conn


def create_table(conn, table_name, column_order):
    """
    Creates a new table in the SQLite database with the specified columns.

    Parameters:
        conn (sqlite3.Connection): The SQLite connection.
        table_name (str): The name of the table to create.
        column_order (list): The names of the columns in the table.
    """
    cursor = conn.cursor()
    columns = ', '.join(f'"{col}" TEXT' for col in column_order)
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
    conn.commit()


def create_tables(conn):
    """
    Creates the necessary tables in the SQLite database.
    
    Parameters:
        conn (sqlite3.Connection): The SQLite connection.
    """
    create_table(
        conn, 'indices', """
        index_name TEXT,
        value REAL,
        volume INTEGER,
        change REAL,
        change_percentage REAL,
        date TEXT
    """)

    create_table(
        conn, 'ordinary', """
        symbol TEXT,
        last_traded_price REAL,
        closing_price REAL,
        price_change REAL,
        closing_bid REAL,
        closing_ask REAL,
        volume INTEGER,
        todays_range TEXT,
        week_range TEXT,
        total_prev_yr_div REAL,
        total_current_yr_div REAL,
        date TEXT
    """)

    create_table(
        conn, 'preference', """
        symbol TEXT,
        last_traded_price REAL,
        closing_price REAL,
        price_change REAL,
        closing_bid REAL,
        closing_ask REAL,
        volume INTEGER,
        todays_range TEXT,
        week_range TEXT,
        total_prev_yr_div REAL,
        total_current_yr_div REAL,
        date TEXT
    """)


def close_connection(conn):
    """
    Closes the connection to the SQLite database.
    
    Parameters:
        conn (sqlite3.Connection): The SQLite connection.
    """
    conn.close()


def insert_data_into_db(conn, table_name, data, column_order):
    """
    Inserts the given data into the specified table in the SQLite database.

    Parameters:
        conn (sqlite3.Connection): The SQLite connection.
        table_name (str): The name of the table where the data will be inserted.
        data (list): The data to insert. This should be a list of tuples,
                     where each tuple represents a row of data.
        column_order (list): The order of the columns in the table.
    """
    cursor = conn.cursor()
    for row in data:
        if not isinstance(row, (list, tuple)):
            print(
                f"Warning: skipping non-list/non-tuple value in data for table {table_name}."
            )
            continue
        row = list(row) + [None] * (len(column_order) - len(row)
                                    )  # Add None for missing values
        placeholders = ', '.join('?' * len(row))
        columns = ', '.join(
            f'"{col}"'
            for col in column_order)  # Add double quotes around column names
        cursor.execute(
            f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
            row)
    conn.commit()
