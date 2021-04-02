import json
import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode, b64decode

PUBLIC_KEY_LEN = 600

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 1234))

# Get public key
public_key = client.recv(PUBLIC_KEY_LEN)
public_key = b64decode(public_key)


def prepare_data(public_key: bytes, data) -> str:
    ''' Encodes and encrypts data to be sent '''
    # Encode data
    encoded_data = json.dumps(data)

    # Encrypt data
    key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(key)
    encrypted_data = cipher.encrypt(encoded_data.encode('utf-8'))

    return b64encode(encrypted_data)


# Test sending data
import time
for i in range(5):
    print(i)
    client.send(prepare_data(public_key, {
        'browser': 'edgy',
        'hello': 'world',
        'id': i,
    }))
    time.sleep(1)
