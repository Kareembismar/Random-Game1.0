"""Drawing the game onto a tcod console. Nothing in here mutates game state."""

import tcod.console

from game.entity import Entity
from game.game_map import GameMap


def render_map(console: tcod.console.Console, game_map: GameMap) -> None:
    # Copy the whole tile grid onto the console in one numpy assignment —
    # this is the payoff of storing tiles as a structured array (see tiles.py).
    console.rgb[0 : game_map.width, 0 : game_map.height] = game_map.tiles["graphic"]


def render_entity(console: tcod.console.Console, entity: Entity) -> None:
    console.print(entity.x, entity.y, entity.char, fg=entity.color)
