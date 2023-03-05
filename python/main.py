import socket
import threading

import constants
import messages


def handle_client(conn, addr):
    print(f'{addr} connected')
    
    try:
        messages.authenticate(conn)
    except Exception as e:
        pass



if __name__ == "__main__":
    all_threads = []
    print('Starting server')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((constants.IP, constants.PORT))
    server.listen()
    print(f'Listening at {constants.IP} on port {constants.PORT}')


    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        all_threads.append(thread)
        print(f'Active connections: {threading.active_count() - 1}')
