# encoding: utf-8
"""Provides the Wolf class."""

__author__  = "Yannis Van Achter"
__date__    = "2023-06-16"
__version__ = "1.0"


class Wolf:
    """Wolf class

    Attributes (getters):
    ---------------------
        type : type of wolf (str)
        player : player of the wolf (int)
        bonus : bonus of the wolf (int)
        passified : passified of the wolf (bool)
        
    Attributes (setters):
    ---------------------
        health_points : health points of the wolf (int)
        passified : passified of the wolf (bool)
        bonus : bonus of the wolf (int)
        
    Methods:
    --------
        str(self) : return a string with all the attributes of the wolf (str)
        dict(self) : return a dictionnary with all the attributes of the wolf (dict)
    """
    
    def __init__(self, type: str, player: int, energy: int, **kwargs):
        """Create a new Wolf object.

        Args:
        -----
            type (str): Type of the wolf. (alpha, omega, normal)
            player (int): Player of the wolf. (1, 2)
            **kwargs (dict): Optional arguments.
                energy (int): Energy of the wolf. (default: ENERGY_MAX)
                bonus (int): Bonus of the wolf. (default: 0)
                passified (bool): Passified of the wolf. (default: False)
        """
        if type not in ("alpha", "omega", "normal"):
            pass 
        if player not in (1, 2):
            pass
        if energy < 1:
            pass
        
        self._type = type
        self._player = player
        self._energy = energy
        self._bonus = kwargs.get("bonus", 0)
        self._passified = kwargs.get("passified", False)
        
    def __str__(self):
        return f"{self._type} wolf of player {self._player} with {self._energy} energy \
            points. Bonus: {self._bonus}, Passified: {self._passified}"
    
    def __dict__(self):
        return {
            "type": self._type, 
            "player": self._player,
            "energy": self._energy,
            "bonus": self._bonus, 
            "passified": self._passified,
        }
    
    @property
    def type(self):
        return self._type
    
    @property
    def player(self):
        return self._player
    
    @property
    def health_points(self):
        return self._energy
        
    @property
    def attack_points(self):
        if self._passified:
            return 0
        
        return int((self._energy + self._bonus) / 10)
    
    @property
    def passified(self):
        return self._passified
    
    @property
    def bonus(self):
        return self._bonus
    
    @health_points.setter
    def health_points(self, value: int):
        if type(value) not in (int, float):
            raise TypeError("Health points must be a number.")
        
        value = int(value)
        if self._energy + value < 0:
            self._energy = 0
        elif self._energy + value > ENERGY_MAX:
            self._energy = ENERGY_MAX
        elif 0 <= self._energy + value <= ENERGY_MAX:
            self._energy += value
        else: 
            raise ValueError(f"Health points must be between 0 and {ENERGY_MAX}.")
    
    @passified.setter
    def passified(self, value: bool):
        if type(value) is not bool:
            raise TypeError("Passified must be a boolean.")
        self._passified = value
    
    @bonus.setter
    def bonus(self, value):
        value = int(value)
        if value < 0:
            self._bonus = 0
            return
        self._bonus = value