"""
User Interface system for Halloween Haunt: Candy Quest
Includes menus, HUD, tutorial overlays, and game screens
"""

import pygame
import math
import random
from typing import List, Tuple, Optional, Callable
from halloween_haunt import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CANDIES_TO_COLLECT,
    WHITE, BLACK, ORANGE, RED, GREEN, BLUE, GRAY, DARK_GRAY, YELLOW,
    TRANSPARENT_GRAY, GameState, asset_manager
)

class Button:
    """Interactive button for menus"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 font: pygame.font.Font, callback: Optional[Callable] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.callback = callback
        self.hovered = False
        self.pressed = False
        
        # Colors
        self.normal_color = DARK_GRAY
        self.hover_color = GRAY
        self.press_color = BLACK
        self.text_color = WHITE
        
    def update(self, mouse_pos: Tuple[int, int], mouse_pressed: bool):
        """Update button state based on mouse input"""
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        if self.hovered and mouse_pressed:
            self.pressed = True
        elif self.pressed and not mouse_pressed:
            # Button was released while hovered - trigger callback
            if self.hovered and self.callback:
                self.callback()
            self.pressed = False
    
    def draw(self, screen: pygame.Surface):
        """Draw the button"""
        # Choose color based on state
        if self.pressed:
            color = self.press_color
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.normal_color
        
        # Draw button background
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)  # Border
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class Menu:
    """Base class for menu screens"""
    
    def __init__(self):
        self.buttons: List[Button] = []
        self.background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._create_background()
    
    def _create_background(self):
        """Create the background surface"""
        # Default gradient background
        for y in range(SCREEN_HEIGHT):
            color_intensity = int(20 + 30 * (y / SCREEN_HEIGHT))
            color = (color_intensity, color_intensity // 2, color_intensity)
            pygame.draw.line(self.background_surface, color, (0, y), (SCREEN_WIDTH, y))
    
    def add_button(self, x: int, y: int, width: int, height: int, text: str, callback: Callable):
        """Add a button to the menu"""
        font = asset_manager.load_font("assets/fonts/creepy.ttf", 24)
        button = Button(x, y, width, height, text, font, callback)
        self.buttons.append(button)
    
    def update(self, mouse_pos: Tuple[int, int], mouse_pressed: bool):
        """Update menu state"""
        for button in self.buttons:
            button.update(mouse_pos, mouse_pressed)
    
    def draw(self, screen: pygame.Surface):
        """Draw the menu"""
        screen.blit(self.background_surface, (0, 0))
        
        for button in self.buttons:
            button.draw(screen)

class MainMenu(Menu):
    """Main menu screen"""
    
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        
        # Create spooky background
        self._create_spooky_background()
        
        # Title
        self.title_font = asset_manager.load_font("assets/fonts/creepy.ttf", 50)
        
        # Add buttons
        button_width = 200
        button_height = 50
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = SCREEN_HEIGHT // 2
        
        self.add_button(center_x, start_y, button_width, button_height, 
                       "Start New Game", self._start_new_game)
        self.add_button(center_x, start_y + 60, button_width, button_height, 
                       "Load Game", self._load_game)
        self.add_button(center_x, start_y + 120, button_width, button_height, 
                       "Settings", self._show_settings)
        self.add_button(center_x, start_y + 180, button_width, button_height, 
                       "Quit", self._quit_game)
    
    def _create_spooky_background(self):
        """Create enhanced Halloween-themed background with animations"""
        # Animated gradient background
        time_factor = pygame.time.get_ticks() * 0.001
        
        for y in range(SCREEN_HEIGHT):
            # Create pulsing, swirling colors
            red_intensity = int(15 + 25 * math.sin(time_factor + y * 0.01) + 10 * math.sin(time_factor * 0.7))
            green_intensity = int(5 + 15 * math.sin(time_factor * 0.8 + y * 0.015))
            blue_intensity = int(20 + 30 * math.sin(time_factor * 1.2 + y * 0.008))
            
            color = (max(0, min(255, red_intensity)), 
                    max(0, min(255, green_intensity)), 
                    max(0, min(255, blue_intensity)))
            pygame.draw.line(self.background_surface, color, (0, y), (SCREEN_WIDTH, y))
        
        # Add floating ghostly orbs
        for i in range(8):
            angle = time_factor * 0.5 + i * math.pi / 4
            radius = 80 + 40 * math.sin(time_factor * 0.3 + i)
            x = SCREEN_WIDTH // 2 + int(radius * math.cos(angle))
            y = SCREEN_HEIGHT // 2 + int(radius * math.sin(angle) * 0.5)
            
            # Create glowing orb
            orb_color = (200, 200, 255, 100)
            pygame.draw.circle(self.background_surface, orb_color, (x, y), 15)
            pygame.draw.circle(self.background_surface, (255, 255, 255, 50), (x, y), 8)
        
        # Add animated bats flying across the screen
        for i in range(3):
            bat_x = ((pygame.time.get_ticks() * 0.1 + i * 200) % (SCREEN_WIDTH + 100)) - 50
            bat_y = 100 + i * 80 + int(20 * math.sin(time_factor * 2 + i))
            
            # Simple bat shape
            bat_points = [
                (bat_x, bat_y),
                (bat_x - 8, bat_y - 5),
                (bat_x - 15, bat_y + 2),
                (bat_x - 8, bat_y + 8),
                (bat_x, bat_y + 5),
                (bat_x + 8, bat_y + 8),
                (bat_x + 15, bat_y + 2),
                (bat_x + 8, bat_y - 5)
            ]
            pygame.draw.polygon(self.background_surface, (30, 30, 30), bat_points)
        
        # Add flickering candles/torches on the sides
        for side in [-1, 1]:
            torch_x = SCREEN_WIDTH // 2 + side * (SCREEN_WIDTH // 3)
            torch_y = SCREEN_HEIGHT - 100
            
            # Torch pole
            pygame.draw.line(self.background_surface, (60, 30, 10), 
                           (torch_x, torch_y), (torch_x, torch_y - 40), 3)
            
            # Flickering flame
            flicker = math.sin(time_factor * 10 + side * 3) * 0.3 + 0.7
            flame_size = int(8 * flicker)
            
            flame_colors = [(255, 100, 0), (255, 150, 0), (255, 200, 0)]
            for j, color in enumerate(flame_colors):
                pygame.draw.circle(self.background_surface, color, 
                                 (torch_x, torch_y - 45 - j * 2), flame_size - j * 2)
        
        # Add some floating pumpkins
        for i in range(4):
            pumpkin_x = 100 + i * 150
            pumpkin_y = SCREEN_HEIGHT - 80 + int(10 * math.sin(time_factor + i))
            
            # Pumpkin body
            pygame.draw.ellipse(self.background_surface, ORANGE, 
                              (pumpkin_x - 15, pumpkin_y - 10, 30, 20))
            
            # Pumpkin face
            face_y = pumpkin_y - 5
            pygame.draw.circle(self.background_surface, BLACK, (pumpkin_x - 8, face_y), 2)
            pygame.draw.circle(self.background_surface, BLACK, (pumpkin_x + 8, face_y), 2)
            
            # Jagged mouth
            mouth_points = [
                (pumpkin_x - 5, face_y + 5),
                (pumpkin_x - 2, face_y + 8),
                (pumpkin_x, face_y + 6),
                (pumpkin_x + 2, face_y + 8),
                (pumpkin_x + 5, face_y + 5)
            ]
            pygame.draw.lines(self.background_surface, BLACK, False, mouth_points, 2)
    
    def _start_new_game(self):
        """Start a new game"""
        self.game_manager.start_new_game()
    
    def _load_game(self):
        """Load saved game"""
        self.game_manager.load_game()
    
    def _show_settings(self):
        """Show settings menu"""
        self.game_manager.show_settings()
    
    def _quit_game(self):
        """Quit the game"""
        self.game_manager.quit_game()
    
    def draw(self, screen: pygame.Surface):
        """Draw the main menu with enhanced visual effects"""
        super().draw(screen)

        # Get time for animations
        time_factor = pygame.time.get_ticks() * 0.001

        # Draw animated title with enhanced glow
        title_text = "Halloween Haunt: Candy Quest"
        title_surface = self.title_font.render(title_text, True, ORANGE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        
        # Beta version indicator
        beta_font = asset_manager.load_font("assets/fonts/creepy.ttf", 20)
        beta_text = "BETA VERSION"
        beta_surface = beta_font.render(beta_text, True, RED)
        beta_rect = beta_surface.get_rect(center=(SCREEN_WIDTH // 2, 130))

        # Pulsing glow effect
        glow_intensity = 0.5 + 0.5 * math.sin(time_factor * 2)
        glow_color = (int(255 * glow_intensity), int(100 * glow_intensity), 0)

        # Multi-layer glow effect
        for offset in range(1, 6):
            glow_surface = self.title_font.render(title_text, True, glow_color)
            alpha = int(100 * (1 - offset/6))
            glow_surface.set_alpha(alpha)
            screen.blit(glow_surface, (title_rect.x - offset, title_rect.y - offset))
            screen.blit(glow_surface, (title_rect.x + offset, title_rect.y + offset))

        # Add subtle floating motion to title
        float_offset = int(3 * math.sin(time_factor * 1.5))
        screen.blit(title_surface, (title_rect.x, title_rect.y + float_offset))
        
        # Draw beta version text with blinking effect
        blink_factor = math.sin(time_factor * 4)
        if blink_factor > -0.5:  # Make it blink by hiding it sometimes
            screen.blit(beta_surface, beta_rect)

        # Draw animated subtitle
        subtitle_font = asset_manager.load_font("assets/fonts/creepy.ttf", 20)
        subtitle_text = "Collect 15 candies and return home!"
        subtitle_surface = subtitle_font.render(subtitle_text, True, WHITE)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))

        # Add typing effect to subtitle
        if not hasattr(self, 'subtitle_chars'):
            self.subtitle_chars = 0
            self.last_char_time = 0

        if self.subtitle_chars < len(subtitle_text):
            if pygame.time.get_ticks() - self.last_char_time > 50:  # 50ms per character
                self.subtitle_chars += 1
                self.last_char_time = pygame.time.get_ticks()

        animated_subtitle = subtitle_text[:self.subtitle_chars]
        animated_surface = subtitle_font.render(animated_subtitle, True, WHITE)
        screen.blit(animated_surface, subtitle_rect)

        # Add blinking cursor if subtitle is still typing
        if self.subtitle_chars < len(subtitle_text) and int(time_factor * 2) % 2:
            cursor_x = subtitle_rect.x + animated_surface.get_width()
            cursor_y = subtitle_rect.y
            pygame.draw.line(screen, WHITE, (cursor_x, cursor_y), (cursor_x, cursor_y + subtitle_surface.get_height()), 2)

        # Enhanced button effects
        for i, button in enumerate(self.buttons):
            # Add subtle hover glow
            if button.rect.collidepoint(pygame.mouse.get_pos()):
                glow_rect = button.rect.inflate(10, 10)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                glow_surface.fill((255, 150, 0, 50))
                screen.blit(glow_surface, glow_rect)

            # Add floating animation to buttons
            button_float = int(2 * math.sin(time_factor * 1.2 + i * 0.5))
            original_y = button.rect.y
            button.rect.y = original_y + button_float

            button.draw(screen)

            # Reset button position
            button.rect.y = original_y

        # Draw footer text with fade effect
        footer_font = asset_manager.load_font("assets/fonts/creepy.ttf", 16)
        footer_text = "Press ESC in game for pause menu • Use WASD or Arrow Keys to move"
        footer_surface = footer_font.render(footer_text, True, (200, 200, 200))
        footer_rect = footer_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))

        # Add fade from edges
        footer_bg = pygame.Surface((footer_surface.get_width() + 40, footer_surface.get_height() + 10), pygame.SRCALPHA)
        footer_bg.fill((0, 0, 0, 120))
        screen.blit(footer_bg, (footer_rect.x - 20, footer_rect.y - 5))

        screen.blit(footer_surface, footer_rect)

        # Add version info
        version_font = asset_manager.load_font("assets/fonts/creepy.ttf", 12)
        version_text = "v1.0 - Enhanced Edition"
        version_surface = version_font.render(version_text, True, (150, 150, 150))
        version_rect = version_surface.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10))
        screen.blit(version_surface, version_rect)

class PauseMenu(Menu):
    """Pause menu overlay"""
    
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        
        # Create modern semi-transparent overlay with blur effect
        self.overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._create_pause_overlay()
        
        # Add buttons with enhanced styling
        button_width = 220
        button_height = 55
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = SCREEN_HEIGHT // 2 - 50
        
        self.add_button(center_x, start_y, button_width, button_height, 
                       "Resume Game", self._resume_game)
        self.add_button(center_x, start_y + 70, button_width, button_height, 
                       "Settings", self._show_settings)
        self.add_button(center_x, start_y + 140, button_width, button_height, 
                       "Restart Level", self._restart_level)
        self.add_button(center_x, start_y + 210, button_width, button_height, 
                       "Main Menu", self._return_to_menu)
        self.add_button(center_x, start_y + 280, button_width, button_height, 
                       "Quit Game", self._quit_game)
    
    def _create_pause_overlay(self):
        """Create modern pause overlay with blur and vignette effect"""
        # Base dark overlay
        self.overlay_surface.fill((0, 0, 0))
        
        # Add vignette effect (darker corners)
        for y in range(SCREEN_HEIGHT):
            for x in range(SCREEN_WIDTH):
                distance_from_center = math.sqrt(
                    ((x - SCREEN_WIDTH//2) / (SCREEN_WIDTH//2)) ** 2 + 
                    ((y - SCREEN_HEIGHT//2) / (SCREEN_HEIGHT//2)) ** 2
                )
                if distance_from_center > 0.7:
                    alpha = min(150, int(150 * (distance_from_center - 0.7) / 0.3))
                    overlay_color = (0, 0, 0, alpha)
                    self.overlay_surface.set_at((x, y), overlay_color)
        
        # Add subtle animated particles
        time_factor = pygame.time.get_ticks() * 0.001
        for i in range(20):
            angle = time_factor * 0.5 + i * math.pi / 10
            radius = 100 + 50 * math.sin(time_factor * 0.3 + i)
            x = SCREEN_WIDTH // 2 + int(radius * math.cos(angle))
            y = SCREEN_HEIGHT // 2 + int(radius * math.sin(angle) * 0.5)
            
            if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                particle_alpha = int(30 + 20 * math.sin(time_factor * 2 + i))
                self.overlay_surface.set_at((x, y), (100, 100, 150, particle_alpha))
    
    def _resume_game(self):
        """Resume the game"""
        self.game_manager.resume_game()
    
    def _show_settings(self):
        """Show settings"""
        self.game_manager.show_settings()
    
    def _restart_level(self):
        """Restart the current level"""
        self.game_manager.restart_level()
    
    def _return_to_menu(self):
        """Return to main menu"""
        self.game_manager.return_to_main_menu()
    
    def _quit_game(self):
        """Quit game"""
        self.game_manager.quit_game()
    
    def draw(self, screen: pygame.Surface):
        """Draw modern pause menu with enhanced visual effects"""
        # Draw the overlay
        screen.blit(self.overlay_surface, (0, 0))
        
        # Get time for animations
        time_factor = pygame.time.get_ticks() * 0.001
        
        # Draw animated "PAUSED" title with modern styling
        title_font = asset_manager.load_font("assets/fonts/creepy.ttf", 64)
        title_text = "PAUSED"
        title_surface = title_font.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))
        
        # Add multiple glow layers for depth
        glow_colors = [(255, 100, 0), (255, 150, 0), (255, 200, 0)]
        for i, color in enumerate(glow_colors):
            glow_surface = title_font.render(title_text, True, color)
            offset = (i + 1) * 2
            alpha = int(120 * (1 - i/3))
            glow_surface.set_alpha(alpha)
            screen.blit(glow_surface, (title_rect.x - offset, title_rect.y - offset))
            screen.blit(glow_surface, (title_rect.x + offset, title_rect.y + offset))
        
        # Add subtle pulsing effect to title
        pulse_scale = 1.0 + 0.05 * math.sin(time_factor * 3)
        if pulse_scale > 1.0:
            pulsed_surface = pygame.transform.scale(title_surface, 
                (int(title_surface.get_width() * pulse_scale), int(title_surface.get_height() * pulse_scale)))
            pulsed_rect = pulsed_surface.get_rect(center=title_rect.center)
            pulsed_surface.set_alpha(50)
            screen.blit(pulsed_surface, pulsed_rect)
        
        screen.blit(title_surface, title_rect)
        
        # Draw modern styled buttons with enhanced effects
        for i, button in enumerate(self.buttons):
            # Enhanced button background with gradient
            button_bg = pygame.Surface((button.rect.width, button.rect.height), pygame.SRCALPHA)
            
            # Create gradient background
            for y in range(button.rect.height):
                alpha = int(200 + 55 * math.sin(y * 0.1 + time_factor))
                color = (50, 50, 70, alpha)
                pygame.draw.line(button_bg, color, (0, y), (button.rect.width, y))
            
            # Add border with glow
            pygame.draw.rect(button_bg, (150, 150, 200, 180), (0, 0, button.rect.width, button.rect.height), border_radius=8)
            pygame.draw.rect(button_bg, (200, 200, 255, 100), (2, 2, button.rect.width-4, button.rect.height-4), border_radius=6)
            
            screen.blit(button_bg, button.rect)
            
            # Enhanced hover effects
            if button.rect.collidepoint(pygame.mouse.get_pos()):
                # Hover glow
                hover_surface = pygame.Surface((button.rect.width + 20, button.rect.height + 20), pygame.SRCALPHA)
                glow_intensity = int(100 + 50 * math.sin(time_factor * 4))
                pygame.draw.rect(hover_surface, (255, 255, 255, glow_intensity), 
                               (0, 0, button.rect.width + 20, button.rect.height + 20), border_radius=10)
                screen.blit(hover_surface, (button.rect.x - 10, button.rect.y - 10))
                
                # Subtle scale effect
                scale_factor = 1.02
                scaled_rect = button.rect.copy()
                scaled_rect.width = int(button.rect.width * scale_factor)
                scaled_rect.height = int(button.rect.height * scale_factor)
                scaled_rect.center = button.rect.center
                
                # Draw scaled button
                scaled_bg = pygame.transform.scale(button_bg, (scaled_rect.width, scaled_rect.height))
                screen.blit(scaled_bg, scaled_rect)
                
                # Draw scaled text
                scaled_font = asset_manager.load_font("assets/fonts/creepy.ttf", 26)
                scaled_text = scaled_font.render(button.text, True, (255, 255, 255))
                scaled_text_rect = scaled_text.get_rect(center=scaled_rect.center)
                screen.blit(scaled_text, scaled_text_rect)
            else:
                # Draw normal button
                button.draw(screen)
            
            # Add floating animation
            float_offset = int(3 * math.sin(time_factor * 1.5 + i * 0.7))
            button.rect.y += float_offset
            
            if not button.rect.collidepoint(pygame.mouse.get_pos()):
                button.draw(screen)
            
            button.rect.y -= float_offset
        
        # Add modern UI hints
        hint_font = asset_manager.load_font("assets/fonts/creepy.ttf", 14)
        hint_text = "Click buttons or press ESC to resume"
        hint_surface = hint_font.render(hint_text, True, (180, 180, 180))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        
        # Hint background
        hint_bg = pygame.Surface((hint_surface.get_width() + 20, hint_surface.get_height() + 10), pygame.SRCALPHA)
        hint_bg.fill((0, 0, 0, 120))
        screen.blit(hint_bg, (hint_rect.x - 10, hint_rect.y - 5))
        
        screen.blit(hint_surface, hint_rect)

class HUD:
    """Heads-up display for gameplay"""
    
    def __init__(self):
        self.font = asset_manager.load_font("assets/fonts/creepy.ttf", 24)
        self.small_font = asset_manager.load_font("assets/fonts/creepy.ttf", 18)
        
        # Load heart sprite or create fallback
        self.heart_sprite = asset_manager.load_image("assets/ui/heart.png", RED, (20, 20))
    
    def draw(self, screen: pygame.Surface, player, level_info: dict, message: str = ""):
        """Draw the HUD"""
        # Background bar
        hud_height = 60
        hud_surface = pygame.Surface((SCREEN_WIDTH, hud_height), pygame.SRCALPHA)
        hud_surface.fill((0, 0, 0, 128))
        screen.blit(hud_surface, (0, 0))
        
        # Health hearts
        heart_x = 10
        heart_y = 10
        for i in range(player.health):
            if self.heart_sprite.get_width() > 10:
                screen.blit(self.heart_sprite, (heart_x + i * 25, heart_y))
            else:
                # Fallback: red hearts
                pygame.draw.circle(screen, RED, (heart_x + i * 25 + 10, heart_y + 10), 8)
        
        # Candy counter
        candy_text = f"Candies: {player.candies_collected}/{CANDIES_TO_COLLECT}"
        candy_surface = self.font.render(candy_text, True, ORANGE)
        screen.blit(candy_surface, (150, 15))
        
        # Score
        score_text = f"Score: {player.score}"
        score_surface = self.font.render(score_text, True, YELLOW)
        screen.blit(score_surface, (350, 15))
        
        # Level info
        level_text = f"Level {level_info.get('number', 1)}"
        level_surface = self.font.render(level_text, True, WHITE)
        screen.blit(level_surface, (550, 15))
        
        # Night mode indicator
        if level_info.get('night_mode', False):
            night_surface = self.small_font.render("NIGHT MODE", True, (100, 100, 255))
            screen.blit(night_surface, (650, 20))
        
        # Message at bottom
        if message:
            message_surface = self.font.render(message, True, WHITE)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            
            # Background for message
            bg_rect = pygame.Rect(message_rect.x - 10, message_rect.y - 5, 
                                 message_rect.width + 20, message_rect.height + 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            
            screen.blit(message_surface, message_rect)
        
        # Power-up indicators
        self._draw_powerups(screen, player)
    
    def _draw_powerups(self, screen: pygame.Surface, player):
        """Draw active power-up indicators"""
        if not player.active_powerups:
            return
        
        powerup_x = SCREEN_WIDTH - 200
        powerup_y = 70
        
        for i, powerup in enumerate(player.active_powerups):
            # Background
            bg_rect = pygame.Rect(powerup_x, powerup_y + i * 30, 180, 25)
            pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
            
            # Power-up name
            powerup_names = {
                "CANDY_MAGNET": "Candy Magnet",
                "GHOST_REPEL": "Ghost Repel",
                "SPEED_BOOST": "Speed Boost",
                "EXTRA_HEART": "Extra Heart",
                "ZOMBIE_POWER": "Zombie Power",
                "INVISIBILITY": "Invisibility",
                "TIME_SLOW": "Time Slow",
                "DOUBLE_POINTS": "Double Points",
                "SHIELD": "Shield"
            }
            
            name = powerup_names.get(powerup.type.name, "Unknown")
            time_left = powerup.duration // 60  # Convert to seconds
            
            text = f"{name} ({time_left}s)"
            text_surface = self.small_font.render(text, True, GREEN)
            screen.blit(text_surface, (powerup_x + 5, powerup_y + i * 30 + 5))

class TutorialOverlay:
    """Tutorial overlay system"""
    
    def __init__(self):
        self.font = asset_manager.load_font("assets/fonts/creepy.ttf", 20)
        self.small_font = asset_manager.load_font("assets/fonts/creepy.ttf", 16)
        
        self.current_step = 0
        self.steps = [
            "Welcome! You're a ghost trick-or-treater. Use WASD/arrows to move.",
            "Collect candies (orange glows) by approaching and pressing SPACE. Goal: Get 15!",
            "Avoid ghosts—they deduct a heart on contact! You have 3 hearts total.",
            "Find Easter eggs for bonuses, like hidden stashes (press SPACE to interact).",
            "ESC for pause menu. Return to house (blue door) to finish level."
        ]
        
        self.fade_in_timer = 0
        self.display_timer = 0
        self.fade_out_timer = 0
        self.step_duration = 300  # 5 seconds at 60 FPS
        self.fade_duration = 60   # 1 second fade
        
        self.skip_button_rect = pygame.Rect(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 40, 100, 30)
        self.completed = False
    
    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool) -> bool:
        """Update tutorial state. Returns True if tutorial is complete."""
        if self.completed:
            return True
        
        # Check skip button
        if mouse_clicked and self.skip_button_rect.collidepoint(mouse_pos):
            self.completed = True
            return True
        
        # Update timers
        if self.fade_in_timer < self.fade_duration:
            self.fade_in_timer += 1
        elif self.display_timer < self.step_duration:
            self.display_timer += 1
        elif self.fade_out_timer < self.fade_duration:
            self.fade_out_timer += 1
        else:
            # Move to next step
            self.current_step += 1
            if self.current_step >= len(self.steps):
                self.completed = True
                return True
            
            # Reset timers for next step
            self.fade_in_timer = 0
            self.display_timer = 0
            self.fade_out_timer = 0
        
        return False
    
    def advance_step(self):
        """Manually advance to next tutorial step"""
        if not self.completed and self.display_timer > 60:  # Minimum 1 second display
            self.fade_out_timer = self.fade_duration  # Skip to fade out
    
    def draw(self, screen: pygame.Surface):
        """Draw tutorial overlay"""
        if self.completed or self.current_step >= len(self.steps):
            return
        
        # Calculate alpha based on fade timers
        alpha = 255
        if self.fade_in_timer < self.fade_duration:
            alpha = int(255 * (self.fade_in_timer / self.fade_duration))
        elif self.fade_out_timer > 0:
            alpha = int(255 * (1 - self.fade_out_timer / self.fade_duration))
        
        # Create overlay surface
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(128, alpha // 2)))
        screen.blit(overlay, (0, 0))
        
        # Tutorial panel
        panel_width = 600
        panel_height = 120
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((50, 50, 50, alpha))
        pygame.draw.rect(panel_surface, (255, 255, 255, alpha), (0, 0, panel_width, panel_height), 3)
        
        # Tutorial text
        current_text = self.steps[self.current_step]
        
        # Wrap text
        words = current_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if self.font.size(test_line)[0] <= panel_width - 40:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw lines
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, (255, 255, 255, alpha))
            panel_surface.blit(text_surface, (20, 20 + i * 25))
        
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Step indicator
        step_text = f"Step {self.current_step + 1} / {len(self.steps)}"
        step_surface = self.small_font.render(step_text, True, (200, 200, 200, alpha))
        screen.blit(step_surface, (panel_x + 10, panel_y + panel_height + 10))
        
        # Skip button
        skip_surface = pygame.Surface((100, 30), pygame.SRCALPHA)
        skip_surface.fill((100, 100, 100, alpha))
        pygame.draw.rect(skip_surface, (255, 255, 255, alpha), (0, 0, 100, 30), 2)
        
        skip_text = self.small_font.render("Skip Tutorial", True, (255, 255, 255, alpha))
        skip_text_rect = skip_text.get_rect(center=(50, 15))
        skip_surface.blit(skip_text, skip_text_rect)
        
        screen.blit(skip_surface, self.skip_button_rect)

class GameOverScreen:
    """Game over screen"""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.font = asset_manager.load_font("assets/fonts/creepy.ttf", 36)
        self.small_font = asset_manager.load_font("assets/fonts/creepy.ttf", 24)
        
        # Input field for high score name
        self.name_input = ""
        self.input_active = False
        self.cursor_timer = 0
        
        # Buttons
        self.buttons = []
        self._create_buttons()
    
    def _create_buttons(self):
        """Create buttons for game over screen"""
        button_width = 200
        button_height = 50
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        # Restart button
        restart_btn = Button(center_x, 400, button_width, button_height, 
                           "Restart Level", self.small_font, self._restart_level)
        self.buttons.append(restart_btn)
        
        # Main menu button
        menu_btn = Button(center_x, 460, button_width, button_height, 
                        "Main Menu", self.small_font, self._main_menu)
        self.buttons.append(menu_btn)
    
    def _restart_level(self):
        """Restart the current level"""
        self.game_manager.restart_level()
    
    def _main_menu(self):
        """Return to main menu"""
        self.game_manager.return_to_main_menu()
    
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    self.input_active = False
                    # Save high score if name entered
                    if self.name_input.strip():
                        # This would be called from game manager with actual score
                        pass
                elif event.key == pygame.K_BACKSPACE:
                    self.name_input = self.name_input[:-1]
                else:
                    if len(self.name_input) < 20:
                        self.name_input += event.unicode
    
    def update(self, mouse_pos: Tuple[int, int], mouse_pressed: bool):
        """Update game over screen"""
        for button in self.buttons:
            button.update(mouse_pos, mouse_pressed)
        
        self.cursor_timer += 1
        if self.cursor_timer >= 60:
            self.cursor_timer = 0
    
    def draw(self, screen: pygame.Surface, final_score: int = 0, is_high_score: bool = False):
        """Draw game over screen"""
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((20, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(game_over_text, game_over_rect)
        
        # Score
        score_text = f"Final Score: {final_score}"
        score_surface = self.small_font.render(score_text, True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(score_surface, score_rect)
        
        # High score input
        if is_high_score:
            hs_text = "New High Score! Enter your name:"
            hs_surface = self.small_font.render(hs_text, True, YELLOW)
            hs_rect = hs_surface.get_rect(center=(SCREEN_WIDTH // 2, 250))
            screen.blit(hs_surface, hs_rect)
            
            # Input box
            input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 280, 200, 30)
            pygame.draw.rect(screen, WHITE, input_rect)
            pygame.draw.rect(screen, BLACK, input_rect, 2)
            
            # Input text
            input_text = self.name_input
            if self.input_active and self.cursor_timer < 30:
                input_text += "|"
            
            input_surface = self.small_font.render(input_text, True, BLACK)
            screen.blit(input_surface, (input_rect.x + 5, input_rect.y + 5))
            
            if not self.input_active:
                self.input_active = True
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)

class VictoryScreen:
    """Victory screen after completing all levels"""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.font = asset_manager.load_font("assets/fonts/creepy.ttf", 48)
        self.small_font = asset_manager.load_font("assets/fonts/creepy.ttf", 24)
        
        # Animation
        self.celebration_timer = 0
        
        # Buttons
        button_width = 200
        button_height = 50
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.endless_btn = Button(center_x, 400, button_width, button_height, 
                                 "Endless Mode", self.small_font, self._start_endless)
        self.menu_btn = Button(center_x, 460, button_width, button_height, 
                              "Main Menu", self.small_font, self._main_menu)
    
    def _start_endless(self):
        """Start endless mode"""
        self.game_manager.start_endless_mode()
    
    def _main_menu(self):
        """Return to main menu"""
        self.game_manager.return_to_main_menu()
    
    def update(self, mouse_pos: Tuple[int, int], mouse_pressed: bool):
        """Update victory screen"""
        self.celebration_timer += 1
        
        self.endless_btn.update(mouse_pos, mouse_pressed)
        self.menu_btn.update(mouse_pos, mouse_pressed)
    
    def draw(self, screen: pygame.Surface, total_score: int):
        """Draw victory screen"""
        # Celebratory background
        for y in range(SCREEN_HEIGHT):
            color_intensity = int(50 + 30 * math.sin(y * 0.01 + self.celebration_timer * 0.1))
            color = (color_intensity, color_intensity // 2, 0)
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Victory text
        victory_text = "You Survived Halloween!"
        victory_surface = self.font.render(victory_text, True, ORANGE)
        victory_rect = victory_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        # Add glow effect
        for offset in range(1, 4):
            glow_surface = self.font.render(victory_text, True, (255, 100, 0))
            screen.blit(glow_surface, (victory_rect.x - offset, victory_rect.y - offset))
        
        screen.blit(victory_surface, victory_rect)
        
        # Total score
        score_text = f"Total Score: {total_score}"
        score_surface = self.small_font.render(score_text, True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 220))
        screen.blit(score_surface, score_rect)
        
        # Congratulations message
        congrats = "You've mastered all 5 levels of Halloween Haunt!"
        congrats_surface = self.small_font.render(congrats, True, WHITE)
        congrats_rect = congrats_surface.get_rect(center=(SCREEN_WIDTH // 2, 280))
        screen.blit(congrats_surface, congrats_rect)
        
        # Draw buttons
        self.endless_btn.draw(screen)
        self.menu_btn.draw(screen)

class SettingsMenu(Menu):
    """Settings menu for volume and options"""
    
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        
        # Settings values
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.fullscreen = False
        
        # Slider properties
        self.music_slider_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 220, 200, 10)
        self.sfx_slider_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 270, 200, 10)
        self.music_handle_rect = pygame.Rect(0, 0, 15, 20)
        self.sfx_handle_rect = pygame.Rect(0, 0, 15, 20)
        self.dragging_music = False
        self.dragging_sfx = False
        
        # Create UI elements
        self._create_ui_elements()
        self._update_slider_positions()
    
    def _create_ui_elements(self):
        """Create settings UI elements"""
        # Back button
        self.add_button(50, SCREEN_HEIGHT - 80, 100, 40, "Back", self._go_back)
        
        # Fullscreen toggle
        self.add_button(SCREEN_WIDTH // 2 - 75, 300, 150, 40, 
                       "Toggle Fullscreen", self._toggle_fullscreen)
    
    def _go_back(self):
        """Return to previous menu"""
        self.game_manager.return_from_settings()
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        self.game_manager.toggle_fullscreen()
    
    def _update_slider_positions(self):
        """Update slider handle positions based on volume values"""
        # Music slider handle position
        music_pos = self.music_slider_rect.x + (self.music_volume * self.music_slider_rect.width) - 7
        self.music_handle_rect.centerx = int(music_pos)
        self.music_handle_rect.centery = self.music_slider_rect.centery
        
        # SFX slider handle position
        sfx_pos = self.sfx_slider_rect.x + (self.sfx_volume * self.sfx_slider_rect.width) - 7
        self.sfx_handle_rect.centerx = int(sfx_pos)
        self.sfx_handle_rect.centery = self.sfx_slider_rect.centery
    
    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool):
        """Update settings menu with slider interactions"""
        super().update(mouse_pos, mouse_clicked)
        
        # Get current mouse state
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Handle slider interactions
        if mouse_pressed:
            if self.music_handle_rect.collidepoint(mouse_pos) or self.dragging_music:
                self.dragging_music = True
                relative_x = mouse_pos[0] - self.music_slider_rect.x
                self.music_volume = max(0.0, min(1.0, relative_x / self.music_slider_rect.width))
                self._update_slider_positions()
            
            elif self.sfx_handle_rect.collidepoint(mouse_pos) or self.dragging_sfx:
                self.dragging_sfx = True
                relative_x = mouse_pos[0] - self.sfx_slider_rect.x
                self.sfx_volume = max(0.0, min(1.0, relative_x / self.sfx_slider_rect.width))
                self._update_slider_positions()
        else:
            # Stop dragging when mouse is released
            if self.dragging_music or self.dragging_sfx:
                # Apply volume changes to sound manager
                self.game_manager.sound_manager.set_music_volume(self.music_volume)
                self.game_manager.sound_manager.set_sfx_volume(self.sfx_volume)
            self.dragging_music = False
            self.dragging_sfx = False
    
    def draw(self, screen: pygame.Surface):
        """Draw enhanced settings menu with visual effects"""
        super().draw(screen)

        # Get time for animations
        time_factor = pygame.time.get_ticks() * 0.001

        # Create settings panel background
        panel_width = 500
        panel_height = 350
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = 120

        # Animated panel background with subtle gradient
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        for y in range(panel_height):
            alpha = int(180 + 20 * math.sin(y * 0.02 + time_factor))
            color = (30, 30, 50, alpha)
            pygame.draw.line(panel_surface, color, (0, y), (panel_width, y))

        # Add border with glow effect
        pygame.draw.rect(panel_surface, (100, 100, 150), (0, 0, panel_width, panel_height), 3)
        pygame.draw.rect(panel_surface, (150, 150, 200), (2, 2, panel_width-4, panel_height-4), 1)

        screen.blit(panel_surface, (panel_x, panel_y))

        # Enhanced title with glow
        title_font = asset_manager.load_font("assets/fonts/creepy.ttf", 36)
        title_text = "Settings"
        title_surface = title_font.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 160))

        # Add glow effect to title
        glow_color = (100, 100, 200)
        for offset in range(1, 4):
            glow_surface = title_font.render(title_text, True, glow_color)
            alpha = int(80 * (1 - offset/4))
            glow_surface.set_alpha(alpha)
            screen.blit(glow_surface, (title_rect.x - offset, title_rect.y - offset))

        screen.blit(title_surface, title_rect)

        # Volume sliders with enhanced styling
        font = asset_manager.load_font("assets/fonts/creepy.ttf", 20)

        # Music volume section
        music_y = 220
        music_text = f"Music Volume: {int(self.music_volume * 100)}%"
        music_surface = font.render(music_text, True, WHITE)
        screen.blit(music_surface, (SCREEN_WIDTH // 2 - 100, music_y - 20))

        # Enhanced music slider background
        slider_bg = pygame.Rect(SCREEN_WIDTH // 2 - 100, music_y, 200, 12)
        pygame.draw.rect(screen, (60, 60, 80), slider_bg, border_radius=6)

        # Slider fill based on volume
        fill_width = int(200 * self.music_volume)
        if fill_width > 0:
            fill_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, music_y, fill_width, 12)
            pygame.draw.rect(screen, (100, 150, 255), fill_rect, border_radius=6)

        # Enhanced music slider handle
        handle_color = (200, 200, 255) if self.dragging_music else (255, 255, 255)
        pygame.draw.circle(screen, handle_color, self.music_handle_rect.center, 8)
        pygame.draw.circle(screen, (50, 50, 100), self.music_handle_rect.center, 8, 2)

        # SFX volume section
        sfx_y = 280
        sfx_text = f"SFX Volume: {int(self.sfx_volume * 100)}%"
        sfx_surface = font.render(sfx_text, True, WHITE)
        screen.blit(sfx_surface, (SCREEN_WIDTH // 2 - 100, sfx_y - 20))

        # Enhanced SFX slider background
        slider_bg = pygame.Rect(SCREEN_WIDTH // 2 - 100, sfx_y, 200, 12)
        pygame.draw.rect(screen, (60, 60, 80), slider_bg, border_radius=6)

        # Slider fill based on volume
        fill_width = int(200 * self.sfx_volume)
        if fill_width > 0:
            fill_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, sfx_y, fill_width, 12)
            pygame.draw.rect(screen, (100, 255, 150), fill_rect, border_radius=6)

        # Enhanced SFX slider handle
        handle_color = (200, 255, 200) if self.dragging_sfx else (255, 255, 255)
        pygame.draw.circle(screen, handle_color, self.sfx_handle_rect.center, 8)
        pygame.draw.circle(screen, (50, 100, 50), self.sfx_handle_rect.center, 8, 2)

        # Fullscreen toggle button enhancement
        for button in self.buttons:
            if "Toggle Fullscreen" in button.text:
                # Add status indicator
                status_color = GREEN if self.fullscreen else GRAY
                status_text = "ON" if self.fullscreen else "OFF"
                status_font = asset_manager.load_font("assets/fonts/creepy.ttf", 16)
                status_surface = status_font.render(f"Fullscreen: {status_text}", True, status_color)
                screen.blit(status_surface, (SCREEN_WIDTH // 2 - 50, 350))

        # Add subtle animated elements
        for i in range(5):
            angle = time_factor + i * math.pi / 2.5
            radius = 100 + 20 * math.sin(time_factor * 0.5 + i)
            x = SCREEN_WIDTH // 2 + int(radius * math.cos(angle))
            y = SCREEN_HEIGHT // 2 + int(radius * math.sin(angle) * 0.3)

            # Small floating particles
            particle_color = (150, 150, 255, 100)
            pygame.draw.circle(screen, particle_color, (x, y), 2)

        # Instructions at bottom
        instr_font = asset_manager.load_font("assets/fonts/creepy.ttf", 14)
        instr_text = "Click and drag sliders • Press buttons to toggle options"
        instr_surface = instr_font.render(instr_text, True, (180, 180, 180))
        instr_rect = instr_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(instr_surface, instr_rect)