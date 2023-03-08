import messages
import constants
import exceptions

class Robot:
    def __init__(self, connection):
        self.connection = connection
        self.heading = (None, None)
        self.coords = (None, None)
        self.obstacle = False

        self.determine_heading()
        self.move_to_x_axis()
        self.move_to_y_axis()


    def __update_coords(self):
        msg = self.connection.get(messages.CLIENT_OK_LENGTH)[2:]
        self.coords = tuple([self.connection.to_int(num) for num in msg.split()])
        
        if self.coords == (0, 0):
            raise exceptions.PickUpSecret

        print(f'NEW COORDS: {self.coords}')
    

    def determine_heading(self):
        self.__move()
        first_coords = self.coords

        self.__move()
        second_coords = self.coords

        x = second_coords[0] - first_coords[0]
        y = second_coords[1] - first_coords[1]

        self.heading = (x, y)
        
        print(f'FIRST HEADING: {self.heading}')
    

    def navigate_to_center(self):
        pass
    

    def __turn_to_face_x_axis(self):
        if self.coords[1] < 0:
            while self.heading != constants.NORTH:
                self.__turn_left()
            
        if self.coords[1] > 0:
            while self.heading != constants.SOUTH:
                self.__turn_right()
    

    def move_to_x_axis(self):
        self.__turn_to_face_x_axis()

        while self.coords[1] != 0:
            self.__move()

            if self.obstacle:
                self.__avoid_obstacle()
            

    def __turn_to_face_y_axis(self):
        if self.coords[0] < 0:
            while self.heading != constants.EAST:
                self.__turn_left()
        
        if self.coords[0] > 0:
            while self.heading != constants.WEST:
                self.__turn_right()
    

    def __avoid_obstacle(self):
        self.__turn_left()
        self.__move()
        self.__move()
        self.__turn_right()
        self.__move()
        self.__move()
    

    def move_to_y_axis(self):
        self.__turn_to_face_y_axis()

        while self.coords[0] != 0:
            self.__move()
        

        if self.obstacle:
            self.__avoid_obstacle()
        

    def __move(self):
        last_coords = self.coords
        self.connection.send(messages.SERVER_MOVE)
        self.__update_coords()
        if self.coords == last_coords:
            self.obstacle == True
        else:
            self.obstacle == False


    def __turn_left(self):
        self.connection.send(messages.SERVER_TURN_LEFT)
        
        if self.heading == constants.EAST:
            self.heading = constants.NORTH
        elif self.heading == constants.NORTH:
            self.heading = constants.WEST
        elif self.heading == constants.WEST:
            self.heading = constants.SOUTH
        else:
            self.heading = constants.EAST
        
        self.__update_coords()
        
        print(f'NEW HEADING: {self.heading}')
   

    def __turn_right(self):
        self.connection.send(messages.SERVER_TURN_RIGHT)

        if self.heading == constants.EAST:
            self.heading = constants.SOUTH
        elif self.heading == constants.SOUTH:
            self.heading = constants.WEST
        elif self.heading == constants.WEST:
            self.heading = constants.NORTH
        else:
            self.heading = constants.EAST

        self.__update_coords()

        print(f'NEW HEADING: {self.heading}')