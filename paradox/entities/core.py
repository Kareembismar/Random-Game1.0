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
        # The reactive pulse stays code-drawn (ASSETS.md rule 4: a baked-in glow
        # is a dead glow) — a thin ring breathing around the cell.
        pulse = math.sin(self.t * config.CORE_PULSE_SPEED)
        pygame.draw.circle(
            surface, config.COLOR_DIM_GREEN, (self.x, self.y), config.CORE_RADIUS + 8 + pulse * 3, 1
        )
