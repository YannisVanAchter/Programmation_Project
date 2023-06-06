# encoding: utf-8

from .view import View

from databasecontroler import DatabaseControler
from rulescontroler import RulesControler
from ia import get_ia_order

class AIView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def user_input(self):
        return get_ia_order(self._database, self._controler._rules)
    
    def display_map(self):
        return 
    
    def display_winner(self, winner: int, name: str = None):
        return 
    