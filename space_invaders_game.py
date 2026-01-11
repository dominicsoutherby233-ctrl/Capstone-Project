from space_invaders_OOP import MovingObject, LaserMovingDown, LaserMovingUp, Player, Laser, Alien, GameBoard, GameBoardChannel, GameBoardRow, GameBoardColumn

import time
import random
import bext

import sys
import termios
import tty
import select

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(fd)

def key_hit():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

alien = '👾'
laser = '[bold red] |'
laser_down = '[bold green] |'
explosion_emoji = '💥'
player_emoji = '🚀'

laser_speed = 5
alien_speed = 1

bext.hide_cursor()

def set_up_game(col_nums, row_nums):

    game_cols = []

    for col in range(col_nums):

        game_cols.append(GameBoardColumn(["  "]*row_nums))

    game_cols[0].elements[-1] = Player()

    game = GameBoard(game_cols)

    return game

def player_inputs():

    game.player_can_shoot()

    current = time.time()

    while time.time() - current < 0.1:
        if key_hit():
            input = sys.stdin.read(1)

            if input in {'a', 'd'}:
                game.player_moves(input)
            elif input == 's':
                game.player_shoots()

game = set_up_game(20,40)

game.print()

while game.player_loses() is False:

    if random.random()<0.1:
        game.aliens_shoot()

    for tick in range(laser_speed):
        player_inputs()
        game.move_lasers_up()
        game.move_lasers_down()

    for tick in range(alien_speed):
        player_inputs()
        game.move_aliens_down()

    game.aliens_strafe()

    game.clean_up_explosions()

print(f'{game.get_score()} aliens were stopped!')

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

bext.show_cursor()
