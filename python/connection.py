import socket

import constants
import exceptions
import messages

class Connection:
    __MSG_END = '\a\b'
    __FORMAT = 'utf-8'

    def __init__(self, conn):
        self.conn = conn
        self.robot = None


    def __check_syntax(self, msg):
        if self.__MSG_END not in msg:
            raise exceptions.ServerSyntaxError
        
        return msg[:-2]
    

    def __check_recharge(self, msg):
        # checks if the robot is recharging
        if msg == messages.CLIENT_RECHARGING:
            new_msg = self.get(messages.CLIENT_FULL_POWER_LENGTH)

            if new_msg != messages.CLIENT_FULL_POWER:
                # other message than CLIENT_FULL_POWER is sent
                raise exceptions.ServerLogicError
            
            return 1
        
        return 0
    

    def __to_int(self, num):
        try:
            num = int(num)
        except:
            raise exceptions.ServerSyntaxError
        
        return num
    

    def __get_username_hash(self):
        username = self.get(messages.CLIENT_USERNAME_LENGTH)
        print(username)
        return (sum([ord(char) for char in username]) * 1000) % constants.HASH_SIZE
    

    def __get_key_pair(self):
        key_id = self.__to_int(self.get(messages.CLIENT_KEY_ID_LENGTH))

        # is not an int
        
        # is not in 0 - 5
        if key_id < 0 and key_id > 5:
            raise exceptions.ServerKeyOutOfRange

        return constants.KEY_PAIRS[key_id]
    

    def __get_hashes_from_keys(self, uname_hash, key_pair):
        server_hash = (uname_hash + key_pair[0]) % constants.HASH_SIZE
        client_hash = (uname_hash + key_pair[1]) % constants.HASH_SIZE

        return server_hash, client_hash
    

    def __get_hash_from_client(self):
        hash_from_client = self.__to_int(self.get(messages.CLIENT_CONFIRMATION_LENGHT))

        return hash_from_client

    
    def __confirm_hashes(self, client_hash, hash_from_client):
        if client_hash != hash_from_client:
            self.send(messages.SERVER_LOGIN_FAILED)
            raise exceptions.ServerLoginFailed
        
        self.send(messages.SERVER_OK)

        

    def send(self, msg):
        msg = str(msg)
        msg += self.__MSG_END
        msg = msg.encode()
        self.conn.send(msg)
    

    def get(self, message_length):
        msg = ''

        for i in range(message_length):
            msg += self.conn.recv(1).decode(self.__FORMAT)

            if '\a\b' in msg:
                break
        
        self.__check_syntax(msg)

        if self.__check_recharge(msg):
            # if recharged successfully, continue in communication
            return self.get(message_length)
        
        msg = self.__check_syntax(msg)
        
        return msg
    

    def authenticate(self):
        uname_hash = self.__get_username_hash()

        self.send(messages.SERVER_KEY_REQUEST)
        key_pair = self.__get_key_pair()

        server_hash, client_hash = self.__get_hashes_from_keys(uname_hash, key_pair)

        self.send(server_hash)

        hash_from_client = self.__get_hash_from_client()


        self.__confirm_hashes(client_hash, hash_from_client)