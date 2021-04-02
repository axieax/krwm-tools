import jwt
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from secrets import token_urlsafe
from base64 import b64encode

JWT_ALGORITHM = 'HS256'

data = {
    'sessions': [],
    'private_key': b'',
    'public_key': b'',
    'jwt_secret': b'',
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
    # generate jwt secret token
    data['jwt_secret'] = token_urlsafe()

def get_public_key() -> bytes:
    return b64encode(data['public_key']).decode('utf-8')

def decrypt_data(session_id: str, browser_name: str, encrypted_data: str) -> None:
    if not valid_session(session_id):
        return

    # decrypt data
    private_key = data['private_key']
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_data = cipher.decrypt(encrypted_data)
    # decide data
    decoded = jwt.decode(decrypted_data, data['secret_key'], algorithms=[JWT_ALGORITHM])
    print(browser_name)
    print(decoded)

def new_session() -> str:
    session_id = token_urlsafe()
    data['sessions'].append(session_id)
    return session_id

def valid_session(session_id: str) -> bool:
    return session_id in data['sessions']

def delete_session(session_id: str) -> None:
    if valid_session(session_id):
        data['sessions'].remove(session_id)

