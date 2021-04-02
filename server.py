from flask import Flask, request
from threading import Thread
from listener import initialise_listener, new_session, get_public_key, decrypt_data, delete_session

APP = Flask(__name__)

@APP.route('/', methods=['GET', 'POST', 'DELETE'])
def index():
    if request.method == 'GET':
        session_id = new_session()
        print(session_id)
        print(get_public_key())
        return {
            'public_key': get_public_key(),
            'session_id': session_id,
        }
    elif request.method == 'POST':
        payload = request.json()
        decrypt_data(payload['session_id'], payload['browser_name'], payload['data'])
        return {}
    else:
        session_id = request.args.get('session_id')
        delete_session(session_id)
        return {}

def run():
    APP.run(host='0.0.0.0')

def start_server():
    t = Thread(target=run)
    t.start()

if __name__ == '__main__':
    initialise_listener()
    start_server()
