"""Sprite/image loading: scale once at load, cache rotations, always fall back.

Implements the rules in paradox/assets/ASSETS.md:
- scale to gameplay size a single time (rule 3)
- pre-render rotation steps instead of rotating per frame (rule 2)
- the art points UP, so movement angles need a -90 degree correction (rule 1)
- every load falls back to a drawn placeholder; the game must stay fully
  playable with the assets folder deleted (rule 7)

Additive-blit note (used by every glow and trail in the game): BLEND_RGB_ADD
sums RGB channels and ignores alpha, so anything meant for additive drawing
keeps its brightness in RGB — dimming is multiplied into the pixels at build
time, and "transparent" regions must simply be black.
"""

import math
from pathlib import Path

import pygame

from paradox import config

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
_STEP = 360.0 / config.SPRITE_ROT_STEPS

_store: dict | None = None


def load_image(rel_name: str, size: tuple[int, int] | None = None, alpha: bool = True):
    """A non-square image (logo, background, panel), or None if missing.

    Callers own their fallback — a menu without background art is a color
    fill, not a crash.
    """
    try:
        img = pygame.image.load(str(ASSETS_DIR / rel_name))
        img = img.convert_alpha() if alpha else img.convert()
        if size is not None:
            img = pygame.transform.smoothscale(img, size)
        return img
    except (pygame.error, FileNotFoundError, OSError):
        return None


def load_sprite(rel_name: str, size: int, fallback_color: tuple[int, int, int]) -> pygame.Surface:
    try:
        img = pygame.image.load(str(ASSETS_DIR / rel_name)).convert_alpha()
        return pygame.transform.smoothscale(img, (size, size))
    except (pygame.error, FileNotFoundError, OSError):
        # Drawn stand-in: an up-pointing arrowhead, same convention as the art.
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        s = size - 1
        pygame.draw.polygon(surf, fallback_color, [(s // 2, 0), (s, s), (s // 2, int(s * 0.72)), (0, s)])
        return surf


class RotSprite:
    """A sprite pre-rendered at every SPRITE_ROT_STEPS rotation.

    transform.rotate on a dozen ghosts at 60 FPS would tank the frame budget,
    so every orientation is baked once and draw time is a list lookup.
    """

    def __init__(self, base: pygame.Surface):
        self.frames = [
            pygame.transform.rotozoom(base, i * _STEP, 1.0) for i in range(config.SPRITE_ROT_STEPS)
        ]

    def frame_for(self, angle_rad: float) -> pygame.Surface:
        """Frame for a movement angle (radians, screen-space atan2(vy, vx)).

        The art faces up and pygame rotates counterclockwise, while screen y
        points down — so the movement angle maps to a rotation of
        (-degrees(angle) - 90). Verified by a pixel probe in the smoke test.
        """
        deg = (-math.degrees(angle_rad) - 90.0) % 360.0
        return self.frames[round(deg / _STEP) % config.SPRITE_ROT_STEPS]


def _glow(img: pygame.Surface, scale: float, alpha: int) -> pygame.Surface:
    """Soft halo for additive blits: scaled-up sprite, brightness baked into RGB.

    One unrotated copy serves every facing — a blurry halo doesn't visibly
    rotate.
    """
    w, h = img.get_size()
    g = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
    g.fill((alpha, alpha, alpha), special_flags=pygame.BLEND_RGB_MULT)
    return g


def _soft_dot(radius: int, color: tuple[int, int, int], intensity: float) -> pygame.Surface:
    """Radial-gradient dot for additive blits (motion trails)."""
    s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        k = (intensity / 255.0) * ((radius - r) / radius)
        pygame.draw.circle(s, tuple(int(c * k) for c in color), (radius, radius), r)
    return s


def get_store() -> dict:
    """Lazy singleton; the loading screen pre-warms it as one of its work steps."""
    global _store
    if _store is None:
        player = load_sprite("sprites/player.png", config.PLAYER_PX, config.COLOR_WHITE)

        core = load_sprite("sprites/core.png", config.CORE_PX, config.COLOR_GREEN)
        b = int(255 * config.CORE_BRIGHTNESS)  # Section 0: the player must out-shine cores
        core.fill((b, b, b), special_flags=pygame.BLEND_RGB_MULT)

        # Pulsing inner glow = pre-baked intensity ladder; draw picks by sine.
        n = config.GLOW_PULSE_LEVELS
        inner = [
            _glow(
                player,
                config.GLOW_INNER_SCALE,
                config.GLOW_INNER_ALPHA - config.GLOW_INNER_PULSE
                + round(2 * config.GLOW_INNER_PULSE * i / (n - 1)),
            )
            for i in range(n)
        ]
        trail = [
            _soft_dot(
                config.TRAIL_DOT_RADIUS,
                config.COLOR_GREEN,
                config.TRAIL_ALPHA * (1 - i / config.TRAIL_LEN),
            )
            for i in range(config.TRAIL_LEN)
        ]

        _store = {
            "player": RotSprite(player),
            "player_glow_inner": inner,
            "player_glow_outer": _glow(player, config.GLOW_OUTER_SCALE, config.GLOW_OUTER_ALPHA),
            "core": core,
            "core_glow": _glow(core, config.GLOW_SCALE, config.GLOW_ALPHA),
            "trail": trail,  # index 0 = newest/brightest
            "ghost_fresh": RotSprite(
                load_sprite("sprites/ghost_decay_1_fresh.png", config.GHOST_PX, config.COLOR_MAGENTA)
            ),
            "ghost_worn": RotSprite(
                load_sprite("sprites/ghost_decay_2_worn.png", config.GHOST_PX, config.COLOR_MAGENTA)
            ),
            "ghost_faded": RotSprite(
                load_sprite("sprites/ghost_decay_3_faded.png", config.GHOST_PX, config.COLOR_MAGENTA)
            ),
        }
    return _store
