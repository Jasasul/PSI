import messages

class Robot:
    def __init__(self, connection):
        self.connection = connection
        self.heading = (None, None)
        self.coords = (None, None)

        self.__move()
        self.__move()
    

    def __update_coords(self):
        msg = self.connection.get(messages.CLIENT_OK_LENGTH)[2:]
        self.coords = tuple([self.connection.to_int(num) for num in msg.split()])
        x, y = msg.split()
        x = self.connection.to_int(x)
        y = self.connection.to_int(y)
        print(self.coords)


    def __move(self):
        self.connection.send(messages.SERVER_MOVE)
        self.__update_coords()

    def __turn_right(self):
        self.connection.send(messages.SERVER_TURN_RIGHT)
        self.__update_coords()
   
    def __turn_left(self):
        self.connection.send(messages.SERVER_TURN_LEFT)
        self.__update_coords()