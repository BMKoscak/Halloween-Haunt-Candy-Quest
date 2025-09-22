"""
Special features for Halloween Haunt: Candy Quest
Church puzzles, cemetery digging mini-game, and advanced power-ups
"""

import pygame
import random
import math
from typing import List, Tuple, Optional, Dict
from halloween_haunt import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE,
    WHITE, BLACK, ORANGE, GRAY, RED, GREEN, BLUE, BROWN, YELLOW, PURPLE,
    asset_manager, camera
)
from entities import Player, Particle

class ChurchPuzzle:
    """Church interior puzzle - rearrange symbols for bonus candy"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.active = False
        self.completed = False
        self.symbols = ["cross", "candle", "bible", "angel"]
        self.current_order = self.symbols.copy()
        self.target_order = ["angel", "bible", "candle", "cross"]
        self.selected_symbol = 0
        
        # Visual properties
        self.symbol_positions = []
        self.puzzle_rect = pygame.Rect(x - 100, y - 50, 200, 100)
        
        # Initialize symbol positions
        for i in range(len(self.symbols)):
            symbol_x = x - 75 + i * 50
            symbol_y = y
            self.symbol_positions.append((symbol_x, symbol_y))
        
        random.shuffle(self.current_order)
    
    def interact(self, player: Player) -> Tuple[bool, str, List[Particle]]:
        """Interact with the church puzzle"""
        distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        
        if distance > 50:
            return False, "Get closer to the altar!", []
        
        if self.completed:
            return False, "Puzzle already solved!", []
        
        if not self.active:
            self.active = True
            return True, "Use WASD to rearrange symbols, SPACE to confirm.", []
        
        return False, "", []
    
    def handle_input(self, keys_pressed: pygame.key.ScancodeWrapper, space_pressed: bool) -> Tuple[bool, List[Particle]]:
        """Handle puzzle input. Returns (completed, particles)"""
        if not self.active or self.completed:
            return False, []
        
        particles = []
        
        # Move selected symbol
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
            if self.selected_symbol > 0:
                # Swap with left symbol
                self.current_order[self.selected_symbol], self.current_order[self.selected_symbol - 1] = \
                    self.current_order[self.selected_symbol - 1], self.current_order[self.selected_symbol]
                self.selected_symbol -= 1
        
        elif keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            if self.selected_symbol < len(self.current_order) - 1:
                # Swap with right symbol
                self.current_order[self.selected_symbol], self.current_order[self.selected_symbol + 1] = \
                    self.current_order[self.selected_symbol + 1], self.current_order[self.selected_symbol]
                self.selected_symbol += 1
        
        # Check solution on space press
        if space_pressed:
            if self.current_order == self.target_order:
                self.completed = True
                self.active = False
                
                # Create celebration particles
                for _ in range(20):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(2, 5)
                    vx = math.cos(angle) * speed
                    vy = math.sin(angle) * speed
                    color = random.choice([YELLOW, WHITE, BLUE])
                    particles.append(Particle(self.x, self.y, vx, vy, color, 90))
                
                return True, particles
            else:
                # Wrong solution - shuffle again
                random.shuffle(self.current_order)
        
        return False, particles
    
    def draw(self, screen: pygame.Surface):
        """Draw the church puzzle"""
        if not self.active:
            return
        
        screen_x = int(self.x - camera.x)
        screen_y = int(self.y - camera.y)
        
        # Draw puzzle background
        puzzle_surface = pygame.Surface((200, 100), pygame.SRCALPHA)
        puzzle_surface.fill((50, 30, 20, 200))
        pygame.draw.rect(puzzle_surface, YELLOW, (0, 0, 200, 100), 3)
        
        screen.blit(puzzle_surface, (screen_x - 100, screen_y - 50))
        
        # Draw symbols
        font = asset_manager.load_font("assets/fonts/creepy.ttf", 16)
        
        for i, symbol in enumerate(self.current_order):
            symbol_x = screen_x - 75 + i * 50
            symbol_y = screen_y
            
            # Highlight selected symbol
            if i == self.selected_symbol:
                pygame.draw.circle(screen, WHITE, (symbol_x, symbol_y), 20, 2)
            
            # Draw symbol (simplified text representation)
            symbol_text = {
                "cross": "✞",
                "candle": "🕯",
                "bible": "📖",
                "angel": "👼"
            }.get(symbol, symbol[0].upper())
            
            text_surface = font.render(symbol_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(symbol_x, symbol_y))
            screen.blit(text_surface, text_rect)
        
        # Draw instructions
        instruction_font = asset_manager.load_font("assets/fonts/creepy.ttf", 12)
        instruction_text = "WASD to move, SPACE to check"
        instruction_surface = instruction_font.render(instruction_text, True, WHITE)
        instruction_rect = instruction_surface.get_rect(center=(screen_x, screen_y + 60))
        screen.blit(instruction_surface, instruction_rect)

class CemeteryDigging:
    """Cemetery digging mini-game for hidden treasures"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.active = False
        self.completed = False
        self.dig_progress = 0
        self.required_digs = 5
        self.dig_timer = 0
        self.dig_cooldown = 30  # frames between digs
        
        # Visual properties
        self.dirt_particles: List[Particle] = []
        
    def interact(self, player: Player) -> Tuple[bool, str, List[Particle]]:
        """Start digging interaction"""
        distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        
        if distance > 30:
            return False, "Find a good spot to dig!", []
        
        if self.completed:
            return False, "Already dug up treasure here!", []
        
        if not self.active:
            self.active = True
            return True, f"Dig here! Press SPACE rapidly ({self.required_digs} times)", []
        
        return False, "", []
    
    def dig(self) -> Tuple[bool, List[Particle]]:
        """Perform a dig action. Returns (completed, particles)"""
        if not self.active or self.completed or self.dig_timer > 0:
            return False, []
        
        self.dig_progress += 1
        self.dig_timer = self.dig_cooldown
        
        # Create dirt particles
        particles = []
        for _ in range(5):
            angle = random.uniform(-math.pi/4, math.pi/4)  # Upward spray
            speed = random.uniform(3, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2  # Upward bias
            particles.append(Particle(self.x, self.y - 10, vx, vy, BROWN, 45))
        
        # Check if digging is complete
        if self.dig_progress >= self.required_digs:
            self.completed = True
            self.active = False
            
            # Create treasure particles
            for _ in range(15):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 4)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                color = random.choice([YELLOW, ORANGE, GREEN])
                particles.append(Particle(self.x, self.y, vx, vy, color, 60))
            
            return True, particles
        
        return False, particles
    
    def update(self):
        """Update digging state"""
        if self.dig_timer > 0:
            self.dig_timer -= 1
        
        # Update dirt particles
        self.dirt_particles = [p for p in self.dirt_particles if p.lifetime > 0]
        for particle in self.dirt_particles:
            particle.update()
    
    def draw(self, screen: pygame.Surface):
        """Draw digging site"""
        screen_x = int(self.x - camera.x)
        screen_y = int(self.y - camera.y)
        
        if self.active and not self.completed:
            # Draw digging area
            pygame.draw.circle(screen, BROWN, (screen_x, screen_y), 15, 2)
            
            # Draw progress indicator
            progress_width = 30
            progress_height = 5
            progress_x = screen_x - progress_width // 2
            progress_y = screen_y + 25
            
            pygame.draw.rect(screen, GRAY, (progress_x, progress_y, progress_width, progress_height))
            
            fill_width = int(progress_width * (self.dig_progress / self.required_digs))
            pygame.draw.rect(screen, GREEN, (progress_x, progress_y, fill_width, progress_height))
        
        elif self.completed:
            # Draw treasure marker
            pygame.draw.circle(screen, YELLOW, (screen_x, screen_y), 8)
            pygame.draw.circle(screen, ORANGE, (screen_x, screen_y), 5)
        
        # Draw dirt particles
        for particle in self.dirt_particles:
            particle.draw(screen, camera.x, camera.y)

class JackOLanternTrap:
    """Explosive jack-o'-lantern trap for higher levels"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.triggered = False
        self.explosion_timer = 0
        self.explosion_duration = 30
        self.trigger_radius = 40
        self.damage_radius = 60
        
        # Visual properties
        self.glow_timer = 0
        self.explosion_particles: List[Particle] = []
    
    def update(self, player: Player) -> Tuple[bool, List[Particle]]:
        """Update trap. Returns (exploded, particles)"""
        self.glow_timer += 1
        
        if self.triggered:
            self.explosion_timer += 1
            
            if self.explosion_timer >= self.explosion_duration:
                # Check if player is in damage radius
                distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
                
                if distance <= self.damage_radius:
                    # Damage player
                    if player.take_damage():
                        pass  # Player was damaged
                
                # Create explosion particles
                particles = []
                for _ in range(25):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(4, 8)
                    vx = math.cos(angle) * speed
                    vy = math.sin(angle) * speed
                    color = random.choice([RED, ORANGE, YELLOW])
                    particles.append(Particle(self.x, self.y, vx, vy, color, 40))
                
                return True, particles
        else:
            # Check if player is within trigger radius
            distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
            
            if distance <= self.trigger_radius:
                self.triggered = True
        
        return False, []
    
    def draw(self, screen: pygame.Surface):
        """Draw jack-o'-lantern trap"""
        if self.explosion_timer >= self.explosion_duration:
            return  # Already exploded
        
        screen_x = int(self.x - camera.x)
        screen_y = int(self.y - camera.y)
        
        if self.triggered:
            # Flashing warning
            if (self.explosion_timer // 5) % 2:
                color = RED
            else:
                color = ORANGE
        else:
            # Normal glow
            glow_intensity = int(50 + 30 * math.sin(self.glow_timer * 0.1))
            color = ORANGE
        
        # Draw pumpkin (simplified)
        pygame.draw.circle(screen, color, (screen_x, screen_y), 12)
        
        # Draw face
        pygame.draw.circle(screen, BLACK, (screen_x - 4, screen_y - 3), 2)  # Left eye
        pygame.draw.circle(screen, BLACK, (screen_x + 4, screen_y - 3), 2)  # Right eye
        
        # Mouth (simple line)
        mouth_points = [
            (screen_x - 6, screen_y + 3),
            (screen_x - 2, screen_y + 6),
            (screen_x + 2, screen_y + 6),
            (screen_x + 6, screen_y + 3)
        ]
        pygame.draw.lines(screen, BLACK, False, mouth_points, 2)
        
        # Warning indicator when triggered
        if self.triggered:
            warning_radius = 20 + int(10 * math.sin(self.explosion_timer * 0.3))
            pygame.draw.circle(screen, RED, (screen_x, screen_y), warning_radius, 2)

class PowerUpGenerator:
    """Generates and manages special power-ups from Easter eggs"""
    
    @staticmethod
    def create_zombie_power(player: Player) -> List[Particle]:
        """Create zombie power-up effect - temporary ghost immunity"""
        from halloween_haunt import PowerUpType
        
        player.add_powerup(PowerUpType.ZOMBIE_POWER, 900)  # 15 seconds
        
        # Create spooky green particles
        particles = []
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            particles.append(Particle(player.x, player.y, vx, vy, GREEN, 90))
        
        return particles
    
    @staticmethod
    def create_candy_rain(player_x: float, player_y: float) -> List['SpecialCandy']:
        """Create temporary candy rain around player"""
        candies = []
        
        for _ in range(8):
            # Spawn candies in circle around player
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(50, 100)
            x = player_x + math.cos(angle) * radius
            y = player_y + math.sin(angle) * radius
            
            candy = SpecialCandy(x, y, "rain", 15)
            candies.append(candy)
        
        return candies
    
    @staticmethod
    def create_ghost_freeze(ghosts: List) -> int:
        """Freeze all ghosts temporarily"""
        freeze_duration = 300  # 5 seconds
        
        for ghost in ghosts:
            ghost.frozen_timer = freeze_duration
            ghost.original_vx = ghost.vx
            ghost.original_vy = ghost.vy
            ghost.vx = 0
            ghost.vy = 0
        
        return freeze_duration

class SpecialCandy:
    """Temporary candy from special effects"""
    
    def __init__(self, x: float, y: float, candy_type: str, points: int, lifetime: int = 600):
        self.x = x
        self.y = y
        self.type = candy_type
        self.points = points
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.collected = False
        
        # Visual properties
        self.glow_timer = 0
        self.radius = 8
        
        # Create collision rect
        self.rect = pygame.Rect(x - self.radius, y - self.radius, 
                               self.radius * 2, self.radius * 2)
    
    def update(self):
        """Update special candy"""
        self.glow_timer += 1
        self.lifetime -= 1
    
    def is_expired(self) -> bool:
        """Check if candy has expired"""
        return self.lifetime <= 0
    
    def collect(self, player: Player) -> List[Particle]:
        """Collect this special candy"""
        particles = []
        
        if not self.collected and self.lifetime > 0:
            self.collected = True
            player.collect_candy(self.points)
            
            # Create sparkly particles
            for _ in range(12):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 4)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                color = random.choice([YELLOW, WHITE, BLUE])
                particles.append(Particle(self.x, self.y, vx, vy, color, 45))
        
        return particles
    
    def draw(self, screen: pygame.Surface):
        """Draw special candy with unique effects"""
        if self.collected or self.lifetime <= 0:
            return
        
        screen_x = int(self.x - camera.x)
        screen_y = int(self.y - camera.y)
        
        # Fade out as lifetime decreases
        alpha = min(255, int(255 * (self.lifetime / max(1, self.max_lifetime))))
        
        # Different colors for different types
        if self.type == "rain":
            color = BLUE
        else:
            color = YELLOW
        
        # Draw with glow and fade
        glow_intensity = int(30 + 20 * math.sin(self.glow_timer * 0.2))
        glow_radius = self.radius + 4
        
        # Glow effect
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*color, min(alpha, glow_intensity)), 
                          (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (screen_x - glow_radius, screen_y - glow_radius))
        
        # Main candy
        pygame.draw.circle(screen, color, (screen_x, screen_y), self.radius)

class SpecialFeaturesManager:
    """Manages all special features and mini-games"""
    
    def __init__(self):
        self.church_puzzles: List[ChurchPuzzle] = []
        self.digging_sites: List[CemeteryDigging] = []
        self.traps: List[JackOLanternTrap] = []
        self.special_candies: List[SpecialCandy] = []
        
        self.active_puzzle: Optional[ChurchPuzzle] = None
        self.active_digging: Optional[CemeteryDigging] = None
        
    def add_church_puzzle(self, x: float, y: float):
        """Add a church puzzle"""
        puzzle = ChurchPuzzle(x, y)
        self.church_puzzles.append(puzzle)
    
    def add_digging_site(self, x: float, y: float):
        """Add a cemetery digging site"""
        site = CemeteryDigging(x, y)
        self.digging_sites.append(site)
    
    def add_trap(self, x: float, y: float):
        """Add a jack-o'-lantern trap"""
        trap = JackOLanternTrap(x, y)
        self.traps.append(trap)
    
    def update(self, player: Player, keys_pressed: pygame.key.ScancodeWrapper, 
               space_pressed: bool) -> Tuple[List[Particle], str]:
        """Update all special features"""
        particles = []
        message = ""
        
        # Update church puzzles
        if self.active_puzzle:
            completed, puzzle_particles = self.active_puzzle.handle_input(keys_pressed, space_pressed)
            particles.extend(puzzle_particles)
            
            if completed:
                player.score += 100
                player.heal(1)
                message = "Church puzzle solved! +100 points, +1 health!"
                self.active_puzzle = None
        
        # Update digging sites
        if self.active_digging:
            self.active_digging.update()
            
            if space_pressed:
                completed, dig_particles = self.active_digging.dig()
                particles.extend(dig_particles)
                
                if completed:
                    # Grant zombie power
                    zombie_particles = PowerUpGenerator.create_zombie_power(player)
                    particles.extend(zombie_particles)
                    message = "Found ancient relic! Zombie power activated!"
                    self.active_digging = None
        
        # Update traps
        for trap in self.traps[:]:  # Use slice copy to allow removal during iteration
            exploded, explosion_particles = trap.update(player)
            particles.extend(explosion_particles)
            
            if exploded:
                self.traps.remove(trap)
        
        # Update special candies
        for candy in self.special_candies[:]:
            candy.update()
            
            if candy.is_expired():
                self.special_candies.remove(candy)
        
        return particles, message
    
    def handle_interactions(self, player: Player) -> Tuple[List[Particle], str]:
        """Handle player interactions with special features"""
        particles = []
        message = ""
        
        # Check church puzzle interactions
        for puzzle in self.church_puzzles:
            if not puzzle.completed:
                success, puzzle_message, puzzle_particles = puzzle.interact(player)
                if success:
                    self.active_puzzle = puzzle
                    message = puzzle_message
                    particles.extend(puzzle_particles)
                    break
        
        # Check digging site interactions  
        for site in self.digging_sites:
            if not site.completed:
                success, dig_message, dig_particles = site.interact(player)
                if success:
                    self.active_digging = site
                    message = dig_message
                    particles.extend(dig_particles)
                    break
        
        # Check special candy collection
        for candy in self.special_candies:
            if not candy.collected:
                distance = math.sqrt((player.x - candy.x) ** 2 + (player.y - candy.y) ** 2)
                if distance <= 20:
                    candy_particles = candy.collect(player)
                    particles.extend(candy_particles)
        
        return particles, message
    
    def draw(self, screen: pygame.Surface):
        """Draw all special features"""
        # Draw church puzzles
        for puzzle in self.church_puzzles:
            puzzle.draw(screen)
        
        # Draw digging sites
        for site in self.digging_sites:
            site.draw(screen)
        
        # Draw traps
        for trap in self.traps:
            trap.draw(screen)
        
        # Draw special candies
        for candy in self.special_candies:
            candy.draw(screen)
    
    def spawn_candy_rain(self, player_x: float, player_y: float):
        """Spawn candy rain effect"""
        rain_candies = PowerUpGenerator.create_candy_rain(player_x, player_y)
        self.special_candies.extend(rain_candies)
    
    def freeze_ghosts(self, ghosts: List):
        """Apply ghost freeze effect"""
        return PowerUpGenerator.create_ghost_freeze(ghosts)