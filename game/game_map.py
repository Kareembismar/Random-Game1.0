"""The dungeon map: a grid of tiles plus the questions the game asks of it."""

import numpy as np

from game import tiles


class GameMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # One structured cell per tile, everything starts as wall and gets
        # carved out. order="F" means the array indexes as [x, y], matching
        # how we talk about screen coordinates everywhere else.
        self.tiles = np.full((width, height), fill_value=tiles.wall, order="F")

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and bool(self.tiles["walkable"][x, y])


def make_test_map(width: int, height: int) -> GameMap:
    """Stage-1 placeholder: one big room with some obstacles to bump into.

    Replaced by real procedural generation in stage 2.
    """
    game_map = GameMap(width, height)
    game_map.tiles[1:-1, 1:-1] = tiles.floor  # carve the interior, keep a border wall
    game_map.tiles[30:33, 20:23] = tiles.wall  # a 3x3 pillar
    game_map.tiles[50, 10:30] = tiles.wall  # a long wall segment with ends you can walk around
    return game_map
