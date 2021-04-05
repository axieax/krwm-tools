""" IMPORTS """
import json
import pywintypes
from win32crypt import CryptUnprotectData
from base64 import b64decode
from Crypto.Cipher import AES
from util.general import FORMAT


""" CONSTANTS """
# Encryption key prefix
ENC_KEY_PREFIX = len('DPAPI')

# Encryption format: {prefix}{nonce}{ciphertext}{authentication_tag}
ENC_PREFIX_LEN = len('v10')
ENC_NONCE_LEN = 96 // 8
ENC_TAG_LEN = 128 // 8


def get_encryption_key(browser_path: str) -> str:
    """ Retrieve the encryption / master key for AES encryption and decryption """
    # Extract the encrypted encryption key from local state
    local_state_path = browser_path + '/Local State'
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
            # Decrypts with Window's DPAPI
            return win_decrypt(foo)
        except pywintypes.error:
            # Decrypts with Chromium's new standard
            return chromium_decrypt(foo, encryption_key)
    else:
        return foo


def chromium_decrypt(encrypted_str: bytes, encryption_key: str) -> str:
    """ Decrypt strings encrypted on Chromium version >= 80 """
    # Encryption format: {prefix}{nonce}{ciphertext}{authentication_tag}
    # Extract nonce and encrypted payload
    nonce = encrypted_str[ENC_PREFIX_LEN: ENC_PREFIX_LEN + ENC_NONCE_LEN]
    ciphertext = encrypted_str[ENC_PREFIX_LEN + ENC_NONCE_LEN: -ENC_TAG_LEN]
    # Decipher the AES-encrypted payload with encryption key and nonce
    cipher = AES.new(encryption_key, AES.MODE_GCM, nonce)
    decrypted_payload = cipher.decrypt(ciphertext).decode(FORMAT)
    return decrypted_payload


def win_decrypt(encrypted_str: bytes) -> str:
    """ Decrypts input with Window's DPAPI """
    return CryptUnprotectData(encrypted_str, None, None, None, 0)[1]
