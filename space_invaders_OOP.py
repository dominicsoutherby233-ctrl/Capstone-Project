from abc import ABC, abstractmethod
import time
import random
import bext
import rich
from time import sleep

alien = '👾'
laser = '[bold red] |'
laser_down = '[bold green] |'
explosion_emoji = '💥'
player_emoji = '🚀'

laser_speed = 5
alien_speed = 1


class MovingObject(ABC):
    """Moving object abstract class for all moving objects in script."""

    def __init__(self,
                 object_emoji: str, health: int) -> MovingObject:
        """Initialise a moving object with direction and speed"""

        self.object_emoji = object_emoji
        self.health = health
        self.timer = 1e20

    def get_hit(self):
        """Loses 1 health and explode if health becomes 0"""

        self.health -= 1

        if self.health == 0:
            self.explode()

    def explode(self):
        """Replace emoji with explosion if health becomes 0"""

        self.object_emoji = explosion_emoji
        self.timer = time.time() + 5  # timer for 'explosion cleanup'


class Ship(MovingObject):
    """Ship object class. Alien ships and player ships both shoot and strafe"""

    def __init__(self, object_emoji: str, health: int):
        """Initializing Ship objects with direction, speed, emoji and health"""

        super().__init__(object_emoji, health)


class Alien(Ship):
    """Alien ships"""

    def __init__(self):
        health = 1
        super().__init__(alien, health)


class Player(Ship):
    """Player moves only side to side"""

    def __init__(self):
        health = 10
        emoji = player_emoji
        super().__init__(emoji, health)

        self.fired = False


class Laser(MovingObject):
    def __init__(self):
        health = 1
        emoji = laser
        super().__init__(emoji, health)


class LaserMovingUp(Laser):
    """Lasers fired from Player"""

    def __init__(self):
        super().__init__()


class LaserMovingDown(Laser):
    """Lasers fired from Aliens"""

    def __init__(self):
        super().__init__()
        self.object_emoji = laser_down


class GameBoardChannel:
    """Parent class for board row and board column"""

    def __init__(self, elements: list[MovingObject | str]) -> GameBoardChannel:

        if any(isinstance(element, int) for element in elements):
            raise TypeError(f"{elements} contains a number")

        self.elements = elements

    def move_element_over(self, element: MovingObject, direction: str, danger_object: type, new_index):
        """Move specified element over to the left or right"""

        score = 0
        index = self.elements.index(element)

        if new_index > len(self.elements)-1 or new_index < 0 or\
                (type(self.elements[new_index]) == type(element) and self.elements[new_index].health > 0):
            return score

        if self.collision_occurs(element, danger_object, direction) is True:
            # Laser is 'destroyed' and Ship loses health
            element = self.return_ship(element, self.elements[new_index])
            element.get_hit()

            if isinstance(element, Alien):
                score = 1

        self.elements[new_index] = element
        self.elements[index] = '  '

        return score

    def return_ship(self, element_1: MovingObject, element_2: MovingObject):
        """Returns the Ship element out of two and Player element over Alien"""

        for element in [element_1, element_2]:
            if isinstance(element, Player):
                return element

        if isinstance(element_1, Ship):
            return element_1
        return element_2

    def collides_with(self):
        """Returns class type that 'collides' with object type given"""

        return MovingObject

    def strafe(self, objects_moving: list[MovingObject], objects_type: type, direction_moving: str):
        """Strafe objects moving in direction in specific channel"""

        collision_object = self.collides_with()

        score = 0

        for object in self.loop_through(objects_moving, direction_moving):

            new_element_index = self.new_index(
                self.elements.index(object), direction_moving)

            scoring = self.move_element_over(
                object, direction_moving, collision_object, new_element_index)

            score += scoring

        return score

    def loop_through(self, objects: list[MovingObject], direction: str):
        """Loop 'left to right' if objects moving up or left
        Loop 'right to left' if objects moving down or right"""

        if direction == 'left' or direction == 'up':
            return objects
        if direction == 'right' or direction == 'down':
            return reversed(objects)

    def new_index(self, element_index: int, direction_moving: str):
        """Returns new index of a moving object"""

        index_differences = {True: 1, False: -1}

        index_difference = index_differences[direction_moving in {
            'down', 'right'}]

        return element_index + index_difference

    def collision_occurs(self, element: MovingObject | str, collision_object: MovingObject, direction: str):
        """Returns whether element moving will hit another object"""

        element_index = self.elements.index(element)

        if direction in {'up', 'left'}:
            index_dir = -1
        if direction in {'down', 'right'}:
            index_dir = +1

        if isinstance(self.elements[element_index+index_dir], collision_object):
            return self.elements[element_index+index_dir].health > 0


class GameBoardColumn(GameBoardChannel):
    """Class for individual game board channels"""

    def __init__(self, elements: list[MovingObject | str]) -> GameBoardColumn:

        super().__init__(elements)

    def move_aliens_down(self):
        """Move all Alien objects down the game board"""

        aliens_in_col = [element for element in self.elements if isinstance(
            element, Alien) and element.health > 0]

        aliens_being_moved = [element for element in self.elements[:-1] if isinstance(
            #avoid index error if alien is last element
            element, Alien) and element.health > 0]

        if len(aliens_being_moved) != len(aliens_in_col):
            self.elements[-1] = '  '

        score = self.strafe(aliens_being_moved, Alien, 'down')

        if random.random() < 0.1:
            self.elements[0] = Alien()

        return score

    def move_lasers_up(self):
        """Move all LaserMovingUp objects up the game board"""

        lasers_in_col = [element for element in self.elements if isinstance(
            element, LaserMovingUp) and element.health > 0]

        lasers_being_moved = [element for element in self.elements[1:] if isinstance(
            # avoid index error if laser is first element
            element, LaserMovingUp) and element.health > 0]

        if lasers_in_col == []:
            return 0

        if len(lasers_being_moved) != len(lasers_in_col):
            self.elements[0] = '  '

        score = self.strafe(lasers_being_moved, LaserMovingUp, 'up')

        return score

    def move_lasers_down(self):
        """Move all LaserMovingDown objects up the game board"""

        lasers_in_col = [element for element in self.elements if isinstance(
            element, LaserMovingDown) and element.health > 0]

        lasers_being_moved = [element for element in self.elements[:-1] if isinstance(
            # avoid index error if laser is last element
            element, LaserMovingDown) and element.health > 0]

        if lasers_in_col == []:
            return 0

        if len(lasers_being_moved) != len(lasers_in_col):
            self.elements[-1] = '  '

        score = self.strafe(lasers_being_moved, LaserMovingDown, 'down')

        return score

    def alien_shoots(self):
        """First Alien in column shoots a laser"""

        aliens_in_col = [element for element in reversed(self.elements[:-1])
                         if isinstance(element, Alien) and
                         element.health > 0]

        for alien in aliens_in_col:

            index = self.elements.index(alien)

            if isinstance(self.elements[index+1], MovingObject):

                self.elements[index+1].get_hit()
                return

            self.elements[index+1] = LaserMovingDown()
            return

        return

    def player_gets_hit(self) -> None:
        """Function is called when entry before player is an Alien and alien_shoots() has been called."""

        self.elements[-1].get_hit()

    def clean_up_explosions(self):
        """Remove objects with explosion emoji if timer has completed"""

        explosions = [element for element in self.elements
                      if isinstance(element, MovingObject) and
                      element.object_emoji == explosion_emoji]

        for explosion in explosions:

            if explosion.timer <= time.time():
                index = self.elements.index(explosion)
                self.elements[index] = '  '

    def player_shoots(self):
        """creates an instance of LaserMovingUp object above player or
        'hit' element directly ahead of Player"""

        score = 0

        player = self.elements[-1]
        element_above_player = self.elements[-2]

        if player.fired is True:
            return score

        if isinstance(element_above_player, (LaserMovingDown, Alien)):

            element_above_player.get_hit()
            player.fired = True

            if isinstance(element_above_player, Alien):
                score = 1

        self.elements[-2] = LaserMovingUp()
        self.elements[-1].fired = True

        return score

    def player_can_shoot(self):
        """change player instance 'fired' attribute to False"""

        self.elements[-1].fired = False

    def contains_player(self):
        """Returns if column contains player"""

        return any(isinstance(element, Player) for element in self.elements)

    def player_loses(self):
        if isinstance(self.elements[-1], Player) and self.elements[-1].health < 1 or\
                isinstance(self.elements[-1], Alien):
            return True
        return False


class GameBoardRow(GameBoardChannel):
    """Class for individual game board rows"""

    def __init__(self, elements: list[MovingObject | str]) -> GameBoardRow:

        super().__init__(elements)

    def aliens_strafe(self) -> None:
        """Aliens strafe (1-strafe_prob)% of the time"""

        strafe_prob = 0.3

        if random.random() < 1 - strafe_prob:
            return 0

        # collect all aliens that aren't destroyed
        aliens = [
            element for element in self.elements if isinstance(element, Alien) and element.health > 0]

        if len(aliens) == 0:
            return 0

        # equal probability of left or right strafe
        if random.random() < 0.5:
            strafe_dir = 'left'
        else:
            strafe_dir = 'right'

        score = self.strafe(aliens, Alien, strafe_dir)

        return score

    def player_moves(self, player_input):
        """Player moves left or right"""

        players = [
            element for element in self.elements if isinstance(element, Player)]

        if player_input == 'd':
            player_strafe = 'right'

        if player_input == 'a':
            player_strafe = 'left'

        score = self.strafe(players, Player, player_strafe)

        return score

    def print(self):
        """print each element in the row"""

        for element in self.elements:
            if isinstance(element, str):
                rich.print(element, end='')
            else:
                rich.print(element.object_emoji, end='')


class GameBoard:
    """Class for full game board"""

    def __init__(self, columns: list[GameBoardColumn]):
        self.columns = columns
        self.score = 0

    def player_moves(self, player_input: str):
        """Player move left or right depending on input (a or d)"""

        game_board_rows = self.convert_to_rows()
        self.score += game_board_rows[-1].player_moves(player_input)

        self.columns = self.convert_to_columns(game_board_rows)

        self.print()

        pass

    def player_shoots(self):
        """Player ships shoot"""

        columns_with_players = [
            col for col in self.columns if col.contains_player() is True]

        for column in columns_with_players:
            self.score += column.player_shoots()

        self.print()

    def aliens_shoot(self):
        """Alien ships shoot"""

        for column in self.columns:
            column.alien_shoots()

        self.print()

    def move_lasers_up(self):
        """Move lasers either up and down"""

        for column in self.columns:
            self.score += column.move_lasers_up()

        self.print()

    def move_lasers_down(self):
        """Move lasers either up and down"""

        for column in self.columns:
            self.score += column.move_lasers_down()

        self.print()

    def move_aliens_down(self):
        """Move aliens down"""

        for column in self.columns:
            self.score += column.move_aliens_down()

        self.print()

    def aliens_strafe(self):
        """Alien objects strafe left or right across the board"""

        game_board_rows = self.convert_to_rows()  # convert game board to rows

        for row in game_board_rows:

            self.score += row.aliens_strafe()  # strafe aliens in each row separately

        # convert back into game board columns
        self.columns = self.convert_to_columns(game_board_rows)

        self.print()

    def player_can_shoot(self):
        """Changes player 'fired' attribute to False"""

        columns_with_players = [
            col for col in self.columns if col.contains_player() is True]

        for column in columns_with_players:
            column.player_can_shoot()

    def convert_to_columns(self: GameBoard, game_board_rows: list[GameBoardRow]) -> list[GameBoardColumn]:
        """Create game board from list of rows instead of columns"""

        row_elements = [row.elements for row in game_board_rows]

        return [GameBoardColumn(list(row)) for row in (list(zip(*row_elements)))]

    def convert_to_rows(self: GameBoard) -> list[GameBoardRow]:
        """Convert game board into list of 'rows' for strafing elements"""

        column_elements = [column.elements for column in self.columns]

        return [GameBoardRow(list(row)) for row in (list(zip(*column_elements)))]

    def clean_up_explosions(self):
        """Remove objects with 'explosion' emoji"""

        for column in self.columns:
            column.clean_up_explosions()

        self.print()

    def get_score(self):

        return self.score

    def player_loses(self) -> bool:
        """Returns is player has lost in any game column"""
        for col in self.columns:

            if col.player_loses():
                return True

        return False

    def print(self):
        """Print the gameboard"""

        bext.clear()
        rows = self.convert_to_rows()

        for index, row in enumerate(rows):

            bext.goto(0, index)
            row.print()


if __name__ == "__main__":

    bext.clear()
    bext.hide_cursor()
    bext.show_cursor()

    alien_1 = Alien(4, [1, 1])
    alien_1.strafe = 'down'
    alien_2 = Alien(4, [1, 1])
    alien_2.strafe = 'down'
    player = Player(0)
    player_2 = Player(0)
    player_2.object_emoji = 't'
    laser_1 = LaserMovingDown([0, 0])
    laser_1_2 = LaserMovingDown([0, 0])
    laser_2 = LaserMovingUp([0, 0])
    laser_3 = LaserMovingUp([0, 0])
    laser_4 = LaserMovingUp([0, 0])
    laser_5 = LaserMovingUp([0, 0])

    test_column_1 = GameBoardColumn(
        0, [laser_2, '  ', '  ', alien_1, '  ', laser_3, '  ', '  ', laser_1])
    test_column_2 = GameBoardColumn(
        1, [alien_2, '  ', '  ', laser_1_2, '  ', '  ', '  ', '  ', player])
    test_column_3 = GameBoardColumn(
        2, [laser_4, '  ', '  ', '  ', '  ', '  ', '  ', '  ', player_2])
    test_column_4 = GameBoardColumn(
        1, ['  ', '  ', '  ', laser_5, '  ', '  ', '  ', '  ', '  '])

    game_board = GameBoard([test_column_1, test_column_2,
                            test_column_3, test_column_4])

    game_board.print()
    print(player.health)
    while True:
        test_input = input()

        if test_input == 'ma':
            game_board.move_aliens_down()
            game_board.print()

        if test_input == 'mld':
            game_board.move_lasers_down()
            game_board.print()

        if test_input == 'as':
            game_board.aliens_shoot()
            game_board.print()

        if test_input == 'sa':
            game_board.aliens_strafe()
            game_board.print()

        if test_input == 'mlu':
            game_board.move_lasers_up()
            game_board.print()

        if test_input == 'cleanup':
            game_board.clean_up_explosions()
            game_board.print()

        if test_input == 's':
            game_board.player_shoots()
            game_board.print()

        if test_input == 'a':
            game_board.player_moves('a')
            game_board.print()

        if test_input == 'd':
            game_board.player_moves('d')
            game_board.print()

        print(player.health)
