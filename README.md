# PARADOX

Single-screen arcade survival. Harvest cores, bank them, survive the loop —
every loop you clear spawns a copy of you replaying your exact path, and
touching it kills you. One hit, one death, `R` to go again.

Built with [pygame-ce](https://pyga.me/), managed with [uv](https://docs.astral.sh/uv/).
Full design: [PARADOX_build_spec.md](PARADOX_build_spec.md).

## Run

```
uv run main.py
```

(uv creates the environment and installs dependencies automatically on first run.)

## Controls (Phase 1)

| Key | Action |
| --- | --- |
| `W A S D` / arrows | Move |
| `R` (after death) | Instant new run |
| `Esc` | Quit (becomes pause in Phase 2) |

## How a run works

Collect cores (green orbs) and carry them to the portal to bank them —
carried cores raise your multiplier but are lost if you die. When every core
of the loop is banked, the loop advances: new cores spawn, and a ghost spawns
for each previous loop, replaying that loop's exact path. Ghosts are harmless
while materializing (the shrinking ring is the countdown), lethal after, and
collapse when their recording ends. Fast loops make short-lived ghosts.

## File map

| File | What it does |
| --- | --- |
| `main.py` | Launcher — calls `paradox.main.run()`. |
| `paradox/config.py` | **Every tunable number.** Speeds, timings, colors, counts. |
| `paradox/main.py` | Window, clock, event pump, state-machine loop. |
| `paradox/states/base.py` | `State` ABC + stack-based `StateManager`. |
| `paradox/states/play.py` | The game: loops, cores, banking, collisions, HUD. |
| `paradox/states/gameover.py` | Death screen; `R` restarts within one frame. |
| `paradox/entities/player.py` | Movement: acceleration/friction, normalized diagonals. |
| `paradox/entities/ghost.py` | Recording playback, phase-in, lethality, despawn. |
| `paradox/entities/core.py` | The collectible. |
| `paradox/entities/portal.py` | Bank zone; relocates on every bank. |
| `paradox/systems/recorder.py` | Timestamped path recording + interpolated playback. |
| `paradox/systems/sprites.py` | Asset loading: scale once, cached rotations, drawn fallbacks. |
| `paradox/ui/fonts.py` | `SysFont` with a fallback chain. |
| `paradox/assets/` | Sprite/UI/background art + `ASSETS.md` integration rules. |

## Build phases

- [x] Phase 1 — playable core: movement, cores, banking, loops, ghost replay, death, instant restart
- [ ] Phase 2 — screens: loading, menu, pause, game over, save file
- [ ] Phase 3 — feel: shake, hit-stop, particles, trails, tweens, CRT, procedural audio
- [ ] Phase 4 — content: power-ups, difficulty layering, arena contraction, glitch effects

The tcod roguelike this repo started as lives on the `archive/tcod-roguelike` branch.
