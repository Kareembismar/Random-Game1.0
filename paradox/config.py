"""PARADOX — every tunable number lives here. Tune feel by editing this file only."""

TITLE = "PARADOX"

# --- Window / timing ---------------------------------------------------------
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
MAX_FRAME_DT = 0.05  # dt clamp for window-drag stalls; see the main loop

# --- Arena ---------------------------------------------------------------------
ARENA_RECT = (50, 80, 1180, 600)  # (left, top, width, height); HUD strip above
GRID_STEP = 60
SWEEP_PERIOD = 6.0  # seconds for the scanline sweep to cross the arena
SWEEP_BRIGHTNESS = 46  # additive intensity of the sweep strip

# --- Player --------------------------------------------------------------------
PLAYER_MAX_SPEED = 420.0  # px/s
PLAYER_ACCEL_TIME = 0.08  # seconds to reach full speed
PLAYER_FRICTION = 12.0  # velocity damping per second when there's no input
PLAYER_RADIUS = 12  # physics/clamp radius
PLAYER_HIT_RADIUS = 9  # collision radius — smaller than visual, kind to the player
ORBIT_RADIUS = 26  # carried cores circle the player at this distance
ORBIT_SPEED = 2.6  # radians/s of that orbit
TRAIL_LEN = 12  # motion-trail samples, one per frame (Section 0)
TRAIL_ALPHA = 120  # newest trail dot brightness; fades to 0 down the tail
TRAIL_DOT_RADIUS = 7

# --- Cores ---------------------------------------------------------------------
CORES_BASE = 5  # spawn count is CORES_BASE + loop number...
CORES_CAP = 12  # ...capped here
CORE_RADIUS = 9  # logic size; the visual is the CORE_PX sprite
CORE_PICKUP_RADIUS = 20
CORE_MIN_DIST_FROM_PLAYER = 140
CORE_MIN_DIST_APART = 90
CORE_MARGIN = 30  # minimum distance from the arena edge
CORE_PULSE_SPEED = 5.0
CORE_RING_MIN = 18  # procedural "pick me up" ring radius range (Section 0)
CORE_RING_MAX = 22

# --- Portal --------------------------------------------------------------------
PORTAL_RADIUS = 34
PORTAL_BANK_RADIUS = 34  # stand within this of the center to bank
PORTAL_MIN_RELOCATE_DIST = 300
PORTAL_MIN_FROM_PLAYER = 250  # initial placement only
PORTAL_MARGIN = 70

# --- Scoring -------------------------------------------------------------------
CORE_VALUE = 100
MULTIPLIER_PER_CORE = 0.35  # multiplier = 1 + this * cores carried

# --- Ghosts --------------------------------------------------------------------
GHOST_PHASE_IN = 1.5  # seconds of harmless materializing at loop start
GHOST_HIT_RADIUS = 8  # smaller than visual — always err generous to the player
GHOST_MAX = 12  # active-ghost cap; oldest recordings drop beyond this
GHOST_DESPAWN_TIME = 0.25  # collapse-out animation length
GHOST_RING_START = 36  # phase-in countdown ring starting radius

# --- Death ---------------------------------------------------------------------
DEATH_FREEZE = 0.35  # freeze-frame before the game over screen appears
DEATH_FLASH = 0.25  # white flash decay time within that freeze
DEATH_FLASH_ALPHA = 230

# --- Colors --------------------------------------------------------------------
COLOR_BG = (6, 9, 7)
COLOR_BG_PORTAL = (10, 26, 16)
COLOR_GRID = (14, 36, 21)  # Section 0: grid raised to ~alpha-28 over the bg
COLOR_GREEN = (80, 255, 140)
COLOR_DIM_GREEN = (34, 110, 62)
COLOR_MAGENTA = (255, 64, 220)
COLOR_YELLOW = (255, 230, 90)
COLOR_WHITE = (235, 240, 235)
COLOR_HUD_DIM = (95, 125, 100)

# --- Fonts ---------------------------------------------------------------------
FONT_CHAIN = "consolas,couriernew,monospace"
FONT_TINY = 16
FONT_SMALL = 20
FONT_MID = 30
FONT_BIG = 56

# --- Sprites (see paradox/assets/ASSETS.md) --------------------------------------
PLAYER_PX = 44  # gameplay render sizes; sources are oversized on purpose
GHOST_PX = 44
CORE_PX = 34  # Section 0: bigger — the sprite's fine detail mushes below 30px
CORE_BRIGHTNESS = 0.75  # Section 0: cores lose the contrast fight on purpose
SPRITE_ROT_STEPS = 72  # pre-rendered rotation granularity (5 degrees)
GLOW_SCALE = 1.8  # generic halo (cores)
GLOW_ALPHA = 70
GLOW_INNER_SCALE = 1.4  # player inner glow: pulsing (Section 0)
GLOW_INNER_ALPHA = 130
GLOW_INNER_PULSE = 25  # +/- alpha swing of the pulse
GLOW_PULSE_HZ = 2.5
GLOW_PULSE_LEVELS = 12  # pre-baked pulse intensities (additive blits ignore set_alpha)
GLOW_OUTER_SCALE = 2.2  # player outer glow: steady (Section 0)
GLOW_OUTER_ALPHA = 55
GHOST_ALPHA_TIERS = (200, 120, 70)  # fresh / worn / faded
GHOST_FRESH_MAX_AGE = 1  # age in loops; 0 = the loop you just played
GHOST_WORN_MAX_AGE = 4

# --- Screens ---------------------------------------------------------------------
BOOT_CPS = 35  # loading-screen typing speed, chars/sec (any key fast-forwards)
LOADING_MIN_TIME = 2.2  # never flicker past the boot screen
LOGO_WIDTH = 560
MENU_PARTICLES = 46
MENU_IDLE_GHOSTS = 3
