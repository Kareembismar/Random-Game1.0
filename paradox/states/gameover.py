"""Minimal Phase 1 death screen. The freeze-frame/flash treatment is Phase 3."""

import pygame

from paradox import config
from paradox.states.base import State
from paradox.states.play import PlayState
from paradox.ui.fonts import get_font


class GameOverState(State):
    def __init__(self, score: int, loop: int):
        self.score = score
        self.loop = loop

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_r:
            # THE interaction: R = a brand-new run, same frame, nothing between.
            self.manager.replace(PlayState())
        elif event.key == pygame.K_ESCAPE:
            self.manager.running = False  # Phase 2: back to the menu instead

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(config.COLOR_BG)
        cx = surface.get_width() // 2
        title = get_font(config.FONT_BIG).render("TERMINATED", True, config.COLOR_MAGENTA)
        surface.blit(title, (cx - title.get_width() // 2, 240))
        small = get_font(config.FONT_SMALL)
        stats = small.render(f"SCORE {self.score:,}    LOOP {self.loop}", True, config.COLOR_GREEN)
        surface.blit(stats, (cx - stats.get_width() // 2, 330))
        prompt = small.render("[R] RUN AGAIN     [ESC] QUIT", True, config.COLOR_WHITE)
        surface.blit(prompt, (cx - prompt.get_width() // 2, 400))
