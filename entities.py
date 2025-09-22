"""
Core game entity classes for Halloween Haunt: Candy Quest
"""

import pygame
import math
import random
import os
from typing import List, Tuple, Optional
from halloween_haunt import (
    TILE_SIZE, PLAYER_MAX_SPEED, PLAYER_ACCELERATION, PLAYER_DECELERATION,
    GHOST_SPEED, GHOST_CHASE_SPEED, GHOST_DETECTION_RADIUS,
    PLAYER_MAX_HEALTH, INVINCIBILITY_DURATION,
    WHITE, BLACK, ORANGE, GRAY, RED, GREEN, BLUE, BROWN, DARK_GRAY, YELLOW, PURPLE,
    TileType, PowerUp, PowerUpType, Particle,
    asset_manager, camera
)

class Player:
    """Player character - young trick-or-treater in ghost costume"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.health = PLAYER_MAX_HEALTH
        self.candies_collected = 0
        self.score = 0
        self.invincible_timer = 0
        
        # Visual properties
        self.radius = 12
        self.facing_direction = 0  # radians
        
        # Power-ups
        self.active_powerups: List[PowerUp] = []
        
        # Initialize power-up states
        self.invisibility_active = False
        self.time_slow_active = False
        self.double_points_active = False
        self.shield_active = False
        
        # Load sprite with fallback
        self.sprite = asset_manager.load_image(
            "assets/sprites/player_ghost.png",
            WHITE,
            (24, 24)
        )
        
        # Create collision rect
        self.rect = pygame.Rect(x - self.radius, y - self.radius, 
                               self.radius * 2, self.radius * 2)
    
    def update(self, keys_pressed: pygame.key.ScancodeWrapper, tile_map: 'TileMap'):
        """Update player movement and state"""
        # Handle input for movement
        acceleration_x = 0.0
        acceleration_y = 0.0
        
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
            acceleration_x = -PLAYER_ACCELERATION
        if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            acceleration_x = PLAYER_ACCELERATION
        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
            acceleration_y = -PLAYER_ACCELERATION
        if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            acceleration_y = PLAYER_ACCELERATION
            

        
        # Apply acceleration
        self.vx += acceleration_x
        self.vy += acceleration_y
        
        # Apply deceleration when no input
        if acceleration_x == 0:
            self.vx *= (1.0 - PLAYER_DECELERATION)
        if acceleration_y == 0:
            self.vy *= (1.0 - PLAYER_DECELERATION)
        
        # Apply speed modifiers from power-ups
        speed_multiplier = 1.0
        invisibility_active = False
        time_slow_active = False
        double_points_active = False
        shield_active = False
        
        for powerup in self.active_powerups:
            if powerup.type == PowerUpType.SPEED_BOOST:
                speed_multiplier *= 1.5
            elif powerup.type == PowerUpType.INVISIBILITY:
                invisibility_active = True
            elif powerup.type == PowerUpType.TIME_SLOW:
                time_slow_active = True
            elif powerup.type == PowerUpType.DOUBLE_POINTS:
                double_points_active = True
            elif powerup.type == PowerUpType.SHIELD:
                shield_active = True
        
        # Store power-up states for external access
        self.invisibility_active = invisibility_active
        self.time_slow_active = time_slow_active
        self.double_points_active = double_points_active
        self.shield_active = shield_active
        
        # Limit maximum speed
        max_speed = PLAYER_MAX_SPEED * speed_multiplier
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if speed > max_speed:
            self.vx = (self.vx / speed) * max_speed
            self.vy = (self.vy / speed) * max_speed
        
        # Calculate new position
        new_x = self.x + self.vx
        new_y = self.y + self.vy
        
        # Check collision with walls
        if not self._check_wall_collision(new_x, self.y, tile_map):
            self.x = new_x
        else:
            self.vx = 0
            
        if not self._check_wall_collision(self.x, new_y, tile_map):
            self.y = new_y
        else:
            self.vy = 0
        
        # Update collision rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        # Update facing direction
        if abs(self.vx) > 0.1 or abs(self.vy) > 0.1:
            self.facing_direction = math.atan2(self.vy, self.vx)
        
        # Update invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        
        # Update power-ups
        self._update_powerups()
    
    def _check_wall_collision(self, x: float, y: float, tile_map: 'TileMap') -> bool:
        """Check if position would collide with walls"""
        # Get tile coordinates for player's corners
        corners = [
            (x - self.radius, y - self.radius),  # Top-left
            (x + self.radius, y - self.radius),  # Top-right
            (x - self.radius, y + self.radius),  # Bottom-left
            (x + self.radius, y + self.radius)   # Bottom-right
        ]
        
        for corner_x, corner_y in corners:
            tile_x = int(corner_x // TILE_SIZE)
            tile_y = int(corner_y // TILE_SIZE)
            
            if tile_map.is_solid_tile(tile_x, tile_y):
                return True
        
        return False
    
    def _update_powerups(self):
        """Update active power-up effects"""
        self.active_powerups = [p for p in self.active_powerups if p.duration > 0]
        for powerup in self.active_powerups:
            powerup.duration -= 1
    
    def take_damage(self) -> bool:
        """Take damage if not invincible and not shielded. Returns True if damage taken."""
        if self.invincible_timer <= 0 and not self.shield_active:
            self.health -= 1
            self.invincible_timer = INVINCIBILITY_DURATION
            return True
        return False
    
    def collect_candy(self, points: int = 10):
        """Collect a candy and add to counters"""
        # Apply double points power-up
        actual_points = points * (2 if self.double_points_active else 1)
        self.candies_collected += 1
        self.score += actual_points
    
    def add_powerup(self, powerup_type: PowerUpType, duration: int):
        """Add a power-up effect"""
        # Remove existing powerup of same type
        self.active_powerups = [p for p in self.active_powerups if p.type != powerup_type]
        
        # Add new powerup
        self.active_powerups.append(PowerUp(powerup_type, duration))
    
    def heal(self, amount: int = 1):
        """Heal the player"""
        self.health = min(5, self.health + amount)  # Max 5 hearts
    
    def draw(self, screen: pygame.Surface):
        """Draw the player with improved, non-square ghost design"""
        screen_x = int(self.x - camera.x)
        screen_y = int(self.y - camera.y)
        
        # Draw sprite or enhanced fallback ghost
        if False:  # Force fallback shapes for better visuals
            sprite_rect = self.sprite.get_rect(center=(screen_x, screen_y))
            screen.blit(self.sprite, sprite_rect)
        else:
            # Enhanced beautiful ghost design - much more rounded and fluid
            color = WHITE
            if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2:
                color = (200, 200, 255)  # Slight blue tint when invincible
            
            # Main ghost body - smooth, rounded shape (not square!)
            body_width = 18
            body_height = 22
            
            # Create a smooth elliptical body
            body_points = []
            num_points = 16
            for i in range(num_points):
                angle = (i / num_points) * 2 * math.pi
                # Elliptical shape with slight point at bottom
                if angle > math.pi * 0.8 and angle < math.pi * 1.2:  # Bottom area
                    radius_x = body_width * 0.7
                    radius_y = body_height * 0.8
                else:
                    radius_x = body_width
                    radius_y = body_height
                
                x_offset = radius_x * math.cos(angle)
                y_offset = radius_y * math.sin(angle)
                
                # Add slight wave to bottom for wavy edge
                if angle > math.pi * 0.7 and angle < math.pi * 1.3:
                    wave = 2 * math.sin(angle * 3)
                    y_offset += wave
                
                body_points.append((screen_x + x_offset, screen_y + y_offset))
            
            pygame.draw.polygon(screen, color, body_points)
            
            # Smooth outline
            pygame.draw.polygon(screen, BLACK, body_points, 1)
            
            # Large, expressive eyes (not tiny dots)
            eye_y = screen_y - 2
            eye_size = 4
            
            # Left eye with shine
            pygame.draw.circle(screen, BLACK, (screen_x - 6, eye_y), eye_size)
            pygame.draw.circle(screen, WHITE, (screen_x - 5, eye_y - 1), 2)  # Eye shine
            pygame.draw.circle(screen, (255, 255, 255, 150), (screen_x - 4, eye_y - 2), 1)  # Extra shine
            
            # Right eye with shine
            pygame.draw.circle(screen, BLACK, (screen_x + 6, eye_y), eye_size)
            pygame.draw.circle(screen, WHITE, (screen_x + 7, eye_y - 1), 2)  # Eye shine
            pygame.draw.circle(screen, (255, 255, 255, 150), (screen_x + 8, eye_y - 2), 1)  # Extra shine
            
            # Friendly mouth (not just a circle)
            mouth_center_y = screen_y + 4
            mouth_width = 8
            mouth_height = 3
            
            # Draw a gentle smile curve
            mouth_points = []
            for i in range(mouth_width + 1):
                x = screen_x - mouth_width//2 + i
                # Create a smile curve using sine wave
                smile_offset = math.sin((i / mouth_width) * math.pi) * mouth_height
                y = mouth_center_y + smile_offset
                mouth_points.append((x, y))
            
            pygame.draw.lines(screen, BLACK, False, mouth_points, 2)
            
            # Add power-up visual effects
            time_factor = pygame.time.get_ticks() * 0.001
            
            # Invisibility effect - semi-transparent with particles
            if self.invisibility_active:
                # Create invisibility particles
                for i in range(3):
                    angle = time_factor * 2 + i * math.pi * 2 / 3
                    radius = 25 + 5 * math.sin(time_factor * 3 + i)
                    particle_x = screen_x + int(radius * math.cos(angle))
                    particle_y = screen_y + int(radius * math.sin(angle) * 0.5)
                    particle_color = (200, 200, 255, 150)
                    pygame.draw.circle(screen, particle_color, (particle_x, particle_y), 2)
            
            # Time slow effect - clock-like particles
            if self.time_slow_active:
                # Create clock hand particles
                for i in range(4):
                    angle = time_factor * 0.5 + i * math.pi / 2
                    radius = 20
                    clock_x = screen_x + int(radius * math.cos(angle))
                    clock_y = screen_y + int(radius * math.sin(angle))
                    clock_color = (100, 200, 255, 180)
                    pygame.draw.circle(screen, clock_color, (clock_x, clock_y), 1)
            
            # Shield effect - protective aura
            if self.shield_active:
                # Create shield aura
                shield_radius = self.radius + 8 + 3 * math.sin(time_factor * 4)
                shield_color = (100, 200, 255, 100)
                pygame.draw.circle(screen, shield_color, (screen_x, screen_y), int(shield_radius), 2)
                # Add shield sparkles
                for i in range(6):
                    angle = time_factor * 3 + i * math.pi / 3
                    sparkle_radius = self.radius + 6
                    sparkle_x = screen_x + int(sparkle_radius * math.cos(angle))
                    sparkle_y = screen_y + int(sparkle_radius * math.sin(angle))
                    pygame.draw.circle(screen, (150, 220, 255), (sparkle_x, sparkle_y), 1)
            
            # Add subtle shadow under the ghost
            shadow_color = (0, 0, 0, 50)
            shadow_surface = pygame.Surface((body_width * 2, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, shadow_color, (0, 0, body_width * 2, 8))
            screen.blit(shadow_surface, (screen_x - body_width, screen_y + body_height - 2))

class Ghost:
    """Enemy ghost that patrols and chases the player"""
    
    def __init__(self, x: float, y: float, patrol_points: List[Tuple[float, float]] = None):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.vx = 0.0
        self.vy = 0.0
        
        # AI behavior
        self.state = "patrol"  # "patrol", "chase", "return"
        self.patrol_points = patrol_points or [(x, y)]
        self.current_patrol_target = 0
        self.chase_timer = 0
        
        # Visual properties
        self.radius = 10
        self.alpha = 180  # Semi-transparent
        
        # Load sprite with fallback
        self.sprite = asset_manager.load_image(
            "assets/sprites/ghost_enemy.png",
            GRAY,
            (20, 20)
        )
        
        # Create collision rect
        self.rect = pygame.Rect(x - self.radius, y - self.radius,
                               self.radius * 2, self.radius * 2)
    
    def update(self, player: Player, tile_map: 'TileMap'):
        """Update ghost AI and movement"""
        # Store player reference for movement methods
        self._player_ref = player
        
        # Check if player is nearby for chasing
        distance_to_player = math.sqrt(
            (self.x - player.x) ** 2 + (self.y - player.y) ** 2
        )
        
        # State management (respect player power-ups)
        started_chasing = False
        if self.state == "patrol":
            # Don't detect invisible player
            if distance_to_player <= GHOST_DETECTION_RADIUS and not player.invisibility_active:
                self.state = "chase"
                self.chase_timer = 300  # 5 seconds at 60 FPS
                started_chasing = True
        elif self.state == "chase":
            self.chase_timer -= 1
            if self.chase_timer <= 0 or distance_to_player > GHOST_DETECTION_RADIUS * 1.5:
                self.state = "return"
        elif self.state == "return":
            distance_to_start = math.sqrt(
                (self.x - self.start_x) ** 2 + (self.y - self.start_y) ** 2
            )
            if distance_to_start < 20:
                self.state = "patrol"
        
        # Movement based on state
        if self.state == "chase":
            self._chase_player(player)
        elif self.state == "return":
            self._return_to_start()
        else:
            self._patrol()
        
        # Apply movement
        new_x = self.x + self.vx
        new_y = self.y + self.vy
        
        # Simple collision check (ghosts can pass through some obstacles)
        if not self._check_wall_collision(new_x, self.y, tile_map):
            self.x = new_x
        if not self._check_wall_collision(self.x, new_y, tile_map):
            self.y = new_y
        
        # Update collision rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        return started_chasing
    
    def _chase_player(self, player: Player):
        """Chase the player"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        
        if distance > 0:
            speed = GHOST_CHASE_SPEED
            # Apply time slow effect
            if player.time_slow_active:
                speed *= 0.4  # Slow down to 40% speed
            
            self.vx = (dx / distance) * speed
            self.vy = (dy / distance) * speed
    
    def _return_to_start(self):
        """Return to starting position"""
        dx = self.start_x - self.x
        dy = self.start_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        
        if distance > 0:
            speed = GHOST_SPEED
            # Apply time slow effect
            if self._player_ref and self._player_ref.time_slow_active:
                speed *= 0.4  # Slow down to 40% speed
            
            self.vx = (dx / distance) * speed
            self.vy = (dy / distance) * speed
        else:
            self.vx = 0
            self.vy = 0
    
    def _patrol(self):
        """Patrol between waypoints"""
        if not self.patrol_points:
            self.vx = 0
            self.vy = 0
            return
        
        target_x, target_y = self.patrol_points[self.current_patrol_target]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        
        if distance < 10:
            # Reached patrol point, move to next
            self.current_patrol_target = (self.current_patrol_target + 1) % len(self.patrol_points)
        else:
            # Move toward current patrol point
            speed = GHOST_SPEED
            # Apply time slow effect
            if hasattr(self, '_player_ref') and self._player_ref and self._player_ref.time_slow_active:
                speed *= 0.4  # Slow down to 40% speed
            
            self.vx = (dx / distance) * speed
            self.vy = (dy / distance) * speed
    
    def _check_wall_collision(self, x: float, y: float, tile_map: 'TileMap') -> bool:
        """Check collision with solid walls"""
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        return tile_map.is_solid_tile(tile_x, tile_y)
    
    def draw(self, screen: pygame.Surface):
        """Draw the ghost with improved, menacing design"""
        screen_x = int(self.x - camera.x)
        screen_y = int(self.y - camera.y)
        
        # Draw sprite with transparency or enhanced spooky ghost
        if False:  # Force fallback shapes for better visuals
            # Apply transparency to sprite
            temp_surface = self.sprite.copy()
            temp_surface.set_alpha(self.alpha)
            sprite_rect = temp_surface.get_rect(center=(screen_x, screen_y))
            screen.blit(temp_surface, sprite_rect)
        else:
            # Enhanced spooky enemy ghost design - more fluid and terrifying
            ghost_color = (100, 100, 150) if self.state != "chase" else (150, 80, 80)
            outline_color = (50, 50, 100) if self.state != "chase" else (100, 40, 40)
            
            # Create ghost surface with transparency
            ghost_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            
            # Main ghost body - smooth, flowing shape (not blocky!)
            body_width = self.radius * 1.8
            body_height = self.radius * 2.2
            
            # Create flowing body shape using ellipse with distortion
            body_points = []
            num_points = 20
            for i in range(num_points):
                angle = (i / num_points) * 2 * math.pi
                
                # Create irregular, flowing shape
                radius_x = body_width * (0.8 + 0.3 * math.sin(angle * 2))
                radius_y = body_height * (0.9 + 0.2 * math.cos(angle * 3))
                
                # Add more distortion for bottom wavy edge
                if angle > math.pi * 0.6 and angle < math.pi * 1.4:
                    wave_distortion = 0.4 * math.sin(angle * 4 + pygame.time.get_ticks() * 0.01)
                    radius_y *= (1 + wave_distortion)
                
                x_offset = radius_x * math.cos(angle)
                y_offset = radius_y * math.sin(angle)
                
                body_points.append((self.radius * 1.5 + x_offset, self.radius * 1.5 + y_offset))
            
            pygame.draw.polygon(ghost_surface, (*ghost_color, self.alpha), body_points)
            
            # Add flowing outline
            pygame.draw.polygon(ghost_surface, (*outline_color, self.alpha), body_points, 2)
            
            # Menacing eyes that glow when chasing
            eye_y = self.radius * 1.5 - 3
            eye_size = 3 if self.state != "chase" else 4
            
            if self.state == "chase":
                # Glowing red eyes when chasing
                eye_color = (255, 50, 50)
                glow_color = (255, 100, 100, 150)
                
                # Eye glow effect
                for eye_offset in [-5, 5]:
                    pygame.draw.circle(ghost_surface, glow_color, 
                                     (int(self.radius * 1.5 + eye_offset), int(eye_y)), eye_size + 2)
            else:
                eye_color = (200, 200, 255)
            
            # Left eye
            pygame.draw.circle(ghost_surface, eye_color, 
                             (int(self.radius * 1.5 - 5), int(eye_y)), eye_size)
            # Right eye  
            pygame.draw.circle(ghost_surface, eye_color, 
                             (int(self.radius * 1.5 + 5), int(eye_y)), eye_size)
            
            # Frown mouth (scary!)
            mouth_y = self.radius * 1.5 + 4
            mouth_width = 6
            
            # Create a frown curve
            frown_points = []
            for i in range(mouth_width + 1):
                x = self.radius * 1.5 - mouth_width//2 + i
                # Create a frown using inverted sine wave
                frown_offset = -math.sin((i / mouth_width) * math.pi) * 2
                y = mouth_y + frown_offset
                frown_points.append((x, y))
            
            pygame.draw.lines(ghost_surface, (50, 50, 50, self.alpha), False, frown_points, 2)
            
            # Add wispy trailing effects when moving
            if abs(self.vx) > 0.5 or abs(self.vy) > 0.5:
                trail_alpha = int(self.alpha * 0.6)
                for i in range(4):
                    trail_offset = 6 + i * 3
                    trail_x = self.radius * 1.5 - int(self.vx * trail_offset * 1.5)
                    trail_y = self.radius * 1.5 - int(self.vy * trail_offset * 1.5)
                    
                    # Create smaller trailing ghost shapes
                    trail_size = self.radius - i
                    if trail_size > 0:
                        pygame.draw.circle(ghost_surface, (*ghost_color, trail_alpha // (i + 1)), 
                                         (trail_x, trail_y), trail_size)
            
            # Add pulsing effect when chasing
            if self.state == "chase":
                pulse = math.sin(pygame.time.get_ticks() * 0.02) * 0.1 + 0.9
                scaled_surface = pygame.transform.scale(ghost_surface, 
                    (int(ghost_surface.get_width() * pulse), int(ghost_surface.get_height() * pulse)))
                scaled_rect = scaled_surface.get_rect(center=(screen_x, screen_y))
                screen.blit(scaled_surface, scaled_rect)
            else:
                screen.blit(ghost_surface, (screen_x - self.radius * 1.5, screen_y - self.radius * 1.5))

class Candy:
    """Collectible candy scattered around the map"""
    
    def __init__(self, x: float, y: float, candy_type: str = "normal", points: int = 10):
        self.x = x
        self.y = y
        self.type = candy_type  # "normal", "cursed", "bonus"
        self.points = points
        self.collected = False
        
        # Visual properties
        self.radius = 6
        self.glow_timer = 0
        
        # Load sprite with fallback
        sprite_path = "assets/sprites/candy.png"
        if candy_type == "cursed":
            sprite_path = "assets/sprites/candy_cursed.png"
        elif candy_type == "bonus":
            sprite_path = "assets/sprites/candy_bonus.png"
        
        fallback_color = ORANGE
        if candy_type == "cursed":
            fallback_color = (255, 100, 0)  # Dark orange with red tint
        elif candy_type == "bonus":
            fallback_color = YELLOW
        
        self.sprite = asset_manager.load_image(sprite_path, fallback_color, (12, 12))
        
        # Create collision rect
        self.rect = pygame.Rect(x - self.radius, y - self.radius,
                               self.radius * 2, self.radius * 2)
    
    def update(self):
        """Update candy animation"""
        self.glow_timer += 1
    
    def collect(self, player: Player) -> List[Particle]:
        """Collect this candy and apply effects"""
        particles = []
        
        if not self.collected:
            self.collected = True
            player.collect_candy(self.points)
            
            # Apply special effects based on type
            if self.type == "cursed":
                # Cursed candy: halve speed for 5 seconds
                player.add_powerup(PowerUpType.SPEED_BOOST, 300)  # Negative effect
            elif self.type == "bonus":
                # Bonus candy: extra points and small heal
                player.score += self.points  # Double points
                player.heal(1)
            
            # Create pickup particles
            for _ in range(8):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 3)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                particles.append(Particle(
                    self.x, self.y, vx, vy, YELLOW, 30
                ))
        
        return particles
    
    def draw(self, screen: pygame.Surface):
        """Draw the candy with glow effect"""
        if self.collected:
            return
        
        screen_x = int(self.x - camera.x)
        screen_y = int(self.y - camera.y)
        
        # Draw glow effect
        glow_intensity = int(50 + 30 * math.sin(self.glow_timer * 0.1))
        glow_color = ORANGE
        if self.type == "cursed":
            glow_color = RED
        elif self.type == "bonus":
            glow_color = YELLOW
        
        glow_radius = self.radius + 3
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*glow_color, glow_intensity), 
                          (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (screen_x - glow_radius, screen_y - glow_radius))
        
        # Draw sprite or detailed Halloween candy
        if False:  # Force fallback shapes for better visuals
            sprite_rect = self.sprite.get_rect(center=(screen_x, screen_y))
            screen.blit(self.sprite, sprite_rect)
        else:
            # Detailed Halloween candy designs
            if self.type == "cursed":
                # Cursed candy: dark skull-shaped
                pygame.draw.circle(screen, (100, 0, 50), (screen_x, screen_y), self.radius)
                pygame.draw.circle(screen, (150, 0, 0), (screen_x, screen_y), self.radius - 1)
                # Skull eyes
                pygame.draw.circle(screen, BLACK, (screen_x - 2, screen_y - 1), 1)
                pygame.draw.circle(screen, BLACK, (screen_x + 2, screen_y - 1), 1)
                # Skull mouth
                pygame.draw.rect(screen, BLACK, (screen_x - 1, screen_y + 1, 2, 1))
                
            elif self.type == "bonus":
                # Bonus candy: golden star
                star_points = []
                for i in range(10):
                    angle = i * math.pi / 5
                    radius = self.radius if i % 2 == 0 else self.radius // 2
                    x = screen_x + radius * math.cos(angle - math.pi / 2)
                    y = screen_y + radius * math.sin(angle - math.pi / 2)
                    star_points.append((x, y))
                pygame.draw.polygon(screen, YELLOW, star_points)
                pygame.draw.polygon(screen, (255, 255, 150), star_points, 1)
                # Center gem
                pygame.draw.circle(screen, WHITE, (screen_x, screen_y), 2)
                
            else:
                # Normal candy: pumpkin design
                pygame.draw.circle(screen, ORANGE, (screen_x, screen_y), self.radius)
                pygame.draw.circle(screen, (255, 165, 0), (screen_x, screen_y), self.radius - 1)
                # Pumpkin ridges
                for i in range(3):
                    ridge_x = screen_x - 3 + i * 3
                    pygame.draw.line(screen, (200, 120, 0), 
                                   (ridge_x, screen_y - self.radius + 2),
                                   (ridge_x, screen_y + self.radius - 2), 1)
                # Stem
                pygame.draw.rect(screen, (0, 100, 0), 
                               (screen_x - 1, screen_y - self.radius - 2, 2, 3))
                # Jack-o'-lantern face
                if self.glow_timer % 60 < 30:  # Blinking effect
                    pygame.draw.circle(screen, BLACK, (screen_x - 2, screen_y - 1), 1)
                    pygame.draw.circle(screen, BLACK, (screen_x + 2, screen_y - 1), 1)
                    # Smile
                    smile_points = [(screen_x - 2, screen_y + 2), (screen_x, screen_y + 3), (screen_x + 2, screen_y + 2)]
                    pygame.draw.lines(screen, BLACK, False, smile_points, 1)

class TileMap:
    """Manages the tile-based game map"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles = [[TileType.EMPTY for _ in range(width)] for _ in range(height)]
        
        # Load tile sprites with detailed fallbacks
        self.tile_sprites = {}
        self._create_tile_sprites()
    
    def _create_tile_sprites(self):
        """Create detailed tile sprites with artistic fallbacks"""
        
        # Try loading assets first, create detailed fallbacks if not found
        for tile_type in TileType:
            sprite_path = f"assets/tiles/{tile_type.name.lower()}.png"
            
            # Try to load actual sprite first
            try:
                if os.path.exists(sprite_path):
                    sprite = pygame.image.load(sprite_path).convert_alpha()
                    sprite = pygame.transform.scale(sprite, (TILE_SIZE, TILE_SIZE))
                    self.tile_sprites[tile_type] = sprite
                    continue
            except:
                pass
            
            # Create detailed fallback sprites
            sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            
            if tile_type == TileType.EMPTY:
                # Grass with small details
                sprite.fill((0, 80, 0))
                for i in range(8):
                    x = random.randint(2, TILE_SIZE - 3)
                    y = random.randint(2, TILE_SIZE - 3)
                    pygame.draw.circle(sprite, (0, 100, 0), (x, y), 1)
            
            elif tile_type == TileType.STREET:
                # Asphalt with cracks
                sprite.fill((40, 40, 40))
                pygame.draw.line(sprite, (30, 30, 30), (0, TILE_SIZE//2), (TILE_SIZE, TILE_SIZE//2), 1)
                for i in range(3):
                    x = random.randint(5, TILE_SIZE - 5)
                    y = random.randint(5, TILE_SIZE - 5)
                    pygame.draw.line(sprite, (50, 50, 50), (x-2, y), (x+2, y), 1)
            
            elif tile_type == TileType.WALL:
                # Stone brick wall
                sprite.fill((100, 100, 100))
                for row in range(2):
                    for col in range(2):
                        brick_x = col * (TILE_SIZE // 2)
                        brick_y = row * (TILE_SIZE // 2)
                        pygame.draw.rect(sprite, (120, 120, 120), 
                                       (brick_x, brick_y, TILE_SIZE//2 - 1, TILE_SIZE//2 - 1))
                        pygame.draw.rect(sprite, (80, 80, 80), 
                                       (brick_x, brick_y, TILE_SIZE//2 - 1, TILE_SIZE//2 - 1), 1)
            
            elif tile_type == TileType.HOUSE:
                # House with roof and door
                sprite.fill((80, 50, 30))  # Brown walls
                # Roof
                pygame.draw.polygon(sprite, (60, 30, 10), 
                                  [(0, TILE_SIZE//3), (TILE_SIZE//2, 0), (TILE_SIZE, TILE_SIZE//3)])
                # Door
                pygame.draw.rect(sprite, (40, 20, 10), 
                               (TILE_SIZE//3, TILE_SIZE//2, TILE_SIZE//3, TILE_SIZE//2))
                # Window
                pygame.draw.rect(sprite, YELLOW, (TILE_SIZE//6, TILE_SIZE//3, 6, 6))
            
            elif tile_type == TileType.CHURCH:
                # Gothic church
                sprite.fill((60, 60, 80))
                # Spire
                pygame.draw.polygon(sprite, (40, 40, 60), 
                                  [(TILE_SIZE//2 - 4, TILE_SIZE//4), (TILE_SIZE//2, 0), 
                                   (TILE_SIZE//2 + 4, TILE_SIZE//4)])
                # Cross
                pygame.draw.line(sprite, WHITE, (TILE_SIZE//2, 2), (TILE_SIZE//2, 8), 1)
                pygame.draw.line(sprite, WHITE, (TILE_SIZE//2 - 2, 4), (TILE_SIZE//2 + 2, 4), 1)
            
            elif tile_type == TileType.GRAVE:
                # Tombstone
                sprite.fill((0, 80, 0))  # Grass base
                # Stone
                pygame.draw.rect(sprite, (120, 120, 120), 
                               (TILE_SIZE//4, TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2))
                pygame.draw.circle(sprite, (120, 120, 120), 
                                 (TILE_SIZE//2, TILE_SIZE//4), TILE_SIZE//4)
                # RIP text
                pygame.draw.line(sprite, BLACK, (TILE_SIZE//2 - 4, TILE_SIZE//3), 
                               (TILE_SIZE//2 + 4, TILE_SIZE//3), 1)
            
            elif tile_type == TileType.TREE:
                # Spooky tree
                sprite.fill((0, 80, 0))  # Grass base
                # Trunk
                pygame.draw.rect(sprite, (60, 40, 20), 
                               (TILE_SIZE//2 - 3, TILE_SIZE//2, 6, TILE_SIZE//2))
                # Branches
                for i in range(4):
                    angle = i * math.pi / 2
                    end_x = TILE_SIZE//2 + 8 * math.cos(angle)
                    end_y = TILE_SIZE//3 + 8 * math.sin(angle)
                    pygame.draw.line(sprite, (40, 25, 15), 
                                   (TILE_SIZE//2, TILE_SIZE//3), (int(end_x), int(end_y)), 2)
            
            elif tile_type == TileType.DOOR:
                # Wooden door
                sprite.fill((100, 60, 30))
                pygame.draw.rect(sprite, (80, 40, 20), (2, 2, TILE_SIZE-4, TILE_SIZE-4), 2)
                # Handle
                pygame.draw.circle(sprite, YELLOW, (TILE_SIZE - 8, TILE_SIZE//2), 2)
            
            elif tile_type == TileType.CHURCH_DOOR:
                # Gothic door
                sprite.fill((40, 20, 60))
                # Arch
                pygame.draw.arc(sprite, (60, 40, 80), (4, 4, TILE_SIZE-8, TILE_SIZE-8), 
                              0, math.pi, 3)
                pygame.draw.rect(sprite, (60, 40, 80), (8, TILE_SIZE//2, TILE_SIZE-16, TILE_SIZE//2))
            
            elif tile_type == TileType.CEMETERY_GATE:
                # Iron gate
                sprite.fill((0, 80, 0))  # Grass base
                for i in range(4):
                    x = 4 + i * 6
                    pygame.draw.line(sprite, BLACK, (x, 4), (x, TILE_SIZE - 4), 2)
                # Top spikes
                for i in range(4):
                    x = 4 + i * 6
                    pygame.draw.polygon(sprite, BLACK, [(x-2, 8), (x, 4), (x+2, 8)])
            
            elif tile_type == TileType.TRASH_CAN:
                # Metal trash can
                sprite.fill((0, 80, 0))  # Grass base
                pygame.draw.rect(sprite, (100, 100, 100), 
                               (TILE_SIZE//4, TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2))
                pygame.draw.ellipse(sprite, (120, 120, 120), 
                                  (TILE_SIZE//4, TILE_SIZE//4, TILE_SIZE//2, 8))
                # Handles
                pygame.draw.circle(sprite, (80, 80, 80), (TILE_SIZE//4, TILE_SIZE//2), 2)
                pygame.draw.circle(sprite, (80, 80, 80), (3*TILE_SIZE//4, TILE_SIZE//2), 2)
            
            self.tile_sprites[tile_type] = sprite
    
    def set_tile(self, x: int, y: int, tile_type: TileType):
        """Set a tile at the given coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile_type
    
    def get_tile(self, x: int, y: int) -> TileType:
        """Get the tile type at given coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return TileType.WALL  # Out of bounds is considered wall
    
    def is_solid_tile(self, x: int, y: int) -> bool:
        """Check if a tile blocks movement"""
        tile = self.get_tile(x, y)
        solid_tiles = {
            TileType.WALL, TileType.HOUSE, TileType.CHURCH, 
            TileType.GRAVE, TileType.TREE, TileType.TRASH_CAN
        }
        return tile in solid_tiles
    
    def is_door_tile(self, x: int, y: int) -> bool:
        """Check if a tile is a door (for level completion/transitions)"""
        tile = self.get_tile(x, y)
        return tile in {TileType.DOOR, TileType.CHURCH_DOOR, TileType.CEMETERY_GATE}
    
    def draw(self, screen: pygame.Surface, highlight_house: bool = False, house_pos: Tuple[int, int] = None):
        """Draw the visible portion of the tile map"""
        # Calculate visible tile range
        start_x = max(0, int(camera.x // TILE_SIZE) - 1)
        end_x = min(self.width, int((camera.x + screen.get_width()) // TILE_SIZE) + 2)
        start_y = max(0, int(camera.y // TILE_SIZE) - 1)
        end_y = min(self.height, int((camera.y + screen.get_height()) // TILE_SIZE) + 2)
        
        # Draw visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.tiles[y][x]
                sprite = self.tile_sprites.get(tile_type, self.tile_sprites[TileType.EMPTY])
                
                screen_x = x * TILE_SIZE - camera.x
                screen_y = y * TILE_SIZE - camera.y
                
                screen.blit(sprite, (screen_x, screen_y))
                
                # Add special highlighting for house destination
                if highlight_house and house_pos and x == house_pos[0] // TILE_SIZE and y == house_pos[1] // TILE_SIZE:
                    # Draw glowing destination marker
                    time_factor = pygame.time.get_ticks() * 0.005
                    glow_intensity = int(100 + 50 * math.sin(time_factor))
                    
                    # Pulsing glow around house
                    glow_surface = pygame.Surface((TILE_SIZE + 20, TILE_SIZE + 20), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, (255, 255, 0, glow_intensity), 
                                   (0, 0, TILE_SIZE + 20, TILE_SIZE + 20), border_radius=10)
                    screen.blit(glow_surface, (screen_x - 10, screen_y - 10))
                    
                    # "HOME" text above house
                    font = asset_manager.load_font("assets/fonts/creepy.ttf", 16)
                    home_text = font.render("HOME", True, YELLOW)
                    text_rect = home_text.get_rect(center=(screen_x + TILE_SIZE//2, screen_y - 10))
                    
                    # Text background
                    bg_rect = pygame.Rect(text_rect.x - 5, text_rect.y - 2, text_rect.width + 10, text_rect.height + 4)
                    pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
                    
                    screen.blit(home_text, text_rect)

class EasterEgg:
    """Hidden collectible with special rewards"""
    
    def __init__(self, x: float, y: float, egg_type: str, reward: str):
        self.x = x
        self.y = y
        self.type = egg_type  # "stash", "puzzle", "dig", "secret"
        self.reward = reward  # Description of reward
        self.activated = False
        self.interaction_radius = 20
        
        # Visual properties
        self.visible = egg_type != "secret"  # Secret eggs are invisible until found
        self.glow_timer = 0
        
        # Create collision rect
        self.rect = pygame.Rect(x - 10, y - 10, 20, 20)
    
    def update(self):
        """Update Easter egg animation"""
        self.glow_timer += 1
    
    def interact(self, player: Player) -> Tuple[bool, str, List[Particle]]:
        """Attempt to interact with Easter egg. Returns (success, message, particles)"""
        particles = []
        
        if self.activated:
            return False, "Already found!", []
        
        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        if distance > self.interaction_radius:
            return False, "Get closer!", []
        
        self.activated = True
        self.visible = True
        
        # Apply reward
        message = f"Found Easter egg: {self.reward}!"
        
        if "health" in self.reward.lower():
            player.heal(1)
        elif "magnet" in self.reward.lower():
            player.add_powerup(PowerUpType.CANDY_MAGNET, 600)  # 10 seconds
        elif "repel" in self.reward.lower():
            player.add_powerup(PowerUpType.GHOST_REPEL, 900)  # 15 seconds
        elif "speed" in self.reward.lower():
            player.add_powerup(PowerUpType.SPEED_BOOST, 420)  # 7 seconds
        elif "invisibility" in self.reward.lower():
            player.add_powerup(PowerUpType.INVISIBILITY, 720)  # 12 seconds
        elif "time slow" in self.reward.lower():
            player.add_powerup(PowerUpType.TIME_SLOW, 480)  # 8 seconds
        elif "double points" in self.reward.lower():
            player.add_powerup(PowerUpType.DOUBLE_POINTS, 600)  # 10 seconds
        elif "shield" in self.reward.lower():
            player.add_powerup(PowerUpType.SHIELD, 900)  # 15 seconds
        elif "points" in self.reward.lower():
            player.score += 25
        
        # Create celebration particles
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice([YELLOW, ORANGE, RED, GREEN])
            particles.append(Particle(self.x, self.y, vx, vy, color, 60))
        
        return True, message, particles
    
    def draw(self, screen: pygame.Surface):
        """Draw the Easter egg if visible"""
        if not self.visible or self.activated:
            return
        
        screen_x = int(self.x - camera.x)
        screen_y = int(self.y - camera.y)
        
        # Draw glowing effect
        glow_intensity = int(80 + 40 * math.sin(self.glow_timer * 0.15))
        glow_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*PURPLE, glow_intensity), (15, 15), 12)
        screen.blit(glow_surface, (screen_x - 15, screen_y - 15))
        
        # Draw egg shape
        pygame.draw.ellipse(screen, PURPLE, (screen_x - 8, screen_y - 10, 16, 20))
        pygame.draw.ellipse(screen, YELLOW, (screen_x - 6, screen_y - 8, 12, 16))