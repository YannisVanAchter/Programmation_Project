
from .view import View

class UserView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def user_input(self):
        # TODO: Make a better input than in basic view
        pass
     