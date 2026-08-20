"""Main menu: RUN / HOW IT WORKS / RECORDS / QUIT, plus enough ambient dread
(drifting particles, wandering past occupants) to sell the concept before
anything is pressed. Keyboard-first; mouse hover/click also works.
"""

import math
import random

import pygame

from paradox import config
from paradox.states.base import State
from paradox.states.play import PlayState
from paradox.systems import save, sprites
from paradox.ui import widgets
from paradox.ui.fonts import get_font

ITEMS = ("RUN", "HOW IT WORKS", "RECORDS", "QUIT")

HOW_PAGES = (
    ("WASD to move. Collect cores.", "Carry them to the portal to bank them."),
    ("Every loop you survive spawns a copy of you", "walking your last path. It kills you."),
    ("Clear loops FAST. Your ghost only lives", "as long as your last loop took."),
)


class MenuState(State):
    def __init__(self):
        self.mode = "main"  # main | how | records
        self.selected = 0
        self.page = 0
        self.t = 0.0
        self._rects: list[pygame.Rect] = []
        rng = random.Random()
        self.particles = [
            [rng.uniform(0, config.WINDOW_WIDTH), rng.uniform(0, config.WINDOW_HEIGHT), rng.uniform(4, 14)]
            for _ in range(config.MENU_PARTICLES)
        ]
        self.idle_ghosts = [
            {
                "cx": rng.uniform(220, config.WINDOW_WIDTH - 220),
                "cy": rng.uniform(160, config.WINDOW_HEIGHT - 160),
                "ax": rng.uniform(60, 170),
                "ay": rng.uniform(30, 90),
                "sx": rng.uniform(0.05, 0.15),
                "sy": rng.uniform(0.04, 0.11),
                "p": rng.uniform(0, math.tau),
            }
            for _ in range(config.MENU_IDLE_GHOSTS)
        ]
        self.bg = sprites.load_image(
            "backgrounds/bg_menu.png", (config.WINDOW_WIDTH, config.WINDOW_HEIGHT), alpha=False
        )
        # Chromatic-aberration copies of the logo: red and cyan, offset and
        # breathing (drawn under the clean copy). Baked once here.
        self.logo = self.logo_r = self.logo_c = None
        raw = sprites.load_image("ui/logo.png")
        if raw is not None:
            lw = config.LOGO_WIDTH
            lh = round(raw.get_height() * lw / raw.get_width())
            self.logo = pygame.transform.smoothscale(raw, (lw, lh))
            self.logo_r = self.logo.copy()
            self.logo_r.fill((255, 70, 70), special_flags=pygame.BLEND_RGB_MULT)
            self.logo_c = self.logo.copy()
            self.logo_c.fill((70, 220, 255), special_flags=pygame.BLEND_RGB_MULT)

    # ---- events ----------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.mode == "main":
            self._event_main(event)
        else:
            self._event_sub(event)

    def _event_main(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.selected = (self.selected - 1) % len(ITEMS)
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.selected = (self.selected + 1) % len(ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate(self.selected)
        elif event.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self._rects):
                if r.collidepoint(event.pos):
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._rects):
                if r.collidepoint(event.pos):
                    self._activate(i)

    def _event_sub(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.mode = "main"
        elif self.mode == "how" and event.key in (pygame.K_a, pygame.K_LEFT):
            self.page = (self.page - 1) % len(HOW_PAGES)
        elif self.mode == "how" and event.key in (pygame.K_d, pygame.K_RIGHT):
            self.page = (self.page + 1) % len(HOW_PAGES)

    def _activate(self, index: int) -> None:
        if index == 0:
            self.manager.replace(PlayState())
        elif index == 1:
            self.mode, self.page = "how", 0
        elif index == 2:
            self.mode = "records"
        else:
            self.manager.running = False

    # ---- simulation ----------------------------------------------------------

    def update(self, dt: float) -> None:
        self.t += dt
        for p in self.particles:
            p[1] -= p[2] * dt  # slow upward drift, wrap at the top
            if p[1] < -4:
                p[1] = config.WINDOW_HEIGHT + 4

    # ---- drawing ----------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        if self.bg is not None:
            surface.blit(self.bg, (0, 0))
        else:
            surface.fill(config.COLOR_BG)

        for x, y, _speed in self.particles:
            pygame.draw.circle(surface, config.COLOR_DIM_GREEN, (x, y), 1)

        store = sprites.get_store()
        for g in self.idle_ghosts:  # past occupants, wandering the lab
            gx = g["cx"] + math.sin(self.t * g["sx"] * math.tau + g["p"]) * g["ax"]
            gy = g["cy"] + math.sin(self.t * g["sy"] * math.tau + g["p"] * 1.7) * g["ay"]
            vx = math.cos(self.t * g["sx"] * math.tau + g["p"]) * g["ax"] * g["sx"]
            vy = math.cos(self.t * g["sy"] * math.tau + g["p"] * 1.7) * g["ay"] * g["sy"]
            frame = store["ghost_faded"].frame_for(math.atan2(vy, vx))
            frame.set_alpha(70)
            surface.blit(frame, frame.get_rect(center=(gx, gy)))
            frame.set_alpha(255)

        if self.mode == "main":
            self._draw_main(surface)
        elif self.mode == "how":
            self._draw_how(surface)
        else:
            self._draw_records(surface)

    def _draw_main(self, surface: pygame.Surface) -> None:
        w = surface.get_width()
        cx = w // 2
        offset = 2.0 + 1.2 * math.sin(self.t * 1.4)  # breathing aberration

        if self.logo is not None:
            base = self.logo.get_rect(midtop=(cx, 66))
            surface.blit(self.logo_r, base.move(-offset, 0))
            surface.blit(self.logo_c, base.move(offset, 0))
            surface.blit(self.logo, base)
            title_bottom = base.bottom
        else:
            big = get_font(config.FONT_BIG + 20)
            for color, dx in (((255, 70, 70), -offset), ((70, 220, 255), offset), (config.COLOR_WHITE, 0)):
                img = big.render("PARADOX", True, color)
                surface.blit(img, img.get_rect(midtop=(cx + dx, 90)))
            title_bottom = 90 + big.get_height()

        sub = get_font(config.FONT_SMALL).render("you are the hazard", True, config.COLOR_HUD_DIM)
        surface.blit(sub, sub.get_rect(midtop=(cx, title_bottom + 6)))

        self._rects = widgets.draw_menu(surface, ITEMS, self.selected, cx, title_bottom + 62)

        d = save.get()
        corner = get_font(config.FONT_TINY).render(
            f"BEST: {d['best_score']:,}    DEEPEST LOOP: {d['deepest_loop']}", True, config.COLOR_HUD_DIM
        )
        surface.blit(corner, (18, config.WINDOW_HEIGHT - 30))

    def _panel(self, surface: pygame.Surface) -> pygame.Rect:
        rect = pygame.Rect(0, 0, 820, 430)
        rect.center = (surface.get_width() // 2, surface.get_height() // 2)
        widgets.draw_frame(surface, rect)
        return rect

    def _draw_how(self, surface: pygame.Surface) -> None:
        rect = self._panel(surface)
        cx = rect.centerx
        title = get_font(config.FONT_MID).render("HOW IT WORKS", True, config.COLOR_GREEN)
        surface.blit(title, title.get_rect(midtop=(cx, rect.top + 58)))
        small = get_font(config.FONT_SMALL)
        for i, line in enumerate(HOW_PAGES[self.page]):
            img = small.render(line, True, config.COLOR_WHITE)
            surface.blit(img, img.get_rect(midtop=(cx, rect.top + 165 + i * 36)))
        pager = small.render(
            f"< A        {self.page + 1}/{len(HOW_PAGES)}        D >", True, config.COLOR_HUD_DIM
        )
        surface.blit(pager, pager.get_rect(midtop=(cx, rect.bottom - 120)))
        hint = get_font(config.FONT_TINY).render("ESC — BACK", True, config.COLOR_HUD_DIM)
        surface.blit(hint, hint.get_rect(midtop=(cx, rect.bottom - 66)))

    def _draw_records(self, surface: pygame.Surface) -> None:
        rect = self._panel(surface)
        cx = rect.centerx
        d = save.get()
        title = get_font(config.FONT_MID).render("RECORDS", True, config.COLOR_GREEN)
        surface.blit(title, title.get_rect(midtop=(cx, rect.top + 50)))
        small = get_font(config.FONT_SMALL)
        lines = [
            f"BEST SCORE        {d['best_score']:,}",
            f"DEEPEST LOOP      {d['deepest_loop']}",
            f"TOTAL RUNS        {d['total_runs']}",
        ]
        if d["top_scores"]:
            lines.append("")
            for i, s in enumerate(d["top_scores"], start=1):
                lines.append(f"{i}.  {s['score']:>8,}   LOOP {s.get('loop', '?')}   {s.get('date', '')}")
        else:
            lines += ["", "NO RUNS ON RECORD."]
        for i, line in enumerate(lines):
            if line:
                img = small.render(line, True, config.COLOR_WHITE if i < 3 else config.COLOR_HUD_DIM)
                surface.blit(img, img.get_rect(midtop=(cx, rect.top + 118 + i * 30)))
        hint = get_font(config.FONT_TINY).render("ESC — BACK", True, config.COLOR_HUD_DIM)
        surface.blit(hint, hint.get_rect(midtop=(cx, rect.bottom - 56)))
