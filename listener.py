import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from secrets import token_urlsafe
from base64 import b64encode, b64decode

data = {
    'sessions': [],
    'private_key': b'',
    'public_key': b'',
}


def initialise_listener() -> None:
    # Generate RSA pairs
    key = RSA.generate(bits=2048)
    # generate private key
    private_key = key.export_key()
    data['private_key'] = private_key
    # generate public key
    public_key = key.publickey().export_key()
    data['public_key'] = public_key

def get_public_key() -> bytes:
    return b64encode(data['public_key']).decode('utf-8')

def decrypt_data(session_id: str, browser_name: str, encrypted_data: str) -> None:
    # check for valid session
    if not valid_session(session_id):
        return
    # decode encrypted data
    encrypted_data = b64decode(encrypted_data)
    # decrypt data
    private_key = RSA.import_key(data['private_key'])
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_data = cipher.decrypt(encrypted_data)
    # decode data
    decoded = json.loads(decrypted_data)
    print(browser_name)
    print(decoded)

def new_session() -> str:
    # generate new session id
    session_id = token_urlsafe()
    data['sessions'].append(session_id)
    return session_id

def valid_session(session_id: str) -> bool:
    return session_id in data['sessions']

def delete_session(session_id: str) -> None:
    if valid_session(session_id):
        data['sessions'].remove(session_id)
