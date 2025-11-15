# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 11:10:41 2025

@author: domin
"""
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
import readchar
import msvcrt
import math
from time import sleep
import time
import random
from rich.panel import Panel
from rich.live import Live
from rich.align import Align
from rich import box

console = Console()

alien = '👾'
laser = '[bold red] |'
explosion = '💥'
player = '🚀'



def split_col(column,s_o_l):
    try:
        first_ship = find_ship(column)
    except ValueError:
        return [], column, False
    try:
        first_laser = column.index(laser)
    except ValueError:
        return column, [], False
    
    ship_laser = (first_ship, first_laser)
    ships =  column[ :ship_laser[ s_c_d[s_o_l][0] ] + s_c_d[s_o_l][1]  ]
    lasers = column[  ship_laser[ s_c_d[s_o_l][0] ] + s_c_d[s_o_l][1]: ]
    
    return ships, lasers, True

def update_visuals(new_battle):
    " Updates space battle visual to show player, ships and laser "
    " New battle is a list of lists that contain characters only, not \n"
    print_version = []
    for test_index, column in enumerate(new_battle):
        
        zip_pairs = zip(column, transpose)
        pairs = [''.join((pair)) for pair in zip_pairs]
        
        for index,y in enumerate(pairs):
            
            if y == '\n':
                try:
                    pairs[index] = stars[test_index][index] + '\n'
                except IndexError:
                    print(test_index, 'test')
                    print(index, 'index')
                    sleep(10)
            elif y == laser+'\n':
                pairs[index] = stars[test_index][index]  + '[bold red]|\n[/]'
                #pairs[index] = stars[test_index][index] 
                
        print_version.append(''.join(pairs))
        
            
    battlefield =  Panel(Columns(print_version, padding = (0,0), expand=True), 
                         padding = (0,0), width = width, 
                         expand=True)
    
    return Align.center(battlefield)
   
def player_moves_shoots(shot):
    """ Player moves and shoots once per alien ship movement """
    """ Function returns whether player has shot laser or not """
    command = readchar.readkey()
    global player_pos
    if command in ('a','d'):
        
        pm_1 = input_dict[command]
        
        space_battle[ mod(player_pos) ][-1] = '  '
        space_battle[ mod(player_pos+pm_1) ][-1] = player

        player_pos = player_pos + pm_1
        
    if command == 's' and shot == False:
        """Shoot laser"""
        if space_battle[player_pos % c_number][-2] in list(alien):
            space_battle[player_pos % c_number][-2] = explosion
        else:
            space_battle[player_pos % c_number][-2] = laser
            
        return True
    
    return shot

def move(current_game, s_o_l):
    new_game = []
    for channel in current_game:
        temp_channel = channel[:-1]
        (ships, lasers, destroy) = split_col(temp_channel,s_o_l)
        
        w_column = (ships, lasers)
        key = move_dict[s_o_l]
        
        if (ships, lasers, destroy)[ key[0] ]:
            
            rotating_column = (ships, lasers, destroy)[ key[1] ]           
            rotating_column, removed =  rotate(rotating_column, key[0]),\
                                        (ships, lasers, destroy)[ key[1] ][ key[2] ]
                
            if removed in list(alien) or (removed == laser and destroy):
                try:
                    w_column[key[3]][key[4]] = explosion   
                    global player_score
                    player_score += 1
                except IndexError:
                    global game_end
                    game_end = True
                    return current_game
                         
            if s_o_l == 'ship':           
                new_channel = rotating_column+lasers          
            if s_o_l == 'laser':                 
                new_channel = ships+rotating_column
            
            new_channel =  new_channel + [channel[-1]]
            
        else:
            new_channel = channel
            
        new_game.append(new_channel)       
    return new_game

def mod(x):
    return x%c_number

def rotate(column, reverse = False):
    if reverse == False:
        return [''] + column[:-1]
    if reverse == True:
        return column[1:] + ['']  

def find_ship(column):
    
    return max([index for index,char in enumerate(column) \
                if char in alien and char != ''])

def destroy_ships(current_game):
    for chan_num, channel in enumerate(current_game[1:-1],1):
        
        for x in exes(channel):
            
            if current_game[chan_num-1][x]  == '<':
                current_game[chan_num-1][x] = ''
            if current_game[chan_num+1][x] == '>':
                current_game[chan_num+1][x] = ''
    return current_game

def clear_debris(current_game):
    for chan_num, channel in enumerate(current_game):
        
        for x in exes(channel):
            current_game[chan_num][x] = ''
    return current_game

def exes(collumn):
    indices = []
    for index, char in enumerate(collumn):
        if char == explosion:
            indices.append(index)
    return indices

def add_aliens(current_game, time, run_function):
        if run_function == True:
            if math.sqrt(time)/(5*math.sqrt(tick_number)) > random.random():
                new_ship_center = random.choice(list(range(1,c_number-1)))
    
                s_l = len(alien)
                
                for i,xcoord in enumerate(range(new_ship_center- int((s_l-1)/2) ,new_ship_center+ int((s_l-1)/2+1)) ):
                    current_game[xcoord][0] = alien[i]
    
        #    return current_game
        return current_game
    
def perform_changes(space_battle, functions):
    saved_battle = space_battle
    for function in functions:
        space_battle = function(space_battle)
    
    return space_battle, saved_battle

def timer_and_clean_debris(timer, space_battle):
    if not timer:
        " keep track of debris cleanup putside of function "
        global debris_cleanup
        debris_cleanup = time.time() + 1.5
        timer = True      
    
    " removes explosion emoji after timer "
    if time.time() >= debris_cleanup: 
        
        timer = False
        space_battle, saved_battle = perform_changes(space_battle, 
                [lambda x: clear_debris(x)]
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
            [ '[light blue]\n\n' + key, show_color_option('\n  ' + option + '\n', colors[index]) ]
            )
    return output

def show_color_option(text_a_emoji, colour):
    """ Returns Panel of option with colour scheme """
    return Panel(text_a_emoji, border_style= colour, box = box.HEAVY, padding = 0)

def ask_player_choice():
    """ Asks for player input repeatedly until input is r, p or s """
    correct_input = False
    while correct_input == False:        
        player_choice = readchar.readkey()
        correct_input = player_choice in {'e','m','h'}
        if correct_input == False:
            console.print('THIS WASN\'T ONE OF THE OPTIONS!!!', style = 'bold red on white')            
    return player_choice

def refresh_menu(player_choice = None):
    """ Print header, prompt and options """
    console.clear()
    console.rule('[bold purple on white]Space Invaders', 
                 style = 'red', characters= '❌', align='center')    
    buttons = create_buttons(player_choice)
    
    console.print('\n\n')
    console.print('\n\nChoose your difficulty! \n\
(Enter choice by inputing corresponding letter)\n\n',
                      style = 'purple on white', justify='center')
    " Print buttons "
    console.print(Align.center(Columns(buttons, align='center', equal=True )))
    
def set_up_game():
    
   " game tick every 1.5 seconds "
   global game_tick_time
   global tick_number
   global player_pos
   global transpose
   global colour
   global pad
   global width
   global space_battle
   global c_number
   global height
   global stars
   global player_score
   
   game_tick_time = 0.1
   tick_number = 500

   " Create base battlefield "

   height = 45
   c_number = 20
   width = 3*c_number

 
   stars = make_stars(c_number, height+1)
   transpose = ['\n']*height + ['']
   
   
   player_score = 0
   player_pos = 0

   space_battle = [['']*height + [player]]
   for column in range(c_number-1):
       space_battle.append(['']*height+['  '])

   space_battle = add_aliens(space_battle, 500, True)
    
def make_stars(c_num, height):
    stars = []
    prob = 0.01
    for x in range(c_num):
        stars_col = []
        for y in range(height+1):
            
            if random.random()<prob:
                stars_col.append('[grey78]●[/]')
            elif random.random()<prob:
                stars_col.append('[misty_rose1].[/]')
            elif random.random()<prob:
                stars_col.append('[dark_sea_green]•[/]')
            elif random.random()<prob:
                stars_col.append('[cyan1].[/]')
            elif random.random()<prob:
                stars_col.append('[plum2]•[/]')
            else:
                stars_col.append(' ')
        stars.append(stars_col)
            
    return stars

""" Dictionairies """
input_dict = {
    'a':-1,
    'd':1
    }

move_dict = {
    'ship': [False,0,-1,1,0], 
    'laser':[True,1,0,0,-1]
    }



coloures_borders_dict = {'e': ['magenta','white','white'],
               'm': ['white','magenta','white'],
               'h': ['white','white','magenta'],
               None: ['white','white','white']}

difficulty_dict = {'e': [5,1],'m': [3,1],'h':[2,1]}

player_options = [('e:','EASY  '),('m:','MEDIUM  '),('h:','HARD  ')]

""" Player Menu """
with console.screen():
    refresh_menu()
    difficulty_setting = ask_player_choice()
    refresh_menu(difficulty_setting)
    with console.status( '[purple]Setting up game', 
                         spinner = 'point' ):
        set_up_game()
        sleep(4)
        
    s_s,l_s = difficulty_dict[difficulty_setting]

s_c_d = {
    'ship': [1,0,s_s],
    'laser':[0,1,l_s]
    }

with console.screen():
    """ Game loop """
    console.rule('[bold purple on white]Space Invaders', 
                 style = 'red', characters= '❌', align='center')   
    with Live(update_visuals(space_battle), refresh_per_second=60) as Live:

        timer = False
        game_end = False
        tick = 0
        while not(game_end):
        
            " start timer to clear debris and/or clear debris "
            timer,space_battle = timer_and_clean_debris(timer, space_battle) 
                
            " Player can shoot once per 5 game ticks "
            if tick%5 == 0:
                shot = False
            start_time = time.time()
        
            " Player moves or shoots if input detected "
            while time.time() - start_time < game_tick_time:                
                if msvcrt.kbhit():
                    shot = player_moves_shoots(shot)
                    Live.update(update_visuals(space_battle))
                
            " Game tick and updte visuals "    
            for item in s_c_d.keys():
                
                if tick % s_c_d[item][2] == 0:
                    space_battle, saved_battle = perform_changes(space_battle, 
                        [lambda x: move(x,item), 
                         lambda x: add_aliens(x, tick,item == 'ship') ]
                        )    
                    if game_end == True:
                        break  
                    if saved_battle != space_battle:
                        Live.update(update_visuals(space_battle)) 
 
            tick+=1
     

          
with console.screen():
    console.print('\n\n\nYou lost!! You took out {} aliens though!'\
                  .format(player_score), justify='center')  
    sleep(5)      
       
            

        
        
