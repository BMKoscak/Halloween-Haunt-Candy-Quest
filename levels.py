"""
Level management and map generation for Halloween Haunt:         # Create starter house at bottom of map
        self._create_house(2, MAP_HEIGHT - 5, 4, 3)
        # Spawn player on the street (horizontal street in center)
        self.spawn_x = 12 * TILE_SIZE  # Middle of the street
        self.spawn_y = (MAP_HEIGHT - 6) * TILE_SIZE  # On the horizontal street
        self.house_x = 4 * TILE_SIZE  # Door position for level completion
        self.house_y = (MAP_HEIGHT - 2) * TILE_SIZE  # Door positionQuest
"""

import pygame
import random
import math
from typing import List, Tuple, Dict, Optional
from halloween_haunt import (
    MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, CANDIES_TO_COLLECT,
    TileType
)
from entities import TileMap, Candy, Ghost, EasterEgg

class Level:
    """Manages individual game levels with maps, entities, and progression"""
    
    def __init__(self, level_number: int):
        self.level_number = level_number
        self.tile_map = TileMap(MAP_WIDTH, MAP_HEIGHT)
        self.candies: List[Candy] = []
        self.ghosts: List[Ghost] = []
        self.easter_eggs: List[EasterEgg] = []
        
        # Level properties
        self.spawn_x = 0
        self.spawn_y = 0
        self.house_x = 0
        self.house_y = 0
        self.completed = False
        
        # Dynamic properties based on level
        self.ghost_count = min(3 + level_number, 8)
        self.night_mode = level_number >= 4
        self.has_church_interior = level_number >= 3
        self.has_cemetery_boss = level_number >= 5
        
        # Generate the level
        self._generate_map()
        self._place_entities()
        self._place_special_features()
    
    def _generate_map(self):
        """Generate the tile-based map for this level"""
        # Fill with grass by default
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                self.tile_map.set_tile(x, y, TileType.EMPTY)
        
        # Generate based on level number
        if self.level_number == 1:
            self._generate_level_1()
        elif self.level_number == 2:
            self._generate_level_2()
        elif self.level_number == 3:
            self._generate_level_3()
        elif self.level_number == 4:
            self._generate_level_4()
        else:  # Level 5+
            self._generate_level_5()
    
    def _generate_level_1(self):
        """Basic town layout for tutorial/first level"""
        # Create starting house (bottom-left area)
        self._create_house(2, MAP_HEIGHT - 5, 4, 3)
        # Spawn player on the street (horizontal street)
        self.spawn_x = 12 * TILE_SIZE  # Middle of the street
        self.spawn_y = (MAP_HEIGHT - 6) * TILE_SIZE  # On the horizontal street
        self.house_x = 4 * TILE_SIZE  # Door position for level completion
        self.house_y = (MAP_HEIGHT - 2) * TILE_SIZE  # Door position
        

        
        # Create main street (horizontal)
        for x in range(1, MAP_WIDTH - 1):
            self.tile_map.set_tile(x, MAP_HEIGHT - 7, TileType.STREET)
            self.tile_map.set_tile(x, MAP_HEIGHT - 6, TileType.STREET)
        
        # Create vertical street
        for y in range(5, MAP_HEIGHT - 2):
            self.tile_map.set_tile(10, y, TileType.STREET)
            self.tile_map.set_tile(11, y, TileType.STREET)
        
        # Add some houses along the street
        self._create_house(15, MAP_HEIGHT - 5, 3, 2)
        self._create_house(20, MAP_HEIGHT - 5, 3, 2)
        
        # Simple church
        self._create_church(25, 8, 4, 6)
        
        # Small cemetery
        self._create_cemetery(MAP_WIDTH - 8, 2, 6, 6)
        
        # Add some trees and obstacles
        for _ in range(8):
            x = random.randint(0, MAP_WIDTH - 1)
            y = random.randint(0, MAP_HEIGHT - 1)
            if self.tile_map.get_tile(x, y) == TileType.EMPTY:
                if random.random() < 0.7:
                    self.tile_map.set_tile(x, y, TileType.TREE)
                else:
                    self.tile_map.set_tile(x, y, TileType.TRASH_CAN)
    
    def _generate_level_2(self):
        """More complex town with alleys"""
        # Reuse level 1 as base
        self._generate_level_1()
        
        # Add more alleys
        # Vertical alley
        for y in range(2, MAP_HEIGHT - 8):
            self.tile_map.set_tile(7, y, TileType.STREET)
        
        # Horizontal alley
        for x in range(12, 25):
            self.tile_map.set_tile(x, 12, TileType.STREET)
        
        # Add more houses
        self._create_house(5, 8, 3, 3)
        self._create_house(13, 5, 3, 3)
        
        # More obstacles
        for _ in range(5):
            x = random.randint(0, MAP_WIDTH - 1)
            y = random.randint(0, MAP_HEIGHT - 1)
            if self.tile_map.get_tile(x, y) == TileType.EMPTY:
                self.tile_map.set_tile(x, y, TileType.TRASH_CAN)
    
    def _generate_level_3(self):
        """Add church interior and more complexity"""
        self._generate_level_2()
        
        # Larger church with interior access
        self._create_church(23, 6, 6, 8)
        
        # Add church door
        self.tile_map.set_tile(25, 13, TileType.CHURCH_DOOR)
        
        # Extended cemetery with gate
        self._create_cemetery(MAP_WIDTH - 10, 1, 8, 8)
        self.tile_map.set_tile(MAP_WIDTH - 6, 8, TileType.CEMETERY_GATE)
    
    def _generate_level_4(self):
        """Timed challenges and more hazards"""
        self._generate_level_3()
        
        # Add more complex street layout
        # Diagonal street
        for i in range(8):
            x = 3 + i
            y = 3 + i
            if x < MAP_WIDTH and y < MAP_HEIGHT:
                self.tile_map.set_tile(x, y, TileType.STREET)
        
        # More buildings
        self._create_house(1, 1, 4, 4)
        self._create_house(MAP_WIDTH - 6, MAP_HEIGHT - 6, 4, 4)
    
    def _generate_level_5(self):
        """Final level with all features"""
        self._generate_level_4()
        
        # Add boss area in cemetery
        # Larger cemetery
        for x in range(MAP_WIDTH - 12, MAP_WIDTH):
            for y in range(0, 10):
                if x < MAP_WIDTH - 2 and y < 8:
                    self.tile_map.set_tile(x, y, TileType.EMPTY)  # Open area for boss
                elif self.tile_map.get_tile(x, y) == TileType.EMPTY:
                    if random.random() < 0.3:
                        self.tile_map.set_tile(x, y, TileType.GRAVE)
        
        # Add walls around cemetery
        for x in range(MAP_WIDTH - 12, MAP_WIDTH):
            self.tile_map.set_tile(x, 0, TileType.WALL)
            if x < MAP_WIDTH - 1:
                self.tile_map.set_tile(x, 9, TileType.WALL)
        
        for y in range(0, 10):
            self.tile_map.set_tile(MAP_WIDTH - 12, y, TileType.WALL)
            self.tile_map.set_tile(MAP_WIDTH - 1, y, TileType.WALL)
    
    def _create_house(self, x: int, y: int, width: int, height: int):
        """Create a house structure"""
        # Walls
        for dx in range(width):
            for dy in range(height):
                if dx == 0 or dx == width - 1 or dy == 0 or dy == height - 1:
                    self.tile_map.set_tile(x + dx, y + dy, TileType.WALL)
                else:
                    self.tile_map.set_tile(x + dx, y + dy, TileType.HOUSE)
        
        # Door (on bottom wall)
        door_x = x + width // 2
        door_y = y + height - 1
        self.tile_map.set_tile(door_x, door_y, TileType.DOOR)
    
    def _create_church(self, x: int, y: int, width: int, height: int):
        """Create a church structure"""
        # Walls
        for dx in range(width):
            for dy in range(height):
                if dx == 0 or dx == width - 1 or dy == 0 or dy == height - 1:
                    self.tile_map.set_tile(x + dx, y + dy, TileType.WALL)
                else:
                    self.tile_map.set_tile(x + dx, y + dy, TileType.CHURCH)
        
        # Church door
        door_x = x + width // 2
        door_y = y + height - 1
        self.tile_map.set_tile(door_x, door_y, TileType.CHURCH_DOOR)
    
    def _create_cemetery(self, x: int, y: int, width: int, height: int):
        """Create a cemetery area"""
        # Fence around cemetery
        for dx in range(width):
            for dy in range(height):
                if dx == 0 or dx == width - 1 or dy == 0 or dy == height - 1:
                    self.tile_map.set_tile(x + dx, y + dy, TileType.WALL)
        
        # Random graves inside
        for dx in range(1, width - 1):
            for dy in range(1, height - 1):
                if random.random() < 0.4:
                    self.tile_map.set_tile(x + dx, y + dy, TileType.GRAVE)
        
        # Cemetery gate
        gate_x = x + width // 2
        gate_y = y + height - 1
        self.tile_map.set_tile(gate_x, gate_y, TileType.CEMETERY_GATE)
    
    def _place_entities(self):
        """Place candies, ghosts, and Easter eggs on the map"""
        self._place_candies()
        self._place_ghosts()
        self._place_easter_eggs()
    
    def _place_candies(self):
        """Place candies around the map"""
        candies_placed = 0
        attempts = 0
        max_attempts = 1000
        
        while candies_placed < CANDIES_TO_COLLECT + 5 and attempts < max_attempts:
            x = random.randint(1, MAP_WIDTH - 2) * TILE_SIZE + TILE_SIZE // 2
            y = random.randint(1, MAP_HEIGHT - 2) * TILE_SIZE + TILE_SIZE // 2
            
            tile_x = int(x // TILE_SIZE)
            tile_y = int(y // TILE_SIZE)
            
            # Check if position is valid (not in walls, not too close to spawn)
            if (not self.tile_map.is_solid_tile(tile_x, tile_y) and
                abs(x - self.spawn_x) > TILE_SIZE * 2 and
                abs(y - self.spawn_y) > TILE_SIZE * 2):
                
                # Determine candy type
                candy_type = "normal"
                points = 10
                
                if self.level_number >= 3 and random.random() < 0.1:
                    candy_type = "cursed"
                    points = 20
                elif random.random() < 0.15:
                    candy_type = "bonus"
                    points = 25
                
                self.candies.append(Candy(x, y, candy_type, points))
                candies_placed += 1
            
            attempts += 1
    
    def _place_ghosts(self):
        """Place ghosts with patrol routes"""
        for i in range(self.ghost_count):
            # Find valid spawn position
            attempts = 0
            while attempts < 100:
                x = random.randint(2, MAP_WIDTH - 3) * TILE_SIZE + TILE_SIZE // 2
                y = random.randint(2, MAP_HEIGHT - 3) * TILE_SIZE + TILE_SIZE // 2
                
                tile_x = int(x // TILE_SIZE)
                tile_y = int(y // TILE_SIZE)
                
                # Check distance from player spawn
                distance_to_spawn = ((x - self.spawn_x) ** 2 + (y - self.spawn_y) ** 2) ** 0.5
                
                if (not self.tile_map.is_solid_tile(tile_x, tile_y) and
                    distance_to_spawn > TILE_SIZE * 5):
                    
                    # Create patrol route
                    patrol_points = self._create_patrol_route(x, y)
                    
                    ghost = Ghost(x, y, patrol_points)
                    self.ghosts.append(ghost)
                    break
                
                attempts += 1
        
        # Add boss ghost for level 5+
        if self.has_cemetery_boss:
            boss_x = (MAP_WIDTH - 6) * TILE_SIZE
            boss_y = 4 * TILE_SIZE
            boss_patrol = [
                (boss_x, boss_y),
                (boss_x - TILE_SIZE * 2, boss_y),
                (boss_x - TILE_SIZE * 2, boss_y + TILE_SIZE * 2),
                (boss_x, boss_y + TILE_SIZE * 2)
            ]
            boss_ghost = Ghost(boss_x, boss_y, boss_patrol)
            self.ghosts.append(boss_ghost)
    
    def _create_patrol_route(self, start_x: float, start_y: float) -> List[Tuple[float, float]]:
        """Create a patrol route for a ghost"""
        route = [(start_x, start_y)]
        
        # Add 2-4 additional patrol points
        num_points = random.randint(2, 4)
        
        for _ in range(num_points):
            # Try to find a nearby walkable position
            for _ in range(10):
                offset_x = random.randint(-3, 3) * TILE_SIZE
                offset_y = random.randint(-3, 3) * TILE_SIZE
                
                new_x = start_x + offset_x
                new_y = start_y + offset_y
                
                tile_x = int(new_x // TILE_SIZE)
                tile_y = int(new_y // TILE_SIZE)
                
                if not self.tile_map.is_solid_tile(tile_x, tile_y):
                    route.append((new_x, new_y))
                    break
        
        return route
    
    def _place_easter_eggs(self):
        """Place hidden Easter eggs"""
        egg_count = 5 + self.level_number  # 6-10 eggs per level
        
        for i in range(egg_count):
            attempts = 0
            while attempts < 50:
                x = random.randint(1, MAP_WIDTH - 2) * TILE_SIZE + TILE_SIZE // 2
                y = random.randint(1, MAP_HEIGHT - 2) * TILE_SIZE + TILE_SIZE // 2
                
                tile_x = int(x // TILE_SIZE)
                tile_y = int(y // TILE_SIZE)
                
                if not self.tile_map.is_solid_tile(tile_x, tile_y):
                    # Determine egg type and reward
                    egg_types = ["stash", "bonus", "powerup"]
                    if self.level_number >= 3:
                        egg_types.extend(["puzzle", "dig"])
                    
                    egg_type = random.choice(egg_types)
                    
                    rewards = {
                        "stash": "Extra candy stash (+25 points)",
                        "bonus": "Health boost (+1 heart)",
                        "powerup": random.choice([
                            "Candy magnet (10 seconds)",
                            "Ghost repel (15 seconds)", 
                            "Speed boost (7 seconds)",
                            "Invisibility (12 seconds)",
                            "Time slow (8 seconds)",
                            "Double points (10 seconds)",
                            "Shield (15 seconds)"
                        ])
                    }
                    
                    reward = rewards.get(egg_type, "Mystery bonus!")
                    
                    # Some eggs are secret (invisible until found)
                    if random.random() < 0.3:
                        egg_type = "secret"
                    
                    self.easter_eggs.append(EasterEgg(x, y, egg_type, reward))
                    break
                
                attempts += 1
    
    def _place_special_features(self):
        """Place special features like church puzzles, digging sites, and traps"""
        # Initialize special feature locations
        self.special_feature_locations = {}
        
        # Church puzzles (level 3+)
        if self.level_number >= 3:
            # Add puzzle in church area
            church_x = 25 * TILE_SIZE + TILE_SIZE // 2
            church_y = 10 * TILE_SIZE + TILE_SIZE // 2
            self.special_feature_locations['church_puzzle'] = (church_x, church_y)
        
        # Cemetery digging sites (level 2+)  
        if self.level_number >= 2:
            # Add digging sites in cemetery
            dig_sites = []
            for i in range(2):
                dig_x = (MAP_WIDTH - 6 + i * 2) * TILE_SIZE + TILE_SIZE // 2
                dig_y = (3 + i) * TILE_SIZE + TILE_SIZE // 2
                dig_sites.append((dig_x, dig_y))
            self.special_feature_locations['dig_sites'] = dig_sites
        
        # Jack-o'-lantern traps (level 4+)
        if self.level_number >= 4:
            trap_locations = []
            for _ in range(2 + self.level_number // 2):
                attempts = 0
                while attempts < 30:
                    x = random.randint(5, MAP_WIDTH - 5) * TILE_SIZE + TILE_SIZE // 2
                    y = random.randint(5, MAP_HEIGHT - 5) * TILE_SIZE + TILE_SIZE // 2
                    
                    tile_x = int(x // TILE_SIZE)
                    tile_y = int(y // TILE_SIZE)
                    
                    # Check if position is valid
                    if (not self.tile_map.is_solid_tile(tile_x, tile_y) and
                        abs(x - self.spawn_x) > TILE_SIZE * 3 and
                        abs(y - self.spawn_y) > TILE_SIZE * 3):
                        trap_locations.append((x, y))
                        break
                    attempts += 1
            
            self.special_feature_locations['traps'] = trap_locations
    
    def get_spawn_position(self) -> Tuple[float, float]:
        """Get the player spawn position for this level"""
        return self.spawn_x, self.spawn_y
    
    def get_house_position(self) -> Tuple[float, float]:
        """Get the house position for level completion"""
        return self.house_x, self.house_y
    
    def check_level_completion(self, player_x: float, player_y: float, candies_collected: int) -> bool:
        """Check if level completion conditions are met"""
        if candies_collected < CANDIES_TO_COLLECT:
            return False
        
        # Check if player is near the house
        distance_to_house = ((player_x - self.house_x) ** 2 + (player_y - self.house_y) ** 2) ** 0.5
        
        if distance_to_house <= TILE_SIZE * 1.5:
            self.completed = True
            return True
        
        return False
    
    def update(self, player):
        """Update all level entities"""
        # Update ghosts and check for chase events
        chase_events = []
        for ghost in self.ghosts:
            started_chasing = ghost.update(player, self.tile_map)
            if started_chasing:
                chase_events.append(ghost)
        
        # Update candies
        for candy in self.candies:
            candy.update()
        
        # Update Easter eggs
        for egg in self.easter_eggs:
            egg.update()
            
        return chase_events
    
    def draw(self, screen: pygame.Surface, highlight_house: bool = False):
        """Draw the level"""
        # Draw tile map
        self.tile_map.draw(screen, highlight_house, (self.house_x, self.house_y))
        
        # Draw candies
        for candy in self.candies:
            candy.draw(screen)
        
        # Draw Easter eggs
        for egg in self.easter_eggs:
            egg.draw(screen)
        
        # Draw ghosts
        for ghost in self.ghosts:
            ghost.draw(screen)

class LevelManager:
    """Manages level loading and progression"""
    
    def __init__(self):
        self.current_level_number = 1
        self.max_level = 5
        self.levels = {}
    
    def load_level(self, level_number: int) -> Level:
        """Load a specific level"""
        self.current_level_number = level_number
        
        if level_number not in self.levels:
            self.levels[level_number] = Level(level_number)
        
        return self.levels[level_number]
    
    def next_level(self) -> Optional[Level]:
        """Advance to the next level"""
        if self.current_level_number < self.max_level:
            self.current_level_number += 1
            return self.load_level(self.current_level_number)
        return None
    
    def restart_current_level(self) -> Level:
        """Restart the current level"""
        # Clear the cached level to force regeneration
        if self.current_level_number in self.levels:
            del self.levels[self.current_level_number]
        return self.load_level(self.current_level_number)
    
    def is_final_level(self) -> bool:
        """Check if current level is the final level"""
        return self.current_level_number >= self.max_level

class CemeteryArea:
    """Special cemetery area with unique gameplay"""
    
    def __init__(self, entrance_x: float, entrance_y: float):
        self.entrance_x = entrance_x
        self.entrance_y = entrance_y
        self.tile_map = TileMap(MAP_WIDTH, MAP_HEIGHT)
        self.candies: List[Candy] = []
        self.ghosts: List[Ghost] = []
        self.easter_eggs: List[EasterEgg] = []
        
        # Cemetery-specific properties
        self.boss_ghost = None
        self.dig_sites: List[Tuple[float, float]] = []
        self.treasures_found = 0
        self.completed = False
        
        # Generate cemetery layout
        self._generate_cemetery()
        self._place_cemetery_entities()
    
    def _generate_cemetery(self):
        """Generate the cemetery area layout"""
        # Fill with dark grass
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                self.tile_map.set_tile(x, y, TileType.EMPTY)
        
        # Create cemetery boundaries (walls/fences)
        for x in range(MAP_WIDTH):
            self.tile_map.set_tile(x, 0, TileType.WALL)
            self.tile_map.set_tile(x, MAP_HEIGHT - 1, TileType.WALL)
        
        for y in range(MAP_HEIGHT):
            self.tile_map.set_tile(0, y, TileType.WALL)
            self.tile_map.set_tile(MAP_WIDTH - 1, y, TileType.WALL)
        
        # Add cemetery gate (entrance/exit)
        gate_x = int(self.entrance_x // TILE_SIZE)
        gate_y = int(self.entrance_y // TILE_SIZE)
        self.tile_map.set_tile(gate_x, gate_y, TileType.CEMETERY_GATE)
        
        # Add graves randomly
        for _ in range(25):
            x = random.randint(2, MAP_WIDTH - 3)
            y = random.randint(2, MAP_HEIGHT - 3)
            if self.tile_map.get_tile(x, y) == TileType.EMPTY:
                self.tile_map.set_tile(x, y, TileType.GRAVE)
        
        # Add some mausoleums (houses)
        for _ in range(3):
            x = random.randint(3, MAP_WIDTH - 6)
            y = random.randint(3, MAP_HEIGHT - 6)
            if self.tile_map.get_tile(x, y) == TileType.EMPTY:
                self._create_mausoleum(x, y, 3, 3)
        
        # Add spooky trees
        for _ in range(8):
            x = random.randint(2, MAP_WIDTH - 3)
            y = random.randint(2, MAP_HEIGHT - 3)
            if self.tile_map.get_tile(x, y) == TileType.EMPTY:
                self.tile_map.set_tile(x, y, TileType.TREE)
    
    def _create_mausoleum(self, x: int, y: int, width: int, height: int):
        """Create a mausoleum structure"""
        for dx in range(width):
            for dy in range(height):
                if dx == 0 or dx == width - 1 or dy == 0 or dy == height - 1:
                    self.tile_map.set_tile(x + dx, y + dy, TileType.WALL)
                else:
                    self.tile_map.set_tile(x + dx, y + dy, TileType.HOUSE)
        
        # Add door
        door_x = x + width // 2
        door_y = y + height - 1
        self.tile_map.set_tile(door_x, door_y, TileType.DOOR)
    
    def _place_cemetery_entities(self):
        """Place entities specific to the cemetery"""
        # Add cemetery ghosts (more aggressive)
        for i in range(6):
            attempts = 0
            while attempts < 50:
                x = random.randint(2, MAP_WIDTH - 3) * TILE_SIZE + TILE_SIZE // 2
                y = random.randint(2, MAP_HEIGHT - 3) * TILE_SIZE + TILE_SIZE // 2
                
                tile_x = int(x // TILE_SIZE)
                tile_y = int(y // TILE_SIZE)
                
                if not self.tile_map.is_solid_tile(tile_x, tile_y):
                    patrol_points = [
                        (x, y),
                        (x + 64, y),
                        (x, y + 64),
                        (x - 64, y)
                    ]
                    ghost = Ghost(x, y, patrol_points)
                    self.ghosts.append(ghost)
                    break
                attempts += 1
        
        # Add boss ghost in center
        boss_x = MAP_WIDTH // 2 * TILE_SIZE
        boss_y = MAP_HEIGHT // 2 * TILE_SIZE
        boss_patrol = [
            (boss_x, boss_y),
            (boss_x + 100, boss_y),
            (boss_x, boss_y + 100),
            (boss_x - 100, boss_y)
        ]
        self.boss_ghost = Ghost(boss_x, boss_y, boss_patrol)
        self.boss_ghost.radius = 12  # Bigger boss
        self.ghosts.append(self.boss_ghost)
        
        # Add digging sites
        for _ in range(5):
            attempts = 0
            while attempts < 30:
                x = random.randint(3, MAP_WIDTH - 3) * TILE_SIZE + TILE_SIZE // 2
                y = random.randint(3, MAP_HEIGHT - 3) * TILE_SIZE + TILE_SIZE // 2
                
                tile_x = int(x // TILE_SIZE)
                tile_y = int(y // TILE_SIZE)
                
                if not self.tile_map.is_solid_tile(tile_x, tile_y):
                    self.dig_sites.append((x, y))
                    break
                attempts += 1
        
        # Add special cemetery candies
        for _ in range(8):
            attempts = 0
            while attempts < 50:
                x = random.randint(2, MAP_WIDTH - 3) * TILE_SIZE + TILE_SIZE // 2
                y = random.randint(2, MAP_HEIGHT - 3) * TILE_SIZE + TILE_SIZE // 2
                
                tile_x = int(x // TILE_SIZE)
                tile_y = int(y // TILE_SIZE)
                
                if not self.tile_map.is_solid_tile(tile_x, tile_y):
                    candy = Candy(x, y, "bonus", 25)  # Bonus candies in cemetery
                    self.candies.append(candy)
                    break
                attempts += 1
        
        # Add cemetery Easter eggs
        for _ in range(3):
            attempts = 0
            while attempts < 30:
                x = random.randint(2, MAP_WIDTH - 3) * TILE_SIZE + TILE_SIZE // 2
                y = random.randint(2, MAP_HEIGHT - 3) * TILE_SIZE + TILE_SIZE // 2
                
                tile_x = int(x // TILE_SIZE)
                tile_y = int(y // TILE_SIZE)
                
                if not self.tile_map.is_solid_tile(tile_x, tile_y):
                    egg = EasterEgg(x, y, "secret", "Ancient cemetery relic (+100 points, zombie power)")
                    self.easter_eggs.append(egg)
                    break
                attempts += 1
    
    def check_exit(self, player_x: float, player_y: float) -> bool:
        """Check if player is exiting the cemetery"""
        distance = math.sqrt((player_x - self.entrance_x) ** 2 + (player_y - self.entrance_y) ** 2)
        return distance < TILE_SIZE * 1.5
    
    def update(self, player):
        """Update cemetery entities"""
        # Update ghosts
        chase_events = []
        for ghost in self.ghosts:
            started_chasing = ghost.update(player, self.tile_map)
            if started_chasing:
                chase_events.append(ghost)
        
        # Update candies
        for candy in self.candies:
            candy.update()
        
        # Update Easter eggs
        for egg in self.easter_eggs:
            egg.update()
        
        # Check if boss is defeated (for completion)
        if self.boss_ghost and self.boss_ghost not in self.ghosts:
            self.completed = True
        
        return chase_events
    
    def draw(self, screen: pygame.Surface):
        """Draw the cemetery"""
        self.tile_map.draw(screen)
        
        # Draw candies
        for candy in self.candies:
            candy.draw(screen)
        
        # Draw Easter eggs
        for egg in self.easter_eggs:
            egg.draw(screen)
        
        # Draw ghosts
        for ghost in self.ghosts:
            ghost.draw(screen)