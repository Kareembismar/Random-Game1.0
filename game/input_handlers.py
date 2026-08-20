"""Translate raw tcod events into game Actions. No game logic lives here."""

import tcod.event
from tcod.event import KeySym

from game.actions import Action, Move, Quit

# Every movement key in one place. Adding a keybinding = adding a line.
# (KeySym.H is the h key — tcod names letter keys in uppercase.)
MOVE_KEYS: dict[KeySym, tuple[int, int]] = {
    # Arrow keys.
    KeySym.UP: (0, -1),
    KeySym.DOWN: (0, 1),
    KeySym.LEFT: (-1, 0),
    KeySym.RIGHT: (1, 0),
    # Vi keys.
    KeySym.H: (-1, 0),
    KeySym.J: (0, 1),
    KeySym.K: (0, -1),
    KeySym.L: (1, 0),
}


def handle_event(event: tcod.event.Event) -> Action | None:
    """Return the Action this event means, or None if it means nothing."""
    match event:
        case tcod.event.Quit():  # window close button
            return Quit()
        case tcod.event.KeyDown(sym=KeySym.ESCAPE):
            return Quit()
        case tcod.event.KeyDown(sym=sym) if sym in MOVE_KEYS:
            dx, dy = MOVE_KEYS[sym]
            return Move(dx, dy)
    return None
