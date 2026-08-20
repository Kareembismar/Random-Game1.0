"""Things that exist at a position on the map: the player now; orcs, items later."""


class Entity:
    """A generic thing on the map.

    Deliberately a plain class: when you add monsters or items later, either
    subclass this or add fields to it — no framework needed at this size.
    """

    def __init__(self, x: int, y: int, char: str, color: tuple[int, int, int], name: str):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name

    def move(self, dx: int, dy: int) -> None:
        """Shift position. Legality (walls, bounds) is the engine's job, not ours."""
        self.x += dx
        self.y += dy
