"""Font access with a safe fallback chain. Never crash over a missing font."""

import pygame

from paradox import config

_cache: dict[int, pygame.font.Font] = {}


def get_font(size: int) -> pygame.font.Font:
    if size not in _cache:
        # SysFont walks the comma-separated chain and falls back to pygame's
        # bundled default font if none of them exist on this machine.
        _cache[size] = pygame.font.SysFont(config.FONT_CHAIN, size)
    return _cache[size]
