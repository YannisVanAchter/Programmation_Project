"""compilation of other python file in script reprtory 

This compilation is the one which correctly work.
The only request at this time is colored V 1.4.3
The IA here in based on random choice
"""
__author__  ="Yannis Van Achter <yannis.van.achter@gmail.com>"
__date__    = "29 march 2022"
__version__ = "1.0"

# --- Modules ---
# native modules
import copy
import os 
import os.path as pt 
import time 
import socket
import re 
import ast

from random import choice , randint

# pip modules
from colored import fore, back, style

# -- Fonction to play at distance of the other player from B. Frenay, UNamur professor ---
def create_server_socket(local_port, verbose):
    """Creates a server socket.
    
    Parameters
    ----------
    local_port: port to listen to (int)
    verbose: True if verbose (bool)
    
    Return
    ------
    socket_in: server socket (socket.socket)
    
    """
    
    socket_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_in.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # deal with a socket in TIME_WAIT state

    if verbose:
        print(' binding on local port %d to accept a remote connection' % local_port)
    
    try:
        socket_in.bind(('', local_port))
    except:
        raise IOError('local port %d already in use by your group or the referee' % local_port)
    socket_in.listen(1)
    
    if verbose:
        print('   done -> can now accept a remote connection on local port %d\n' % local_port)
        
    return socket_in


def create_client_socket(remote_IP, remote_port, verbose):
    """Creates a client socket.
    
    Parameters
    ----------
    remote_IP: IP address to send to (int)
    remote_port: port to send to (int)
    verbose: True if verbose (bool)
    
    Return
    ------
    socket_out: client socket (socket.socket)
    
    """

    socket_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # deal with a socket in TIME_WAIT state
    
    connected = False
    msg_shown = False
    
    while not connected:
        try:
            if verbose and not msg_shown:
                print(' connecting on %s:%d to send orders' % (remote_IP, remote_port))
                
            socket_out.connect((remote_IP, remote_port))
            connected = True
            
            if verbose:
                print('   done -> can now send orders to %s:%d\n' % (remote_IP, remote_port))
        except:
            if verbose and not msg_shown:
                print('   connection failed -> will try again every 100 msec...')
                
            time.sleep(.1)
            msg_shown = True
            
    return socket_out
    
    
def wait_for_connection(socket_in, verbose):
    """Waits for a connection on a server socket.
    
    Parameters
    ----------
    socket_in: server socket (socket.socket)
    verbose: True if verbose (bool)
    
    Return
    ------
    socket_in: accepted connection (socket.socket)
    
    """
    
    if verbose:
        print(' waiting for a remote connection to receive orders')
        
    socket_in, remote_address = socket_in.accept()
    
    if verbose:
        print('   done -> can now receive remote orders from %s:%d\n' % remote_address)
        
    return socket_in            


def set_IP(other_group):
    """Ask for the IP of the other computer
    
    Show your IP and ask for the IP of the remote
    
    Parameters:
    -----------
        other_group (int): n° of the group to remote
    Returns:
    --------
        other_IP (str): IP of the other computer 
        
    """
    my_IP = socket.gethostbyname_ex(socket.gethostname())[-1][0]
    print(f"Your IP is : {my_IP}")
    other_IP = ''
    while other_IP == '':
        other_IP = input('Enter other_IP : ')
        if other_IP == '':
            other_IP = '127.0.0.1'
        elif not re.search(r"[0-9]{3}\.[0-9]{2}\.[0-9]{3}\.[0-9]{3}", other_IP):
            other_IP = ''
            
    return other_IP     


def create_connection(your_group, other_group=0, verbose=True):
    """Creates a connection with a referee or another group.
    
    Parameters
    ----------
    your_group: id of your group (int)
    other_group: id of the other group, if there is no referee (int, optional)
    verbose: True only if connection progress must be displayed (bool, optional)
    
    Return
    ------
    connection: socket(s) to receive/send orders (dict of socket.socket)
    
    Raise
    -----
    IOError: if your group fails to create a connection
    
    Note
    ----
    Creating a connection can take a few seconds (it must be initialised on both sides).
    
    If there is a referee, leave other_group=0, otherwise other_IP is the id of the other group.
    
    If the referee or the other group is on the same computer than you, leave other_IP='127.0.0.1',
    otherwise other_IP is the IP address of the computer where the referee or the other group is.
    
    The returned connection can be used directly with other functions in this module.
            
    """
    other_IP = set_IP(other_group)

    # init verbose display
    if verbose:
        print('\n[--- starts connection -----------------------------------------------------\n')
        
    # check whether there is a referee
    if other_group == 0:
        if verbose:
            print('** group %d connecting to referee on %s **\n' % (your_group, other_IP))
        
        # create one socket (client only)
        socket_out = create_client_socket(other_IP, 42000+your_group, verbose)
        
        connection = {'in':socket_out, 'out':socket_out}
        
        if verbose:
            print('** group %d successfully connected to referee on %s **\n' % (your_group, other_IP))
    else:
        if verbose:
            print('** group %d connecting to group %d on %s **\n' % (your_group, other_group, other_IP))

        # create two sockets (server and client)
        socket_in = create_server_socket(42000+your_group, verbose)
        socket_out = create_client_socket(other_IP, 42000+other_group, verbose)
        
        socket_in = wait_for_connection(socket_in, verbose)
        
        connection = {'in':socket_in, 'out':socket_out}

        if verbose:
            print('** group %d successfully connected to group %d on %s **\n' % (your_group, other_group, other_IP))
        
    # end verbose display
    if verbose:
        print('----------------------------------------------------- connection started ---]\n')

    return connection
        
        
def bind_referee(group_1, group_2, verbose=True):
    """Put a referee between two groups.
    
    Parameters
    ----------
    group_1: id of the first group (int)
    group_2: id of the second group (int)
    verbose: True only if connection progress must be displayed (bool, optional)
    
    Return
    ------
    connections: sockets to receive/send orders from both players (dict)
    
    Raise
    -----
    IOError: if the referee fails to create a connection
    
    Note
    ----
    Putting the referee in place can take a few seconds (it must be connect to both groups).
        
    connections contains two connections (dict of socket.socket) which can be used directly
    with other functions in this module.  connection of first (second) player has key 1 (2).
            
    """
    my_IP = socket.gethostbyname_ex(socket.gethostname())[-1][0]
    print(f"Your IP is : {my_IP}")
    
    # init verbose display
    if verbose:
        print('\n[--- starts connection -----------------------------------------------------\n')

    # create a server socket (first group)
    if verbose:
        print('** referee connecting to first group %d **\n' % group_1)        

    socket_in_1 = create_server_socket(42000+group_1, verbose)
    socket_in_1 = wait_for_connection(socket_in_1, verbose)

    if verbose:
        print('** referee succcessfully connected to first group %d **\n' % group_1)        
        
    # create a server socket (second group)
    if verbose:
        print('** referee connecting to second group %d **\n' % group_2)        

    socket_in_2 = create_server_socket(42000+group_2, verbose)
    socket_in_2 = wait_for_connection(socket_in_2, verbose)

    if verbose:
        print('** referee succcessfully connected to second group %d **\n' % group_2)        
    
    # end verbose display
    if verbose:
        print('----------------------------------------------------- connection started ---]\n')

    return {1:{'in':socket_in_1, 'out':socket_in_1},
            2:{'in':socket_in_2, 'out':socket_in_2}}


def close_connection(connection):
    """Closes a connection with a referee or another group.
    
    Parameter
    ---------
    connection: socket(s) to receive/send orders (dict of socket.socket)
    
    """
    
    # get sockets
    socket_in = connection['in']
    socket_out = connection['out']
    
    # shutdown sockets
    socket_in.shutdown(socket.SHUT_RDWR)    
    socket_out.shutdown(socket.SHUT_RDWR)
    
    # close sockets
    socket_in.close()
    socket_out.close()
    
    
def notify_remote_orders(connection, orders):
    """Notifies orders to a remote player.
    
    Parameters
    ----------
    connection: sockets to receive/send orders (dict of socket.socket)
    orders: orders to notify (str)
        
    Raise
    -----
    IOError: if remote player cannot be reached
    
    """

    # deal with null orders (empty string)
    if orders == '':
        orders = 'null'
    
    # send orders
    try:
        connection['out'].sendall(orders.encode())
    except:
        raise IOError('remote player cannot be reached')


def get_remote_orders(connection):
    """Returns orders from a remote player.

    Parameter
    ---------
    connection: sockets to receive/send orders (dict of socket.socket)
        
    Return
    ------
    player_orders: orders given by remote player (str)

    Raise
    -----
    IOError: if remote player cannot be reached
            
    """
   
    # receive orders    
    try:
        orders = connection['in'].recv(65536).decode()
    except:
        raise IOError('remote player cannot be reached')
        
    # deal with null orders
    if orders == 'null':
        orders = ''
        
    return orders


# -- Anonimous Fonction of data_manager -- 
set_board_value = lambda size , min=20 , max=40 : max if size > max else (min if size < min else size)

# -- Anonimous fonction of UI --
format_string = lambda string : string +fore.GOLD_1 + back.DARK_BLUE + style.RESET

# -- Anomimous fonctions of game --
get_distance = lambda wolve1, wolve2  : max(abs(wolve2[0] - wolve1[0] ) , abs(wolve2[1] - wolve1[1]))

get_entity_coord = lambda wolve : (int(str.split(wolve, '-')[0]) , int(str.split(wolve, '-')[1]))

can_eat = lambda target_coord, wolve : (wolve[0]-1 <= target_coord[0] <= wolve[0] + 1) and (wolve[1]-1 <= target_coord[1] <= wolve[1] + 1)

can_attack = lambda  target_coord , wolve , db : can_eat(target_coord , wolve) and (not db['wolves'][wolve]['passified']) and (target_coord in db['wolves'])


# --- Fonction  of data_manager ---
def load_file(filename : str) -> (str):
    """load file asked

    Parameteres:
    ------------
        filename: path of the file (str)
    
    Raise:
    ------
        FileExistsError: [description]
    
    Return:
    -------
        loaded_file: list of line from the file (list)
        
    Version:
    --------
        specification: Yannis Van Achter (v.1 05/02/2022)
        implementation: Yannis Van Achter (v.1 05/02/2022)
    """
    if not pt.exists(filename) or not pt.isfile(filename):
        raise FileExistsError(f'Check if {filename} exist or is a file')
    
    fh = open(filename , 'r')
    loaded_file = fh.read()
    fh.close()
    
    return loaded_file

def create_map(size_str : str)  -> (dict):
    """create a map
    
    Parameters:
    -----------
        size_str : x y (str)
        db : data base of game (dic)
    
    Return:
    -------
        db : upgraded data base of game (dic)
        
    Version:
    --------
        specification: Yannis Van Achter (v.2 10/02/2022)
        implementation: Yannis Van Achter (v.2 10/02/2022)
    """
    return  {'y_max' :set_board_value(int(str.split(size_str, ' ')[0])),
             'x_max' :set_board_value(int(str.split(size_str, ' ')[1]), max = 60)}

def add_wolves(line : str, db : dict , Player_1 : str , Player_2 : str)  -> (dict):
    """add wolves in there team and set spawn point and heath point
    
    Parameters:
    -----------
        line : 'x y type heathpoint' (str)
        db : data base of the game (dic)
    
    Return:
    -------
        db: data base of the game upgraded (dic)
        
    Version:
    --------
        specification: Yannis Van Achter (v.1 07/02/2022)
        implementation: Yannis Van Achter (v.2 10/02/2022)
    """
    line_split = str.split(line, ' ')
    
    if line[0] == '1':
        player,type_p = Player_1,1
    else: 
        player,type_p = Player_2,2
    
    db['wolves'][(int(line_split[1]),int(line_split[2]))] = {
        'type' : line_split[3].lower(), 'energy' : 100, 
    'property' : type_p, 'bonus' : 0 , 'passified' : False ,'Player' : player
    }
        
    return db

def add_food(line : str, db : dict)  -> (dict):
    """add wolves in there team and set spawn point and heath point
    
    Parameters:
    -----------
        line : 'x y type heathpoint' (str)
        db : data base of the game (dic)
    
    Return:
    -------
        db: data base of the game upgraded (dic)
        
    Version:
    --------
        specification: Yannis Van Achter (v.1 07/02/2022)
        implementation: Yannis Van Achter (v.2 10/02/2022)
    """
    line_split = str.split(line, ' ')
    
    db['foods'][(int(line_split[0]),int(line_split[1]))] = {
        'type' : line_split[2], 'energy' : int(line_split[3])
        }
    
    return db

def data_create(file_path : str , Player_1 : str , Player_2 : str)  -> (dict):
    """create all data request for the game
    
    Parameter:
    ----------
        file_path : path to file to  create map(str)

    Return:
    -------
        db: game database (dic)
        
    Version:
    --------
        specification: Yannis Van Achter (v.1 10/02/2022)
        implementation: Yannis Van Achter (v.1 10/02/2022)
    """
    file: list[str] = load_file(file_path).split('\n')
    db_alpha_game = {}
    processing = None
    for line in file:
        if line != '':
            if line == 'map:':
                processing = line[:-1]
            elif line == 'werewolves:':
                processing , db_alpha_game['wolves']= line[:-1] , {}
            elif line == 'foods:':
                processing , db_alpha_game['foods'] = line[:-1] , {}

            elif processing == 'map' and line != 'map:':
                db_alpha_game['board'] = create_map(line)
            elif processing == 'werewolves' and line != 'werewolves:':
                db_alpha_game = add_wolves(line, db_alpha_game , Player_1 , Player_2)
            elif processing == 'foods' and line != 'foods:':
                db_alpha_game = add_food(line, db_alpha_game)
    
    return db_alpha_game

def move_entity(old_coord : tuple , new_coord : tuple, db : dict)  -> (dict):
    """move data from old coordinate to new and delete old
    
    Parameters:
    -----------
        old_coord : actual coordinate (tuple)
        new_coord : new coordonate (tuple)
        db : data base of game (dic)
        
    Return:
    -------
        db: database update (dic)
    
    Version:
    --------
        specification: Yannis Van Achter (v.1 10/02/2022)
        implementation: Yannis Van Achter (v.1 10/02/2022)
    """
    if new_coord not in db['wolves']:
        data_item = db['wolves'][old_coord]
        db['wolves'][new_coord] = data_item
        db['wolves'].pop(old_coord)
    
    return db

def attack(attack_coord : tuple, target_coord : tuple, db : dict , copy : dict)  -> (dict):
    """attack the other wolve
    
    Parameters:
    -----------
        attack_coord : (y,x) (tuple)
        target_coord : (y,x) (tuple)
        db : database of game (dict)
        copy : copy of db on wich order are applied (dict)
        
    Return:
    -------
        db : upgrade database of game (dic)
        
    Version:
    --------
        specification: Yannis Van Achter (v.1 11/02/2022)
        implementation: Yannis Van Achter (v.1 11/02/2022)
    """
    if target_coord in db['wolves'] and attack_coord in db['wolves']:
        copy['wolves'][target_coord]['energy'] -= round((db['wolves'][attack_coord]['energy'] + db['wolves'][attack_coord]['bonus'])/10)
    
    return copy

def eat(wolve_coord : tuple, food_source : tuple, db : dict) -> (dict):
    """give health to wolve and substract heath to food
    
    Parameters:
    -----------
        wolve_coord : (y,x)(tuple)
        food_source : (y,x)(tuple)
        db : database of game (dic)
        
    Return:
    -------
        db : database updated (dic)
        
    Version:
    --------
        specification: Yannis Van Achter (v.1 11/02/2022)
        implementation: Yannis Van Achter (v.1 11/02/2022)
    """
    if wolve_coord in db['wolves'] and food_source in db['foods'] and 'property' not in db['foods'][food_source]:
        while db['foods'][food_source]['energy'] > 0 and db['wolves'][wolve_coord]['energy'] < 100:
            db['wolves'][wolve_coord]['energy'] += 1
            db['foods'][food_source]['energy'] -= 1
    
    return db

# -- Fonction of UI --
def show_map(db : dict) -> (None):
    """show map in terminal

    Parameter:
    -----------
        db : data base of game (dic)
        
    Version:
    -------
        specification : Yannis Van Achter (v1 21/02/2022)
        implementation : Yannis Van Achter (v1 21/02/2022)
    """
    clear()
    #  dictionary of numbers 𝐛𝐲 𝐄𝐬𝐭𝐞𝐛𝐚𝐧 𝐁𝐚𝐫𝐫𝐚𝐜𝐡𝐨.
    dict_number = {
        "1":"⁰¹","2":"⁰²","3":"⁰³","4":"⁰⁴","5":"⁰⁵","6":"⁰⁶",
        "7":"⁰⁷","8":"⁰⁸","9":"⁰⁹","10":"¹⁰","11":"¹¹","12":"¹²",
        "13":"¹³","14":"¹⁴","15":"¹⁵","16":"¹⁶","17":"¹⁷","18":"¹⁸",
        "19":"¹⁹","20":"²⁰","21":"²¹","22":"²²","23":"²³","24":"²⁴",
        "25":"²⁵","26":"²⁶","27":"²⁷","28":"²⁸","29":"²⁹","30":"³⁰",
        "31":"³¹","32":"³²","33":"³³","34":"³⁴","35":"³⁵","36":"³⁶",
        "37":"³⁷","38":"³⁸","39":"³⁹","40":"⁴⁰","41":"⁴¹","42":"⁴²",
        "43":"⁴³","44":"⁴⁴","45":"⁴⁵","46":"⁴⁶","47":"⁴⁷","48":"⁴⁸",
        "49":"⁴⁹","50":"⁵⁰","51":"⁵¹","52":"⁵²","53":"⁵³","54":"⁵⁴",
        "55":"⁵⁵","56":"⁵⁶","57":"⁵⁷","58":"⁵⁸","59":"⁵⁹","60":"⁶⁰",
        "61":"  "
    }
    id_wolve , wolve_list ,id_food , food_list = 0, sorted(list(db['wolves'].keys())),0 , sorted(list(db['foods'].keys()))
    for y in range(db['board']['y_max'] + 2):
        for x in range(db['board']['x_max'] + 2):
            if (x == 0 or x == (db['board']['x_max']+1) ) and  y !=0:
                string = (('  ') if (y == (db['board']['y_max']+1)) else str(dict_number[str(y)]))
            elif (y == 0 or y == (db['board']['y_max']+1)) and x != 0:
                string = (('  ') if x == (db['board']['x_max']+1) else str(dict_number[str(x)]))
            else:
                if (y,x) in db['wolves']:
                    string = str(find_entity((y,x) , db['wolves']))
                elif (y,x) in db['foods']:
                    string = str(find_entity((y,x) , db['foods']))
                else:
                    string = '  '
            print(string , end='|')
            
        if id_wolve < len(db['wolves']):
            print(f"Emoticone : {find_entity(wolve_list[id_wolve], db['wolves'])} : {wolve_list[id_wolve]} : Energy {db['wolves'][wolve_list[id_wolve]]['energy']}"+fore.DARK_BLUE + back.WHITE + style.RESET , end='')
            id_wolve += 1
        elif id_food < len(food_list):
            print(f"Emoticone : {find_entity(food_list[id_food], db['foods'])} : {food_list[id_food]} : Energy {db['foods'][food_list[id_food]]['energy']}"+fore.DARK_BLUE + back.WHITE + style.RESET , end='')
            id_food += 1
            
        print(('\n' + ('--+') * (db['board']['x_max'] + 2)) , end='')
        if id_wolve < len(db['wolves']):
            print(f"Emoticone : {find_entity(wolve_list[id_wolve], db['wolves'])} : {wolve_list[id_wolve]} : Energy {db['wolves'][wolve_list[id_wolve]]['energy']}"+fore.DARK_BLUE + back.WHITE + style.RESET , end='')
            id_wolve += 1
        elif id_food < len(food_list):
            print(f"Emoticone : {find_entity(food_list[id_food], db['foods'])} : {food_list[id_food]} : Energy {db['foods'][food_list[id_food]]['energy']}"+fore.DARK_BLUE + back.WHITE + style.RESET , end='')
            id_food += 1
        print()
    
    
def find_entity(position : tuple, db : dict) -> (str):
    """find emoji for entity based on positon

    Parameters:
    -----------
        db : part of data base of game (dic)
        position : coord (y,x) of entity (tuple)
        
    Note:
    -----
        The db is the part wich contain wolves or foods
        
    Version:
    -------
        specification : Yannis Van Achter (v1 21/02/2022)
        implementation : Yannis Van Achter (v1 21/02/2022)
    """
    # dictionary of objets 𝐛𝐲 𝐄𝐬𝐭𝐞𝐛𝐚𝐧 𝐁𝐚𝐫𝐫𝐚𝐜𝐡𝐨..
    colored_wolf = {"OMEGA_RED": fore.LIGHT_YELLOW + back.LIGHT_MAGENTA + "🐺" + style.RESET,
                "OMEGA_BLUE": fore.LIGHT_YELLOW + back.LIGHT_CYAN + "🐺" + style.RESET,
                "NORMAL_BLUE": fore.LIGHT_YELLOW + back.LIGHT_BLUE + "🐺" + style.RESET,
                "NORMAL_RED": fore.LIGHT_YELLOW + back.LIGHT_RED + "🐺" + style.RESET,
                "ALPHA_RED": fore.LIGHT_YELLOW + back.RED + "🐺" + style.RESET,
                "ALPHA_BLUE": fore.LIGHT_YELLOW + back.DARK_BLUE + "🐺" + style.RESET,
                "BERRIES": fore.LIGHT_RED + back.DARK_GREEN + "🍒" + style.RESET,
                "APPLES": fore.LIGHT_RED + back.DARK_GREEN + "🍎" + style.RESET,
                "RABBITS": fore.WHITE + back.DARK_GREEN + "🐇" + style.RESET,
                "DEERS": fore.YELLOW + back.DARK_GREEN + "🦌" + style.RESET,
                "MICE": fore.WHITE + back.DARK_GREEN + "🐭" + style.RESET,
                }
    if 'property' not in db[position]:
        try:
            return colored_wolf[db[position]['type'].upper()]
        except KeyError:
            return fore.WHITE + back.DARK_GREEN + "  " + style.RESET
    else : 
        wolve_to_show = db[position]['type'].upper() + ('_RED' if db[position]['property'] == 2 else '_BLUE')
        return colored_wolf[wolve_to_show]

def clear() -> (None):
    """Clear terminal 

    Version : 
    ---------
        Specification : Yannis Van Achter (v1 12/03/2022)
        implementation : Yannis Van Achter (v1 28/03/2022)
    """
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)

# -- Fonction of IA --
def get_IA_order(db : dict , player : int) -> (str):
    """get IA order of group 3

    Parameters:
    -----------
        db : data base of game (dict)
        player : number of player that IA is (int)
        
    Return:
    -------
        order_string : string of all order for each wolve (str)
    """
    copy = db
    order_string = ''
    orders: dict[int, list[str]] = {player : []}
    for wolve_coord in copy['wolves']:
        if copy['wolves'][wolve_coord]['property'] == player:
            # uncorrect_order = True
            # while uncorrect_order:
            action = choice(['*' , '<' , '@' , 'pacify'])
            if action == 'pacify' and str.startswith(copy['wolves'][wolve_coord]['type'] , 'omega'):
                order_string += f'{wolve_coord[0]}-{wolve_coord[1]}:{action} '
                orders[player].append(f'{wolve_coord[0]}-{wolve_coord[1]}:{action}')
            elif action == '@':
                on_y ,on_x = randint(-1,1) ,  randint(-1,1)
                new_coord = (wolve_coord[0] + on_y , wolve_coord[1] + on_x)
                if can_move(new_coord , wolve_coord , db):
                    order_string += f'{wolve_coord[0]}-{wolve_coord[1]}:{action}{new_coord[0]}-{new_coord[1]} '
                    orders[player].append(f'{wolve_coord[0]}-{wolve_coord[1]}:{action}{new_coord[0]}-{new_coord[1]}')
            elif action == '<':
                food_source_coord = get_entity_around(wolve_coord , db['foods'])
                if food_source_coord != None and can_eat(food_source_coord , wolve_coord) \
                    and db['wolves'][wolve_coord]['energy'] < 90 :
                    order_string += f'{wolve_coord[0]}-{wolve_coord[1]}:{action}{food_source_coord[0]}-{food_source_coord[1]}'
                    orders[player].append(f'{wolve_coord[0]}-{wolve_coord[1]}:{action}{food_source_coord[0]}-{food_source_coord[1]}')
            elif action == '*':
                target_coord = get_entity_around(wolve_coord , db['wolves'])
                if target_coord != None and can_attack(target_coord , wolve_coord , db) \
                    and db['wolves'][target_coord]['property'] != db['wolves'][wolve_coord]['property']:
                    order_string += f'{wolve_coord[0]}-{wolve_coord[1]}:{action}{target_coord[0]}-{target_coord[1]} '
                    orders[player].append(f'{wolve_coord[0]}-{wolve_coord[1]}:{action}{target_coord[0]}-{target_coord[1]}')
    
    return order_string.strip()


def get_entity_around(wolve_coord : tuple[int,int] , db : dict) -> (tuple[int, int]):
    """return the first entity around a wolve in the db

    Parameters:
    -----------
        wolve_coord : coord y,x of the entity on who we do research (list(int))
        db : part of database in which we do research (dict)

    Returns:
    --------
        target_coord : coord y,x of first entity found (list(int))
        
    Version:
    --------
        specification : Yannis Van Achter (v1. 09/03/2022)
        implementation : Yannis Van Achter (v1. 09/03/2022)
    """
    for entity_coord in db:
        if can_eat(entity_coord , wolve_coord):
            return entity_coord

# -- Fonctions of game --
def check_order(order: str) -> (bool):
    """Check if the order is a corrected formated 

    used regex expression to check is this order is corrected format

    Parameters:
    -----------
        order (str): one order 

    Returns:
    --------
        bool: True if this is corrected format
    
    """
    try:
        order = order.split(':')
        return (re.search(r"([@]{1}[1-60]{1}[\-]{1}[1-40]{1})|([\<]{1}[1-60]{1}[\-]{1}[1-40]{1})|pacify", order[1]) != None  or (re.search("[1-60]{1}[\-]{1}[1-40]{1}", order[1]) != None and order[1].startswith('*'))) and \
            ((re.search(r"([1-60]{1}[\-]{1}[1-40]{1})", order[0])) != None)
    except:
        return False


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
    string_order = ''
    order_entered = True
    my_wolves = [wolve for wolve, data in db['wolves'].items() if data['property'] == n_player] # get wolve of my team to ask for order
    print('If you don\'t want to write an order press \'enter\'')
    while len(my_wolves) != 0 and order_entered:
        my_wolves_copy = my_wolves.copy()
        for wolve_coord in my_wolves_copy:
            order = input(f'The player named : {player}, can enter his order for the wolve at \"{wolve_coord[0]}-{wolve_coord[1]}:').strip()
            if check_order(f"{wolve_coord[0]}-{wolve_coord[1]}:" + order):
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
        print(f"ValueError: this path does not exist or is not a file {map_path}")
        return None
    
    # create connection between 2 computer if nessesary
    connection = {}
    if type_1 == 'remote':
        try:
            connection[1] = create_connection(group_2, group_1)
        except Exception as error:
            exit(error)
    if type_2 == 'remote':
        try:
            connection[2] = create_connection(group_1, group_2)
        except Exception as error:
            exit(error)
        
    db: dict = data_create(map_path , group_1 , group_2)
    
    order = {}
    winner = []
    game_round = 0
    while len(winner) == 0 and game_round < 200:
        show_map(db)
        if type_1 == 'remote':
            order[1] = get_remote_orders(connection[1])
        elif type_1 == 'player':
            order[1] = get_instructions(group_1, db, 1)
        elif type_1 == 'IA':
            order[1] = get_IA_order(db , 1)
        if type_2 == 'remote':
            notify_remote_orders(connection[2], order[1])
        order[1] = order[1].split(' ')
        
        if type_2 == 'remote':
            order[2] = get_remote_orders(connection[2])
        elif type_2 == 'player':
            order[2] = get_instructions(group_2, db, 2)
        elif type_2 == 'IA':
            order[2] = get_IA_order(db , 2)
        if type_1 == 'remote':
            notify_remote_orders(connection[1], order[2])
        time.sleep(0.3)
        order[2] = order[2].split(' ')
        
        time.sleep(0.5)

        db, attacked = order_prosses(db, order)
        
        if attacked: # if any wolve attack an other the game end after 200 turn
            game_round +=1
        else:
            game_round = 0
        
        winner = game_over(db)
    
    show_map(db)
    
    if game_round < 200:
        if len(winner) == 2:
            print(f'Both of you won')
        elif winner[0] == 2:
            print(f'The winner is : {group_2}')
        elif winner[0] == 1:
            print(f'The winner is : {group_1}')
    else:
        total = {1 : 0, 2:0}
        for wolve, data in db['wolves'].items():
            total[data['property']] += data['energy']
        
        if total[1] == total[2]:
            print(f'Both of you won with security you have the same energy score : {total[1]}')
            winner = [1,2]
        elif total[1] > total[2]:
            print(f'The winner is : {group_1}')
            winner = [1]
        elif total[1] < total[2]:
            print(f'The winner is : {group_2}')
            winner = [2]
      
    # close connection, if necessary
    if type_1 == 'remote':
        close_connection(connection[1])
    if type_2 == 'remote':
        close_connection(connection[2])    
    
    return winner

        
def order_prosses(db : dict , orders : dict) -> (dict):
    """db modification proccess
    
    Parameters:
    -----------
        db : database of game (dic)
        orders : print of player (dict)
    
    Return:
    -------
        [dict]: dictionnary of all modification to do the data baser
        [bool]: True if at least one order was to attack a wolf otherwise False
        
    Version:
    --------
        specification: Yannis Van Achter (v.1 11/02/2022)
        implementation: Yannis Van Achter (v.2 13/02/2022)
    """
    used_wolves = []
    
    db , passifier, used_wolves = pacified(db , orders=orders) # pacification 
    
    db = get_bonus(db)
    if type(db) == tuple:
        db = db[0]
    
    db , used_wolves = get_eat(db, orders, used_wolves)
    
    db , used_wolves, attacked = fight(db, orders , used_wolves)

    db, used_wolves = get_move_order(db , orders , used_wolves)
    
    db = get_bonus(db , False)
    
    db , passifier , used_wolves = pacified(db, passifier = passifier , value  =  False) # dépacification 
    
    return db, attacked

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
    if type(db) == tuple:
        db = db[0]
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
                            db = eat(wolve , target_coord, db)
                            used_wolves.append(wolve)
            if type(db) == tuple:
                db = db[0]
    
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
                        db = move_entity(wolve, new_coord, db)
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
    copy_ = copy.deepcopy(db)
    attacked = False
    for player in orders:
        for order in orders[player]:
            if len(order) >= 7:
                order = str.split(order, ':')
                wolve = get_entity_coord(str.strip(order[0])) 
                if wolve in db['wolves'] and str.startswith(order[1], '*') and (wolve not in used_wolves) \
                    and db['wolves'][wolve]['property'] == player:
                    target_coord = get_entity_coord(str.strip(order[1][1:])) # saut de 1 pour aller direct après le '*'
                    if can_attack(target_coord , wolve , db):
                        db = attack(wolve , target_coord, db, copy_)
                        if db['wolves'][target_coord]['energy'] < 0:
                            db['wolves'][target_coord]['energy'] = 0
                        used_wolves.append(wolve)
                        attacked = True
                    
    return copy_, used_wolves, attacked

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
                            if db['wolves'][wolve]['energy'] >= 40 and  db['wolves'][wolve]['property'] == player:
                                db['wolves'][wolve]['energy'] -= 40
                                used_wolves.append(wolve)
                                for y in range(wolve[0]-6, wolve[0]+7):
                                    for x in range(wolve[1]-6, wolve[1]+7):
                                        if (y,x) in db['wolves']:
                                            db['wolves'][(y,x)]['passified'] = value
                                            passifier.append((y,x))

    else:
        for wolve in db['wolves']:
            db['wolves'][wolve]['passified'] = value
        passifier = []
    
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

    ask and transform input sting into int

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
    prompt = ''.join(map(str, prompt))
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
    
    clear()
    
    type_player = ('player', 'IA', 'remote')

    # load history of winner
    if pt.isfile('./winner_history.txt'):
        file = load_file('./winner_history.txt')
        all_winner = ast.literal_eval(file)
    else:
        all_winner = {}
    
    conti = input('Start a game ? (yes/no) : ').lower()
    while conti.startswith('y'):
        map_path = './map/'
        map_path = map_path + choice(os.listdir(map_path)) if input('Do you want a random map ? (yes/no) : ').lower().startswith('y') else input('Enter the map path \n here: ')
        type_1: str =  get_type(f"Who play this game as player 1 {type_player}: ")
        type_2: str = get_type(f"Who play this game as player 2 {type_player}: ")
        group_1: int =  get_int('Enter the id of the player : ') if type_1 == 'remote' or type_2 == 'remote' else input('Enter your user name : ')
        group_2: int = get_int('Enter the id of the player : ') if type_2 == 'remote' or type_1 == 'remote' else input('Enter your user name : ')
 
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
    