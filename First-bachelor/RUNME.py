"""
game file for Python 3.9. Based on INFOB132 year 2021-2022 request at UNamur
"""
__author__  ="Yannis Van Achter <yannis.van.achter@gmail.com>"
__date__    = "15 april 2022"
__version__ = "1.0"


# -- Modules --
# native modules
from time import sleep

# self modules
from script.game import launch_game as gm # file where I test and write new code
from script.engine_gr_3 import launch_game as eng # file where everything is ready to use

if __name__=="__main__":
    if input('Do you want run the file where you can find an IA ? (yes/no) : ').lower().startswith('y'):
        print('The game will be run in the game.py file module')
        sleep(1)
        gm()
    else:
        print('The game will be run in the engine_gr_3.py file this file have an AI based on random choice')
        sleep(1)
        eng()