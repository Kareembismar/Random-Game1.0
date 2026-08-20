# PARADOX — Phase 2+ Spec

> Give this to Claude Code alongside the original `PARADOX_build_spec.md`.
> Section 0 first. Do not start Section 1 until Section 0 is done and I've looked at it.

---

## 0. Readability fixes — do these before anything else

The current build has a legibility problem that will make every new feature feel worse than it is. Fix it first.

**The player must be the brightest object on screen.** Right now the cores out-glow the drone and the player reads as a faint smudge. In a one-hit-kill game, if the player can't instantly find themselves, every death feels unfair.

- Render the player at **44px** (currently far smaller). Set `PLAYER_PX = 44` in `config.py`.
- Add a two-layer additive glow beneath the player: an inner layer at 1.4x size / alpha 130, an outer at 2.2x / alpha 55, both `BLEND_RGB_ADD`. Pulse the inner alpha ±25 on a 2.5Hz sine.
- Add the motion trail from the original spec — 12 previous positions, fading alpha 120 → 0, drawn additively. This is what makes fast movement legible.
- Drop core brightness ~25% so the player wins the contrast fight.

**Cores are too detailed for their size.** `core.png` has fine hexagonal clamps that turn to mush below 30px.
- Bump `CORE_PX` to **34**, and
- Draw a procedural pulsing ring around each core in code (radius 18-22, oscillating) rather than relying on sprite detail for the "pickup me" read.

**Fix the pause binding.** The HUD reads `ESC — QUIT`. Esc opens the pause menu; the pause menu contains Quit. Update the hint text to `ESC — PAUSE`.

**Arena floor is too empty.** Raise the grid line alpha to ~28 and add a slow vertical scanline sweep (a 2px bright line drifting top to bottom every 6s). Costs nothing, makes the space feel alive instead of blank.

---

## 1. Difficulty escalation

Difficulty must stay **fair and learnable**. The whole appeal is that ghosts are deterministic — you died because of a decision, not a dice roll. Every layer below escalates pressure without breaking that contract.

Introduce one new pressure at a time so the player can absorb each:

| Loop | New pressure |
|---|---|
| 1 | Nothing. No ghosts. Learn the controls. |
| 2 | First ghost appears. |
| 3 | Cores rise to 8. Portal relocation distance increases to 400px. |
| 4 | **Arena contraction** begins — bounds shrink 15px per loop, floor at 62% of original area. |
| 5 | **Adaptive core placement** switches on. |
| 7 | **Core decay** switches on. |
| 9 | **Portal drift** switches on. |
| 12 | **Desync** switches on. |

### Adaptive core placement (loop 5+)
Build a coarse heatmap of the arena (32x18 cells) and accumulate a weight for every cell your ghost paths pass through. When spawning cores, weight the random pick **toward** high-traffic cells — roughly 65% of cores in the top-tercile-density cells, 35% anywhere valid.

This is the smartest difficulty lever in the game: it puts the reward exactly where your own past routes are thickest, without adding a single new enemy. Still perfectly fair — the density is a direct consequence of your own play.

Never spawn a core inside a cell that a ghost occupies during its first 1.5s.

### Core decay (loop 7+)
Cores begin dimming 12 seconds after loop start and vanish at 16 seconds, respawning elsewhere after a 2s gap. Show the decay as the sprite desaturating and the ring shrinking. Punishes hoarding without acting; rewards route planning.

### Portal drift (loop 9+)
The portal drifts at 20px/s toward a slowly-changing target point instead of sitting still. Never accelerates, never chases the player — it wanders. You have to lead it.

### Desync (loop 12+)
One randomly chosen ghost per loop replays at 1.15x speed, marked with a visibly harsher glitch effect and a distinct audio tone so it is **identifiable on sight**. This is the only place determinism bends, it arrives very late, and it is always telegraphed. Do not apply it to more than one ghost per loop.

### What NOT to add
No enemies that chase the player. No projectiles. No random hazards. The moment something kills you that you couldn't have predicted, the "my fault, run it back" loop breaks and the player quits for good.

---

## 2. Records system

A single high score number is not enough to keep someone playing. Track a spread of things so almost every run beats *something*.

```json
{
  "best_score": 18220,
  "deepest_loop": 9,
  "best_single_bank": 3420,
  "longest_run_seconds": 187.4,
  "most_near_misses": 34,
  "total_runs": 47,
  "runs_since_record": 12,
  "loop_bests": {"1": 400, "2": 950, "3": 1800, "4": 3100},
  "best_run_curve": [400, 950, 1800, 3100, 4900],
  "top_scores": [{"score": 18220, "loop": 9, "date": "2026-08-19"}]
}
```

**`loop_bests`** is the important one. At the start of each loop, flash `LOOP 6 BEST — 4,200` for 1.5s in the corner. Now every loop has a target, not just the run as a whole.

**Live pace indicator.** During play, show a small `▲ +340` or `▼ −180` under the score comparing your current score to your best run's score *at this same loop*. Turn it green when ahead, magenta when behind. This single element does more for retention than any amount of content — the player is always racing something.

**Game over screen** shows a small bar chart: score-per-loop for this run overlaid on your best run's curve. You can see exactly where it fell apart.

**Records screen** in the main menu lists all tracked stats, plus `RUNS SINCE LAST RECORD: 12`.

---

## 3. Physicality

"More realistic" here doesn't mean photorealism — it means things should have **weight and consequence**. Chase that.

### Carried cores have mass
This is the most important addition in this whole document.

```python
load_factor = 1.0 - (0.045 * cores_carried)   # floor at 0.6
max_speed   = BASE_SPEED * load_factor
turn_rate   = BASE_TURN  * load_factor
```

Eight cores means you're at 64% speed and turn like a barge. The greed mechanic stops being an abstract number on the HUD and becomes something you feel in your hands — every extra core you grab is a physical decision about whether you can still escape.

Sell it visually: the drone visibly sags and tilts, thruster particles thicken, engine pitch drops, and the orbiting cores swing wider with more lag.

### Thrusters
Emit particles opposite the acceleration vector, not the velocity vector — so you see the burn when the player *changes* direction, which is where the skill lives. Particle count scales with acceleration magnitude.

### Inertia and drift
Reversing direction at full speed should produce a short visible slide. Target: ~0.18s to fully reverse. Not floaty, but not on rails.

### Dynamic lighting
Render a light layer before the sprites: a radial green pool under the player, a magenta pool under each ghost, composited additively onto the floor. Where a magenta pool touches the player's green one, brighten the overlap toward white. Now proximity danger is readable in your peripheral vision instead of requiring you to track twelve sprites.

### Camera
Offset the view up to 30px toward the player's movement direction, eased. Zoom out 1% per active ghost, capped at 8%. Both subtle enough that nobody consciously notices and everybody feels.

### Audio
Each ghost emits a low positional hum, panned by screen position, volume by distance. Six ghosts becomes a genuinely oppressive wall of sound. Add one drone layer to the music bed every 2 loops.

---

## 4. New systems

### 4.1 Near-miss detection — build this one first

When the player passes within **34px** of a lethal ghost without dying:

- 60ms of slow-motion (time scale 0.35)
- A sharp high tick, and a brief white rim-flash on the ghost that was grazed
- `+25` score, floating up from the point of the graze
- Increment a `NEAR MISS` counter in the HUD

This is the highest-value feature on this list. It takes the thing that already feels thrilling — barely surviving — and pays you for it. It converts panic into intent. Cap it to one trigger per ghost per 0.5s so a long parallel run doesn't machine-gun it.

### 4.2 Death replay

You already record every ghost path, so this is nearly free: on death, replay the last **2.5 seconds** at 0.35x speed with all ghosts visible and a red ring marking the killer. Then cut to the game over screen.

Seeing your own mistake in slow motion is what converts a death into a retry instead of a quit. Allow skipping with any key.

### 4.3 Loop rank

Grade each loop clear on time, and stamp it large in the center for 0.8s:

| Rank | Clear time |
|---|---|
| S | under 12s |
| A | under 18s |
| B | under 26s |
| C | anything slower |

The rank isn't cosmetic — it *is* the ghost length you just created. Print it plainly under the stamp: `NEXT GHOST: 11.4s`. This teaches the game's core idea in one beat, without a tutorial.

### 4.4 Death cause readout

On the game over screen: `KILLED BY — YOUR LOOP-3 SELF`

Track which recording the fatal ghost came from. It's one line of code, it's thematically perfect, and it's funny in a way that makes people screenshot it.

### 4.5 Bank chain

Bank at least one core on every loop without dying and a chain counter builds. At chain 5+, all banks earn a flat +15% for the rest of the run. Breaking the chain (a loop where you bank nothing) resets it. Gives deep runs a compounding payoff.

### 4.6 The game over line

Under the score, one dynamically chosen sentence, in this priority order:

1. `340 POINTS FROM YOUR BEST.` (if within 15%)
2. `YOUR LOOP-6 BEST STILL STANDS: 4,200.` (if you reached it and fell short)
3. `NEW RECORD.` (flashing)
4. `12 RUNS SINCE YOUR LAST RECORD.`

That first line is worth more for retention than any feature above it. Being told you were *close* is the thing that makes a hand reach for R.

---

## 5. Build order

**Phase 2A** — Section 0 in full. Stop, let me look at it.
**Phase 2B** — Near-miss (4.1), carried-core mass (3), loop rank (4.3). These three change how the game *plays*; test them before adding anything cosmetic.
**Phase 2C** — Records system (2), including the live pace indicator and the game over line.
**Phase 2D** — Difficulty layers (1), one loop-gate at a time.
**Phase 2E** — Death replay (4.2), dynamic lighting, camera, audio.
**Phase 2F** — Bank chain, death cause readout, remaining polish.

Commit after each. Keep every new number in `config.py`.

---

## 6. Acceptance criteria

- [ ] The player is unambiguously the brightest, easiest-to-locate object on screen at all times
- [ ] HUD reads `ESC — PAUSE` and Esc opens the pause menu
- [ ] Carrying 8 cores is visibly and physically harder to maneuver with than carrying 0
- [ ] A near miss triggers slow-mo, a tick, and a score popup, and cannot machine-gun
- [ ] Every loop start flashes that loop's personal best
- [ ] The live pace indicator correctly shows ahead/behind versus the best run at the same loop
- [ ] Death replay shows the last 2.5s and can be skipped
- [ ] Loop rank stamp displays and states the resulting next-ghost duration
- [ ] Nothing in the game can kill the player without having been visible and predictable for at least 1.5s
- [ ] Adaptive core placement never spawns a core inside a ghost's first 1.5s of path
- [ ] All records survive a full application restart
- [ ] 60 FPS holds with 12 ghosts, dynamic lighting, and 300 particles
