"""The player: a lab drone with a little weight to it — and, per Section 0,
unambiguously the brightest thing on screen (layered glow + motion trail)."""

import collections
import math

import pygame

from paradox import config
from paradox.systems import sprites


class Player:
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.angle = -math.pi / 2  # facing up until you move
        self.carried = 0  # cores held, orbiting until banked (or lost on death)
        self.t = 0.0  # local clock for orbit + glow pulse
        self.trail: collections.deque[tuple[float, float]] = collections.deque(maxlen=config.TRAIL_LEN)

    def update(self, dt: float, move_x: float, move_y: float, arena: pygame.Rect) -> None:
        self.t += dt

        length = math.hypot(move_x, move_y)
        if length > 0:
            # Normalize so diagonals aren't ~41% faster than cardinals.
            nx, ny = move_x / length, move_y / length
            accel = config.PLAYER_MAX_SPEED / config.PLAYER_ACCEL_TIME
            self.vx += nx * accel * dt
            self.vy += ny * accel * dt
            speed = math.hypot(self.vx, self.vy)
            if speed > config.PLAYER_MAX_SPEED:
                scale = config.PLAYER_MAX_SPEED / speed
                self.vx *= scale
                self.vy *= scale
        else:
            # No input: damp velocity so stopping feels weighty but quick.
            decay = max(0.0, 1.0 - config.PLAYER_FRICTION * dt)
            self.vx *= decay
            self.vy *= decay

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Clamp to the arena; kill the velocity component pressing into a wall
        # so you don't "stick" when steering away from it.
        r = config.PLAYER_RADIUS
        if self.x < arena.left + r:
            self.x = arena.left + r
            self.vx = max(self.vx, 0.0)
        elif self.x > arena.right - r:
            self.x = arena.right - r
            self.vx = min(self.vx, 0.0)
        if self.y < arena.top + r:
            self.y = arena.top + r
            self.vy = max(self.vy, 0.0)
        elif self.y > arena.bottom - r:
            self.y = arena.bottom - r
            self.vy = min(self.vy, 0.0)

        if math.hypot(self.vx, self.vy) > 20:  # keep the last facing when idle
            self.angle = math.atan2(self.vy, self.vx)

        self.trail.appendleft((self.x, self.y))

    def draw(self, surface: pygame.Surface) -> None:
        store = sprites.get_store()

        # Motion trail (Section 0): newest brightest, additive so it reads as light.
        for i, (tx, ty) in enumerate(self.trail):
            if i == 0:
                continue  # current position sits under the drone itself
            dot = store["trail"][i]
            surface.blit(dot, dot.get_rect(center=(tx, ty)), special_flags=pygame.BLEND_RGB_ADD)

        # Two-layer glow (Section 0): steady wide halo + pulsing inner halo.
        center = (self.x, self.y)
        outer = store["player_glow_outer"]
        surface.blit(outer, outer.get_rect(center=center), special_flags=pygame.BLEND_RGB_ADD)
        levels = store["player_glow_inner"]
        k = 0.5 + 0.5 * math.sin(self.t * math.tau * config.GLOW_PULSE_HZ)
        inner = levels[min(len(levels) - 1, int(k * len(levels)))]
        surface.blit(inner, inner.get_rect(center=center), special_flags=pygame.BLEND_RGB_ADD)

        frame = store["player"].frame_for(self.angle)
        surface.blit(frame, frame.get_rect(center=center))

        # Carried cores orbit you — how loaded (and how at-risk) you are, at a glance.
        for i in range(self.carried):
            a = self.t * config.ORBIT_SPEED + i * math.tau / max(1, self.carried)
            cx = self.x + math.cos(a) * config.ORBIT_RADIUS
            cy = self.y + math.sin(a) * config.ORBIT_RADIUS
            pygame.draw.circle(surface, config.COLOR_GREEN, (cx, cy), 4)
