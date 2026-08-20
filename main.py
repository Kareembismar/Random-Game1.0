"""Entry point: window setup and the main loop.

The loop is the classic roguelike beat: draw everything, block until the
player does something, apply it, repeat. Turn-based means no frame timing —
tcod.event.wait() sleeps until there's input, so the game uses ~0% CPU idle.
"""

import tcod.console
import tcod.context
import tcod.event

from game.engine import Engine
from game.entity import Entity
from game.game_map import make_test_map
from game.input_handlers import handle_event

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 45  # Bottom 5 screen rows are reserved for the message log (stage 5).


def main() -> None:
    game_map = make_test_map(MAP_WIDTH, MAP_HEIGHT)
    player = Entity(x=40, y=22, char="@", color=(255, 255, 255), name="Player")
    engine = Engine(player, game_map)

    # order="F" makes the console's arrays index as [x, y], same as the map.
    console = tcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")

    # No tileset passed: tcod ships a built-in font, so there's no asset file
    # to manage. To restyle later, load a tilesheet here and pass tileset=...
    with tcod.context.new(console=console, title="Roguelike", vsync=True) as context:
        while engine.running:
            console.clear()
            engine.render(console)
            context.present(console)

            for event in tcod.event.wait():
                action = handle_event(event)
                if action is not None:
                    engine.handle_action(action)


if __name__ == "__main__":
    main()
