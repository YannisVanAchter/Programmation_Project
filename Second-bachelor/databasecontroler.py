# encoding utf-8

import os.path as pt
from typing import Union

from model.wolf import Wolf
from model.food import Food


def __check_line_format(func):
    """Decorator to check if the line match the pattern

    Args:
        func (Callable): the function to decorate

    Raises:
        ValueError: If the line doesn't match the pattern

    Returns:
        Callable: the decorated function
    """
    import re

    pattern = r"(\d+)\s+(\d+)\s+(\w+)(?:\s+(\w+))?"

    def warp(self, line: str):
        try:
            if re.match(pattern, line) is not None:
                return func(self, line)
            raise ValueError(f"'{line}' didn't match the pattern: {pattern}")
        except (TypeError, ValueError, IndexError) as e:
            raise ValueError(f"'{line}' is not a valid line") from e

    return warp


class DatabaseControler:
    def __init__(self, map_path: str = None):
        self._wolfs: dict[tuple[int], Wolf] = dict()
        self._foods: dict[tuple[int], Food] = dict()
        self._map_path = map_path
        self._map_size: dict[str, int] = {"x": None, "y": None}

    @__check_line_format
    def _line_to_dict_wolf(self, line: str):
        line_split = line.split(" ")
        coord = (int(line_split[1]), int(line_split[2]))
        return {
            "coord": coord,
            "player": int(line_split[0]),
            "type": line_split[3],
        }

    @__check_line_format
    def _line_to_dict_food(self, line: str):
        line_split = line.split(" ")
        coord = (int(line_split[0]), int(line_split[1]))
        return {
            "coord": coord,
            "type": int(line_split[2]),
            "energy": int(line_split[3]),
        }

    def init(self, map_path: str = None):
        """Read the map file and initialize the database

        Args:
        -----
            map_path (str): the path to the map file

        Raises:
        -------
            FileNotFoundError: If map_path doesn't exist
            ValueError: If map_path is not a file

        Returns:
        --------
            dict: the size of the map in x and y coordinate
        """
        self._wolfs.clear()
        self._wolfs.clear()

        if map_path is None and self._map_path is None:
            raise ValueError("map_path must be set")

        if self._map_path is None:
            self._map_path = map_path

        self._map_size = {"x": None, "y": None}

        if not pt.exists(map_path):
            raise FileNotFoundError("map_path doesn't exist")
        if not pt.isfile(map_path):
            raise ValueError("map_path must be a file")

        processing = None
        with open(self._map_path, "r") as map_file:
            for line in map_file.readlines():
                if line.startswith("map"):
                    processing = "map"
                elif line.startswith("wolf"):
                    processing = "wolf"
                elif line.startswith("food"):
                    processing = "food"

                elif processing.startswith("map"):
                    self._map_size["x"], self._map_size["y"] = tuple(line.split(" "))
                    self._map_size["x"] = int(self._map_size["x"])
                    self._map_size["y"] = int(self._map_size["y"])

                elif processing.startswith("wolf"):
                    wolf = self._line_to_dict_wolf(line)
                    self._wolfs[wolf["coord"]] = Wolf(**wolf)
                elif processing.startswith("food"):
                    food = self._line_to_dict_food(line)
                    self._foods[food["coord"]] = Food(**food)

        return self._map_size

    def eat(self, wolf_coord: tuple[int], food_coord: tuple[int], energy_max: int):
        """Eat the food at the given coordinate with the wolf at the given coordinate

        Args:
            wolf_coord (tuple[int]): Wolf coordinate to eat the food
            food_coord (tuple[int]): Food coordinate to be eaten

        Raises:
            ValueError: If wolf_coord is not occupied by a wolf
            ValueError: If food_coord is not occupied by a food
        """
        if wolf_coord not in self._wolfs:
            return
        if food_coord not in self._foods:
            return

        while (
            self._foods[food_coord].energy > 0
            and self._wolfs[wolf_coord].health_points < energy_max
        ):
            self._wolfs[wolf_coord].health_points += 1
            self._foods[food_coord].energy -= 1

    def move(self, wolf_coord: tuple[int], target_coord: tuple[int]):
        """Move the wolf at the given coordinate to the target coordinate

        Args:
            wolf_coord (tuple[int]): the coordinate of the wolf
            target_coord (tuple[int]): the coordinate of the target coordinate
        """
        if target_coord in self._wolfs:
            return
        if wolf_coord not in self._wolfs:
            return

        self._wolfs[target_coord] = self._wolfs.pop(wolf_coord)

    def attack(self, wolf_coord: tuple[int], target_coord: tuple[int]):
        """Attack the wolf at the given coordinate

        Args:
            wolf_coord (tuple[int]): the coordinate of the wolf
            target_coord (tuple[int]): the coordinate of the target wolf
        """
        attack_points = self._wolfs[wolf_coord].attack_points
        # on assignement, the setter check if the value is greater or equal to 0
        # after assignement ==> No need to check here
        self._wolfs[target_coord].health_points -= attack_points

    def passify(self, wolf_coord: tuple[int], value: bool):
        """Passify or unpassify the wolf at the given coordinate
        If value is True or False respectively

        Args:
            wolf_coord (tuple[int]): the coordinate of the wolf
            value (bool, optional): True to passify the wolf, False to unpassify it

        Raises:
            TypeError: if value is not True or False
        """
        if value not in (True, False):
            return
        self._wolfs[wolf_coord].passified = value

    def set_bonus(self, wolf_coord: tuple[int], bonus: int):
        """Set the bonus of the wolf at the given coordinate

        Args:
            wolf_coord (tuple[int]): the coordinate of the wolf
            bonus (int): the bonus to set

        Raises:
            ValueError: if bonus is less than 0
        """
        if bonus < 0:
            return
        self._wolfs[wolf_coord].bonus = bonus

    def get_wolf(self, wolf_coord: tuple[int]) -> Union[Wolf, None]:
        """Return the wolf at the given coordinate

        Args:
            wolf_coord (tuple[int]): the coordinate of the wolf
        """
        self._wolfs.get(wolf_coord)

    def get_alpha_wolfs(self) -> list[Wolf]:
        """Return all alpha wolf"""

        def is_alpha(wolf: Wolf):
            return wolf.type == "alpha"

        return list(filter(is_alpha, self._wolfs.values()))

    def get_food(self, food_coord: tuple[int]) -> Union[Food, None]:
        """Return the food at the given coordinate

        Args:
            food_coord (tuple[int]): the coordinate of the food
        """
        self._foods.get(food_coord)

    def get_wolfs(self, player: int = 0) -> list[Wolf]:
        """Return all wolfs"""

        def of_player(wolf: Wolf):
            if player == 0:
                return True
            return wolf.player == player

        return list(filter(of_player, self._wolfs.values()))

    def get_foods(self) -> list[Food]:
        """Return all foods"""
        return list(self._foods.values())

    def get_entity(self, coord: tuple[int]) -> Union[Wolf, Food, None]:
        """Return the entity at the given coordinate

        Args:
            coord (tuple[int]): the coordinate of the entity
        """
        entity = self.get_wolf(coord)
        if entity is None:
            entity = self.get_food(coord)
        return entity

    def get_map_size(self) -> dict[str, int]:
        """Return the size of the map in x and y coordinate"""
        return self._map_size
