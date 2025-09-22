#!/usr/bin/env python3
"""
Halloween Haunt: Candy Quest - BETA VERSION
A 2D top-down exploration game using Pygame

BETA NOTICE: This is a beta release. Some features may be incomplete.
Please report bugs to the developer: BMKoscak

Run with: python halloween_haunt.py
Create 'assets' folder for custom sprites/sounds if desired.
Game falls back to basic shapes if assets are missing.

Controls:
- WASD/Arrow keys: Movement
- SPACE: Interact (pickup candy, activate Easter eggs)
- ESC: Pause menu
- F11: Toggle fullscreen
- Mouse: Menu navigation

Author: GitHub Copilot
Date: September 2025
"""

import pygame
import sys
import os
import json
import math
import random
from enum import Enum
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 32
MAP_WIDTH = 30  # tiles
MAP_HEIGHT = 20  # tiles

# Movement Constants
PLAYER_MAX_SPEED = 3.0
PLAYER_ACCELERATION = 0.2
PLAYER_DECELERATION = 0.15
GHOST_SPEED = 1.5
GHOST_CHASE_SPEED = 2.5
GHOST_DETECTION_RADIUS = 100

# Game Balance
CANDIES_TO_COLLECT = 15
PLAYER_MAX_HEALTH = 3
INVINCIBILITY_DURATION = 120  # frames (2 seconds at 60 FPS)

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 69, 19)
PURPLE = (128, 0, 128)
TRANSPARENT_GRAY = (128, 128, 128, 128)

# Tile Types
class TileType(Enum):
    EMPTY = 0
    STREET = 1
    HOUSE = 2
    WALL = 3
    CHURCH = 4
    GRAVE = 5
    TREE = 6
    DOOR = 7
    CHURCH_DOOR = 8
    CEMETERY_GATE = 9
    TRASH_CAN = 10

# Game States
class GameState(Enum):
    MAIN_MENU = 0
    TUTORIAL = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    LEVEL_COMPLETE = 5
    VICTORY = 6
    SETTINGS = 7
    CEMETERY = 8

# Power-up Types
class PowerUpType(Enum):
    CANDY_MAGNET = 0
    GHOST_REPEL = 1
    EXTRA_HEART = 2
    SPEED_BOOST = 3
    ZOMBIE_POWER = 4
    INVISIBILITY = 5
    TIME_SLOW = 6
    DOUBLE_POINTS = 7
    SHIELD = 8

@dataclass
class PowerUp:
    """Represents an active power-up effect"""
    type: PowerUpType
    duration: int  # frames remaining
    strength: float = 1.0

class Particle:
    """Simple particle for visual effects"""
    def __init__(self, x: float, y: float, vx: float, vy: float, color: Tuple[int, int, int], lifetime: int):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.98  # slight friction
        self.vy *= 0.98
        self.lifetime -= 1
        
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color = (*self.color, alpha)
            size = max(1, int(3 * (self.lifetime / self.max_lifetime)))
            pygame.draw.circle(screen, self.color, 
                             (int(self.x - camera_x), int(self.y - camera_y)), size)

class AssetManager:
    """Handles loading and fallback for game assets"""
    
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.music_loaded = False
        
    def load_image(self, path: str, fallback_color: Tuple[int, int, int] = WHITE, 
                   size: Tuple[int, int] = (TILE_SIZE, TILE_SIZE)) -> pygame.Surface:
        """Load image with fallback to colored rectangle"""
        if path in self.images:
            return self.images[path]
            
        try:
            if os.path.exists(path):
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, size)
            else:
                # Fallback: create colored rectangle
                image = pygame.Surface(size, pygame.SRCALPHA)
                image.fill(fallback_color)
                
        except pygame.error:
            # Create fallback colored rectangle
            image = pygame.Surface(size, pygame.SRCALPHA)
            image.fill(fallback_color)
            
        self.images[path] = image
        return image
        
    def load_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        """Load sound with graceful fallback"""
        if path in self.sounds:
            return self.sounds[path]
            
        try:
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
            else:
                sound = None  # No sound fallback
        except pygame.error:
            sound = None
            
        self.sounds[path] = sound
        return sound
        
    def load_music(self, path: str) -> bool:
        """Load background music"""
        try:
            if os.path.exists(path):
                pygame.mixer.music.load(path)
                self.music_loaded = True
                return True
        except pygame.error:
            pass
        return False
        
    def load_font(self, path: str, size: int) -> pygame.font.Font:
        """Load font with fallback to system font"""
        key = f"{path}_{size}"
        if key in self.fonts:
            return self.fonts[key]
            
        try:
            if os.path.exists(path):
                font = pygame.font.Font(path, size)
            else:
                font = pygame.font.SysFont('arial', size, bold=True)
        except pygame.error:
            font = pygame.font.SysFont('arial', size, bold=True)
            
        self.fonts[key] = font
        return font

class Camera:
    """Simple camera system for smooth following"""
    
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.smoothing = 0.1
        
    def update(self, target_x: float, target_y: float):
        """Smooth camera movement toward target"""
        self.target_x = target_x - SCREEN_WIDTH // 2
        self.target_y = target_y - SCREEN_HEIGHT // 2
        
        # Keep camera within map bounds
        max_x = MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH
        max_y = MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT
        
        self.target_x = max(0, min(max_x, self.target_x))
        self.target_y = max(0, min(max_y, self.target_y))
        
        # Smooth interpolation
        self.x += (self.target_x - self.x) * self.smoothing
        self.y += (self.target_y - self.y) * self.smoothing

class SaveManager:
    """Handles game save/load functionality"""
    
    def __init__(self):
        self.save_file = "save_data.txt"
        self.high_scores_file = "high_scores.txt"
        
    def save_progress(self, level: int, score: int, tutorial_completed: bool):
        """Save current game progress"""
        data = {
            "level": level,
            "score": score,
            "tutorial_completed": tutorial_completed
        }
        
        try:
            with open(self.save_file, 'w') as f:
                json.dump(data, f)
        except IOError:
            pass  # Fail silently
            
    def load_progress(self) -> Dict[str, Any]:
        """Load saved game progress"""
        default = {"level": 1, "score": 0, "tutorial_completed": False}
        
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
            
        return default
        
    def save_high_score(self, name: str, score: int):
        """Save high score"""
        scores = self.load_high_scores()
        scores.append({"name": name, "score": score})
        scores.sort(key=lambda x: x["score"], reverse=True)
        scores = scores[:5]  # Keep top 5
        
        try:
            with open(self.high_scores_file, 'w') as f:
                json.dump(scores, f)
        except IOError:
            pass
            
    def load_high_scores(self) -> List[Dict[str, Any]]:
        """Load high scores"""
        try:
            if os.path.exists(self.high_scores_file):
                with open(self.high_scores_file, 'r') as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
            
        return []

# Global instances
asset_manager = AssetManager()
camera = Camera()
save_manager = SaveManager()

def main():
    """Main game loop"""
    # Initialize display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Halloween Haunt: Candy Quest - BETA")
    clock = pygame.time.Clock()
    
    # Load icon if available
    try:
        if os.path.exists("assets/icon.png"):
            icon = pygame.image.load("assets/icon.png")
            pygame.display.set_icon(icon)
    except pygame.error:
        pass
    
    # Initialize game
    from game_manager import GameManager
    game_manager = GameManager(screen)
    
    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game_manager.handle_event(event)
                
        game_manager.update(dt)
        game_manager.draw()
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()