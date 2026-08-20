# Roguelike

A terminal roguelike built with [python-tcod](https://python-tcod.readthedocs.io/), managed with [uv](https://docs.astral.sh/uv/).

## Run

```
uv run main.py
```

(uv creates the virtual environment and installs dependencies automatically on first run.)

## Controls

| Key | Action |
| --- | --- |
| Arrow keys or `h` `j` `k` `l` | Move |
| `Escape` or close window | Quit |

## File map

| File | What it does |
| --- | --- |
| `main.py` | Entry point: opens the window, runs the draw → wait-for-input → apply loop. |
| `game/actions.py` | Action types (`Move`, `Quit`) — the vocabulary between input and game rules. |
| `game/input_handlers.py` | Turns tcod keyboard/window events into Actions. Keybindings live here. |
| `game/engine.py` | Game state: owns the map and player, applies Actions (movement rules, quit). |
| `game/entity.py` | `Entity` — anything with a position and a look (player now, monsters/items later). |
| `game/game_map.py` | `GameMap` grid + walkability queries. Currently a hardcoded test map. |
| `game/tiles.py` | Tile type definitions as numpy structured arrays (floor, wall). |
| `game/rendering.py` | Draws the map and entities onto the console. Never mutates state. |

## Build stages

- [x] Stage 1 — movable `@` on a hardcoded map, walls block movement
- [ ] Stage 2 — procedural dungeon generation (rooms + corridors)
- [ ] Stage 3 — field of view + explored-tile memory
- [ ] Stage 4 — orcs, pathfinding, bump-to-attack combat
- [ ] Stage 5 — message log + death screen

## Extending

- **New movement key:** add an entry to `MOVE_KEYS` in `game/input_handlers.py`.
- **New player action:** add an Action class in `game/actions.py`, map a key to it in `input_handlers.py`, handle it in `engine.py`.
- **New tile type:** add a `new_tile(...)` in `game/tiles.py`.
