# encoding utf-8

import json

# model and views
from view import View

# other controler
from databasecontroler import DatabaseControler
from gamecontroler import GameControler

class Controler:
    def __init__(self):
        self._database: DatabaseControler = None
        self._views: list[View] = []
        self._game: GameControler = None
        
    def run(self):
        pass
    
    def _get_player_number(self):
        pass
    
    def _get_map_path(self):
        pass
    
    def _init_database(self):
        pass
    
    def _init_views(self):
        pass
    
    def _init_game(self):
        pass
    
    def launch_game(self):
        self._game = GameControler(self._database, self._views)
    
    def store_winner(self):
        pass
    
    def load_winner(self):
        pass

def main():
    controler = Controler()
    controler.run()

if __name__ == "__main__":
    main()