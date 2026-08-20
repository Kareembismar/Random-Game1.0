"""The portal: bank carried cores here. It relocates every time you use it."""

import math
import random

import pygame

from paradox import config


class Portal:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.t = 0.0

    def update(self, dt: float) -> None:
        self.t += dt

    def relocate(self, arena: pygame.Rect, rng: random.Random) -> None:
        """Jump somewhere new, far enough away that camping it is impossible."""
        zone = arena.inflate(-2 * config.PORTAL_MARGIN, -2 * config.PORTAL_MARGIN)
        best, best_d = (float(zone.centerx), float(zone.centery)), -1.0
        for _ in range(200):
            x = rng.uniform(zone.left, zone.right)
            y = rng.uniform(zone.top, zone.bottom)
            d = math.hypot(x - self.x, y - self.y)
            if d >= config.PORTAL_MIN_RELOCATE_DIST:
                self.x, self.y = x, y
                return
            if d > best_d:
                best, best_d = (x, y), d
        self.x, self.y = best  # arena too tight for the full distance; take the farthest try

    def draw(self, surface: pygame.Surface) -> None:
        r = config.PORTAL_RADIUS + math.sin(self.t * 2.2) * 2
        pygame.draw.circle(surface, config.COLOR_BG_PORTAL, (self.x, self.y), r * 0.8)
        pygame.draw.circle(surface, config.COLOR_GREEN, (self.x, self.y), r, 2)
        pygame.draw.circle(surface, config.COLOR_DIM_GREEN, (self.x, self.y), r * 0.62, 1)
        # A few orbiting sparks suggest the swirl (real inward particles in Phase 3).
        for i in range(3):
            a = self.t * 1.8 + i * math.tau / 3
            sx = self.x + math.cos(a) * r * 0.45
            sy = self.y + math.sin(a) * r * 0.45
            pygame.draw.circle(surface, config.COLOR_GREEN, (sx, sy), 2)
