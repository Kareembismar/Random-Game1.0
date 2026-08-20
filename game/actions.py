"""Actions: what something wants to do, decoupled from which key was pressed.

Input handling produces Actions; the engine consumes them. This seam is why
"support a new key" and "add a new ability" stay independent one-line changes,
and it gives enemy AI (stage 4) the same vocabulary the keyboard uses.
"""

from dataclasses import dataclass


class Action:
    """Base class so the engine can match on action types."""


@dataclass
class Move(Action):
    """Move (or later: bump-attack) one step in a direction."""

    dx: int
    dy: int


class Quit(Action):
    """Leave the game."""
