"""Sprite loading: scale once at load, cache rotations, always have a fallback.

Implements the rules in paradox/assets/ASSETS.md:
- scale to gameplay size a single time (rule 3)
- pre-render rotation steps instead of rotating per frame (rule 2)
- the art points UP, so movement angles need a -90 degree correction (rule 1)
- every load falls back to a drawn placeholder; the game must stay fully
  playable with the assets folder deleted (rule 7)
"""

import math
from pathlib import Path

import pygame

from paradox import config

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
_STEP = 360.0 / config.SPRITE_ROT_STEPS

_store: dict | None = None


def load_sprite(rel_name: str, size: int, fallback_color: tuple[int, int, int]) -> pygame.Surface:
    try:
        img = pygame.image.load(str(ASSETS_DIR / rel_name)).convert_alpha()
        return pygame.transform.smoothscale(img, (size, size))
    except (pygame.error, FileNotFoundError, OSError):
        # Drawn stand-in: an up-pointing arrowhead, same convention as the art,
        # so the rotation math (and the game) works with zero assets present.
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        s = size - 1
        pygame.draw.polygon(surf, fallback_color, [(s // 2, 0), (s, s), (s // 2, int(s * 0.72)), (0, s)])
        return surf


class RotSprite:
    """A sprite pre-rendered at every SPRITE_ROT_STEPS rotation.

    transform.rotate on a dozen 160px ghosts at 60 FPS would tank the frame
    budget, so every orientation is baked once here and draw time becomes a
    list lookup. 5-degree steps are visually indistinguishable from smooth.
    """

    def __init__(self, base: pygame.Surface):
        self.frames = [
            pygame.transform.rotozoom(base, i * _STEP, 1.0) for i in range(config.SPRITE_ROT_STEPS)
        ]

    def frame_for(self, angle_rad: float) -> pygame.Surface:
        """Frame for a movement angle (radians, screen-space atan2(vy, vx)).

        The art faces up and pygame rotates counterclockwise, while screen y
        points down — so the movement angle maps to a rotation of
        (-degrees(angle) - 90). Verified by a pixel probe in the smoke test:
        get this wrong and the drone flies sideways forever.
        """
        deg = (-math.degrees(angle_rad) - 90.0) % 360.0
        return self.frames[round(deg / _STEP) % config.SPRITE_ROT_STEPS]


def _glow(img: pygame.Surface, alpha: int) -> pygame.Surface:
    """Soft halo blitted additively under a sprite.

    Pre-baked once; the dimming is multiplied into the pixels (not set_alpha)
    because additive blits don't reliably honor per-surface alpha. A blurry
    halo doesn't visibly rotate, so one unrotated copy serves every facing.
    """
    w, h = img.get_size()
    g = pygame.transform.smoothscale(img, (int(w * config.GLOW_SCALE), int(h * config.GLOW_SCALE)))
    g.fill((alpha, alpha, alpha), special_flags=pygame.BLEND_RGB_MULT)
    return g


def get_store() -> dict:
    """Lazy singleton. Phase 2's loading screen takes over pre-warming this."""
    global _store
    if _store is None:
        player = load_sprite("sprites/player.png", config.PLAYER_SPRITE_PX, config.COLOR_WHITE)
        core = load_sprite("sprites/core.png", config.CORE_SPRITE_PX, config.COLOR_GREEN)
        _store = {
            "player": RotSprite(player),
            "player_glow": _glow(player, config.GLOW_ALPHA),
            "core": core,
            "core_glow": _glow(core, config.GLOW_ALPHA),
            "ghost_fresh": RotSprite(
                load_sprite("sprites/ghost_decay_1_fresh.png", config.GHOST_SPRITE_PX, config.COLOR_MAGENTA)
            ),
            "ghost_worn": RotSprite(
                load_sprite("sprites/ghost_decay_2_worn.png", config.GHOST_SPRITE_PX, config.COLOR_MAGENTA)
            ),
            "ghost_faded": RotSprite(
                load_sprite("sprites/ghost_decay_3_faded.png", config.GHOST_SPRITE_PX, config.COLOR_MAGENTA)
            ),
        }
    return _store
