"""Pause: the frozen game behind glass. Esc in = Esc out, never ambiguous."""

import pygame

from paradox import config
from paradox.states.base import State
from paradox.states.menu import MenuState
from paradox.states.play import PlayState
from paradox.systems import save
from paradox.ui import widgets
from paradox.ui.fonts import get_font

ITEMS = ("RESUME", "RESTART RUN", "QUIT TO MENU")


class PauseState(State):
    """Sits on top of PlayState on the stack: the game below stops updating
    (only the top state updates) but still draws each frame — this state just
    blurs and dims what's underneath before drawing its own menu."""

    def __init__(self, play: PlayState):
        self.play = play
        self.selected = 0
        self._rects: list[pygame.Rect] = []

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.manager.pop()  # Esc resumes
            elif event.key in (pygame.K_w, pygame.K_UP):
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

    def _activate(self, index: int) -> None:
        if index == 0:
            self.manager.pop()
            return
        # Leaving the run either way: the score is written to the save file
        # first — never silently discard a run.
        save.record_run(self.play.score, self.play.loop)
        if index == 1:
            self.manager.reset_to(PlayState())
        else:
            self.manager.reset_to(MenuState())

    def update(self, dt: float) -> None:
        pass  # everything below is frozen; that's the point

    def draw(self, surface: pygame.Surface) -> None:
        # "Behind glass": cheap blur = downscale then upscale the frame the
        # frozen PlayState just drew beneath us, then dim it.
        w, h = surface.get_size()
        blurred = pygame.transform.smoothscale(
            pygame.transform.smoothscale(surface, (w // 4, h // 4)), (w, h)
        )
        surface.blit(blurred, (0, 0))
        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 130))
        surface.blit(dim, (0, 0))

        panel = pygame.Rect(0, 0, 460, 340)
        panel.center = (w // 2, h // 2)
        widgets.draw_frame(surface, panel)
        title = get_font(config.FONT_MID).render("PAUSED", True, config.COLOR_GREEN)
        surface.blit(title, title.get_rect(midtop=(w // 2, panel.top + 46)))
        self._rects = widgets.draw_menu(surface, ITEMS, self.selected, w // 2, panel.top + 118, spacing=56)
