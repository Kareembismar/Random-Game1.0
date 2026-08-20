"""Game state and the rules for changing it."""

import tcod.console

from game import rendering
from game.actions import Action, Move, Quit
from game.entity import Entity
from game.game_map import GameMap


class Engine:
    """Owns the world (map + entities) and applies Actions to it."""

    def __init__(self, player: Entity, game_map: GameMap):
        self.player = player
        self.game_map = game_map
        self.running = True

    def handle_action(self, action: Action) -> None:
        match action:
            case Move(dx=dx, dy=dy):
                dest_x = self.player.x + dx
                dest_y = self.player.y + dy
                if self.game_map.is_walkable(dest_x, dest_y):
                    self.player.move(dx, dy)
                # Bumping a wall silently does nothing. In stage 4, bumping
                # something alive will mean "attack it".
            case Quit():
                self.running = False

    def render(self, console: tcod.console.Console) -> None:
        rendering.render_map(console, self.game_map)
        rendering.render_entity(console, self.player)
