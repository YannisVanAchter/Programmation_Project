
from view import View

from databasecontroler import DatabaseControler
from rulescontroler import RulesControler, MAX_GAME_LOOP

class GameControler:
    def __init__(self, database: DatabaseControler, views: list[View]):
        self._database = database
        
        self._views = views
        self._map_size = database.get_map_size()
        
        self._rules = RulesControler(database)
        self._view_on_this_computer = View(database, self._rules, 1)
    
    @property
    def winner(self):
        return self._rules.get_winner()
        
    def run(self):
        self._init()
        
        for game_id in range(MAX_GAME_LOOP):
            self._view_on_this_computer.display_map()
            for view_id, view in enumerate(self._views):
                instruction = view.user_input()
                
                self._rules.instruction_setter(instruction, view_id + 1)
                
                # Send the previous instruction to the next view
                for othre_view_id in range(0, len(self._views)):
                    if othre_view_id != view_id:
                        self._views[othre_view_id].send_order(instruction)
                
            self._rules.apply_instruction()
            
            if self._rules.is_winner(game_id):
                break
        
        for view in self._views:
            view.close_connection()
        
        return self._rules.get_winner()
    
    def _init(self):
        for view_id, view in enumerate(self._views):
            view.set_size(self._map_size)
            view.init_connection(view_id + 1, ((view_id + 2) % len(self._views)))
        
        self._rules.check_pre_condition()
        
    def _end(self):
        for view in self._views:
            view.close_connection()
            
        self._view_on_this_computer.display_map()
