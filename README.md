# PARADOX

Single-screen arcade survival. Harvest cores, bank them, survive the loop —
every loop you clear spawns a copy of you replaying your exact path, and
touching it kills you. One hit, one death, `R` to go again.

Built with [pygame-ce](https://pyga.me/), managed with [uv](https://docs.astral.sh/uv/).
Design docs: [PARADOX_build_spec.md](PARADOX_build_spec.md) ·
[PARADOX_phase2_spec.md](PARADOX_phase2_spec.md) ·
[PARADOX_depth_design.md](PARADOX_depth_design.md) ·
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
| `Space` | survey (loop 5+) | Begin the loop early |
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

**You are writing the next loop's level.** The dim magenta line trailing
behind you is the wall you're building — every detour you take becomes a
hazard you have to live with for the next several loops. The bar along the
bottom is the ghost timeline: one row per ghost showing when it arrives, its
harmless phase-in, its lethal window, and when it despawns, with a playhead
sweeping as the loop runs. Read the gaps and plan through them. From loop 5
each loop opens with a three-second survey beat so you can look before you
commit. Grazing a lethal ghost without dying is worth points and a beat of
slow motion.

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
| `paradox/systems/collision.py` | Swept closest-approach — kills and grazes, no tunneling. |
| `paradox/systems/sprites.py` | Asset loading: scale once, cached rotations, fallbacks. |
| `paradox/systems/save.py` | Corruption-proof JSON records in `%APPDATA%/paradox/`. |
| `paradox/ui/fonts.py` | `SysFont` with a fallback chain. |
| `paradox/ui/widgets.py` | 9-sliced panel frame + shared menu drawing. |
| `paradox/ui/timeline.py` | The ghost timeline: arrival, lethal window, despawn. |
| `paradox/ui/crt.py` | Pre-rendered scanline/vignette overlay. |
| `paradox/assets/` | Sprite/UI/background art + `ASSETS.md` integration rules. |

## Build phases

- [x] Phase 1 — playable core: movement, cores, banking, loops, ghost replay, death, instant restart
- [x] Phase 2 screens — loading, menu (+submenus), pause, game over, save file
- [x] Phase 2A — Section 0 readability: player glow layers + trail, core contrast, pause binding, arena sweep
- [x] Depth A — swept collision, brighter glow, ghost stagger, near-miss detection
- [x] Depth B — layer one: live path render, ghost timeline, survey beat
- [ ] Depth C — divergence draft (between-loop cards trading now against later)
- [ ] Depth D — resonance gates (ghosts open your way forward; flood-fill reachability)
- [ ] Depth E — resonance chain, volatile cores, intersections, heavy cores
- [ ] Phase 2B — carried-core mass, loop rank
- [ ] Phase 2C — records system, live pace indicator, game over line
- [ ] Phase 2D — difficulty layers (adaptive cores, decay, portal drift, desync)
- [ ] Phase 2E — death replay, dynamic lighting, camera, audio
- [ ] Phase 2F — bank chain, death cause readout, polish
- [ ] Phase 3 — juice: shake, hit-stop, particles, CRT everywhere, procedural audio
- [ ] Phase 4 — power-ups, arena contraction, glitch effects

Every system added by the depth design can be switched off in
[`paradox/config.py`](paradox/config.py) (`PATH_RENDER_ENABLED`,
`TIMELINE_ENABLED`, `SURVEY_ENABLED`, `NEARMISS_ENABLED`, `GHOST_STAGGER = 0`).

The tcod roguelike this repo started as lives on the `archive/tcod-roguelike` branch.
