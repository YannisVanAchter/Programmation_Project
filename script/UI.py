"""
data_manager module for Python 3.9. Based on INFOB132 request at UNamur
"""
__author__  ="Yannis Van Achter <yannis.van.achter@gmail.com>"
__date__    = "27 February 2022"
__version__ = "1.0"

# -- Modules --
# native modules
import platform
import os

# pip modules
from colored import style, fore, back

# --- Anonimous function ---
format_string = lambda string : string +fore.GOLD_1 + back.DARK_BLUE + style.RESET

# --- Function ---
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
    #  dictionary of numbers 𝐛𝐲 𝐄𝐬𝐭𝐞𝐛𝐚𝐧 𝐁𝐚𝐫𝐫𝐚𝐜𝐡𝐨. (modifed by Yannis Van Achter)
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
    to_show = ''
    id_wolve , wolve_list = 0, list(db['wolves'].keys())
    for y in range(db['board']['y_max'] + 2):
        for x in range(db['board']['x_max'] + 2):
            if (x == 0 or x == (db['board']['x_max']+1) ) and  y !=0:
                to_show += str(dict_number[str(y)])
            elif (y == 0 or y == (db['board']['y_max']+1)) and x != 0:
                to_show += str(dict_number[str(x)])
            else:
                if (y,x) in db['wolves']:
                    to_show += str(find_entity((y,x) , db['wolves']))
                elif (y,x) in db['foods']:
                    to_show += str(find_entity((y,x) , db['foods']))
                else:
                    to_show += '  '
            to_show += '|'
            
        if id_wolve < len(db['wolves']):
            to_show += (f"Emoticone : {find_entity(wolve_list[id_wolve], db['wolves'])} : {wolve_list[id_wolve]} : Energy {db['wolves'][wolve_list[id_wolve]]['energy']}, type : {db['wolves'][wolve_list[id_wolve]]['type']}"+fore.DARK_BLUE + back.WHITE + style.RESET)
            id_wolve += 1
            
        to_show += (('\n' + ('--+') * (db['board']['x_max'] + 2))+fore.DARK_BLUE + back.WHITE + style.RESET)
        
        if id_wolve < len(db['wolves']):
            to_show += (f"Emoticone : {find_entity(wolve_list[id_wolve], db['wolves'])} : {wolve_list[id_wolve]} : Energy {db['wolves'][wolve_list[id_wolve]]['energy']}, type : {db['wolves'][wolve_list[id_wolve]]['type']}"+fore.DARK_BLUE + back.WHITE + style.RESET)
            id_wolve += 1
        to_show += '\n'
    clear()
    print(to_show)
    
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
    colored_wolf = {
        "OMEGA_RED": fore.LIGHT_YELLOW + back.LIGHT_MAGENTA + "🐺" + style.RESET,
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
        "RED" : back.LIGHT_RED + "  " + style.RESET,
        "BLUE" :back.LIGHT_BLUE + "  " + style.RESET,
    }
    if 'property' not in db[position]: # this is not a wolve
        try:
            return colored_wolf[db[position]['type'].upper()]
        except KeyError:
            return fore.WHITE + back.DARK_GREEN + "  " + style.RESET
    else : # this is a wolve
        wolve_to_show = db[position]['type'].upper() + ('_RED' if db[position]['property'] == 2 else '_BLUE')
        try:
            return colored_wolf[wolve_to_show]
        except KeyError:
            return colored_wolf["RED" if str.endswith(wolve_to_show, 'RED') else 'BLUE']

def clear() -> (None):
    """Clear terminal 

    Version : 
    ---------
        Specification : Yannis Van Achter (v1 04/03/2022)
        implementation : Yannis Van Achter (v1 04/03/2022)
    """
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)

if __name__ == '__main__':
    db = {'board': {'y_max': 40, 'x_max': 60}, 
        'wolves': {(2, 1): {'type': 'alpha', 'energy': 100, 'property': 'Player_1', 'bonus': 0, 'passified': False}, 
                (2, 10): {'type': 'omega', 'energy': 100, 'property': 'Player_1', 'bonus': 0, 'passified': False}, 
                (30, 59): {'type': 'normal', 'energy': 100, 'property': 'Player_1', 'bonus': 0, 'passified': False}, 
                (10, 20): {'type': 'normal', 'energy': 100, 'property': 'Player_1', 'bonus': 0, 'passified': False}, 
                (19, 31): {'type': 'alpha', 'energy': 100, 'property': 'Player_2', 'bonus': 0, 'passified': False}, 
                (19, 29): {'type': 'omega', 'energy': 100, 'property': 'Player_2', 'bonus': 0, 'passified': False}, 
                (38, 1): {'type': 'normal', 'energy': 100, 'property': 'Player_2', 'bonus': 0, 'passified': False}, 
                (38, 20): {'type': 'normal', 'energy': 100, 'property': 'Player_2', 'bonus': 0, 'passified': False}}, 
        'foods': {(39, 4): {'type': 'fraise', 'energy': 20, 'property': 'Player_0'}, 
                (10, 32): {'type': 'mice', 'energy': 30, 'property': 'Player_0'}}
        }
    show_map(db)