"""Game over: the damage report. R restarts within one frame, always."""

import pygame

from paradox import config
from paradox.states.base import State
from paradox.states.play import PlayState
from paradox.systems import sprites
from paradox.ui.fonts import get_font


class GameOverState(State):
    def __init__(self, score: int, loop: int, banked: int, longest_loop: float, new_best: bool):
        self.score = score
        self.loop = loop
        self.banked = banked
        self.longest_loop = longest_loop
        self.new_best = new_best
        self.t = 0.0
        self.bg = sprites.load_image(
            "backgrounds/bg_gameover.png", (config.WINDOW_WIDTH, config.WINDOW_HEIGHT), alpha=False
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_r:
            # THE interaction: R = a brand-new run, same frame, nothing between.
            self.manager.replace(PlayState())
        elif event.key == pygame.K_ESCAPE:
            from paradox.states.menu import MenuState  # local import: menu imports play like us

            self.manager.reset_to(MenuState())

    def update(self, dt: float) -> None:
        self.t += dt

    def draw(self, surface: pygame.Surface) -> None:
        if self.bg is not None:
            surface.blit(self.bg, (0, 0))
            dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 130))  # keep the report readable over the art
            surface.blit(dim, (0, 0))
        else:
            surface.fill(config.COLOR_BG)

        cx = surface.get_width() // 2
        title = get_font(config.FONT_BIG).render("TERMINATED", True, config.COLOR_MAGENTA)
        surface.blit(title, title.get_rect(midtop=(cx, 156)))

        small = get_font(config.FONT_SMALL)
        rows = [
            f"SCORE {self.score:,}",
            f"LOOP REACHED {self.loop}",
            f"CORES BANKED {self.banked}",
            f"LONGEST LOOP {self.longest_loop:.1f}s",
        ]
        for i, row in enumerate(rows):
            img = small.render(row, True, config.COLOR_GREEN)
            surface.blit(img, img.get_rect(midtop=(cx, 268 + i * 34)))

        if self.new_best and (self.t * 2.4) % 1 < 0.6:
            flash = get_font(config.FONT_MID).render("NEW RECORD", True, config.COLOR_MAGENTA)
            surface.blit(flash, flash.get_rect(midtop=(cx, 416)))

        prompt = small.render("[R] RUN AGAIN     [ESC] MENU", True, config.COLOR_WHITE)
        surface.blit(prompt, prompt.get_rect(midtop=(cx, 496)))
