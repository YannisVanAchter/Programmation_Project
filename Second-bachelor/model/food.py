# encoding utf-8
"""Provides the Food class."""

__author__  = 'Yannis Van Achter'
__date__    = '2023-06-16'
__version__ = '1.0'


FOOD_TYPES = ("rabbit", "deer", "boar", "bear", "fish", "berry", "mushroom")

class Food:
    """Food class

    Attributes (getters):
    ---------------------
        type : type of food (str)
        energy : energy of the food (int)
        
    Attributes (setters):
    ---------------------
        energy : energy of the food (int)
    
    Methods:
    --------
        str(self) : return a string with the type and the energy of the food
        dict(self) : return a dictionnary with the type and the energy of the food
    """
    
    def __init__(self, type: str, energy: int):
        """__init__ method for Food class

        Args:
            type (str): Type of food (see FOOD_TYPES)
            energy (int): Energy of the food

        Raises:
            ValueError: If type is not in FOOD_TYPES
            ValueError: If energy is not greater of equal to 0
        """
        if type not in FOOD_TYPES:
            raise ValueError("Invalid food type. Food type accepts only: " 
                            + ", ".join(FOOD_TYPES) 
                            + ".")
        if energy < 0:
            raise ValueError("Energy must be greater or equal to 0")
        
        self._type = type
        self._energy = energy
        
    def __str__(self):
        return f"{self._type} with {self._energy} energy points"
    
    def __dict__(self):
        return {"type": self._type, "energy": self._energy}
    
    @property
    def type(self):
        return self._type
    
    @property
    def energy(self):
        return self._energy
    
    @energy.setter
    def energy(self, value: int):
        if type(value) not in (int, float):
            raise TypeError("Energy must be a number.")
        
        value = int(value)
        if self._energy + value < 0:
            self._energy = 0
        elif 0 <= self._energy + value:
            self._energy += value
        else: 
            raise ValueError("Energy must be greater or equal to 0.")
