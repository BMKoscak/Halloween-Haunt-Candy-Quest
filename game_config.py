# Halloween Haunt: Candy Quest - Configuration Settings - BETA VERSION
# Edit these values to customize your gameplay experience!
# 
# BETA NOTICE: This is a beta release - some settings may change in future versions

# Version Information
GAME_VERSION = "BETA v0.9"      # Current game version
IS_BETA = True                  # Beta release flag

# Gameplay Balance
CANDIES_PER_LEVEL = 15          # Candies needed to complete each level
PLAYER_HEALTH = 3               # Starting health (hearts)  
PLAYER_SPEED = 3.0              # Base movement speed
GHOST_SPEED = 1.5               # Enemy movement speed

# Level Progression  
TOTAL_LEVELS = 5                # Number of levels in the game
NIGHT_MODE_DELAY = 10800        # Frames until night mode (3 min at 60 FPS)

# Scoring
NORMAL_CANDY_POINTS = 10        # Points for regular candy
BONUS_CANDY_POINTS = 25         # Points for special candy
EASTER_EGG_POINTS = 50          # Points for finding Easter eggs
LEVEL_COMPLETE_BONUS = 100      # Bonus points per remaining health

# Power-up Durations (in frames at 60 FPS)
CANDY_MAGNET_DURATION = 600     # 10 seconds
GHOST_REPEL_DURATION = 900      # 15 seconds  
SPEED_BOOST_DURATION = 450      # 7.5 seconds
ZOMBIE_POWER_DURATION = 900     # 15 seconds

# Visual Settings
PARTICLE_LIFETIME = 60          # How long visual effects last
SCREEN_SHAKE_INTENSITY = 10     # Strength of screen shake effects
INVINCIBILITY_FRAMES = 120      # Frames of invincibility after damage

# Audio Settings (0.0 to 1.0)
DEFAULT_MUSIC_VOLUME = 0.7      # Background music volume
DEFAULT_SFX_VOLUME = 0.8        # Sound effects volume

# Controls (pygame key constants - don't change unless you know what you're doing)
# Movement keys: WASD and Arrow Keys are hardcoded
# SPACE for interaction
# ESC for pause
# F11 for fullscreen

# Debug Settings
DEBUG_MODE = False              # Enable debug information
SHOW_COLLISION_BOXES = False    # Show collision rectangles
UNLIMITED_HEALTH = False        # Player cannot die (for testing)

# Performance Settings  
TARGET_FPS = 60                 # Game speed (60 recommended)
PARTICLE_LIMIT = 200            # Maximum particles on screen

# Map Generation
MAP_WIDTH_TILES = 30            # Level width in tiles
MAP_HEIGHT_TILES = 20           # Level height in tiles  
TILE_SIZE_PIXELS = 32           # Size of each tile in pixels

# Halloween Theme Intensity 🎃
EXTRA_SPOOKY = True             # More ghosts and effects
CANDY_VARIETY = True            # Enable cursed and bonus candies
JUMP_SCARES = False             # Sudden ghost appearances (not implemented)

"""
🎮 GAMEPLAY TIPS:
- Increase PLAYER_SPEED for easier movement
- Decrease GHOST_SPEED to make enemies less threatening  
- Increase CANDIES_PER_LEVEL for longer levels
- Adjust power-up durations for different strategies
- Set DEBUG_MODE = True to see collision boxes

🎃 DIFFICULTY PRESETS:
Easy Mode: PLAYER_SPEED = 4.0, GHOST_SPEED = 1.0, PLAYER_HEALTH = 5
Normal Mode: Default settings (balanced experience)
Hard Mode: PLAYER_SPEED = 2.5, GHOST_SPEED = 2.0, PLAYER_HEALTH = 2
Nightmare: PLAYER_SPEED = 2.0, GHOST_SPEED = 2.5, PLAYER_HEALTH = 1

👻 Remember: The game is designed to be challenging but fair!
"""