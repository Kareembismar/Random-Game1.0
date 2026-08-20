# PARADOX

Single-screen arcade survival. Harvest cores, bank them, survive the loop —
every loop you clear spawns a copy of you replaying your exact path, and
touching it kills you. One hit, one death, `R` to go again.

Built with [pygame-ce](https://pyga.me/), managed with [uv](https://docs.astral.sh/uv/).
Design docs: [PARADOX_build_spec.md](PARADOX_build_spec.md) ·
[PARADOX_phase2_spec.md](PARADOX_phase2_spec.md) ·
[paradox/assets/ASSETS.md](paradox/assets/ASSETS.md)

## Run

```
uv run main.py
```

Boots: loading terminal → main menu → RUN. High scores persist in
`%APPDATA%/paradox/save.json`.

## Controls

| Key | Where | Action |
| --- | --- | --- |
| `W A S D` / arrows | play | Move |
| `Esc` | play | Pause (Esc again resumes) |
| `W`/`S` + `Enter`/`Space` | menus | Navigate / select (mouse works too) |
| `A` / `D` | HOW IT WORKS | Page panels |
| `R` | death screen | Instant new run |
| any key | loading | Fast-forward the boot text / continue |

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
| `paradox/states/loading.py` | Boot terminal: typed log, real load work, progress bar. |
| `paradox/states/menu.py` | Main menu + HOW IT WORKS + RECORDS, ambient ghosts. |
| `paradox/states/play.py` | The game: loops, cores, banking, collisions, HUD. |
| `paradox/states/pause.py` | Pause overlay (blur-behind-glass); quit paths save the run. |
| `paradox/states/gameover.py` | Damage report; `R` restarts within one frame. |
| `paradox/entities/player.py` | Movement, glow layers, motion trail. |
| `paradox/entities/ghost.py` | Recording playback, phase-in, decay tiers, despawn. |
| `paradox/entities/core.py` | The collectible. |
| `paradox/entities/portal.py` | Bank zone; relocates on every bank. |
| `paradox/systems/recorder.py` | Timestamped path recording + interpolated playback. |
| `paradox/systems/sprites.py` | Asset loading: scale once, cached rotations, fallbacks. |
| `paradox/systems/save.py` | Corruption-proof JSON records in `%APPDATA%/paradox/`. |
| `paradox/ui/fonts.py` | `SysFont` with a fallback chain. |
| `paradox/ui/widgets.py` | 9-sliced panel frame + shared menu drawing. |
| `paradox/ui/crt.py` | Pre-rendered scanline/vignette overlay. |
| `paradox/assets/` | Sprite/UI/background art + `ASSETS.md` integration rules. |

## Build phases

- [x] Phase 1 — playable core: movement, cores, banking, loops, ghost replay, death, instant restart
- [x] Phase 2 screens — loading, menu (+submenus), pause, game over, save file
- [x] Phase 2A — Section 0 readability: player glow layers + trail, core contrast, pause binding, arena sweep
- [ ] Phase 2B — near-miss detection, carried-core mass, loop rank
- [ ] Phase 2C — records system, live pace indicator, game over line
- [ ] Phase 2D — difficulty layers (adaptive cores, decay, portal drift, desync)
- [ ] Phase 2E — death replay, dynamic lighting, camera, audio
- [ ] Phase 2F — bank chain, death cause readout, polish
- [ ] Phase 3 — juice: shake, hit-stop, particles, CRT everywhere, procedural audio
- [ ] Phase 4 — power-ups, arena contraction, glitch effects

The tcod roguelike this repo started as lives on the `archive/tcod-roguelike` branch.
