"""Ghosts: past-you, replaying a recorded loop exactly. The core hazard."""

import pygame

from paradox import config
from paradox.systems import sprites
from paradox.systems.recorder import Recording


class Ghost:
    """Plays back one Recording in real time.

    Timeline of a single ghost, all of it visible on the HUD timeline widget:

        [ delay ][ phase-in 1.5s ][ ---- lethal ---- ][ collapse ]
                 ^ materializes    ^ becomes lethal   ^ recording ends

    The delay staggers arrivals so a stack of ghosts cascades in instead of
    materializing as one wall. The phase-in is the fairness guarantee — the
    shrinking ring is a visible countdown, so nothing that just appeared can
    kill you. Lethality ends when the recording runs out, which is why fast
    loops make short-lived hazards.
    """

    def __init__(self, recording: Recording, age: int, delay: float = 0.0):
        self.recording = recording
        self.age = age  # 0 = your most recent loop; older ghosts decay visually
        self.delay = delay
        self.wait = delay  # counts down before playback begins
        self.t = 0.0
        self.despawn_t: float | None = None  # starts counting when the path ends
        self.flash = 0.0  # white rim-flash timer, set when the player grazes it
        self.nearmiss_cd = 0.0  # per-ghost near-miss cooldown

    # ---- timeline windows (absolute seconds since the loop started) ----------

    @property
    def lethal_start(self) -> float:
        return self.delay + config.GHOST_PHASE_IN

    @property
    def lethal_end(self) -> float:
        return self.delay + self.recording.duration

    @property
    def gone_at(self) -> float:
        return self.lethal_end + config.GHOST_DESPAWN_TIME

    # ---- simulation ----------------------------------------------------------

    def update(self, dt: float) -> None:
        self.flash = max(0.0, self.flash - dt)
        self.nearmiss_cd = max(0.0, self.nearmiss_cd - dt)

        if self.wait > 0.0:
            self.wait -= dt
            if self.wait > 0.0:
                return
            dt = -self.wait  # spill the remainder of the frame into playback
            self.wait = 0.0

        if self.despawn_t is None:
            self.t += dt
            if self.t >= self.recording.duration:
                self.despawn_t = 0.0
        else:
            self.despawn_t += dt

    @property
    def materialized(self) -> bool:
        """False while still waiting to arrive — not drawn, not collidable."""
        return self.wait <= 0.0

    @property
    def expired(self) -> bool:
        return self.despawn_t is not None and self.despawn_t >= config.GHOST_DESPAWN_TIME

    @property
    def lethal(self) -> bool:
        return self.materialized and self.despawn_t is None and self.t >= config.GHOST_PHASE_IN

    def pos(self) -> tuple[float, float, float]:
        return self.recording.sample(self.t)

    def tier(self) -> tuple[str, int]:
        """Decay variant + base alpha by AGE (loops since recorded), per ASSETS.md.

        The timeline widget colours its rows from this too, so a row and the
        thing it describes read as the same object.
        """
        if self.age <= config.GHOST_FRESH_MAX_AGE:
            return "ghost_fresh", config.GHOST_ALPHA_TIERS[0]
        if self.age <= config.GHOST_WORN_MAX_AGE:
            return "ghost_worn", config.GHOST_ALPHA_TIERS[1]
        return "ghost_faded", config.GHOST_ALPHA_TIERS[2]

    # ---- drawing ---------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        if not self.materialized:
            return
        x, y, angle = self.pos()
        key, alpha = self.tier()
        frame = sprites.get_store()[key].frame_for(angle)

        if self.despawn_t is not None:
            # Collapse-out fade. (The portal-implosion effect lands in Phase 3.)
            k = 1.0 - self.despawn_t / config.GHOST_DESPAWN_TIME
            if k <= 0:
                return
            alpha = int(alpha * k)
        elif not self.lethal:
            # Phasing in: extra translucent while harmless.
            k = self.t / config.GHOST_PHASE_IN
            alpha = int(alpha * (0.35 + 0.65 * k))

        frame.set_alpha(alpha)
        surface.blit(frame, frame.get_rect(center=(x, y)))
        frame.set_alpha(255)  # cache frames are shared — leave them clean

        if self.despawn_t is None and not self.lethal:
            k = self.t / config.GHOST_PHASE_IN
            ring = config.GHOST_RING_START * (1.0 - k) + config.PLAYER_RADIUS * k
            pygame.draw.circle(surface, config.COLOR_MAGENTA, (x, y), ring, 1)

        if self.flash > 0.0:  # you just grazed this one
            k = self.flash / config.NEARMISS_FLASH_TIME
            pygame.draw.circle(surface, config.COLOR_WHITE, (x, y), config.NEARMISS_RADIUS * (1.2 - k), 2)
