# encoding: utf-8

from view import View

from databasecontroler import DatabaseControler

BONUS_RANGE = {"alpha": 2, "normal": 1, "omega": 1}
ENERGY_MAX = 100
LIST_TYPE_WOLF = ("alpha", "normal", "omega")
MAX_GAME_LOOP = 200
MAX_MAP_SIZE = {"x": 60, "y": 60}
MAX_NB_PLAYER = 2  # can move
NB_WOLF_PER_PLAYER = 9
NB_ALPHA_WOLF_PER_PLAYER = 1
NB_OMEGA_WOLF_PER_PLAYER = 1
NB_OTHER_WOLF_PER_PLAYER = (
    NB_WOLF_PER_PLAYER - NB_ALPHA_WOLF_PER_PLAYER - NB_OMEGA_WOLF_PER_PLAYER
)
MIN_MAP_SIZE = {"x": 20, "y": 20}
MIN_NB_PLAYER = 2
PASSIFY_RANGE = 2


def check_condition(func):
    def wrap(self: RulesControler, *args, **kwargs):
        # self.check_pre_condition()
        r = func(self, *args, **kwargs)
        self.check_post_condition()
        return r

    return wrap


class RulesControler:
    def __init__(self, database: DatabaseControler, views: list[View] = None):
        self._database = database
        self._instruction = {i: [] for i in range(1, MAX_NB_PLAYER + 1)}
        self._views = views

    @property
    def instruction(self):
        return self._instruction

    def check_pre_condition(self):
        map_size = self._database.get_map_size()
        if not (MIN_MAP_SIZE["x"] <= map_size["x"] <= MAX_MAP_SIZE["x"]):
            raise ValueError(
                "map_size['x'] must be between {} and {}".format(
                    MIN_MAP_SIZE["x"], MAX_MAP_SIZE["x"]
                )
            )
        if not (MIN_MAP_SIZE["y"] <= map_size["y"] <= MAX_MAP_SIZE["y"]):
            raise ValueError(
                "map_size['y'] must be between {} and {}".format(
                    MIN_MAP_SIZE["y"], MAX_MAP_SIZE["y"]
                )
            )
        if not (MIN_NB_PLAYER <= len(self._views) <= MAX_NB_PLAYER):
            raise ValueError(
                f"N° of player must be between {MIN_NB_PLAYER} and {MAX_NB_PLAYER}"
            )

        wolfs = {(t, p): 0 for t in LIST_TYPE_WOLF for p in range(1, MAX_NB_PLAYER + 1)}
        for wolf in self._database.get_wolfs():
            wolfs[(wolf.type, wolf.player)] += 1

        for type_wolf in LIST_TYPE_WOLF:
            for player in range(1, MAX_NB_PLAYER + 1):
                nb_wolf = wolfs.get((type_wolf, player), -1)
                if nb_wolf == -1:
                    continue

                if type_wolf == "alpha":
                    if nb_wolf != NB_ALPHA_WOLF_PER_PLAYER:
                        raise ValueError(
                            f"Player {player} must have {NB_ALPHA_WOLF_PER_PLAYER} alpha wolf"
                        )
                elif type_wolf == "omega":
                    if nb_wolf != NB_OMEGA_WOLF_PER_PLAYER:
                        raise ValueError(
                            f"Player {player} must have {NB_OMEGA_WOLF_PER_PLAYER} omega wolf"
                        )
                else:
                    if nb_wolf != NB_OTHER_WOLF_PER_PLAYER:
                        raise ValueError(
                            f"Player {player} must have {NB_OTHER_WOLF_PER_PLAYER} normal wolf"
                        )

    def check_post_condition(self):
        self._instruction = {i: [] for i in range(1, MAX_NB_PLAYER + 1)}

    def instruction_setter(self, value: str, player: int):
        if player not in [i for i in range(1, MAX_NB_PLAYER + 1)]:
            raise ValueError("player must be between 1 and {}".format(MAX_NB_PLAYER))

        self._instruction[player] = value.split(" ")

    @check_condition
    def apply_instruction(self):
        pass

    def _apply_move_instruction(self):
        pass

    def _is_correct_distance(
        self, wolf_coord: tuple[int], target_coord: tuple[int], distance_max: int
    ):
        if distance_max <= 0:
            return wolf_coord == target_coord

        current_distance = abs(wolf_coord[0] - target_coord[0]), abs(
            wolf_coord[1] - target_coord[1]
        )

        return max(current_distance) <= distance_max

    def _apply_eat_instruction(self):
        pass

    def _apply_attack_instruction(self):
        pass

    def _apply_passify_instruction(self):
        pass

    def _set_bonus(self, to_zero: bool = False):
        pass

    def is_winner(self, id_game_loop: int):
        if id_game_loop == MAX_GAME_LOOP:
            return True

        # Check if there is a alpha wolf with 0 health point
        alpha_wolfs = self._database.get_alpha_wolfs()
        nb_wolf_dead = 0
        for wolf in alpha_wolfs:
            if wolf.health_points == 0:
                nb_wolf_dead += 1

        return nb_wolf_dead == (len(alpha_wolfs) - 1)

    def get_winner(self):
        """Get the winner of the game

        Returns:
            int: the player who win the game
        """
        player = -1
        max_health_point = -1
        for wolf in self._database.get_alpha_wolfs():
            if wolf.health_points > max_health_point:
                player = wolf.player
                max_health_point = wolf.health_points
        return player
