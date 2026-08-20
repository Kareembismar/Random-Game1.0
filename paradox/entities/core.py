"""Cores: the collectible. Grab them, carry them, bank them before you die."""

import math

import pygame

from paradox import config
from paradox.systems import sprites


class Core:
    def __init__(self, x: float, y: float, phase: float = 0.0):
        self.x = x
        self.y = y
        self.t = phase  # random start phase so the field doesn't pulse in unison

    def update(self, dt: float) -> None:
        self.t += dt

    def draw(self, surface: pygame.Surface) -> None:
        store = sprites.get_store()
        glow = store["core_glow"]
        surface.blit(glow, glow.get_rect(center=(self.x, self.y)), special_flags=pygame.BLEND_RGB_ADD)
        img = store["core"]
        surface.blit(img, img.get_rect(center=(self.x, self.y)))
        # The "pick me up" read is this procedural ring, not sprite detail
        # (Section 0) — a thin ring breathing between CORE_RING_MIN and MAX.
        mid = (config.CORE_RING_MIN + config.CORE_RING_MAX) / 2
        amp = (config.CORE_RING_MAX - config.CORE_RING_MIN) / 2
        r = mid + amp * math.sin(self.t * config.CORE_PULSE_SPEED)
        pygame.draw.circle(surface, config.COLOR_DIM_GREEN, (self.x, self.y), r, 1)
