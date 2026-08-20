"""Tile type definitions for the map.

Design note: instead of a Tile class instantiated per cell, tiles are rows in
a numpy structured array. The map is a big uniform grid, and both rendering
(now) and field-of-view (stage 3) want to process the whole grid at once —
one array assignment instead of a Python loop over 80x45 objects per frame.
tcod's own console and FOV APIs are built around numpy arrays, so this is the
idiomatic shape for the data.
"""

import numpy as np

# What one on-screen cell looks like: glyph + foreground/background color.
# This dtype matches tcod's Console.rgb cells exactly, so a map-sized slice of
# tiles can be copied straight onto the console.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint of the glyph.
        ("fg", "3B"),  # Foreground color: 3 unsigned bytes (RGB).
        ("bg", "3B"),  # Background color.
    ]
)

# One tile type. More fields will arrive with FOV in stage 3 (a separate
# "seen from memory" look for explored-but-not-visible tiles).
tile_dt = np.dtype(
    [
        ("walkable", bool),  # Can an entity stand on it?
        ("transparent", bool),  # Can you see through it? (unused until stage 3)
        ("graphic", graphic_dt),  # How it renders.
    ]
)


def new_tile(*, walkable: bool, transparent: bool, graphic: tuple) -> np.ndarray:
    """Define a tile type. Keyword-only so call sites document themselves."""
    return np.array((walkable, transparent, graphic), dtype=tile_dt)


floor = new_tile(
    walkable=True,
    transparent=True,
    graphic=(ord("."), (110, 110, 110), (0, 0, 0)),
)
wall = new_tile(
    walkable=False,
    transparent=False,
    graphic=(ord("#"), (180, 180, 180), (0, 0, 0)),
)
