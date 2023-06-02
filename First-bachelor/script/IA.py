"""
IA module for Python 3.9. Based on INFOB132 year 2021-2022 request at UNamur
"""
__author__  ="Yannis Van Achter <yannis.van.achter@gmail.com>"
__date__    = "17 march 2022"
__version__ = "1.2"


# -- Modules --
# native module
import ast
import copy
import pickle as pkl

# self modules
try:
    import engine_gr_3 as eng
except ModuleNotFoundError:
    import script.engine_gr_3 as eng

# -- IA funcitons --
def get_IA_order(db : dict , player : int, order_1 : list[str] = []) -> (str):
    """return a formated string of order

    Parameters:
    -----------
        db (dict): database of Game
        player (int): n° of player we are
        order_1 (list[str]): list of order of the first player. Default to empty list
        
    Returns:
    -------
        order_string : string of all order for each wolve
        old_db : old dict of data base 
        
    Notes:
    ------
        The format of a order is the folowing one
        y-x:ayt-xt
        y, x : coord of entity which recieve the order
        a is the action:
            - @ to move at folowing coordonates
            - * to attack the entity at folowing coordonates
            - < to eat at folowing coordonates
            - pacify (only for a omega wolf type) pacify in range of 6 cases arround him
        yt, xt : coord where the action is apply (not requiered if we pacify)
        this encoding is repeated for each wolve 
    
    Versions:
    ---------
        specification: Yannis Van Achter
        implementation: Yannis Van Achter
    """
    fh = open("old_db.txt", "w")
    fh.write(str(db))
    fh.close()
    
    if player == 2:
        db = eng.pacified(db, orders={1:order_1})
        db = eng.get_eat(db, {1:order_1}, [])[0]
        db = eng.fight(db, {1:order_1}, [])[0]
    
    
    wolve_own = [_ for _ in db['wolves'] if db['wolves'][_]['property'] == player] # list of my wolves
    order_string = ''
    one_order_found = True
    while len(wolve_own) != 0 and one_order_found:
            
        _copy_wolve_own_ = copy.deepcopy(wolve_own)
        orders = {player : []}
        for wolve_coord in _copy_wolve_own_:
            if type(db) == tuple:
                db = db[0]
            # print(wolve_coord)
            # print(db['wolves'])
            if wolve_coord not in db['wolves']:
                pass
            elif db['wolves'][wolve_coord]['property'] == player:
                returned = track_alpha(db , wolve_coord, player)
                if type(db) == tuple:
                    db = db[0]
                if returned != None and len(returned) >= 4:
                    order_string += f'{wolve_coord[0]}-{wolve_coord[1]}' + returned
                    orders[player].append((f'{wolve_coord[0]}-{wolve_coord[1]}' + returned).strip())
                    wolve_own.remove(wolve_coord)
            
            if type(db) == tuple:
                db = db[0]
        if type(db) == tuple:
            db = db[0]

        db = eng.order_prosses(db , orders)[0]
               
        if len(_copy_wolve_own_) == len(wolve_own):
            one_order_found = False
    
    old_db = eng.load_file('./old_db.txt')
    old_db = ast.literal_eval(old_db)
    
    return order_string.strip() , old_db

def track_alpha(db , wolve_coord , player):
    """get order for this wolve if we apply the huntinf of alpha strategy

    Parameters:
    -----------
        db : data base of game (dict)
        wolve : name of wolve in process (str)
        player : number of player we are (int)

    Returns:
    --------
        order : order apply to this wolve (str)
        
    Version:
    --------
        specification : Yannis Van Achter (v1 23/03/04)
        implementation : Yannis Van Achter (v1 23/03/04)
    """
    wolve_data = db['wolves'][wolve_coord]
    
    enemy_wolves = [_ for _ in db['wolves'] if db['wolves'][_]['property'] != player] # list of enemy wolves
    alpha_coord = [wolf for wolf in enemy_wolves if str(db['wolves'][wolf]['type']).lower() == 'alpha'][0] # get coord of alpha
    
    if  wolve_data['energy'] > 5:
        alpha_path = get_trajectory(alpha_coord,  wolve_coord, db)
        if eng.can_attack(alpha_coord , wolve_coord, db):
            return f":*{alpha_coord[0]}-{alpha_coord[1]} "
        elif alpha_path in db and eng.can_attack(alpha_path, wolve_coord, db) \
            and db['wolves'][alpha_path]['property'] != player:
            return f":*{alpha_path[0]}-{alpha_path[1]} "
        else:
            wolve_around = get_entity_around(wolve_coord, db['wolves'])
            if len(wolve_around) == 1 and db['wolves'][wolve_around[0]]['property'] != player:
                target_coord = wolve_around[0]
                return f":*{target_coord[0]}-{target_coord[1]} "
            else:
                # get most dangerous
                most_dangerous = ''
                max_energy = 0
                for enemy in wolve_around:
                    if db['wolves'][enemy]['energy'] > max_energy and db['wolves'][enemy]['property'] != player:
                        most_dangerous = enemy
                        max_energy = db['wolves'][enemy]['energy']
                
                if most_dangerous != '': # there is a wolve arround wich is not ours
                    return f":*{most_dangerous[0]}-{most_dangerous[1]} " 
                
                elif eng.can_move(alpha_path , wolve_coord , db):
                    return f":@{alpha_path[0]}-{alpha_path[1]} "
    else:
        food_target_coord = find_nearrest_food(wolve_coord, db)
        if len(food_target_coord) >= 1 and eng.can_eat(food_target_coord[0], wolve_coord):
            food_target_coord = food_target_coord[0]
            return f":<{food_target_coord[0]}-{food_target_coord[1]} "
        else:
            # get coord of our alpha
            alpha_own = [_ for _ in db['wolves'] if str(db['wolves'][_]['type']).lower() == 'alpha' and db['wolves'][_]['property'] == player][0]
            alpha_shield = get_trajectory(alpha_own, wolve_coord, db)
            if eng.get_distance(wolve_coord, alpha_shield) > 1:
                return f":@{alpha_shield[0]}-{alpha_shield[1]} "


def find_nearrest_food(wolve : tuple[int, int], db : dict , min_energy : int = 100) -> (list[tuple[int,int]]):
    """find and short all food source based on coord of wolve

    Parameters:
    -----------
        wolve : wolve coord (tuple[int,int])
        db : part of data base of game which contain food (dict)
        min_energy : minimum required energy (int)

    Return:
    --------
        food_list : list of food wich have ennough energy and sort by distance (list[tuple[int,int], ...])
        
    Version:
    --------
        specification : Yannis Van Achter (v1. 19/03/2022)
        implementation : Yannis Van Achter (v1. 19/03/2022)
    """
    food_list = list(db['foods'].keys())
    # remove food wich don't hava enough energy
    poped = True
    while poped:
        copy = food_list
        poped = False
        for food in copy:
            if (db['foods'][food]['energy'] < min_energy or min_energy == 0) and not poped:
                food_list.remove(food)
                poped = True
                
    # short list by energy
    moved = True
    while moved:
        moved = False
        for food_id in range(1, len(food_list)):
            if db['foods'][food_list[food_id-1]]['energy'] < db['foods'][food_list[food_id]]['energy']:
                moved = True
                food_list[food_id-1], food_list[food_id] = food_list[food_id], food_list[food_id-1] # swap
                
    # sort list by distance
    moved = True
    while moved:
        moved = False
        for id in range(1, len(food_list)):
            if eng.get_distance(wolve , food_list[id-1]) > eng.get_distance(wolve , food_list[id]):
                moved= True
                temp = food_list[id-1]
                food_list[id-1] = food_list[id]
                food_list[id] = temp
    
    return food_list


def get_trajectory(target_coord : tuple[int,int], wolve_coord : tuple[int,int], db: dict, tested: list = []) -> (tuple[int,int]):
    """return the trajectory from wolve to a target

    Parameters:
    -----------
        wolve_coord : wolve coord (tuple[int,int])
        target_coord : target entity coord (tuple[int,int])
        db : data base of game (dict)

    Returns:
    --------
        next_position : the next positon to go at the target (tuple[int,int])
        
    Version:
    --------
        specification : Yannis Van Achter (v1. 19/03/2022)
        implementation : Yannis Van Achter (v1. 19/03/2022)
    """
    def basic_direction(target_coord: tuple[int,int], wolve_coord: tuple[int,int])-> (tuple[int,int]):
        if eng.can_eat(target_coord , wolve_coord):
            return target_coord
        destination = list(wolve_coord).copy()
        delta_x = target_coord[1] - destination[1]
        delta_y = target_coord[0] - destination[0]
        if delta_x < 0:
            destination[1] -= 1
        elif delta_x > 0:
            destination[1] += 1
        if delta_y < 0:
            destination[0] -= 1
        elif delta_y > 0:
            destination[0] += 1
        
        return tuple(destination)
    
    def complex_direction(target_coord: tuple[int,int], wolve_coord: tuple[int,int], db: dict, tested: list[tuple]) -> (tuple[bool,tuple[int,int]]):
        tested.append(wolve_coord)
        if eng.can_eat(target_coord, wolve_coord):
            return True, tested
        for y in range(wolve_coord[0]-1, wolve_coord[0]+2):
            for x in range(wolve_coord[1]-1,wolve_coord[1]+2):
                if (y,x) not in tested:
                    tested.append((y,x))
                    if eng.can_move((y,x), wolve_coord, db):
                        direction = get_trajectory(target_coord, (y,x), db, tested)
                        if direction == target_coord:
                            return True , tested
                    else:
                        return complex_direction(target_coord, wolve_coord, db, tested)
        return False, tested
    
    
    direction = basic_direction(target_coord, wolve_coord)
    if not eng.can_move(direction, wolve_coord, db):
        tested += [direction, wolve_coord]
        posibility = {}
        for y in range(wolve_coord[0]-1, wolve_coord[0]+2):
            for x in range(wolve_coord[1]-1,wolve_coord[1]+2):
                if (y,x) not in tested:
                    tested.append((y,x))
                    if complex_direction(target_coord, (y,x), db, tested)[0]:
                        dist = eng.get_distance((y,x), target_coord)
                        posibility[dist] = (y,x)
        if len(posibility) != 0:
            direction = posibility[min(list(posibility.keys()))] # get coord to go by the minimum distance from wolve to target
    return direction

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
    entity_around = []
    for entity_coord in db:
        if eng.can_eat(entity_coord , wolve_coord):
            entity_around.append(entity_coord)
    return entity_around

if __name__=='__main__':
    db = {'board': {'y_max': 20, 'x_max': 20}, 
        'wolves': {(11, 10): {'type': 'alpha', 'energy': 100, 'property': 1, 'bonus': 0, 'passified': False, 'Player': 'IA'}, 
            (1, 1): {'type': 'omega', 'energy': 100, 'property': 1, 'bonus': 0, 'passified': False, 'Player': 'IA'}, 
            (1, 2): {'type': 'normal', 'energy': 100, 'property': 1, 'bonus': 0, 'passified': False, 'Player': 'IA'}, 
            (2, 1): {'type': 'normal', 'energy': 100, 'property': 1, 'bonus': 0, 'passified': False, 'Player': 'IA'}, 
            (1, 3): {'type': 'normal', 'energy': 100, 'property': 1, 'bonus': 0, 'passified': False, 'Player': 'IA'}, 
            (2, 3): {'type': 'normal', 'energy': 100, 'property': 1, 'bonus': 0, 'passified': False, 'Player': 'IA'},
            (3, 3): {'type': 'normal', 'energy': 100, 'property': 1, 'bonus': 0, 'passified': False, 'Player': 'IA'},
            (3, 2): {'type': 'normal', 'energy': 100, 'property': 1, 'bonus': 0, 'passified': False, 'Player': 'IA'},
            (3, 1): {'type': 'normal', 'energy': 100, 'property': 1, 'bonus': 0, 'passified': False, 'Player': 'IA'},
            (10, 11): {'type': 'alpha', 'energy': 5, 'property': 2, 'bonus': 0, 'passified': False, 'Player': 'AI'}, 
            (20, 20): {'type': 'omega', 'energy': 100, 'property': 2, 'bonus': 0, 'passified': False, 'Player': 'AI'}, 
            (20, 19): {'type': 'normal', 'energy': 100, 'property': 2, 'bonus': 0, 'passified': False, 'Player': 'AI'}, 
            (19, 20): {'type': 'normal', 'energy': 100, 'property': 2, 'bonus': 0, 'passified': False, 'Player': 'AI'}, 
            (20, 18): {'type': 'normal', 'energy': 100, 'property': 2, 'bonus': 0, 'passified': False, 'Player': 'AI'}, 
            (19, 18): {'type': 'normal', 'energy': 100, 'property': 2, 'bonus': 0, 'passified': False, 'Player': 'AI'}, 
            (18, 18): {'type': 'normal', 'energy': 100, 'property': 2, 'bonus': 0, 'passified': False, 'Player': 'AI'}, 
            (18, 19): {'type': 'normal', 'energy': 100, 'property': 2, 'bonus': 0, 'passified': False, 'Player': 'AI'}, 
            (18, 20): {'type': 'normal', 'energy': 100, 'property': 2, 'bonus': 0, 'passified': False, 'Player': 'AI'}}, 
        'foods': {(4, 4): {'type': 'berries', 'energy': 0}, (4, 5): {'type': 'berries', 'energy': 0},
                  (5, 4): {'type': 'berries', 'energy': 0}, (5, 5): {'type': 'berries', 'energy': 0}, 
                  (16, 16): {'type': 'berries', 'energy': 0}, (16, 17): {'type': 'berries', 'energy': 0}, 
                  (17, 16): {'type': 'berries', 'energy': 0}, (17, 17): {'type': 'berries', 'energy': 0}, 
                  (1, 4): {'type': 'apples', 'energy': 0}, (1, 5): {'type': 'apples', 'energy': 0},
                  (20, 16): {'type': 'apples', 'energy': 0}, (20, 17): {'type': 'apples', 'energy': 0}, 
                  (4, 1): {'type': 'mice', 'energy': 0}, (5, 1): {'type': 'mice', 'energy': 0}, 
                  (16, 20): {'type': 'mice', 'energy': 0}, (17, 20): {'type': 'mice', 'energy': 0}, 
                  (5, 7): {'type': 'rabbits', 'energy': 0}, (7, 5): {'type': 'deers', 'energy': 0}, 
                  (16, 14): {'type': 'rabbits', 'energy': 0}, (14, 16): {'type': 'deers', 'energy': 0}}}
    print('1')
    order_1, db = get_IA_order(db, 1)
    print(order_1)
    print('2')
    order_2, db = get_IA_order(db, 2, order_1.split(' '))
    print(order_2)