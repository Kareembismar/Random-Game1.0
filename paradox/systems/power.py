"""POWER — the battery the whole run runs on (verbs & survival, section 4).

Why a battery and not a timer: it converts every decision the game already
has into a two-sided one. "Do I grab that far core?" becomes "can I afford
the trip?", and "how long do I stay out?" now costs ghost length *and*
charge. Cores stop being optional, which closes the hole where a good enough
dodger could ignore the collection game entirely.

The elegant part is what it does to camping. Standing still is genuinely the
cheapest way to conserve charge — and it is also how you build a stationary
pillar of death in that exact corner for every subsequent loop. The
punishment for hiding is the game's own core mechanic, so there is
deliberately no anti-camp rule anywhere in this codebase.
"""

from paradox import config


class Battery:
    """The player's charge. Drains by movement state, refills from cores."""

    def __init__(self, level: float | None = None):
        self.level = config.POWER_START if level is None else level

    # ---- queries ---------------------------------------------------------

    @property
    def fraction(self) -> float:
        return max(0.0, min(1.0, self.level / config.POWER_MAX))

    @property
    def empty(self) -> bool:
        return self.level <= 0.0

    @property
    def critical(self) -> bool:
        return self.level < config.POWER_CRITICAL

    @property
    def distress(self) -> float:
        """0 at the critical threshold rising to 1 at empty — drives the
        ring flash and the floor desaturation."""
        if not self.critical:
            return 0.0
        return min(1.0, (config.POWER_CRITICAL - self.level) / config.POWER_CRITICAL)

    # ---- rates -----------------------------------------------------------

    @staticmethod
    def drain_rate(speed: float) -> float:
        """Charge per second at this speed.

        Three documented rates: idle, and a moving band scaling with how hard
        you're pushing. Note what this curve does NOT create, because it is
        easy to assume otherwise: the moving band is affine (4 + 5k), so cost
        per pixel travelled falls monotonically with speed and bottoms out at
        full sprint. Moving slowly is never a way to save charge — measured,
        it costs 1.67x the power of a sprint over the same route, takes 2.5x
        longer, and writes a 2.5x longer ghost. Speed is therefore not a
        resource decision today; only distance is. Standing still is the
        cheapest per second and cannot advance a loop on its own.
        """
        if speed < config.POWER_IDLE_SPEED:
            return config.POWER_DRAIN_IDLE
        k = min(1.0, speed / config.PLAYER_MAX_SPEED)
        return config.POWER_DRAIN_MOVE_MIN + (
            config.POWER_DRAIN_MOVE_MAX - config.POWER_DRAIN_MOVE_MIN
        ) * k

    # ---- mutation ---------------------------------------------------------

    def drain(self, dt: float, speed: float) -> None:
        self.level = max(0.0, self.level - self.drain_rate(speed) * dt)

    def spend(self, amount: float) -> bool:
        """Pay a flat cost (VENT, build step B). False if you can't afford it."""
        if self.level < amount:
            return False
        self.level -= amount
        return True

    def add(self, amount: float) -> None:
        self.level = min(config.POWER_MAX, self.level + amount)

    def restore(self) -> None:
        """Full recharge — sector transitions (build step E)."""
        self.level = config.POWER_MAX
