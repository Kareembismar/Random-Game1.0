"""The game itself: one run of PARADOX, from loop 1 until death.

A loop runs in two beats: an optional SURVEY (frozen, for planning — loop 5+)
and then the live loop. Esc pushes PauseState on top of this state; death
holds a freeze-frame with a white flash before the report.
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
from paradox.systems import save
from paradox.systems.collision import closest_approach
from paradox.systems.power import Battery
from paradox.systems.recorder import Recorder, Recording
from paradox.ui import timeline
from paradox.ui.fonts import get_font

# One centred line per unlock, shown once for two seconds (complexity budget).
# Dry register: state the rule, don't sell it.
UNLOCK_LINES = {
    config.SURVEY_UNLOCK_LOOP: "SURVEY — THREE SECONDS TO LOOK. SPACE TO BEGIN.",
}


def _move_vector() -> tuple[float, float]:
    """Raw WASD/arrow input as an (x, y) direction. The player normalizes it."""
    keys = pygame.key.get_pressed()
    mx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
    my = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
    return float(mx), float(my)


def _lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _toward_grey(color: tuple[int, int, int], k: float) -> tuple[int, int, int]:
    """Desaturate toward equal-luminance grey. k=0 untouched, k=1 fully grey."""
    lum = int(0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])
    return _lerp_color(color, (lum, lum, lum), k)


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
        self.loop_t = 0.0  # seconds since this loop's live beat began
        self.score = 0
        self.banked_this_loop = 0
        self.total_banked = 0  # across the whole run, for the death report
        self.longest_loop = 0.0  # longest completed loop, seconds
        self.run_time = 0.0
        self.near_misses = 0
        self.slowmo = 0.0  # real seconds of slow motion remaining
        self.survey_t: float | None = None  # counts down during the survey beat
        self.announce = ""
        self.announce_t = 0.0
        self.popups: list[list] = []  # [x, y, text, age] floating score marks
        self.battery = Battery()
        self.dying: float | None = None  # death freeze-frame timer
        self.death_cause = config.DEATH_CAUSE_GHOST
        self.cores: list[Core] = []
        self.total_cores = 0
        self._spawn_cores()
        self.recorder = Recorder()
        self.recorder.start(self.player.x, self.player.y, self.player.angle)
        # Additive strip for the arena's drifting scanline sweep.
        self._sweep = pygame.Surface((self.arena.width, 2))
        k = config.SWEEP_BRIGHTNESS / 255
        self._sweep.fill(tuple(int(c * k) for c in config.COLOR_GREEN))
        self._flash = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        self._flash.fill((255, 255, 255))
        # Grey wash for the low-power desaturation. Drawn over the floor only,
        # never over the entities — the lights going out must never make a
        # lethal ghost harder to see.
        self._wash = pygame.Surface(self.arena.size, pygame.SRCALPHA)

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
        if self.dying is not None:
            return  # no pausing out of your own death
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            from paradox.states.pause import PauseState  # local import: pause imports us

            self.manager.push(PauseState(self))
        elif event.key == pygame.K_SPACE and self.survey_t is not None:
            self._end_survey()  # done looking

    def update(self, dt: float) -> None:
        self.run_time += dt
        self.announce_t = max(0.0, self.announce_t - dt)

        if self.dying is not None:
            # Freeze-frame: nothing simulates, the flash decays, then the report.
            self.dying += dt
            if self.dying >= config.DEATH_FREEZE:
                self._finish_death()
            return

        if self.survey_t is not None:
            # Survey beat: the arena is legible but nothing moves. Cores keep
            # pulsing so the screen doesn't look frozen-broken.
            self.survey_t -= dt
            for core in self.cores:
                core.update(dt)
            self.portal.update(dt)
            if self.survey_t <= 0.0:
                self._end_survey()
            return

        # Near-miss slow motion: the clock burns in real time, the world runs
        # at NEARMISS_TIME_SCALE, so a graze reads as a held breath.
        if self.slowmo > 0.0:
            self.slowmo = max(0.0, self.slowmo - dt)
            dt *= config.NEARMISS_TIME_SCALE

        self.loop_t += dt
        self._update_popups(dt)

        # Swept collision needs where everything WAS as well as where it is.
        prev_player = (self.player.x, self.player.y)
        prev_ghosts = [g.pos()[:2] if g.materialized else None for g in self.ghosts]

        mx, my = _move_vector()
        self.player.update(dt, mx, my, self.arena)
        self.recorder.add(dt, self.player.x, self.player.y, self.player.angle)

        self.portal.update(dt)
        for core in self.cores:
            core.update(dt)
        for ghost in self.ghosts:
            ghost.update(dt)

        self._check_pickups()
        self._check_banking()
        self._check_ghost_proximity(prev_player, prev_ghosts)
        if self.dying is None:
            self._drain_power(dt)

    def _drain_power(self, dt: float) -> None:
        if not config.POWER_ENABLED:
            return
        self.battery.drain(dt, math.hypot(self.player.vx, self.player.vy))
        if self.battery.empty:
            self._die(config.DEATH_CAUSE_POWER)

    def _die(self, cause: str) -> None:
        self.death_cause = cause
        self.dying = 0.0  # freeze-frame starts this instant

    def _update_popups(self, dt: float) -> None:
        for p in self.popups:
            p[1] -= config.POPUP_RISE * dt
            p[3] += dt
        self.popups = [p for p in self.popups if p[3] < config.POPUP_TIME]

    def _check_pickups(self) -> None:
        for core in self.cores[:]:
            if math.hypot(core.x - self.player.x, core.y - self.player.y) <= config.CORE_PICKUP_RADIUS:
                self.cores.remove(core)
                self.player.carried += 1
                self.battery.add(config.POWER_PER_CORE)

    def _check_banking(self) -> None:
        if self.player.carried == 0:
            return
        if math.hypot(self.portal.x - self.player.x, self.portal.y - self.player.y) > config.PORTAL_BANK_RADIUS:
            return
        # Compute the payout BEFORE emptying hands — multiplier reads carried.
        gained = int(round(self.player.carried * config.CORE_VALUE * self.multiplier))
        self.score += gained
        self.banked_this_loop += self.player.carried
        self.total_banked += self.player.carried
        self.battery.add(config.POWER_PER_BANK * self.player.carried)
        self.player.carried = 0
        self.portal.relocate(self.arena, self.rng)
        if self.banked_this_loop >= self.total_cores:
            self._advance_loop()

    def _advance_loop(self) -> None:
        # The loop you just played becomes next loop's newest ghost.
        finished = self.recorder.finish()
        self.longest_loop = max(self.longest_loop, finished.duration)
        self.recordings.append(finished)
        while len(self.recordings) > config.GHOST_MAX:
            self.recordings.pop(0)  # over the cap: the oldest recording is gone for good
        self.loop += 1
        self.banked_this_loop = 0
        self.loop_t = 0.0

        n = len(self.recordings)
        self.ghosts = []
        for i, rec in enumerate(self.recordings):
            age = n - 1 - i
            # Stagger arrivals by age so a deep stack cascades in rather than
            # materializing as one wall — readable, and it opens real gaps.
            delay = min(age * config.GHOST_STAGGER, config.GHOST_STAGGER_MAX)
            self.ghosts.append(Ghost(rec, age=age, delay=delay))

        self._spawn_cores()

        if self.loop in UNLOCK_LINES:
            self.announce = UNLOCK_LINES[self.loop]
            self.announce_t = config.ANNOUNCE_TIME

        if config.SURVEY_ENABLED and self.loop >= config.SURVEY_UNLOCK_LOOP:
            self.survey_t = config.SURVEY_TIME  # recorder starts when the survey ends
        else:
            self.recorder.start(self.player.x, self.player.y, self.player.angle)

    def _end_survey(self) -> None:
        self.survey_t = None
        self.recorder.start(self.player.x, self.player.y, self.player.angle)

    def _check_ghost_proximity(self, prev_player, prev_ghosts) -> None:
        """One swept distance per ghost decides both death and near-miss.

        Using the same measured quantity for both means they can never
        disagree — a graze is exactly "close enough to score, not close
        enough to kill".
        """
        now_player = (self.player.x, self.player.y)
        kill_dist = config.GHOST_HIT_RADIUS + config.PLAYER_HIT_RADIUS

        for ghost, prev in zip(self.ghosts, prev_ghosts):
            if not ghost.lethal:
                continue
            gx, gy, _ = ghost.pos()
            g_from = prev if prev is not None else (gx, gy)
            dist, s = closest_approach(prev_player, now_player, g_from, (gx, gy))

            if dist <= kill_dist:
                self._die(config.DEATH_CAUSE_GHOST)
                return

            if (
                config.NEARMISS_ENABLED
                and dist <= config.NEARMISS_RADIUS
                and ghost.nearmiss_cd <= 0.0
            ):
                self._near_miss(ghost, prev_player, now_player, s)

    def _near_miss(self, ghost: Ghost, p0, p1, s: float) -> None:
        ghost.nearmiss_cd = config.NEARMISS_COOLDOWN  # no machine-gunning
        ghost.flash = config.NEARMISS_FLASH_TIME
        self.near_misses += 1
        self.score += config.NEARMISS_SCORE
        self.slowmo = config.NEARMISS_SLOWMO_TIME
        # Place the popup where the two actually passed each other.
        self.popups.append(
            [p0[0] + (p1[0] - p0[0]) * s, p0[1] + (p1[1] - p0[1]) * s, f"+{config.NEARMISS_SCORE}", 0.0]
        )

    def _finish_death(self) -> None:
        from paradox.states.gameover import GameOverState  # local import: gameover imports us

        new_best = save.record_run(self.score, self.loop)
        self.manager.replace(
            GameOverState(
                score=self.score,
                loop=self.loop,
                banked=self.total_banked,
                longest_loop=self.longest_loop,
                new_best=new_best,
                cause=self.death_cause,
            )
        )

    # ---- drawing -----------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(config.COLOR_BG)
        self._draw_arena(surface)
        self._draw_current_path(surface)  # on the floor, under everything live
        self.portal.draw(surface)
        for core in self.cores:
            core.draw(surface)
        for ghost in self.ghosts:
            ghost.draw(surface)
        self.player.draw(surface)
        self._draw_power(surface)
        if self.survey_t is not None:
            self._draw_survey(surface)
        self._draw_popups(surface)
        self._draw_hud(surface)
        if self.dying is not None:
            alpha = config.DEATH_FLASH_ALPHA * max(0.0, 1.0 - self.dying / config.DEATH_FLASH)
            if alpha > 0:
                self._flash.set_alpha(int(alpha))
                surface.blit(self._flash, (0, 0))

    def _draw_arena(self, surface: pygame.Surface) -> None:
        a = self.arena
        # As power fails the containment field loses its colour first.
        k = self.battery.distress if config.POWER_ENABLED else 0.0
        grid = _toward_grey(config.COLOR_GRID, k)
        border = _toward_grey(config.COLOR_GREEN, k)
        for x in range(a.left, a.right + 1, config.GRID_STEP):
            pygame.draw.line(surface, grid, (x, a.top), (x, a.bottom))
        for y in range(a.top, a.bottom + 1, config.GRID_STEP):
            pygame.draw.line(surface, grid, (a.left, y), (a.right, y))
        # Slow scanline sweep drifting down the arena.
        sweep_y = a.top + (self.run_time % config.SWEEP_PERIOD) / config.SWEEP_PERIOD * (a.height - 2)
        surface.blit(self._sweep, (a.left, sweep_y), special_flags=pygame.BLEND_RGB_ADD)
        pygame.draw.rect(surface, border, a, 2)
        if k > 0.0:
            self._wash.fill((128, 128, 128, int(config.POWER_GREY_WASH * k)))
            surface.blit(self._wash, a.topleft)

    def _draw_power(self, surface: pygame.Surface) -> None:
        """Ring around the drone (where the eyes already are) + a HUD bar.

        The ring sits outside the carried-core orbit and in its own colour:
        when both were green and overlapping, a full necklace of carried cores
        read as a full gauge — worst exactly when you are carrying the most and
        can least afford to misread your charge.
        """
        if not config.POWER_ENABLED:
            return
        frac = self.battery.fraction
        col = config.COLOR_POWER
        if self.battery.critical:
            # Flash between the normal colour and alarm red as it empties.
            pulse = 0.5 + 0.5 * math.sin(self.run_time * math.tau * 4.0)
            col = _lerp_color(config.COLOR_POWER, config.COLOR_POWER_LOW, self.battery.distress * pulse)

        r = config.POWER_RING_RADIUS
        box = pygame.Rect(self.player.x - r, self.player.y - r, r * 2, r * 2)
        pygame.draw.arc(surface, _toward_grey(config.COLOR_DIM_GREEN, 0.6), box, 0, math.tau, 1)
        if frac > 0:
            start = math.pi / 2
            pygame.draw.arc(surface, col, box, start, start + math.tau * frac, 3)

        bar = pygame.Rect(config.POWER_BAR_RECT)
        pygame.draw.rect(surface, config.COLOR_DIM_GREEN, bar, 1)
        inner = bar.inflate(-4, -4)
        inner.width = int(inner.width * frac)
        if inner.width > 0:
            pygame.draw.rect(surface, col, inner)

    def _draw_current_path(self, surface: pygame.Surface) -> None:
        """The wall you are building right now (depth design 2.1).

        Drawn immediately after the floor grid and before anything live, so
        it can never occlude a core or a ghost — which is also why a flat dim
        colour stands in for alpha here: on the floor, over near-black, the
        two are indistinguishable and this costs nothing per frame.
        """
        if not config.PATH_RENDER_ENABLED:
            return
        xs = self.recorder.xs[-config.PATH_SAMPLES :]
        ys = self.recorder.ys[-config.PATH_SAMPLES :]
        if len(xs) < 2:
            return
        pygame.draw.lines(surface, config.COLOR_PATH, False, list(zip(xs, ys)))

    def _draw_survey(self, surface: pygame.Surface) -> None:
        """Frozen planning beat: where each ghost starts and where it goes first."""
        for ghost in self.ghosts:
            _, alpha = ghost.tier()
            col = tuple(int(c * alpha / 255) for c in config.COLOR_MAGENTA)
            sx, sy, _ = ghost.recording.sample(0.0)
            pygame.draw.circle(surface, col, (sx, sy), config.GHOST_RING_START * 0.6, 1)
            steps = 20
            pts = [
                ghost.recording.sample(config.SURVEY_PATH_PREVIEW * i / steps)[:2]
                for i in range(steps + 1)
            ]
            pygame.draw.lines(surface, col, False, pts)

        cx = surface.get_width() // 2
        small = get_font(config.FONT_SMALL)
        label = small.render(f"SURVEY  {self.survey_t:.1f}", True, config.COLOR_GREEN)
        surface.blit(label, label.get_rect(midtop=(cx, self.arena.top + 18)))
        prompt = get_font(config.FONT_TINY).render("SPACE — BEGIN", True, config.COLOR_HUD_DIM)
        surface.blit(prompt, prompt.get_rect(midtop=(cx, self.arena.top + 48)))

    def _draw_popups(self, surface: pygame.Surface) -> None:
        font = get_font(config.FONT_TINY)
        for x, y, text, age in self.popups:
            k = 1.0 - age / config.POPUP_TIME
            img = font.render(text, True, _lerp_color(config.COLOR_BG, config.COLOR_WHITE, k))
            surface.blit(img, img.get_rect(center=(x, y)))

    def _draw_hud(self, surface: pygame.Surface) -> None:
        tiny = get_font(config.FONT_TINY)
        small = get_font(config.FONT_SMALL)
        mid = get_font(config.FONT_MID)

        surface.blit(small.render(f"SCORE {self.score:,}", True, config.COLOR_GREEN), (20, 16))
        best = save.get()["best_score"]
        surface.blit(tiny.render(f"BEST {best:,}", True, config.COLOR_HUD_DIM), (20, 42))
        if config.POWER_ENABLED and self.battery.critical:
            warn = tiny.render("POWER LOW", True, config.COLOR_POWER_LOW)
            surface.blit(warn, (config.POWER_BAR_RECT[0] + config.POWER_BAR_RECT[2] + 10, 58))

        # Multiplier, center: green -> yellow -> magenta as the greed climbs.
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
        if self.near_misses:
            nm = tiny.render(f"NEAR MISS {self.near_misses}", True, config.COLOR_MAGENTA)
            surface.blit(nm, (surface.get_width() - nm.get_width() - 20, 60))

        hint = tiny.render("ESC — PAUSE", True, config.COLOR_HUD_DIM)
        surface.blit(hint, (20, surface.get_height() - 28))

        timeline.draw(surface, self.ghosts, self.loop_t)

        if self.announce_t > 0.0:
            img = small.render(self.announce, True, config.COLOR_WHITE)
            surface.blit(img, img.get_rect(center=(surface.get_width() // 2, self.arena.centery)))
