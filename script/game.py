"""
game module for Python 3.9. Based on INFOB132 year 2021-2022 request at UNamur
"""
__author__  ="Yannis Van Achter <yannis.van.achter@gmail.com>"
__date__    = "15 march 2022"
__version__ = "1.2"


# -- Modules --
# native modules
import time
import os
import os.path as pt
import ast

# self modules
try:
    import data_manager as dm
    import remote_player as rp
    import UI as ui
    import IA as ia
except ModuleNotFoundError:
    import script.data_manager as dm
    import script.remote_player as rp
    import script.UI as ui
    import script.IA as ia

# -- Anomimous fonctions of game--
get_distance = lambda wolve1, wolve2  : max(abs(wolve2[0] - wolve1[0] ) , abs(wolve2[1] - wolve1[1]))

get_entity_coord = lambda wolve : (int(str.split(wolve, '-')[0]) , int(str.split(wolve, '-')[1]))

can_eat = lambda target_coord, wolve : (wolve[0]-1 <= target_coord[0] <= wolve[0] + 1) and (wolve[1]-1 <= target_coord[1] <= wolve[1] + 1)

can_attack = lambda  target_coord , wolve , db : can_eat(target_coord , wolve) and (not db['wolves'][wolve]['passified']) and (target_coord in db['wolves'])

# -- Fonctions of game --
def get_instructions(player : str, db : dict, n_player : int) -> (str):
    """ask for intruction to player

    Parameters:
    ----------
        player (str): name of the player to
        db (dict): data base of game 
        n_player (int): 1 if this is the first player else 2 

    Return:
    --------
        order (str): list of all intruction
        
    Version:
    --------
        specification: Yannis Van Achter (v2 27/02/2022)
        implementation: Yannis Van Achter (v2 03/03/2022)
    """
    import re
    string_order = ''
    order_entered = True
    my_wolves = [wolve for wolve, data in db['wolves'].items() if data['property'] == n_player] # get wolve of my team to ask for order
    print('If you don\'t want to write an order press \'enter\'')
    while len(my_wolves) != 0 and order_entered:
        my_wolves_copy = my_wolves.copy()
        for wolve_coord in my_wolves_copy:
            order = input(f'The player named : {player}, can enter his order for the wolve at \"{wolve_coord[0]}-{wolve_coord[1]}:').strip()
            if re.search(r"([@]{1}[1-60]{1}[\-]{1}[1-40]{1})|([\<]{1}[1-60]{1}[\-]{1}[1-40]{1})|pacify", order) != None:
                string_order += f"{wolve_coord[0]}-{wolve_coord[1]}:" + order + ' '
                my_wolves.remove(wolve_coord)
            elif re.search("[1-60]{1}[\-]{1}[1-40]{1}", order) != None and order.startswith('*'):
                string_order += f"{wolve_coord[0]}-{wolve_coord[1]}:" + order + ' '
                my_wolves.remove(wolve_coord)
        
        # check that at least one order were entered
        if len(my_wolves) == len(my_wolves_copy):
            order_entered = False
    
    return string_order.strip()


def play_game(map_path : str, group_1 : str, type_1 : str, group_2 : str, type_2 : str) -> (list[int]):
    """Play a game. And return the winner by number 1 or 2, if both are present, the both win
    
    Parameters
    ----------
        map_path: path of map file (str)
        group_1: group of player 1 (int)
        type_1: type of player 1 (str)
        group_2: group of player 2 (int)
        type_2: type of player 2 (str)
    
    Note
    ----
        Player type is either 'human', 'AI' or 'remote'.
        
        If there is an external referee, set group id to 0 for remote player.
    
    Return:
    -------
        winner : winner(s) of the game (list[int])
        
    Version:
    --------
        specification: Yannis Van Achter (v.1 11/02/2022)
        implementation: Yannis Van Achter (v.2 13/02/2022)
    """
    if not pt.isfile(map_path):
        raise ValueError('Enter another map_path this one does not exist')
    
    # create connection between 2 computer if nessesary
    if type_1 == 'remote':
        try:
            connection_1 = rp.create_connection(group_2, group_1)
        except (IOError, TypeError, NameError, ValueError, 
        EOFError, FileExistsError, FileNotFoundError) as error:
            exit(error)
    if type_2 == 'remote':
        try:
            connection_2 = rp.create_connection(group_1, group_2)
        except (IOError, TypeError, NameError, ValueError, 
        EOFError, FileExistsError, FileNotFoundError) as error:
            exit(error)
        
    db: dict = dm.data_create(map_path , group_1 , group_2)
    
    order = {}
    winner = []
    game_round = 0
    while len(winner) == 0 and game_round < 200:
        ui.show_map(db)
        
        if type_1 == 'remote':
            order[1] = rp.get_remote_orders(connection_1)
        elif type_1 == 'player':
            order[1] = get_instructions(group_1, db, 1)
        elif type_1 == 'IA':
            order[1], db = ia.get_IA_order(db , 1)
        if type_2 == 'remote':
            rp.notify_remote_orders(connection_2, order[1])
        order[1] = order[1].split(' ')
        
        if type_2 == 'remote':
            order[2] = rp.get_remote_orders(connection_2)
        elif type_2 == 'player':
            order[2] = get_instructions(group_2, db, 2)
        elif type_2 == 'IA':
            order[2], db = ia.get_IA_order(db , 2, order[1])
        if type_1 == 'remote':
            rp.notify_remote_orders(connection_1, order[2])
        time.sleep(0.3)
        order[2] = order[2].split(' ')
        
        db = order_prosses(db, order)
        game_round +=1
        winner = game_over(db)
    
    ui.show_map(db)
    
    if game_round < 200:
        if len(winner) == 2:
            print(f'Both of you won in {game_round} game round')
        elif winner[0] == 2:
            print(f'The winner is : {group_2} in {game_round} game round')
        elif winner[0] == 1:
            print(f'The winner is : {group_1} in {game_round} game round')
    else:
        total = {1 : 0, 2:0}
        for wolve, data in db['wolves'].items():
            total[data['property']] += data['energy']
        
        if total[1] == total[2]:
            print(f'Both of you won with security you have the same energy score : {total[1]}')
            winner = [1,2]
        elif total[1] > total[2]:
            print(f'The winner is : {group_1} in {game_round} game round')
            winner = [1]
        elif total[1] < total[2]:
            print(f'The winner is : {group_2} in {game_round} game round')
            winner = [2]
      
    # close connection, if necessary
    if type_1 == 'remote':
        rp.close_connection(connection_1)
    if type_2 == 'remote':
        rp.close_connection(connection_2)    
    
    return winner

        
def order_prosses(db : dict , orders : dict) -> (dict):
    """db modification proccess
    
    Parameters:
    -----------
        db : database of game (dic)
        orders : print of player (dict)
    
    Return:
    -------
        [dic]: dictionnary of all modification to do the data baser
        
    Version:
    --------
        specification: Yannis Van Achter (v.1 11/02/2022)
        implementation: Yannis Van Achter (v.2 13/02/2022)
    """
    passifier = used_wolves = []
    
    db , passifier, used_wolves = pacified(db , orders=orders) # pacification 
    
    db = get_bonus(db)
    
    db , used_wolves = get_eat(db, orders, used_wolves)
    
    db , used_wolves = fight(db, orders , used_wolves)

    db, used_wolves = get_move_order(db , orders , used_wolves)
    
    db = get_bonus(db , False)
    
    db , passifier , used_wolves = pacified(db, passifier = passifier , value  =  False) # dépacification 
    
    return db

def get_eat(db : dict , orders : dict, used_wolves : list) -> (tuple[dict , list]):
    """anit to wolves to eat
    
    Parameters:
    -----------
        db : data base of game (dic)
        orders : List of all order (list)
    
    Return:
    -------
        db : data base of game (dic)
        
    Version:
    --------
        Spécification: Yannis Van Achter (v1 23/02/2022)
        Implémentation: Yannis Van Achter (v1 23/02/2022)
    """
    for players in orders:
        for order in orders[players]:
            if len(order) >= 7:
                order = str.split(order, ':')
                wolve = get_entity_coord(str.strip(order[0])) 
                if wolve in db['wolves']:
                    if wolve not in used_wolves and db['wolves'][wolve]['property'] == players\
                    and str.startswith(order[1], '<'):
                        target_coord = get_entity_coord(str.strip(order[1][1:])) # saut de 1 pour aller direct après le '<'
                        if can_eat(target_coord , wolve):
                            db = dm.eat(wolve , target_coord, db)
                            used_wolves.append(wolve)
    
    return db , used_wolves

def get_move_order(db : dict , orders : dict, used_wolves : list) -> (tuple[dict , list]):
    """anit to wolves to move
    
    Parameters:
    -----------
        db : data base of game (dict)
        orders : List of all order (dict)
        used_wolves : list of wolves already used (list)
        
    Returns:
    -------
        db : data base of game (dic)
        used_wolves : list of wolves already used (list)
        
    Version:
    --------
        Spécification: Yannis Van Achter (v1 23/02/2022)
        Implémentation: Yannis Van Achter (v1 23/02/2022)
    """
    for player in orders:
        for order in orders[player]:
            if len(order) >= 7:
                order = str.split(order, ':')
                wolve = get_entity_coord(str.strip(order[0])) 
                if wolve in db['wolves'] and str.startswith(order[1], '@') and wolve not in used_wolves \
                    and db['wolves'][wolve]['property'] == player:
                    new_coord = get_entity_coord(str.strip(order[1][1:])) # saut de 1 pour aller direct après le '@'
                    if can_move(new_coord , wolve , db):
                        db = dm.move_entity(wolve, new_coord, db)
                        used_wolves.append(wolve)
    
    return db , used_wolves

def fight(db : dict , orders : dict, used_wolves : list) -> (tuple[dict , list]):
    """Follow fight order and active fight function
    
    Parameters:
    -----------
        db : data base of game (dict)
        orders : List of all order (dict)
        used_wolves : list of wolves already used (list)
        
    Returns:
    -------
        db : data base of game (dic)
        used_wolves : list of wolves already used (list)
        
    Version:
    -------
        specification : Yannis Van Achter (v1. 27/02/2022)
        implementation : Yannis Van Achter (v1. 24/02/2022)
    """
    for player in orders:
        for order in orders[player]:
            if len(order) >= 7:
                order = str.split(order, ':')
                wolve = get_entity_coord(str.strip(order[0])) 
                if wolve in db['wolves'] and str.startswith(order[1], '*') and (wolve not in used_wolves) \
                    and db['wolves'][wolve]['property'] == player:
                    target_coord = get_entity_coord(str.strip(order[1][1:])) # saut de 1 pour aller direct après le '*'
                    if can_attack(target_coord , wolve , db):
                        db = dm.attack(wolve , target_coord, db)
                        if db['wolves'][target_coord]['energy'] < 0:
                            db['wolves'][target_coord]['energy'] = 0
                        used_wolves.append(wolve)
                    
    return db, used_wolves

def pacified(db : dict , passifier : list = [], value : bool = True , orders : dict = {}) -> (tuple[dict, list, list]):
    """pacify or unpacify wolve of game
    
    Parameters:
    -----------
        db : data base of game (dic)
        passifier : all pacified wolve (list)
        value : True if wolve must be passified, False otherwise (bool)
        orders : List of all order (list)
    
    Returns:
    --------
        db: data base of game (dict)
        passifier: list of passified wolves (list)
        
    Version:
    --------
        Spécification : Yannis Van Achter (v1. 17/02/2022)
        Implémentation : Yannis Van Achter (v1. 17/02/2022)
    """
    used_wolves = []
    if value: 
        for player in orders:
            for order in orders[player]:
                if len(order) >= 7:
                    order = order.split(':')
                    if str.startswith(order[1], 'pacify'):
                        wolve = get_entity_coord(str.strip(order[0]))
                        if wolve in db['wolves'] and db['wolves'][wolve]['type'] == 'omega':
                            if db['wolves'][wolve]['energy'] >= 40 and  db[wolve]['property'] == player:
                                db['wolves'][wolve]['energy'] -= 40
                                used_wolves.append(wolve)
                                for y in range(wolve[0]-6, wolve[0]+7):
                                    for x in range(wolve[1]-6, wolve[1]+7):
                                        if (y,x) in db['wolves']:
                                            db['wolves'][(y,x)]['passified'] = value
                                            passifier.append((y,x))

    else:
        for wolve in passifier:
            db['wolves'][wolve]['passified'] = value
            passifier.remove(wolve)
    
    return db , passifier , used_wolves

def get_bonus(db : dict , bonus : bool = True) -> (dict):
    """assin or not the bonus to wolves
    
    Parameters:
    -----------
        db : data base of game (dic)
        bonus : True if get bonus, false if we don't. Defaults to True.(bool, optional)
    
    Return:
    -------
        db : data base of game (dic)
        
    Version:
    --------
        Spécification: Yannis Van Achter (v1 23/02/2022)
        Implémentation: Yannis Van Achter (v1 23/02/2022)
    """
    if bonus:
        for wolve, data in db['wolves'].items():
            if data['type'] == 'alpha':
                for y in range(wolve[0] - 4 , wolve[0] +5):
                    for x in range(wolve[1] - 4 , wolve[1] +5):
                        if (y,x) in db['wolves'] and (db['wolves'][(y,x)]['property'] == data['property']) and ((y,x) != wolve):
                            data['bonus'] += 30 if db['wolves'][(y,x)]['type'] == 'alpha' else 10
            else:
                for y in range(wolve[0] - 2 , wolve[0] +3):
                    for x in range(wolve[1] - 2 , wolve[1] +3):
                        if (y,x) in db['wolves'] and (db['wolves'][(y,x)]['property'] == data['property']) and ((y,x) != wolve):
                            data['bonus'] += 30 if db['wolves'][(y,x)]['type'] == 'alpha' else 10
    else:
        for wolve,data in db['wolves'].items():
            data['bonus'] = 0
    
    return db

def can_move(new_coord : tuple, old_coord : tuple , db : dict) -> (bool):
    """autorise the wolve to move
    
    Parameters:
    -----------
        new_coord: (y,x) (tuple)
        old_coord: (y,x) (tuple)
        db: data base of game (dic)
    
    Return:
    -------
        bool : True if wolve can move to his target, False otherwise
        
    Version:
    --------
        spécification: Yannis Van Achter (v1 16/02/2022)
        implémentation: Yannis Van Achter (v1 16/02/2022)
    """
    if new_coord[0] < 1 or new_coord[0] > db['board']['y_max']:
        return False
    if new_coord[1] < 1 or new_coord[1] > db['board']['x_max']:
        return False
    if new_coord in db['wolves']:
        return False
    
    return can_eat(new_coord, old_coord)

def game_over(db : dict) -> (list[int]):
    """say if game is ended and who win
    
    Parameter:
    ----------
        db : database of game (dic)
    
    Returns:
    --------
        winner : the winner of the game (list[int])
        
    Version:
    --------
        specification: Yannis Van Achter (v.1 11/02/2022)
        implementation: Yannis Van Achter (v.2 11/02/2022)
    """
    winner = []
    delta = {1 : 2, 2 : 1}
    
    for wolve, data in db['wolves'].items():
        if data['type'] == 'alpha' and data['energy'] <=0:
                winner.append(delta[data['property']])
    
    return winner


# -- code to manage winner history and user in general those function are not directly linked to game--
def add_winner(winner: str, all_winner: dict) -> (dict):
    """add winner in history

    add winner in history of winner based on username 

    Parameters:
    ----------
        winner (str): username of winner

    Returns:
    --------
        dict: dict of all winner with username as key and integer 
        
    Version:
    -------
        specification: Yannis Van Achter (v1 29/03/04)
        implementation: Yannis Van Achter (v1 29/03/04)
    """
    if winner in all_winner:
        all_winner[winner] += 1
    else:
        all_winner[winner] = 1
    return all_winner

def get_int(*prompt : list[str,int,float]) -> (int):
    """get int from User

    ask and transform print sting into int

    Args:
        prompt (str): request

    Returns:
        int: number inputed by user
    """
    prompt = ''.join(map(str, prompt))
    while True:
        n = input(prompt)
        try:
            return int(n)
        except (TypeError, ValueError) as error:
            print(error)
        except:
            pass

def get_type(*prompt: list):
    """get type of one of the user

    ask to a user which type he is 'player', 'IA' or 'remote'
    
    Parameters:
    -----------
        *prompt (list): list of ellement to print

    Returns:
    --------
        str: type choosed by user
    """
    type='AA'
    while type not in ('player', 'IA', 'remote'):
        type = input(prompt)
    return type
        

def launch_game() -> (None):
    """launch game of alpha omega

    main program to start game from the Menu in terminal
    to lauch the program you need to run the code from the file 'engine_gr_3.py' or 
    call this function after importing the module
    """
    from random import choice
    
    ui.clear()
    
    type_player = ('player', 'IA', 'remote')

    # load history of winner
    if pt.isfile('./winner_history.txt'):
        file = dm.load_file('./winner_history.txt')
        all_winner = ast.literal_eval(file)
    else:
        all_winner = {}
    
    conti = input('Start a game ? (yes/no) : ').lower()
    while conti.startswith('yes'):
        map_path: str = './map/' + choice(os.listdir('./map')) if input('Do you want a random map ? (yes/no) : ').lower().startswith('yes') else input('Enter the map path \n here: ')
        type_1: str =  get_type(f"Who play this game {type_player}: ")
        group_1: int =  get_int('Enter the id of the player : ') if type_1 == 'remote' else input('Enter your user name')
        type_2: str = get_type(f"Who play this game {type_player}: ")
        group_2: int = get_int('Enter the id of the player : ') if type_2 == 'remote' else input('Enter your user name')
 
        try:
            winner = play_game(map_path, group_1, type_1, group_2, type_2)
        except KeyboardInterrupt as error:
            print(error)
            launch_game()
            break
        except SystemExit as e:
            print(e)
            continue
        
        # add winner to history
        if len(winner)==2:
            all_winner = add_winner(group_1, all_winner)
            all_winner = add_winner(group_2, all_winner)
        elif winner[0]==1:
            all_winner = add_winner(group_1, all_winner)
        elif winner[0]==2:
            all_winner = add_winner(group_2, all_winner)
            
        conti = input('Start a game ? (yes/no) : ').lower() # look if we do a new game
    
    # store winner history in file
    fh = open('./winner_history.txt', 'w')
    fh.write(str(all_winner))
    fh.close()

# -- Code --
if __name__ == '__main__':
    launch_game()
    