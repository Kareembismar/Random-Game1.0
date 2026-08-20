"""Shared UI drawing: the 9-sliced panel frame and keyboard menu lists."""

import pygame

from paradox import config
from paradox.systems import sprites
from paradox.ui.fonts import get_font

_SLICE_INSET = 60  # source-pixel inset for the frame slices (ASSETS.md rule 6)

_slices: list | None | bool = None
_frame_cache: dict[tuple[int, int], pygame.Surface] = {}


def _get_slices():
    """3x3 subsurfaces of panel_frame.png, or False if the asset is missing."""
    global _slices
    if _slices is None:
        img = sprites.load_image("ui/panel_frame.png")
        if img is None:
            _slices = False
        else:
            w, h = img.get_size()
            xs = (0, _SLICE_INSET, w - _SLICE_INSET, w)
            ys = (0, _SLICE_INSET, h - _SLICE_INSET, h)
            _slices = [
                [
                    img.subsurface(pygame.Rect(xs[c], ys[r], xs[c + 1] - xs[c], ys[r + 1] - ys[r]))
                    for c in range(3)
                ]
                for r in range(3)
            ]
    return _slices


def draw_frame(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Translucent panel fill + the 9-sliced frame on top.

    9-slice per ASSETS.md rule 6: corners blit at native size, edges stretch
    along one axis only, so the clipped corners never distort. The art's
    interior is empty, so the dark fill behind it is ours. Assembled once per
    panel size and cached — after that it's a single blit per frame.
    """
    key = (rect.width, rect.height)
    if key not in _frame_cache:
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((8, 14, 10, 215))
        sl = _get_slices()
        if not sl:
            pygame.draw.rect(panel, config.COLOR_GREEN, panel.get_rect(), 2)  # asset-less fallback
        else:
            i = min(_SLICE_INSET, rect.width // 3, rect.height // 3)
            xs = (0, i, rect.width - i, rect.width)
            ys = (0, i, rect.height - i, rect.height)
            for r in range(3):
                for c in range(3):
                    if r == 1 and c == 1:
                        continue  # interior of the art is empty by design
                    target = pygame.Rect(xs[c], ys[r], xs[c + 1] - xs[c], ys[r + 1] - ys[r])
                    if target.width <= 0 or target.height <= 0:
                        continue
                    piece = sl[r][c]
                    if piece.get_size() != target.size:
                        piece = pygame.transform.smoothscale(piece, target.size)
                    panel.blit(piece, target.topleft)
        _frame_cache[key] = panel
    surface.blit(_frame_cache[key], rect.topleft)


def draw_menu(
    surface: pygame.Surface,
    items: tuple[str, ...],
    selected: int,
    center_x: int,
    top_y: int,
    spacing: int = 52,
) -> list[pygame.Rect]:
    """Vertical keyboard menu. Returns item rects so callers can hit-test the mouse.

    The selected item gets the '>' marker, a soft glow, and a slight offset —
    all three, so selection is unmissable in peripheral vision.
    """
    font = get_font(config.FONT_MID)
    rects = []
    for i, label in enumerate(items):
        sel = i == selected
        text = f"> {label}" if sel else label
        img = font.render(text, True, config.COLOR_GREEN if sel else config.COLOR_HUD_DIM)
        x = center_x - img.get_width() // 2 + (10 if sel else 0)
        y = top_y + i * spacing
        if sel:
            glow = font.render(text, True, config.COLOR_DIM_GREEN)
            for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                surface.blit(glow, (x + ox, y + oy))
        surface.blit(img, (x, y))
        rects.append(pygame.Rect(x, y, img.get_width(), img.get_height()))
    return rects
