""" IMPORTS """
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode, b64decode


""" CONSTANTS """
FORMAT = 'utf-8'

key_info = {
    'public_key': b'',
    'cipher': None,
}


def initialise_cipher() -> None:
    """ Generates private and public key pairs for encryption and decryption """
    # generate RSA pairs
    key = RSA.generate(bits=2048)
    # generate private key
    private_key = key.export_key()
    # generate public key
    public_key = key.publickey().export_key()
    # prepare cipher
    cipher = PKCS1_OAEP.new(key)
    # update key info
    global key_info
    key_info = {
        'public_key': public_key,
        'cipher': cipher,
    }


def get_public_key() -> bytes:
    """ Returns the base64-encoded public key """
    return b64encode(key_info['public_key'])


def decrypt_data(encrypted_data: str):
    """ Decrypts received data """
    # decrypt data
    cipher = key_info['cipher']
    decrypted_data = cipher.decrypt(encrypted_data)
    # decode data
    return decrypted_data.decode('utf-8')
