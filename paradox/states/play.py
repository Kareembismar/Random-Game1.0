"""The game itself: one run of PARADOX, from loop 1 until death.

Phase 1 scope: movement, cores, banking, loop advancement, ghost
recording/playback, death. Visuals are deliberate placeholders — the juice
pass (particles, shake, trails, CRT, audio) is Phase 3.
"""

import math
import random

import pygame

from paradox import config
from paradox.entities.core import Core
from paradox.entities.ghost import Ghost
from paradox.entities.player import Player
from paradox.entities.portal import Portal
from paradox.states.base import State
from paradox.systems.recorder import Recorder, Recording
from paradox.ui.fonts import get_font


def _move_vector() -> tuple[float, float]:
    """Raw WASD/arrow input as an (x, y) direction. The player normalizes it."""
    keys = pygame.key.get_pressed()
    mx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
    my = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
    return float(mx), float(my)


def _lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class PlayState(State):
    def __init__(self):
        self.rng = random.Random()
        self.arena = pygame.Rect(config.ARENA_RECT)
        self.player = Player(*self.arena.center)
        self.portal = Portal(
            *self._point_away_from(self.arena.center, config.PORTAL_MIN_FROM_PLAYER, config.PORTAL_MARGIN)
        )
        self.recordings: list[Recording] = []
        self.ghosts: list[Ghost] = []
        self.loop = 1
        self.score = 0
        self.banked_this_loop = 0
        self.cores: list[Core] = []
        self.total_cores = 0
        self._spawn_cores()
        self.recorder = Recorder()
        self.recorder.start(self.player.x, self.player.y, self.player.angle)

    # ---- scoring -------------------------------------------------------

    @property
    def multiplier(self) -> float:
        return 1.0 + config.MULTIPLIER_PER_CORE * self.player.carried

    # ---- setup helpers ---------------------------------------------------

    def _point_away_from(self, origin, min_dist: float, margin: float) -> tuple[float, float]:
        """Random arena point at least min_dist from origin (best effort)."""
        zone = self.arena.inflate(-2 * margin, -2 * margin)
        ox, oy = origin
        best, best_d = (float(zone.centerx), float(zone.centery)), -1.0
        for _ in range(200):
            x = self.rng.uniform(zone.left, zone.right)
            y = self.rng.uniform(zone.top, zone.bottom)
            d = math.hypot(x - ox, y - oy)
            if d >= min_dist:
                return x, y
            if d > best_d:
                best, best_d = (x, y), d
        return best

    def _spawn_cores(self) -> None:
        count = min(config.CORES_BASE + self.loop, config.CORES_CAP)
        zone = self.arena.inflate(-2 * config.CORE_MARGIN, -2 * config.CORE_MARGIN)
        placed: list[tuple[float, float]] = []
        for _ in range(count):
            pos = None
            for _attempt in range(300):
                x = self.rng.uniform(zone.left, zone.right)
                y = self.rng.uniform(zone.top, zone.bottom)
                # Keep spawns off the player and spread apart, per spec.
                if math.hypot(x - self.player.x, y - self.player.y) < config.CORE_MIN_DIST_FROM_PLAYER:
                    continue
                if any(math.hypot(x - px, y - py) < config.CORE_MIN_DIST_APART for px, py in placed):
                    continue
                pos = (x, y)
                break
            if pos is None:  # crowded arena: accept "away from player" over hanging
                pos = self._point_away_from(
                    (self.player.x, self.player.y), config.CORE_MIN_DIST_FROM_PLAYER, config.CORE_MARGIN
                )
            placed.append(pos)
        self.cores = [Core(x, y, self.rng.uniform(0, math.tau)) for x, y in placed]
        self.total_cores = count

    # ---- simulation ------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.running = False  # Phase 2 replaces this with PAUSE

    def update(self, dt: float) -> None:
        mx, my = _move_vector()
        self.player.update(dt, mx, my, self.arena)
        self.recorder.add(dt, self.player.x, self.player.y, self.player.angle)

        self.portal.update(dt)
        for core in self.cores:
            core.update(dt)
        for ghost in self.ghosts:
            ghost.update(dt)
        self.ghosts = [g for g in self.ghosts if not g.expired]

        self._check_pickups()
        self._check_banking()
        self._check_ghost_collision()

    def _check_pickups(self) -> None:
        for core in self.cores[:]:
            if math.hypot(core.x - self.player.x, core.y - self.player.y) <= config.CORE_PICKUP_RADIUS:
                self.cores.remove(core)
                self.player.carried += 1

    def _check_banking(self) -> None:
        if self.player.carried == 0:
            return
        if math.hypot(self.portal.x - self.player.x, self.portal.y - self.player.y) > config.PORTAL_BANK_RADIUS:
            return
        # Compute the payout BEFORE emptying hands — multiplier reads carried.
        gained = int(round(self.player.carried * config.CORE_VALUE * self.multiplier))
        self.score += gained
        self.banked_this_loop += self.player.carried
        self.player.carried = 0
        self.portal.relocate(self.arena, self.rng)
        if self.banked_this_loop >= self.total_cores:
            self._advance_loop()

    def _advance_loop(self) -> None:
        # The loop you just played becomes next loop's newest ghost.
        self.recordings.append(self.recorder.finish())
        while len(self.recordings) > config.GHOST_MAX:
            self.recordings.pop(0)  # over the cap: the oldest recording is gone for good
        self.loop += 1
        self.banked_this_loop = 0
        n = len(self.recordings)
        self.ghosts = [Ghost(rec, age=n - 1 - i) for i, rec in enumerate(self.recordings)]
        self._spawn_cores()
        self.recorder.start(self.player.x, self.player.y, self.player.angle)

    def _check_ghost_collision(self) -> None:
        for ghost in self.ghosts:
            if not ghost.lethal:
                continue
            gx, gy, _ = ghost.pos()
            if (
                math.hypot(gx - self.player.x, gy - self.player.y)
                <= config.GHOST_HIT_RADIUS + config.PLAYER_HIT_RADIUS
            ):
                self._die()
                return

    def _die(self) -> None:
        from paradox.states.gameover import GameOverState  # local import: gameover imports us

        self.manager.replace(GameOverState(score=self.score, loop=self.loop))

    # ---- drawing -----------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(config.COLOR_BG)
        self._draw_arena(surface)
        self.portal.draw(surface)
        for core in self.cores:
            core.draw(surface)
        for ghost in self.ghosts:
            ghost.draw(surface)
        self.player.draw(surface)
        self._draw_hud(surface)

    def _draw_arena(self, surface: pygame.Surface) -> None:
        a = self.arena
        for x in range(a.left, a.right + 1, config.GRID_STEP):
            pygame.draw.line(surface, config.COLOR_GRID, (x, a.top), (x, a.bottom))
        for y in range(a.top, a.bottom + 1, config.GRID_STEP):
            pygame.draw.line(surface, config.COLOR_GRID, (a.left, y), (a.right, y))
        pygame.draw.rect(surface, config.COLOR_GREEN, a, 2)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        small = get_font(config.FONT_SMALL)
        mid = get_font(config.FONT_MID)

        surface.blit(small.render(f"SCORE {self.score:,}", True, config.COLOR_GREEN), (20, 24))

        # Multiplier, center: green → yellow → magenta as the greed climbs.
        carried = self.player.carried
        if carried <= 4:
            col = _lerp_color(config.COLOR_GREEN, config.COLOR_YELLOW, carried / 4)
        else:
            col = _lerp_color(config.COLOR_YELLOW, config.COLOR_MAGENTA, (carried - 4) / 4)
        m = mid.render(f"x{self.multiplier:.2f}", True, col)
        surface.blit(m, (surface.get_width() // 2 - m.get_width() // 2, 18))

        right1 = small.render(f"LOOP {self.loop}", True, config.COLOR_GREEN)
        right2 = small.render(f"CORES {self.banked_this_loop}/{self.total_cores}", True, config.COLOR_HUD_DIM)
        surface.blit(right1, (surface.get_width() - right1.get_width() - 20, 14))
        surface.blit(right2, (surface.get_width() - right2.get_width() - 20, 38))

        esc = small.render("ESC — QUIT", True, config.COLOR_HUD_DIM)
        surface.blit(esc, (20, surface.get_height() - 32))
