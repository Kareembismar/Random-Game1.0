"""CRT overlay: scanlines + vignette, pre-rendered once and blitted last.

Building this per frame would be absurdly slow (it touches every pixel);
building it once at load costs a few milliseconds and after that it's a
single blit. The loading screen uses it now; Phase 3 applies it globally.
"""

import pygame

_cache: dict[tuple[int, int], pygame.Surface] = {}


def get_overlay(size: tuple[int, int]) -> pygame.Surface:
    if size not in _cache:
        w, h = size
        overlay = pygame.Surface(size, pygame.SRCALPHA)

        # Scanlines: a dark 1px line every 3px, low alpha.
        for y in range(0, h, 3):
            pygame.draw.line(overlay, (0, 0, 0, 55), (0, y), (w, y))

        # Vignette: computed per-pixel on a tiny surface, then smoothscaled up —
        # smooth radial falloff without touching all 900k real pixels.
        small = pygame.Surface((64, 36), pygame.SRCALPHA)
        for sy in range(36):
            for sx in range(64):
                dx = (sx / 63 - 0.5) * 2
                dy = (sy / 35 - 0.5) * 2
                d = (dx * dx + dy * dy) ** 0.5
                a = min(130, int(150 * max(0.0, d - 0.62)))
                small.set_at((sx, sy), (0, 0, 0, a))
        overlay.blit(pygame.transform.smoothscale(small, size), (0, 0))

        _cache[size] = overlay
    return _cache[size]
