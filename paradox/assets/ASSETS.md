# PARADOX — Asset Integration Guide

Drop this whole `assets/` folder into `paradox/assets/` and hand this file to Claude Code alongside `PARADOX_build_spec.md`.

All sprites and UI elements are **RGBA PNG with real alpha**, keyed from the original JPEGs. Load with `.convert_alpha()`, never `.convert()`.

---

## Manifest

### `sprites/` — world objects, all pre-trimmed and centered

| File | Size | Use |
|---|---|---|
| `player.png` | 160x160 | The player drone. **Points UP at rest.** |
| `ghost.png` | 160x160 | Divergent copy. Same silhouette as player. |
| `ghost_decay_1_fresh.png` | 160x160 | Ghost from the most recent 1-2 loops |
| `ghost_decay_2_worn.png` | 160x160 | Mid-age ghost, heavier fragmentation |
| `ghost_decay_3_faded.png` | 160x160 | Oldest ghosts, nearly dissolved |
| `core.png` | 96x96 | Collectible energy cell |
| `ghost_spawn.png` | 320x320 | Phase-in effect, played once per ghost at loop start |

### `ui/`

| File | Size | Use |
|---|---|---|
| `logo.png` | 1024x464 | Title on the main menu |
| `panel_frame.png` | 1376x768 | 9-slice frame for menu panels |
| `powerup_phase.png` | 96x96 | Syringe — PHASE SERUM |
| `powerup_dilation.png` | 96x96 | Hourglass — DILATION |
| `powerup_collapse.png` | 96x96 | Collapsing star — COLLAPSE FIELD |
| `powerup_overclock.png` | 96x96 | Lightning bolt — OVERCLOCK |

### `backgrounds/` — no alpha, RGB only

| File | Size | Use |
|---|---|---|
| `bg_menu.png` | 1280x720 | Main menu |
| `bg_loading.png` | 1280x720 | Loading screen |
| `bg_gameover.png` | 1280x720 | Game over screen |
| `floor_tile.png` | 512x512 | Arena floor — **read the warning below** |
| `keyart.png` | 1376x768 | Store page / itch.io only, not in-game |

### `source/`
The 13 unmodified originals. Never load these at runtime — they're kept so assets can be re-derived at different sizes later.

---

## Rules for using these

### 1. The player sprite points UP — correct for it

`pygame.transform.rotate` treats 0° as no rotation, and the sprite art faces up (−Y). Standard `atan2` math gives 0° as facing right. So:

```python
angle_deg = math.degrees(math.atan2(-vel.y, vel.x)) - 90
rotated = pygame.transform.rotate(self.image, angle_deg)
rect = rotated.get_rect(center=self.pos)
```

Getting this wrong makes the drone fly sideways forever and it is not obvious from reading the code. Verify it visually in Phase 1.

### 2. Cache every rotation — do not rotate per frame

`transform.rotate` on a 160x160 surface, 12 ghosts, 60 times a second will tank the framerate. Pre-render rotations once at load into a lookup table:

```python
ROT_STEPS = 72  # 5-degree increments, visually indistinguishable from smooth
self._rot_cache = [
    pygame.transform.rotozoom(base_img, -i * (360 / ROT_STEPS), scale)
    for i in range(ROT_STEPS)
]
# at draw time:
frame = self._rot_cache[int(angle_deg % 360 / (360 / ROT_STEPS))]
```

### 3. Scale down at load, once — never per frame

Source sprites are oversized on purpose so they stay sharp. Downscale to gameplay size a single time during the loading screen:

```python
PLAYER_PX = 44   # in config.py
CORE_PX   = 26
GHOST_PX  = 44
img = pygame.transform.smoothscale(raw, (PLAYER_PX, PLAYER_PX))
```

Do this work inside the loading state so it visibly fills the progress bar. That is what the loading screen is for.

### 4. Glow stays in code

These sprites were keyed to preserve their soft edges, but the *dynamic* glow — the pulse when you pick up a core, the flare when you bank — must still be drawn additively underneath the sprite:

```python
glow = pygame.transform.smoothscale(img, (int(w * 1.8), int(h * 1.8)))
glow.set_alpha(90 + int(60 * math.sin(t * 4)))
surface.blit(glow, glow_rect, special_flags=pygame.BLEND_RGB_ADD)
surface.blit(img, rect)
```

A baked-in glow is a dead glow. The whole feel of this game is that the light reacts.

### 5. Ghost decay variants map to age, not to loop number

```python
age = current_loop - ghost.recorded_on_loop
img = GHOST_FRESH if age <= 2 else (GHOST_WORN if age <= 5 else GHOST_FADED)
```

Layer a per-ghost alpha on top of that (`200 → 120 → 70`) so depth reads even between tiers.

### 6. `panel_frame.png` must be 9-sliced

It's a fixed-size frame with clipped corners and corner brackets. Stretching it whole will distort the corners. Slice it into 9 regions with roughly a 60px inset, stretch only the edges and center, and blit corners at native size. Write a small `draw_frame(surface, rect)` helper in `ui/widgets.py` and use it everywhere.

### 7. Every load needs a fallback

The old project died because a missing `terminal.png` crashed it. Do not repeat that:

```python
def load_sprite(name, size, fallback_color):
    try:
        img = pygame.image.load(ASSETS / name).convert_alpha()
        return pygame.transform.smoothscale(img, (size, size))
    except (pygame.error, FileNotFoundError):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.polygon(surf, fallback_color,
                            [(size//2, 0), (size, size), (size//2, size*0.75), (0, size)])
        return surf
```

The game must launch and be fully playable with the entire `assets/` folder deleted.

---

## Known issues — do not paper over these

**`floor_tile.png` does not tile.** Measured seam error is 6.1 on the left/right edges and 29.9 top/bottom — the vertical seam will be plainly visible as a hard line across the arena. Do **not** use it with a tiling blit. Instead, scale the single image to cover the whole arena as a static backdrop, or crop the cleanest interior region and offset-blend the edges. If you want a true tile, regenerate it with a seamless-tiling toggle.

**`panel_frame.png` originally had a checkerboard painted into it.** The generator drew a picture of a transparency checkerboard rather than producing real transparency. That pattern has been stripped and only the green line work survives — but the interior is now fully empty, so draw your own translucent fill behind it.

**The player sprite has magenta thruster accents.** Magenta is the ghost/hazard color everywhere else in this game, so it reads slightly wrong on the player. Two options: tint those pixels toward amber at load time, or lean in and treat it as the machine already starting to corrupt you. Pick deliberately, don't leave it unconsidered.

**`bg_menu.png` and `bg_loading.png` are 1280x720 exactly** — matching the window. They will not survive a resize. Keep the window fixed for v1, as the spec says.
