import time
from selenium import webdriver
from bs4 import BeautifulSoup


def scrapr_jse_ordinary(url):
    """
    Scrapes ordinary data from the Jamaica Stock Exchange webpage.
    
    Parameters:
        url (str): The webpage URL to scrape.
        
    Returns:
        list: A list of rows, each row containing data about an index.
    """
    options = webdriver.ChromeOptions()
    options.add_argument(
        '--headless')  # Run Chrome in headless mode (without a UI)
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(5)  # Wait for the page to fully load

    page_source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('div', class_='tw-flex tw-flex-col')

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


def scrape_jse_indices(url, chromedriver_path='./chromedriver'):
    """
    Scrapes indices data from the Jamaica Stock Exchange webpage.
    
    Parameters:
        url (str): The webpage URL to scrape.
        chromedriver_path (str): Path to the chromedriver executable.
        
    Returns:
        list: A list of rows, each row containing data about an index.
    """
    options = webdriver.ChromeOptions()
    options.add_argument(
        '--headless')  # Run Chrome in headless mode (without a UI)
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(5)  # Wait for the page to fully load

    page_source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('table', class_='tw-mb-0 tw-divide-y tw-divide-gray-200')

    data = []
    if table:
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            row_data = [col.text.strip() for col in cols]
            data.append(row_data)
    else:
        print(
            "Table not found. Please check the class name and ensure the webpage hasn't changed."
        )

    return data


# scrap preference data
def scrape_jse_preference(url, chromedriver_path='./chromedriver'):
    """
    Scrapes preference data from the Jamaica Stock Exchange webpage.
    
    Parameters:
        url (str): The webpage URL to scrape.
        chromedriver_path (str): Path to the chromedriver executable.
        
    Returns:
        list: A list of rows, each row containing data about an index.
    """
    options = webdriver.ChromeOptions()
    options.add_argument(
        '--headless')  # Run Chrome in headless mode (without a UI)
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(5)  # Wait for the page to fully load

    page_source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(page_source, 'html.parser')
    preference_section = soup.find(
        'h3',
        class_='tw-mt-16 tw-mb-3 tw-text-lg tw-font-bold',
        string='PREFERENCE SHARES')
    data = []
    if preference_section:
        table = preference_section.find_next_sibling(
            'div', class_='tw-flex tw-flex-col')
        if table:
            for row in table.find('tbody').find_all('tr'):
                cols = row.find_all('td')
                row_data = [col.text.strip() for col in cols]
                data.append(row_data)
        else:
            print(
                "Table not found. Please check the class name and ensure the webpage hasn't changed."
            )
    else:
        print(
            "Preference Shares section not found. Please check the heading and ensure the webpage hasn't changed."
        )

    return data


def main(date=None):
    # Base URL of the page to scrape
    BASE_URL = 'https://www.jamstockex.com/trading/trade-quotes/'

    # Construct the URL with the specific date if provided
    URL = f"{BASE_URL}?market=main-market&date={date}" if date else BASE_URL

    # List of scraping functions
    scraping_functions = [
        scrapr_jse_ordinary, scrape_jse_indices, scrape_jse_preference
    ]

    # Loop over the scraping functions
    for scrape in scraping_functions:
        # Scrape the data
        data = scrape(URL)
        # Print the scraped data
        for index_data in data:
            cleaned_data = [item for item in index_data
                            if item]  # Remove empty strings
            print(cleaned_data)


if __name__ == "__main__":
    # Call the main function with a specific date
    main()
