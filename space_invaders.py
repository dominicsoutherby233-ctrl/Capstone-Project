# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 11:10:41 2025

@author: domin
"""
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
import readchar
import math
from time import sleep
import time
import random
from rich.live import Live
from rich.align import Align
from rich import box

console = Console()

alien = '👾'
laser = '[bold red] |'
explosion = '💥'
player = '🚀'

" Making function 'key_hit' for keyboard hit depending on operating system (Windows/MAC)"

try:
    " Windows function "
    import msvcrt

    def key_hit():
        return msvcrt.kbhit()

    os = 'Windows'

except ModuleNotFoundError:
    " MAC function "
    import sys
    import termios
    import tty
    import select

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(fd)

    def key_hit():
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    os = 'MAC'


# def split_col(column, s_o_l):
#     " Splits column into alien portion and laser portion "
#     " If column only contains one of alien/laser, returns whole column "
#     try:
#         first_alien = find_alien(column)
#     except ValueError:
#         return [], column, False
#     try:
#         first_laser = column.index(laser)
#     except ValueError:
#         return column, [], False

#     alien_laser = (first_alien, first_laser)
#     aliens = column[:alien_laser[alien_laser_key[s_o_l][0]] +
#                     alien_laser_key[s_o_l][1]]
#     lasers = column[alien_laser[alien_laser_key[s_o_l][0]] +
#                     alien_laser_key[s_o_l][1]:]

#     return aliens, lasers, True


def update_visuals(new_battle):
    """ Updates space battle visual to show player, ships and laser """
    """ New battle is a list of lists that contain characters only, not \n """
    print_version = []
    for test_index, column in enumerate(new_battle):

        zip_pairs = zip(column, transpose)
        pairs = [''.join((pair)) for pair in zip_pairs]

        " Adding 'stars' background "
        for index, y in enumerate(pairs):

            if y == '\n':
                pairs[index] = stars[test_index][index] + '\n'
            elif y == laser+'\n':
                pairs[index] = stars[test_index][index] + '[bold red]|\n[/]'

        print_version.append(''.join(pairs))

    battlefield = Panel(Columns(print_version, padding=(0, 0), expand=True),
                        padding=(0, 0), width=width,
                        expand=True)

    return Align.center(battlefield)


def player_moves_shoots(shot):
    """ Player moves and shoots once per alien ship movement """
    """ Function returns whether player has shot laser or not """
    if os == 'Windows':
        " Read input for Windows "
        command = readchar.readkey()
    if os == 'MAC':
        " Read input for MAC "
        command = sys.stdin.read(1)

    " Keep track of player position "
    global player_pos
    if command in ('a', 'd'):
        """ Move left or right """

        " Either moving left or right depending on input "
        pm_1 = input_dict[command]

        " 'Moving' player to left or right "
        space_battle[mod(player_pos)][-1] = '  '
        space_battle[mod(player_pos+pm_1)][-1] = player

        " Keeping track of player position so laser occurs in correct position when shooting "
        player_pos = player_pos + pm_1

    if command == 's' and shot == False:
        """ Shoot laser only if player hasn't shot yet """
        if space_battle[player_pos % col_number][-2] in list(alien):
            space_battle[player_pos % col_number][-2] = explosion
        else:
            space_battle[player_pos % col_number][-2] = laser

        " Returns shot = True if player shoots "
        return True

    return shot


""""""


def move(current_game, s_o_l):
    """ Move either aliens down or lasers up depending on 's_o_l' """

    " Initiate new game board "
    new_game = []
    " Key for code efficiency "
    key = move_dict[s_o_l]
    " Retrieving alien or laser emoji "
    s_o_l_emoji = emoji_dict[s_o_l]

    for channel in current_game:
        " Check for game ending and stop function if so "
        if channel[-2] == alien and s_o_l == 'alien':
            global game_end
            game_end = True
            return current_game

        " Remove player 'row' for simplicity "
        temp_channel = channel[:-1]
        " Initiate new game channel "
        new_channel = []
        " Separate aliens/lasers from game channel "
        for index, char in enumerate(temp_channel):
            if char in (s_o_l_emoji, ''):
                new_channel.append(temp_channel[index])
            else:
                new_channel.append('')
        " Move aliens 'down' or lasers 'up' "
        new_channel = rotate(new_channel, key[0])
        " Zip rotated column and initial column to compare "
        zip_col = zip(new_channel, temp_channel)
        " Turn zip object into list "
        joined_column = list(zip_col)
        " Create new channel "
        new_channel = create_col(
            joined_column, not_sol(s_o_l_emoji)) + [channel[-1]]

        new_game.append(new_channel)
    return new_game


def create_col(zip_column, s_o_l):
    """ Compares rotated channel and initial and returns correct result """
    new_col = []
    for entry in zip_column:
        " Entry is in form ('rotated column entry', 'initial column entry ') "
        if set(entry) == {alien, laser}:
            " Alien and laser have 'collided' so replace with 'explosion' emoji and increase player score "
            new_col.append(explosion)
            global player_score
            player_score += 1
        elif s_o_l in entry:
            " Keep emoji that isn't being rotated in new column if it hasn't collided "
            new_col.append(s_o_l)
        elif set(entry) == {explosion, ''}:
            " Keep existing 'explosion' emojis in column "
            new_col.append(explosion)
        else:
            " Append default rotated column entry "
            new_col.append(entry[0])

    return new_col


def rotate(column, reverse=False, cycle=False):
    """ Rotate -> direction or rotate <- direction """
    rotate_dict = {
        True:  {False: [column[-1]], True: [column[0]]},
        False: {False: [''],       True: ['']}
    }

    if reverse == False:
        return rotate_dict[cycle][reverse] + column[:-1]
    if reverse == True:
        return column[1:] + rotate_dict[cycle][reverse]


def not_sol(s_o_l):
    " Returns opposite emoji that is being moved in function 'move()' "
    if s_o_l == laser:
        return alien
    else:
        return laser


""""""


def mod(x):
    return x % col_number


def rotate(column, reverse=False, cycle=False):
    """ Rotate -> direction or rotate <- direction """
    rotate_dict = {
        True:  {False: [column[-1]], True: [column[0]]},
        False: {False: [''],       True: ['']}
    }

    if reverse == False:
        return rotate_dict[cycle][reverse] + column[:-1]
    if reverse == True:
        return column[1:] + rotate_dict[cycle][reverse]


# def find_alien(column):
#     """ Finds last instance of ship in game column """
#     return max([index for index, char in enumerate(column)
#                 if char in alien and char != ''])


def clear_debris(current_game):
    """ Remove explosion emojis """
    for chan_num, channel in enumerate(current_game):

        for explosion in exes(channel):
            current_game[chan_num][explosion] = ''
    return current_game


def exes(column):
    " Finds all instances of explosions in column "
    indices = []
    for index, char in enumerate(column):
        if char == explosion:
            indices.append(index)
    return indices


def add_aliens(current_game, time, run_function):
    " Add alien ships to game "
    if run_function == True:
        if math.sqrt(time)/(spawn_pro*math.sqrt(spawn_mod)) > random.random():
            new_ship_center = random.choice(list(range(1, col_number-1)))

            s_l = len(alien)

            for i, xcoord in enumerate(range(new_ship_center - int((s_l-1)/2), new_ship_center + int((s_l-1)/2+1))):
                current_game[xcoord][0] = alien[i]

    return current_game


def perform_changes(space_battle, functions):
    " Performs all functions in 'functions' to 'space battle' "
    saved_battle = space_battle
    for function in functions:
        space_battle = function(space_battle)

    return space_battle, saved_battle


def timer_and_clean_debris(timer, space_battle):
    """ Clean explosion emojis after certain amount of time """
    if not timer:
        " keep track of debris cleanup outside of function "
        global debris_cleanup
        debris_cleanup = time.time() + 1.5
        timer = True

    " removes explosion emoji after timer "
    if time.time() >= debris_cleanup:

        timer = False
        space_battle, saved_battle = perform_changes(space_battle,
                                                     [lambda x: clear_debris(
                                                         x)]
                                                     )
        if saved_battle != space_battle:
            Live.update(update_visuals(space_battle))

    return timer, space_battle


def create_buttons(player_choice: str):
    """ Creates visual buttons with coloured borders decided by 'colors' """
    output = []
    colors = coloures_borders_dict[player_choice]
    for index, (key, option) in enumerate(player_options):
        output.extend(
            ['[light blue]\n\n' + key,
                show_color_option('\n  ' + option + '\n', colors[index])]
        )
    return output


def show_color_option(text_a_emoji, colour):
    """ Returns Panel of option with colour scheme """
    return Panel(text_a_emoji, border_style=colour, box=box.HEAVY, padding=0)


def ask_player_choice():
    """ Asks for player input repeatedly until input is r, p or s """
    correct_input = False
    while correct_input == False:
        player_choice = readchar.readkey()
        correct_input = player_choice in {'e', 'm', 'h'}
        if correct_input == False:
            console.print('THIS WASN\'T ONE OF THE OPTIONS!!!',
                          style='bold red on white')
    return player_choice


def refresh_menu(player_choice=None):
    """ Print header, prompt and options """
    console.clear()
    console.rule('[bold purple on white]Space Invaders',
                 style='red', characters='❌', align='center')
    buttons = create_buttons(player_choice)

    console.print('\n\n')
    console.print('\n\nChoose your difficulty! \n\
(Enter choice by inputing corresponding letter)\n\n',
                  style='purple on white', justify='center')
    " Print buttons "
    console.print(Align.center(Columns(buttons, align='center', equal=True)))
    console.print('Contols: \n\nw: move left, d: move right, s: shoot',
                  style='white on blue')


def alien_dodge(current_game, run_function):
    """ Make aliens strafe """
    if run_function == True:
        " Only perform if needed "

        " Transform game board into rows instead of columns "
        rows = [list(row) for row in list(zip(*current_game))]

        for index, row in enumerate(rows):
            " Move aliens 30% of time "
            if random.random() < 0.3 and alien in row and laser not in row:
                if random.random() < 0.5:
                    " Move left and right equally "
                    rows[index] = rotate(row, True)
                else:
                    rows[index] = rotate(row)
        return [list(column) for column in zip(*rows)]
    return current_game


def set_up_game():
    """ Initiate all values needed for game """
    " game tick every 1.5 seconds "
    global game_tick_time
    global spawn_mod
    global player_pos
    global transpose
    global colour
    global pad
    global width
    global space_battle
    global col_number
    global height
    global stars
    global player_score

    game_tick_time = 0.1
    " spawn rate moderator  "
    spawn_mod = 500

    " Create base battlefield dimensions"
    height = 45
    col_number = 20
    width = 3*col_number

    " Star background "
    stars = make_stars(col_number, height+1)
    " Transpose vector for printing "
    transpose = ['\n']*height + ['']

    " Initial player score and player position "
    player_score = 0
    player_pos = 0

    " Creating inital game screen "
    space_battle = [['']*height + [player]]
    for column in range(col_number-1):
        space_battle.append(['']*height+['  '])


def make_stars(c_num, height):
    """ Make star background for aesthetic """
    stars = []
    prob = 0.01
    for x in range(c_num):
        stars_col = []
        for y in range(height+1):

            " Different stars to add "
            if random.random() < prob:
                stars_col.append('[grey78]●[/]')
            elif random.random() < prob:
                stars_col.append('[misty_rose1].[/]')
            elif random.random() < prob:
                stars_col.append('[dark_sea_green]•[/]')
            elif random.random() < prob:
                stars_col.append('[cyan1].[/]')
            elif random.random() < prob:
                stars_col.append('[plum2]•[/]')
            else:
                stars_col.append(' ')
        stars.append(stars_col)

    return stars


""" Dictionaries """

emoji_dict = {
    'laser': laser,
    'alien': alien
}
" Dict for player movement "
input_dict = {
    'a': -1,
    'd': 1
}

" Dict for move function efficiency "
move_dict = {
    'alien': [False, 0, -1, 1, 0],
    'laser': [True, 1, 0, 0, -1]
}

" Dict for button colours "
coloures_borders_dict = {'e': ['magenta', 'white', 'white'],
                         'm': ['white', 'magenta', 'white'],
                         'h': ['white', 'white', 'magenta'],
                         None: ['white', 'white', 'white']}

" Dict for difficulty option "
" [inverse ship speed, laser speed, shooting tick, spawn proportion] "
difficulty_dict = {'e': [5, 1, 5, 5], 'm': [5, 1, 7, 4], 'h': [4, 1, 10, 2]}

player_options = [('e:', 'EASY  '), ('m:', 'MEDIUM  '), ('h:', 'HARD  ')]


with console.screen():
    """ Player Menu """
    refresh_menu()

    " Ask for difficulty setting and show selected option "
    difficulty_setting = ask_player_choice()
    refresh_menu(difficulty_setting)
    with console.status('[purple]Setting up game',
                        spinner='point'):
        set_up_game()
        sleep(3)
    " Assigning difficulty values "
    s_s, l_s, shoot_tick, spawn_pro = difficulty_dict[difficulty_setting]

" Dictionary for helpful values "
alien_laser_key = {
    'alien': [1, 0, s_s],
    'laser': [0, 1, l_s]
}

with console.screen():
    """ Game loop """
    console.rule('[bold purple on white]Space Invaders',
                 style='red', characters='❌', align='center')
    with Live(update_visuals(space_battle), refresh_per_second=30) as Live:

        " Timer for 'explosion cleanup' "
        timer = False

        game_end = False
        tick = 0

        while not (game_end):
            " Loop until game ends "

            " start timer to clear debris and/or clear debris "
            timer, space_battle = timer_and_clean_debris(timer, space_battle)

            " Player can shoot once per 5 game ticks "
            if tick % shoot_tick == 0:
                shot = False
            start_time = time.time()

            " Player moves or shoots if input detected "
            while time.time() - start_time < game_tick_time:
                if key_hit():
                    shot = player_moves_shoots(shot)
                    Live.update(update_visuals(space_battle))

            " Game tick and update visuals "
            for item in ['alien', 'laser']:

                if tick % alien_laser_key[item][2] == 0:
                    " Only move lasers/aliens on certain ticks "
                    space_battle, saved_battle = perform_changes(space_battle,
                                                                 [lambda x: move(x, item),
                                                                  lambda x: add_aliens(
                                                                      x, tick, item == 'alien'),
                                                                  lambda x: alien_dodge(x, item == 'alien')]
                                                                 )
                    if game_end == True:
                        " End loop if alien gets through "
                        break
                    if saved_battle != space_battle:
                        " Update visuals if anything has changed "
                        Live.update(update_visuals(space_battle))

            tick += 1

" Only run this if on MAC, not necessary on Windows "
if os == 'MAC':
    " Return terminal settings to default "
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

with console.screen():
    " Player losing screen "
    console.print('\n\n\nYou lost!! You took out {} aliens though!'
                  .format(player_score), justify='center')
    sleep(5)
