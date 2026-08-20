# PARADOX — Build Spec

> Paste this whole file into Claude Code, or save it in the repo root and tell Claude Code:
> `Read PARADOX_build_spec.md and build it. Start with Phase 1 only, then stop and let me test.`

---

## 0. What we're building

A single-screen, top-down arcade survival game called **PARADOX**.

You are a lab assistant harvesting unstable cores from a room that keeps looping. Every loop you survive, the machine spawns a **divergent copy** of you that walks your exact path from the previous loop — and touching it kills you. By loop 6 you're dodging five past versions of yourself at once.

**One hit = death. Press R = instant restart.** No load, no menu, no confirmation. That instant-restart loop is the most important feature in the game; do not put anything between death and the next attempt.

**The core hook:** the ghost replays your recorded path. Clear a loop fast and your ghost is short-lived. Panic and flail around for 40 seconds and next loop has a 40-second wall of death in it. Sloppy play punishes future-you directly.

---

## 1. Tech constraints

- **Replace the existing tcod roguelike entirely.** Delete/archive the old game code. This is a different game.
- **Engine: `pygame-ce`** (community edition — install `pygame-ce`, import as `pygame`). tcod is for grid roguelikes and is the wrong tool here.
- Keep the existing `uv` setup. Add deps via `uv add pygame-ce`.
- Python 3.11+, target Windows (dev machine is Windows 11).
- **Zero art assets required for v1.** Everything is drawn with `pygame.draw` primitives, gradients, and alpha surfaces. Do not add image dependencies. Do not reference `terminal.png` or any tileset — that was the old tcod font error and it should not exist anywhere in the new project.
- Fonts: use `pygame.font.SysFont` with a fallback chain (`consolas`, `couriernew`, `monospace`) so it never crashes on a missing font.
- Sound: use `pygame.mixer` with **procedurally generated** tones (numpy sine/square waves written into `pygame.sndarray`). No audio files. Wrap all audio in try/except so a machine with no audio device still runs the game.
- Target 60 FPS, delta-time based movement (never frame-count based).
- Window: 1280x720, resizable off for v1.

---

## 2. Project structure

```
paradox/
  __init__.py
  main.py            # entry point, game loop, state machine
  config.py          # ALL tunable constants in one place
  states/
    __init__.py
    base.py          # State ABC: handle_event, update(dt), draw(surface)
    loading.py
    menu.py
    play.py
    pause.py
    gameover.py
  entities/
    __init__.py
    player.py
    ghost.py
    core.py          # collectible
    portal.py        # bank zone
    powerup.py
  systems/
    __init__.py
    recorder.py      # path recording + playback
    particles.py
    juice.py         # screen shake, hit-stop, flash
    audio.py         # procedural sfx
    save.py          # high score JSON
  ui/
    __init__.py
    widgets.py       # menu list, buttons, progress bar
    crt.py           # scanline + vignette overlay
```

`main.py` at repo root just does `from paradox.main import run; run()`.

**Every constant lives in `config.py`.** Speeds, colors, timings, spawn counts, multiplier rates. I need to be able to tune feel by editing one file.

---

## 3. State machine

States: `LOADING → MENU → PLAY ⇄ PAUSE → GAMEOVER → (MENU | PLAY)`

Build a proper stack-based state manager. `PAUSE` renders the frozen `PLAY` frame underneath it, dimmed and blurred, rather than replacing it.

### 3.1 LOADING screen

Runs once at startup. Should feel like a lab terminal booting a machine that probably isn't safe.

- Black background, acid-green monospace text, CRT scanlines.
- Boot lines typed out one at a time with a per-character reveal (~35 chars/sec) and a blinking block cursor:
  ```
  > INITIALIZING CONTAINMENT FIELD ......... OK
  > CALIBRATING TEMPORAL RECORDER .......... OK
  > SPAWNING DIVERGENT INSTANCE BUFFER ..... OK
  > ETHICS SUBROUTINE ...................... SKIPPED
  > CHECKING FOR PREVIOUS OCCUPANTS ........ 4 FOUND
  > READY.
  ```
- Segmented progress bar underneath, filling as real work completes.
- **Do the real work here**: build font objects, pre-render the CRT overlay surface, generate all procedural sound buffers, load the save file. Do it across frames so the bar animates instead of freezing.
- Enforce a **minimum 2.2 seconds** on screen even if loading finishes instantly, so it reads as intentional rather than as a flicker.
- Any key press after "READY." skips to menu. Show a subtle `[ PRESS ANY KEY ]` prompt pulsing at the bottom once complete.

### 3.2 MAIN MENU

- Title `PARADOX` in large letters with a chromatic-aberration effect: draw the text three times offset by 2-3px in red, cyan, and white, with the offset breathing slowly via a sine wave.
- Subtitle line, small and dry: `you are the hazard`
- Vertical menu, keyboard-driven:
  ```
  RUN
  HOW IT WORKS
  RECORDS
  QUIT
  ```
- Navigation: **W / S** or arrow keys to move, **Enter** or **Space** to select, **Esc** to back out. Selected item gets a `>` marker, a green glow, and a slight horizontal offset. Mouse hover/click should also work but keyboard is primary.
- Show `BEST: 12,480` and `DEEPEST LOOP: 7` in the corner, read from the save file.
- Background: slow-drifting particle field of dim green dots, plus 2-3 faint idle ghost silhouettes wandering the background as ambient. Sells the concept before you press anything.
- **HOW IT WORKS** is a submenu, not a wall of text. Three short panels the player pages through with A/D:
  1. `WASD to move. Collect cores. Carry them to the portal to bank them.`
  2. `Every loop you survive spawns a copy of you walking your last path. It kills you.`
  3. `Clear loops FAST. Your ghost only lives as long as your last loop took.`
- **RECORDS** shows top 5 scores with the loop reached.

### 3.3 PLAY

The game. Detailed in section 4.

### 3.4 PAUSE

- Triggered by **Esc** during play.
- Freeze all simulation. Render the last play frame, then a dark translucent overlay on top, plus a subtle downscale-upscale blur so it reads as "behind glass."
- Menu: `RESUME`, `RESTART RUN`, `QUIT TO MENU`. Same W/S + Enter navigation.
- **Esc again resumes** — do not make Esc ambiguous.
- Quitting to menu from here still writes the score to the save file. Never silently discard a run.

### 3.5 GAME OVER

- Freeze-frame on death for ~350ms with a hard white flash and heavy shake before this state appears.
- Show: final score, loop reached, cores banked, longest surviving loop. If it's a new best, `NEW RECORD` in flashing magenta.
- Prompt: **`[R] RUN AGAIN     [ESC] MENU`**
- **R must restart within one frame.** No fade, no transition, no confirmation. This is the single most important interaction in the game.

---

## 4. Gameplay spec

### 4.1 Arena

- Playfield is an inset rectangle inside the window (roughly 1180x600 with a HUD strip along the top).
- Border is a glowing containment field: animated green lines with a soft outer bloom (draw the shape 3-4 times at increasing thickness and decreasing alpha).
- Background is near-black with a faint grid, plus a slow parallax scan line drifting downward.
- No level geometry in v1. The ghosts *are* the level.

### 4.2 Player

- Small glowing triangle or diamond, pointed in the direction of travel.
- **WASD movement**, 8-directional, normalized diagonals (do not let diagonal be faster — normalize the input vector).
- Slight acceleration and friction so it feels weighty, not instant-snap. Target: reaches full speed in ~0.08s.
- Leaves a short fading motion trail of ~12 previous positions.
- Clamped to the arena bounds.
- **One hit kills.** Collision with any active ghost = death.

### 4.3 Cores (collectibles)

- Spawn count per loop: `5 + loop_number`, capped at 12.
- Spawn positions are random but must be at least 140px from the player's spawn point and at least 90px from each other.
- Pulsing green orbs with a rotating outer ring.
- Walk over one to pick it up. Picked-up cores orbit the player in a small ring — visually obvious how loaded you are.
- Each carried core adds to your multiplier but is **not scored until banked.**

### 4.4 The Portal (bank zone)

- A circular portal somewhere in the arena. Green swirling ring, particles pulled inward.
- Stand in it to deposit all carried cores: `score += cores_carried * 100 * multiplier`.
- **The portal relocates every time you bank**, to a random position at least 300px from where it was. You never get to camp.
- Loop advances when **all** cores for that loop have been banked.

### 4.5 The multiplier — the greed hook

- `multiplier = 1.0 + (0.35 * cores_carried)`
- Displayed huge and center-top, growing in font size and shifting from green → yellow → magenta as it climbs.
- Carrying 8 cores means a 3.8x multiplier — a huge bank — but you've spent a long time in the arena with the ghosts to get there.
- Add a subtle rising audio tone that pitches up with every core carried. It should make the player nervous.
- Death loses everything carried. Banking locks it in.

### 4.6 Ghosts — the core system

This is the heart of the game. Get it right.

**Recording:**
- During each loop, sample the player's position every frame into a list of `(x, y, facing)` tuples along with the loop's total duration.
- When the loop ends (all cores banked), that recording is stored and a new one starts.

**Playback:**
- At the start of loop N, spawn ghosts for every recording from loops 1..N-1. Loop 4 has 3 ghosts.
- Each ghost steps through its recorded positions at the same rate they were recorded, using delta-time interpolation so it stays framerate-independent.
- When a ghost reaches the end of its recording, it **collapses in a portal implosion effect and despawns for the rest of the loop.** This is the payoff for fast play — short recordings mean short-lived hazards.

**Feel and fairness:**
- Ghosts phase in over **1.5 seconds** at the loop start: translucent, glitching, harmless. A magenta ring shrinks around each one as a visible countdown to "this is lethal now." Never kill the player with something that just materialized.
- Ghost visuals: same shape as the player but rendered in desaturated magenta at ~65% alpha, with per-frame RGB channel offset (draw it twice, offset 2px, in red and cyan) so they read as *wrong*.
- Older ghosts are dimmer and more degraded than recent ones. Visual history depth.
- Ghosts leave a fading trail too, so you can read where they're heading.
- Collision: circle-vs-circle, radius slightly *smaller* than the visual. Always err generous to the player.
- Cap active ghosts at 12 for performance; beyond that, drop the oldest recording.

### 4.7 Power-ups

Spawn one at a random position every `18 - loop_number` seconds (floor 6s). Only one on the field at a time. They expire after 8s with a blinking warn at 2s.

| Name | Effect | Duration |
|---|---|---|
| **PHASE SERUM** | Pass harmlessly through ghosts. Player renders translucent + heavy trail. | 3.5s |
| **DILATION** | All ghosts move at 35% speed. Player unaffected. Add a low pitch-bend on the audio. | 4s |
| **COLLAPSE FIELD** | Permanently deletes the **oldest** recording. That ghost is gone for the rest of the run. | instant |
| **OVERCLOCK** | Player speed x1.75 — but your path is recorded at double density, making next loop's ghost move faster and live longer. | 6s |

**OVERCLOCK is deliberately a trap-with-upside.** It lets you clear the current loop fast at the cost of a worse future. Make the tooltip text honest but tempting: `FASTER NOW. WORSE LATER.` Players finding out this matters is a good moment.

Active power-ups show as icons with draining radial timers in the HUD corner.

### 4.8 HUD

Minimal, top strip only:
- Left: `SCORE 12,480` and below it small `BEST 18,220`
- Center: the multiplier, large
- Right: `LOOP 4` and `CORES 3/9`
- Bottom-left, tiny and dim: `ESC — PAUSE`

### 4.9 Difficulty curve

Difficulty is emergent — it comes from accumulating ghosts, not from tuned enemy stats. But layer in:
- Loop 1: no ghosts. A calm 15 seconds to learn the controls. Never explain this, just let it happen.
- Loop 3+: containment field border starts flickering, background hue shifts slightly toward magenta each loop.
- Loop 5+: occasional 0.15s full-screen glitch (horizontal slice displacement) as flavor.
- Loop 8+: the arena bounds contract inward by 15px per loop, floor at 60% of original size.

---

## 5. Juice requirements — non-negotiable

The mechanics above are only half the game. Feel is the other half. Implement all of these:

- **Screen shake** — trauma-based (a 0-1 float that decays; shake magnitude = trauma²). Core pickup: 0.15. Bank: 0.4. Power-up: 0.3. Death: 1.0.
- **Hit-stop** — freeze the whole simulation for 40ms on bank, 200ms on death.
- **Particles** — a pooled system, never allocate per-frame. Core pickup bursts green. Banking sends a spiral into the portal. Death explodes the player into 60 fragments that fade over 1.2s.
- **Flash** — full-screen white at 0.9 alpha on death, decaying over 250ms.
- **Tweening** — nothing appears instantly. Cores scale up on spawn with an ease-out-back. UI elements slide in. Menu selections ease.
- **CRT overlay** — pre-rendered scanlines at low alpha plus a vignette, blitted last every frame. Pre-render it once at load, never rebuild it.
- **Procedural audio** — short synthesized blips: core pickup (rising square wave), bank (chord sweep), power-up (arpeggio), ghost phase-in (low descending tone), death (noise burst + pitch-down). Generate with numpy at load time.

---

## 6. Persistence

`save.py` writes `%APPDATA%/paradox/save.json` (use `pathlib` + `os.getenv('APPDATA')`, fall back to the working directory):

```json
{
  "best_score": 18220,
  "deepest_loop": 9,
  "total_runs": 47,
  "top_scores": [{"score": 18220, "loop": 9}, ...]
}
```

Corrupt or missing file must never crash the game — wrap in try/except and regenerate defaults.

---

## 7. Build order — do these in phases and stop between each

**Phase 1 — playable core.** Window, state machine skeleton, WASD player with accel/friction, arena bounds, cores spawning and being collected, portal banking, loop advancement, ghost recording and playback with collision and death. Ugly is fine. Placeholder rectangles are fine. **Stop here and let me test it.**

**Phase 2 — screens.** Loading screen, main menu with all submenus, pause overlay, game over screen, save file. Full navigation working with W/S + Enter + Esc.

**Phase 3 — feel.** All of section 5. Screen shake, particles, hit-stop, trails, tweens, CRT, procedural audio.

**Phase 4 — content.** Power-ups, difficulty layering, arena contraction, glitch effects, HUD polish.

Commit after each phase with a clear message. Do not jump ahead to Phase 3 polish while Phase 1 mechanics are still unverified.

---

## 8. Acceptance criteria

- [ ] Game launches to a loading screen, then main menu, with no console errors and no missing-asset warnings
- [ ] No reference to `terminal.png`, tcod, or any tileset remains anywhere in the project
- [ ] WASD moves the player; diagonals are not faster than cardinals
- [ ] Esc during play opens pause; Esc again resumes; quit-to-menu works and preserves the score
- [ ] Ghosts replay the previous loop's path exactly and are harmless during a visible 1.5s phase-in
- [ ] A ghost despawns with a visual effect when its recording ends
- [ ] Dying and pressing R starts a new run in under one frame with no transition
- [ ] High score persists across a full application restart
- [ ] Runs at a stable 60 FPS with 12 ghosts and 200 active particles
- [ ] Every tunable number lives in `config.py`

---

## Appendix A — Art prompts (optional, Phase 5+)

**You do not need any of this for v1.** The game is fully playable with drawn primitives, and the vector look genuinely suits it. Only reach for these if you want a sprite pass later.

Generate at transparent PNG, square canvas, then drop into `paradox/assets/`.

1. **Player sprite** — `Top-down 2D game sprite of a small angular science-lab drone, sharp geometric triangular body, glowing acid-green core at center, dark metallic chassis, viewed directly from above, clean vector style, sharp edges, transparent background, 128x128, no shadow, centered`

2. **Ghost variant** — `Top-down 2D game sprite of a corrupted angular drone, same triangular geometric shape, glitched magenta and violet coloring, semi-transparent body, digital fragmentation and chromatic distortion at the edges, viewed from directly above, vector style, transparent background, 128x128`

3. **Core collectible** — `2D game icon of a small unstable energy cell, hexagonal glass container with swirling acid-green plasma inside, glowing, thin dark metal frame, clean vector style, viewed head-on, transparent background, 64x64`

4. **Portal** — `Top-down 2D game asset of a circular energy portal, concentric acid-green rings, swirling void center, distorted light at the rim, glowing, dark sci-fi laboratory aesthetic, vector style, transparent background, 256x256`

5. **Power-up icons (set)** — `Set of four flat 2D game icons in matching style, thin-line vector, acid-green on dark: a syringe, an hourglass, a collapsing star, a lightning bolt. Sci-fi laboratory aesthetic, uniform stroke weight, transparent background, 64x64 each`

6. **Menu background** — `Dark abandoned science laboratory interior, wide shot, dim acid-green emergency lighting, cluttered machinery and cables, heavy atmospheric haze, faint magenta glow from an unseen source, moody, desaturated, no characters, no text, 1920x1080`

**Tone note for any UI copy Claude Code writes:** dry, deadpan, faintly irritated with the player. `> CHECKING FOR PREVIOUS OCCUPANTS ........ 4 FOUND` is the register. Never cute, never enthusiastic, never explaining the joke.
