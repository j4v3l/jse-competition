""" This module contains functions for creating and managing a SQLite database.

    Raises:
        ValueError: If there are duplicate column names in the table.

    Returns:
        sqlite3.Connection: The SQLite connection.
"""
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
    # Check for duplicate column names
    if len(column_order) != len(set(column_order)):
        print(f"Duplicate column names in {table_name}: {column_order}")
        raise ValueError("Duplicate column names are not allowed")

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
    create_table(conn, 'indices', [
        'index_name', 'value', 'volume', 'change', 'change_percentage', 'date'
    ])

    create_table(conn, 'ordinary', [
        'symbol', 'last_traded_price', 'closing_price', 'price_change',
        'closing_bid', 'closing_ask', 'volume', 'todays_range', 'week_range',
        'total_prev_yr_div', 'total_current_yr_div', 'date'
    ])

    create_table(conn, 'preference', [
        'symbol', 'last_traded_price', 'closing_price', 'price_change',
        'closing_bid', 'closing_ask', 'volume', 'todays_range', 'week_range',
        'total_prev_yr_div', 'total_current_yr_div', 'date'
    ])


def close_connection(conn):
    """
    Closes the connection to the SQLite database.
    
    Parameters:
        conn (sqlite3.Connection): The SQLite connection.
    """
    conn.close()


def insert_data_into_db(conn, table_name, data, column_order):
    """ Inserts data into the specified table in the SQLite database.

    Args:
        conn (sqlite3.Connection): The SQLite connection.
        table_name (str): The name of the table to insert the data into.
        data (list): The data to insert into the table.
        column_order (list): The order of the columns in the table.
    """
    cursor = conn.cursor()
    for row in data:
        if not isinstance(row, (list, tuple)):
            print(
                f"Warning: skipping non-list/non-tuple value in data for table {table_name}."
            )
            continue
        if row[0] == '':
            row = row[1:]  # Skip the first element if it's an empty string
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
