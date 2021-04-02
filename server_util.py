import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode, b64decode

key_info = {
    'private_key': b'',
    'public_key': b'',
}


def initialise_listener() -> None:
    ''' Generates private and public keys for encryption/decryption '''
    # Generate RSA pairs
    key = RSA.generate(bits=2048)
    # generate private key
    private_key = key.export_key()
    key_info['private_key'] = private_key
    # generate public key
    public_key = key.publickey().export_key()
    key_info['public_key'] = public_key


def get_public_key() -> bytes:
    ''' Returns the base64-encoded public key '''
    return b64encode(key_info['public_key'])


def decrypt_data(encrypted_data: str):
    ''' Decrypts received data '''
    # decode encrypted data
    encrypted_data = b64decode(encrypted_data)
    # decrypt data
    private_key = RSA.import_key(key_info['private_key'])
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_data = cipher.decrypt(encrypted_data)
    # decode data
    decoded = json.loads(decrypted_data)
    # TODO: save data
    return decoded
