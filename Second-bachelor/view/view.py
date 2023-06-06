# encoding: utf-8
"""Provides the View class.

This module provides a class to display the game state and ask the user for an input.
Calling a display method will clear the terminal and then call the method.

This View class is the base class for all the views of the game.
We need to implement the following methods:
    - set_size(map_size: dict[str, int])
    - init_connection(player: int)
    - send_order(order: str)
    - display_winner(winner: int, name: str = None)
    - display_error(error: Exception)
    - display_map()
    - user_input()
    
The example below is an implementation of the View class that interact in the terminal.

"""
__author__ = "Yannis Van Achter"
__version__ = "1.0.0"
__date__ = "2023-06-17"

# python modules
import os
from typing import Union

# pip modules
from colored import back, fore, style

# controlers
from databasecontroler import DatabaseControler
from gamecontroler import GameControler

# models and views
from model.wolf import Wolf
from model.food import Food

def display(func):
    def wrap(self: View, *args, **kwargs):
        self.clear_terminal()
        func(self, *args, **kwargs)
    return wrap

class View:
    """Basic view model
    
    Terminal view of the game

    Attributes:
    -----------
        None
        
    Methods:
    --------
        set_size(map_size: dict[str, int])
            Define the size of the map
        clear_terminal()
            Clear the terminal
        init_connection(player: int)
            Init the connection with the remote player
        display_map()
            display the game state
        user_input()
            Ask the user for an input and return it
        send_order(order: str)
            Send an order to the remote player
        display_winner(winner: int, name: str = None)
            Display the winner of the game
        display_error(error: Exception)
            Display an error message
        
    """
    
    def __init__(self, database, controler: GameControler, player: int, nb_player: int):
        self._controler: GameControler = controler
        self._database: DatabaseControler = database
        self._map_size = None
        self._player = player
        self._dict_number = { 
            # dictionary of numbers 𝐛𝐲 𝐄𝐬𝐭𝐞𝐛𝐚𝐧 𝐁𝐚𝐫𝐫𝐚𝐜𝐡𝐨. (modifed by Yannis Van Achter)
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
            "61":"  ", "0": "  ",
        }
        self._colored_food = {
            "BERRIES": fore.LIGHT_RED + back.DARK_GREEN + "🍒" + style.RESET,
            "APPLES": fore.LIGHT_RED + back.DARK_GREEN + "🍎" + style.RESET,
            "RABBITS": fore.WHITE + back.DARK_GREEN + "🐇" + style.RESET,
            "DEERS": fore.YELLOW + back.DARK_GREEN + "🦌" + style.RESET,
            "MICE": fore.WHITE + back.DARK_GREEN + "🐭" + style.RESET,
        }
        self._colored_wolf = { # how to automatically generate this dictionary based on nb_player ?
            # ...
            # ("omega", 3): fore.BLACK + back.LIGHT_YELLOW + "🐺" + style.RESET,
            # ("normal", 3): fore.BLACK + back.LIGHT_GREEN + "🐺" + style.RESET,
            # ("alpha", 3): fore.BLACK + back.LIGHT_WHITE + "🐺" + style.RESET,
            
            ("omega", 2): fore.LIGHT_YELLOW + back.LIGHT_MAGENTA + "🐺" + style.RESET,
            ("normal", 2): fore.LIGHT_YELLOW + back.LIGHT_RED + "🐺" + style.RESET,
            ("alpha", 2): fore.LIGHT_YELLOW + back.RED + "🐺" + style.RESET,
            
            ("omega", 1): fore.LIGHT_YELLOW + back.LIGHT_CYAN + "🐺" + style.RESET,
            ("normal", 1): fore.LIGHT_YELLOW + back.LIGHT_BLUE + "🐺" + style.RESET,
            ("alpha", 1): fore.LIGHT_YELLOW + back.DARK_BLUE + "🐺" + style.RESET,
        }
    
    def set_size(self, map_size: dict[str, int]):
        """Define the size of the map

        Args:
            map_size (dict[str, int]): the size of the map in x and y coordinate

        Raises:
            KeyError: if map_size doesn't have a key 'x' or 'y'
            ValueError: if map_size['x'] or map_size['y'] is not between MIN_MAP_SIZE[axis] and MAX_MAP_SIZE[axis]
        """
        if "x" not in map_size:
            raise KeyError("map_size must have a key 'x' that store the max x coordinate")
        if "y" not in map_size:
            raise KeyError("map_size must have a key 'y' that store the max y coordinate")
        
        x = map_size["x"]
        y = map_size["y"]
        
        self._map_size = {"x": x, "y": y}
        
    def clear_terminal(self):
        """Clear the terminal"""
        command = "clear"
        if os.name in ("nt", "dos"):
            command = "cls"
        os.system(command)
        
    def init_connection(self, my_group, player: int):
        """Init the connection with the remote player
        
        Args:
        -----
            my_group (int): the group of the player
            player (int): the group id of the other player
        """
        pass
    
    def send_order(self, order: str):
        """Send an order to the remote player

        Args:
            order (str): the order to send
        """
        pass
    
    def close_connection(self):
        """Close the connection with the remote player"""
        pass
    
    def user_input(self):
        """Ask the user for an input and return it
        
        Return:
        -------
            str : the user input
        """
        return input("Enter the list of instruction: ").strip().lower()
        
    @display
    def display_map(self):
        """display the game state"""
        map = ""
        for y in range(self._map_size["y"] + 2):
            for x in range(self._map_size["x"] + 2):
                # header and footer
                if (self._map_size["y"] + 1 == y or y == 0) and x != 0:
                    map += back.WHITE + self._dict_number[str(x)] + style.RESET
                    continue
                if (self._map_size["x"] + 1 == x or x == 0) and y != 0:
                    map += back.WHITE + self._dict_number[str(y)] + style.RESET
                    continue
                
                entity = self._database.get_entity((x, y))
                if isinstance(entity, (Wolf, Food)):
                    map += self._get_entity_string(entity)
                else:
                    map += back.WHITE + "  " + style.RESET
                map += '|'
            map += "\n"
            
        # clear the terminal and print the updated map
        self.clear_terminal()
        print(map)
        
    def _get_entity_string(self, entity: Union[Wolf, Food]):
        if isinstance(entity, Wolf):
            return self._colored_wolf[(entity.type.lower(), entity.player)]
        elif isinstance(entity, Food):
            return self._colored_food[entity.type.upper()]
        else:
            return fore.RED + back.WHITE + "??" + style.RESET
    
    @display
    def display_winner(self, winner: int, name: str = None):
        """Display the winner of the game

        Args:
            winner (int): the id of the winner
            name (str, optional): the name of the winner. Defaults to None.
        """
        if name is None:
            name = f"Player {winner}"
        print(fore.GREEN + f"{name} won the game" + style.RESET)
    
    @display
    def display_error(self, error: Exception):
        """Display an error message

        Args:
            error (str): the error message
        """
        print(fore.RED + str(error).upper() + style.RESET)
        print("### ORIGINAL ERROR ###")
        print(type(error), str(error))
        print(error.__traceback__)
