"""
data_manager module for Python 3.9. Based on INFOB132 year 2021-2022 request at UNamur
"""
__author__  ="Yannis Van Achter <yannis.van.achter@gmail.com>"
__date__    = "27 February 2022"
__version__ = "1.0"


# --- Modules ---
# native
import os.path as pt

# -- Anonimous Fonction -- 
set_board_value = lambda size, min=20, max=40: max if size > max else (min if size < min else size)

# --- Fonction ---
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
    
    db['wolves'][(int(line_split[1]),int(line_split[2]))] = {
    'type' : line_split[3].lower(), 'energy' : 100, 
    'property' : int(line[0]), 'bonus' : 0 , 'passified' : False
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

def data_create(file_path : str , Player_1 : str , Player_2 : str)  -> (dict[str, dict[tuple,dict[str, int]]]):
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
    file = load_file(file_path).split('\n')
    
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

def attack(attack_coord : tuple, target_coord : tuple, db : dict)  -> (dict):
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
        db['wolves'][target_coord]['energy'] -= int((db['wolves'][attack_coord]['energy'] + db['wolves'][attack_coord]['bonus'])/10)
    
    return db

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

if __name__ == '__main__':
    db = data_create('./example.ano.txt' , 'IA' , 'AI')
    for key in db:
        print(f'{key} : {db[key]}')