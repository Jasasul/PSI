import socket

import constants
import exceptions

CLIENT_USERNAME_LENGTH = 20
CLIENT_KEY_ID_LENGTH = 5
CLIENT_CONFIRMATION_LENGTH = 7

CLIENT_RECHARGING = 'RECHARGING'
CLIENT_FULL_POWER = 'FULL POWER'
CLIENT_FULL_POWER_LENGTH = 12

SERVER_LOGIC_ERROR = '302 LOGIC ERROR'
SERVER_KEY_REQUEST = '107 KEY REQUEST'
SERVER_OK = '200 OK'
SERVER_LOGIN_FAILED = '300 LOGIN FAILED'
SERVER_SYNTAX_ERROR = '301 SYNTAX ERROR'

def send(conn, msg):
    msg += constants.MSG_END
    msg = msg.encode()
    conn.send(msg)


def authenticate(conn):
    uname_hash = get_username_hash(conn)

    server_key_request(conn)
    key_pair = client_key_id(conn)
    print(f'KEY PAIR {key_pair}')

    server_hash = (uname_hash + key_pair[0]) % 65536
    server_confirmation(conn, server_hash)
    client_hash = client_confirmation(conn)
    client_key_hash = (uname_hash + key_pair[1]) % 65536
    print(server_hash, client_hash)

    if client_key_hash == client_hash:
        server_ok(conn)
    else:
        raise exceptions.ServerLoginFailed


def get_username_hash(conn):
    print('GETTING USERNAME')
    username = get_mesasage(conn, CLIENT_USERNAME_LENGTH)
    print(username)

    uname_hash = 0

    for char in username:
        print(ord(char))
        uname_hash += ord(char)

    
    uname_hash *= 1000
    uname_hash %= 65536
    
    
    return uname_hash


def server_key_request(conn):
    print(SERVER_KEY_REQUEST)
    send(conn, SERVER_KEY_REQUEST)


def client_key_id(conn):
    key_id = get_mesasage(conn, CLIENT_KEY_ID_LENGTH)

    try:
        key_id = int(key_id)
    except:
        raise exceptions.ServerSyntaxError


    if key_id < 0 and key_id > 5:
        raise exceptions.ServerKeyOutOfRange
    
    print(f'KEY ID: {key_id}')
    
    return constants.KEY_PAIRS[key_id]


def server_confirmation(conn, server_hash):
    print(f'SENDING HASH: {server_hash}')
    send(conn, str(server_hash))


def client_confirmation(conn):
    print('CLIENT CONFIRMATION')
    client_hash = get_mesasage(conn, CLIENT_CONFIRMATION_LENGTH)

    try:
        client_hash = int(client_hash)
    except:
        raise exceptions.ServerSyntaxError
    
    print(f'CLIENT HASH: {client_hash}')
    print(type(client_hash))
    return client_hash


def server_ok(conn):
    print(SERVER_OK)
    send(conn, SERVER_OK)


def recv(conn, length):
    msg = ''

    for i in range(length):
        msg += conn.recv(1).decode(constants.FORMAT)
        if msg[-2:] == constants.MSG_END:
            print('msg end')
            break
    
    if constants.MSG_END not in msg:
        raise exceptions.ServerSyntaxError
    
    return msg


def get_mesasage(conn, length):
    msg = recv(conn, length)

    if msg == CLIENT_RECHARGING:
        if recv(conn, CLIENT_FULL_POWER_LENGTH) != CLIENT_FULL_POWER:
            raise exceptions.ServerLogicError

        return recv(conn, length)[:-2]
    return msg[:-2]