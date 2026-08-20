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

# --- Player --------------------------------------------------------------------
PLAYER_MAX_SPEED = 420.0  # px/s
PLAYER_ACCEL_TIME = 0.08  # seconds to reach full speed
PLAYER_FRICTION = 12.0  # velocity damping per second when there's no input
PLAYER_RADIUS = 12  # visual size
PLAYER_HIT_RADIUS = 9  # collision radius — smaller than visual, kind to the player
ORBIT_RADIUS = 26  # carried cores circle the player at this distance
ORBIT_SPEED = 2.6  # radians/s of that orbit

# --- Cores ---------------------------------------------------------------------
CORES_BASE = 5  # spawn count is CORES_BASE + loop number...
CORES_CAP = 12  # ...capped here
CORE_RADIUS = 9
CORE_PICKUP_RADIUS = 20
CORE_MIN_DIST_FROM_PLAYER = 140
CORE_MIN_DIST_APART = 90
CORE_MARGIN = 30  # minimum distance from the arena edge
CORE_PULSE_SPEED = 5.0

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

# --- Colors --------------------------------------------------------------------
COLOR_BG = (6, 9, 7)
COLOR_BG_PORTAL = (10, 26, 16)
COLOR_GRID = (13, 20, 15)
COLOR_GREEN = (80, 255, 140)
COLOR_DIM_GREEN = (34, 110, 62)
COLOR_MAGENTA = (255, 64, 220)
COLOR_YELLOW = (255, 230, 90)
COLOR_WHITE = (235, 240, 235)
COLOR_HUD_DIM = (95, 125, 100)

# --- Fonts ---------------------------------------------------------------------
FONT_CHAIN = "consolas,couriernew,monospace"
FONT_SMALL = 20
FONT_MID = 30
FONT_BIG = 56

# --- Sprites (see paradox/assets/ASSETS.md) --------------------------------------
PLAYER_SPRITE_PX = 44  # gameplay sizes; sources are oversized on purpose
GHOST_SPRITE_PX = 44
CORE_SPRITE_PX = 26
SPRITE_ROT_STEPS = 72  # pre-rendered rotation granularity (5 degrees)
GLOW_SCALE = 1.8  # halo size relative to its sprite
GLOW_ALPHA = 70  # halo intensity, multiplied into the pixels at load
GHOST_ALPHA_TIERS = (200, 120, 70)  # fresh / worn / faded
GHOST_FRESH_MAX_AGE = 1  # age in loops; 0 = the loop you just played
GHOST_WORN_MAX_AGE = 4
