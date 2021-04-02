import json
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode, b64decode

SERVER_URL = ''


def prepare_data(public_key: bytes, data) -> str:
    # encode data
    encoded_data = json.dumps(data)

    # encrypt data
    key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(key)

    encrypted_data = cipher.encrypt(encoded_data.encode('utf-8'))
    encrypted_data = b64encode(encrypted_data).decode('utf-8')

    return encrypted_data



# GET public key and session id
response = requests.get(SERVER_URL)
payload = response.json()
public_key = payload['public_key']
public_key = b64decode(public_key.encode('utf-8'))
session_id = payload['session_id']


# Post data
requests.post(SERVER_URL, json={
    'session_id': session_id,
    'browser_name': 'Chrome',
    'data': prepare_data(public_key, {
        'hello': 'world',
    }),
})

requests.post(SERVER_URL, json={
    'session_id': session_id,
    'browser_name': 'Edgy',
    'data': prepare_data(public_key, {
        'uwu': 'owo',
    }),
})

# Delete session
requests.delete(SERVER_URL, json={
    'session_id': session_id,
})
