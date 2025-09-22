# Halloween Haunt: Candy Quest 🎃👻 
## **BETA VERSION**

A spooky 2D top-down exploration game built with Python and Pygame! Guide a young trick-or-treater in a ghost costume through a haunted town to collect candies while avoiding dangerous ghosts.

> ⚠️ **This is a BETA release** - Some features may be incomplete or contain bugs. Please report any issues to the developer.

## 🎮 Game Overview

Navigate through 5 progressively challenging levels in a spooky Halloween town. Collect exactly 15 candies per level and return them to your starting house to advance. Discover hidden Easter eggs, solve church puzzles, dig up cemetery treasures, and avoid deadly traps!

### 🏆 Core Features

- **5 Unique Levels**: From basic town layout to nightmare mode with aggressive ghosts
- **Tutorial System**: Learn the game mechanics step-by-step
- **Multiple Game Mechanics**: 
  - Candy collection with different types (normal, cursed, bonus)
  - Easter egg hunting with special rewards
  - Church puzzles requiring symbol arrangement
  - Cemetery digging mini-games
  - Jack-o'-lantern traps in higher levels
- **Power-up System**: Candy magnet, ghost repel, speed boost, extra health, zombie power
- **Day/Night Cycle**: Levels get darker and spawn more ghosts over time
- **Save System**: Progress is automatically saved
- **High Score Tracking**: Compete for the best scores

## 🚀 Installation & Setup

### Requirements
- Python 3.7 or higher
- Pygame library

### Quick Start

1. **Install Python** (if not already installed):
   - Download from [python.org](https://python.org)
   - Make sure to add Python to your system PATH

2. **Install Pygame**:
   ```bash
   pip install pygame
   ```

3. **Download the Game**:
   - Download all game files to a folder (e.g., `Halloween/`)
   
4. **Run the Game**:
   ```bash
   cd Halloween
   python halloween_haunt.py
   ```

### Optional: Add Custom Assets

The game works perfectly with built-in graphics, but you can add custom assets for enhanced visuals:

```
Halloween/
├── halloween_haunt.py
├── assets/
│   ├── sprites/
│   │   ├── player_ghost.png      # Player character (24x24)
│   │   ├── ghost_enemy.png       # Enemy ghosts (20x20)
│   │   ├── candy.png             # Regular candy (12x12)
│   │   ├── candy_cursed.png      # Cursed candy (12x12)
│   │   └── candy_bonus.png       # Bonus candy (12x12)
│   ├── tiles/
│   │   ├── grass.png             # Ground tiles (32x32)
│   │   ├── street.png            # Street tiles (32x32)
│   │   ├── house.png             # House tiles (32x32)
│   │   ├── wall.png              # Wall tiles (32x32)
│   │   ├── church.png            # Church tiles (32x32)
│   │   ├── grave.png             # Grave tiles (32x32)
│   │   └── door.png              # Door tiles (32x32)
│   ├── music/
│   │   └── spooky_bg.mp3         # Background music
│   ├── sfx/
│   │   ├── pickup.wav            # Candy pickup sound
│   │   ├── boo.wav               # Ghost contact sound
│   │   ├── win.wav               # Level complete sound
│   │   └── hurt.wav              # Damage sound
│   ├── ui/
│   │   └── heart.png             # Health heart icon (20x20)
│   └── fonts/
│       └── creepy.ttf            # Custom Halloween font
```

## 🎯 How to Play

### Controls
- **WASD** or **Arrow Keys**: Move your character
- **SPACE**: Interact (pickup candy, activate Easter eggs, church puzzles, digging)
- **ESC**: Pause menu
- **F11**: Toggle fullscreen
- **Mouse**: Navigate menus

### Gameplay Mechanics

#### Basic Objective
1. Collect exactly **15 candies** scattered around each level
2. Return to your **starting house** (blue door) to complete the level
3. Survive with at least 1 health point

#### Candy Types
- 🟠 **Normal Candy**: +10 points
- 🔴 **Cursed Candy**: +20 points but reduces speed for 5 seconds
- 🟡 **Bonus Candy**: +25 points and heals 1 health

#### Power-ups (from Easter eggs)
- 🧲 **Candy Magnet**: Auto-collect candies within 50 pixels (10 seconds)
- 👻 **Ghost Repel**: Temporary immunity to ghost damage (15 seconds)  
- ⚡ **Speed Boost**: Increased movement speed (7 seconds)
- ❤️ **Extra Heart**: Gain additional health (up to 5 total)
- 🧟 **Zombie Power**: Repel ghosts and move through them (15 seconds)

#### Special Features

**Church Puzzles** (Level 3+):
- Press SPACE near church altar to activate
- Use WASD to rearrange symbols in correct order: Angel → Bible → Candle → Cross
- Rewards: +100 points and +1 health

**Cemetery Digging** (Level 2+):
- Press SPACE repeatedly (5 times) at digging spots in cemetery
- Rewards: Zombie power activation

**Jack-o'-lantern Traps** (Level 4+):
- Avoid getting too close - they explode and deal damage
- Look for glowing orange pumpkins with warning indicators

#### Difficulty Progression
- **Level 1**: Basic town, few slow ghosts, tutorial available
- **Level 2**: More alleys and obstacles, faster ghosts
- **Level 3**: Church interior puzzles, cemetery access, more hazards
- **Level 4**: Timed challenges, jack-o'-lantern traps, partial night mode
- **Level 5**: Permanent night mode, boss ghost, aggressive AI, all mechanics active

#### Day/Night Cycle
- Each level starts at dusk with normal lighting
- After 3 minutes, night falls: screen darkens and +2 ghosts spawn
- Higher levels (4-5) have permanent night mode

## 📊 Scoring System

- **Candy Collection**: 10-25 points per candy (based on type)
- **Easter Eggs**: 25-50 points each
- **Level Completion Bonus**: 100 × remaining health points
- **Time Bonus**: Extra points for fast completion
- **Church Puzzle**: +100 points + health bonus
- **High Scores**: Top 5 scores saved locally

## 🐛 Troubleshooting

### Game Won't Start
- Ensure Python and Pygame are properly installed: `pip install pygame`
- Check that all game files are in the same directory
- Try running with: `python3 halloween_haunt.py`

### Performance Issues  
- Close other applications to free up system resources
- Try running in windowed mode instead of fullscreen
- Lower the FPS by modifying the `FPS` constant in the code

### No Sound
- The game works fine without sound files
- Check that your system volume is up
- Verify audio files are in the correct `assets/sfx/` and `assets/music/` folders

### Save File Issues
- The game creates `save_data.txt` and `high_scores.txt` automatically
- Delete these files to reset progress
- Make sure the game directory has write permissions

## 🎨 Customization

### Modifying Gameplay
Edit values in `halloween_haunt.py`:
- `CANDIES_TO_COLLECT = 15` (candies needed per level)
- `PLAYER_MAX_SPEED = 3.0` (player movement speed)  
- `GHOST_SPEED = 1.5` (enemy movement speed)
- `PLAYER_MAX_HEALTH = 3` (starting health)

### Adding New Levels
Extend the `Level` class in `levels.py`:
1. Add new `_generate_level_X()` method
2. Update `LevelManager.max_level`
3. Add special features in `_place_special_features()`

## 🏅 Achievement Ideas
- **Speed Runner**: Complete all levels in under 15 minutes
- **Ghost Whisperer**: Complete a level without taking damage
- **Treasure Hunter**: Find all Easter eggs in a single playthrough
- **Perfectionist**: Collect every candy in the level (20+ total)
- **Survivor**: Complete Level 5 with full health

## 📝 Credits

**Developer & Copyright**: BMKoscak  
**Game Design & Programming**: GitHub Copilot  
**Engine**: Python 3 + Pygame  
**Art Style**: Retro pixel art with Halloween theme  
**Music**: pixabay.com

## 🆘 Support

If you encounter any bugs or have suggestions:
1. Check that you're using the latest version of the game
2. Verify all dependencies are installed correctly  
3. Try deleting save files to reset game state
4. **Contact the developer**: Reach out to BMKoscak for direct support and assistance

## 🎃 Happy Halloween!

Enjoy your spooky adventure through the haunted town! Can you survive all 5 levels and achieve the highest score? Good luck, brave ghost! 👻

## ⚠️ Beta Version Notice

This is a **BETA release** of Halloween Haunt: Candy Quest. While the game is fully playable, you may encounter:
- Minor bugs or glitches
- Performance issues on some systems
- Features that may change in the final release
- Save file compatibility issues between versions

Please report any issues to BMKoscak for support and improvements!

---
*Made with ❤️ and lots of Halloween spirit! Perfect for October gaming sessions.*