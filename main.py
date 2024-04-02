"""
    Scrape the Jamaica Stock Exchange (JSE) website for trading data.

    Returns:
        sqlite3.Connection: The SQLite connection.
"""
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import database.database


def scrape_jse_ordinary(soup):
    """_summary_

    Args:
        soup (_type_): _description_

    Returns:
        _type_: _description_
    """
    ordinary_section = soup.find(
        'h3',
        class_='tw-mt-16 tw-mb-3 tw-text-lg tw-font-bold',
        string='ORDINARY SHARES')
    if ordinary_section:
        table = ordinary_section.find_next_sibling(
            'div', class_='tw-flex tw-flex-col')
        return extract_data_from_table(table)
    else:
        print(
            "Ordinary Shares section not found. Please check the heading and ensure the webpage hasn't changed."
        )
        return []


def scrape_jse_indices(soup):
    """_summary_

    Args:
        soup (_type_): _description_

    Returns:
        _type_: _description_
    """
    indices_section = soup.find(
        'div', class_='tw-inline-block tw-min-w-full tw-py-2 tw-align-middle')
    if indices_section:
        table = indices_section.find(
            'table', class_='tw-mb-0 tw-divide-y tw-divide-gray-200')
        return extract_data_from_table(table)
    else:
        print(
            "Indices section not found. Please check the heading and ensure the webpage hasn't changed."
        )
        return []


def scrape_jse_preference(soup):
    """_summary_

    Args:
        soup (_type_): _description_

    Returns:
        _type_: _description_
    """
    preference_section = soup.find(
        'h3',
        class_='tw-mt-16 tw-mb-3 tw-text-lg tw-font-bold',
        string='PREFERENCE SHARES')
    if preference_section:
        table = preference_section.find_next_sibling(
            'div', class_='tw-flex tw-flex-col')
        return extract_data_from_table(table)

    print(
        "Preference Shares section not found. Please check the heading and ensure the webpage hasn't changed."
    )
    return []


def extract_data_from_table(table):
    """_summary_

    Args:
        table (_type_): _description_

    Returns:
        _type_: _description_
    """
    data = []
    if table:
        tbody = table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr'):
                cols = row.find_all('td')
                row_data = [col.text.strip() for col in cols]
                data.append(row_data)
        else:
            print(
                "Tbody not found. Please check the class name and ensure the webpage hasn't changed."
            )
    else:
        print(
            "Table not found. Please check the class name and ensure the webpage hasn't changed."
        )
    return data


def clean_data(row_data, table_name):
    """_summary_

    Args:
        row_data (_type_): _description_
        table_name (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Define the order of the columns
    if table_name == 'indices':
        column_order = [
            'index_name', 'value', 'volume', 'change', 'change_percentage',
            'date'
        ]
    else:
        column_order = [
            'symbol', 'last_traded_price', 'closing_price', 'price_change',
            'closing_bid', 'closing_ask', 'volume', 'todays_range',
            'week_range', 'total_prev_yr_div', 'total_current_yr_div', 'date'
        ]

    # Initialize cleaned_data as a list of None with the same length as column_order
    cleaned_data = [None] * len(column_order)

    # Check if row_data is a dictionary
    if isinstance(row_data, dict):
        # Extract and order the data from the dictionaries
        for i, column in enumerate(column_order):
            cleaned_data[i] = row_data.get(column)
    elif isinstance(row_data, list):
        # If row_data is a list, copy the values to cleaned_data
        cleaned_data[:len(row_data)] = row_data
    else:
        # If row_data is neither a dictionary nor a list, return an empty list
        return []

    return cleaned_data


def main(date=None):
    """_summary_

    Args:
        date (_type_, optional): _description_. Defaults to None.
    """
    # Base URL of the page to scrape
    BASE_URL = 'https://www.jamstockex.com/trading/trade-quotes/'

    # Construct the URL with the specific date if provided
    URL = f"{BASE_URL}?market=main-market&date={date}" if date else BASE_URL

    options = webdriver.ChromeOptions()
    options.add_argument(
        '--headless')  # Run Chrome in headless mode (without a UI)
    driver = webdriver.Chrome(options=options)

    driver.get(URL)
    time.sleep(5)  # Wait for the page to fully load

    page_source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(page_source, 'html.parser')

    # Connect to the SQLite database
    conn = database.database.create_connection()

    # List of scraping functions, corresponding table names, and column orders
    scraping_functions_and_tables = [
        (scrape_jse_indices, 'indices', [
            'index_name', 'value', 'volume', 'change', 'change_percentage',
            'date'
        ]),
        (scrape_jse_ordinary, 'ordinary', [
            'symbol', 'last_traded_price', 'closing_price', 'price_change',
            'closing_bid', 'closing_ask', 'volume', 'todays_range',
            'week_range', 'total_prev_yr_div', 'total_current_yr_div', 'date'
        ]),
        (scrape_jse_preference, 'preference', [
            'symbol', 'last_traded_price', 'closing_price', 'price_change',
            'closing_bid', 'closing_ask', 'volume', 'todays_range',
            'week_range', 'total_prev_yr_div', 'total_current_yr_div', 'date'
        ])
    ]

    # Loop over the scraping functions, table names, and column orders
    for scrape, table_name, column_order in scraping_functions_and_tables:
        # Scrape the data
        data = scrape(soup)

        # Print out the data before it's cleaned
        print(f"Raw data for {table_name}: {data}")

        # Insert the scraped data into the database
        for row_data in data:
            cleaned_data = clean_data(row_data, table_name)
            if cleaned_data:  # Ensure cleaned_data is not an empty list
                database.database.insert_data_into_db(conn, table_name,
                                                      [cleaned_data],
                                                      column_order)


if __name__ == "__main__":
    # Call the main function with a specific date
    main()
