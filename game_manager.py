"""
Main Game Manager for Halloween Haunt: Candy Quest
Coordinates all game systems and manages game states
"""

import pygame
import random
import math
from typing import List, Optional, Tuple
from halloween_haunt import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CANDIES_TO_COLLECT,
    TILE_SIZE, TileType, GameState, Particle, camera, save_manager
)
from entities import Player, Ghost, Candy, EasterEgg
from levels import Level, LevelManager, CemeteryArea
from ui import (MainMenu, PauseMenu, HUD, TutorialOverlay, 
               GameOverScreen, VictoryScreen, SettingsMenu)
from sound import SoundManager
from special_features import SpecialFeaturesManager

class GameManager:
    """Main game manager that coordinates all systems"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        # Game state
        self.current_state = GameState.MAIN_MENU
        self.previous_state = GameState.MAIN_MENU
        
        # Core systems
        self.sound_manager = SoundManager()
        self.level_manager = LevelManager()
        self.special_features = SpecialFeaturesManager()
        
        # Game entities
        self.player: Optional[Player] = None
        self.current_level: Optional[Level] = None
        self.cemetery_area: Optional[CemeteryArea] = None
        
        # UI systems
        self.main_menu = MainMenu(self)
        self.pause_menu = PauseMenu(self)
        self.hud = HUD()
        self.tutorial = TutorialOverlay()
        self.game_over_screen = GameOverScreen(self)
        self.victory_screen = VictoryScreen(self)
        self.settings_menu = SettingsMenu(self)
        
        # Visual effects
        self.particles: List[Particle] = []
        self.screen_shake_timer = 0
        self.screen_shake_intensity = 0
        
        # Game mechanics
        self.night_mode_timer = 0
        self.night_mode_active = False
        self.message_text = ""
        self.message_timer = 0
        self.day_night_cycle_duration = 10800  # 3 minutes at 60 FPS
        
        # Input handling
        self.keys_pressed = pygame.key.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_clicked = False
        
        # Display settings
        self.fullscreen = False
        
        # Load saved progress
        self._load_saved_progress()
    
    def _load_saved_progress(self):
        """Load saved game progress"""
        save_data = save_manager.load_progress()
        self.tutorial.completed = save_data.get("tutorial_completed", False)
    
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                self._handle_escape_key()
            elif event.key == pygame.K_SPACE:
                self._handle_space_key()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.mouse_clicked = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_clicked = False
        
        # Forward events to current screen
        if self.current_state == GameState.GAME_OVER:
            self.game_over_screen.handle_event(event)
    
    def _handle_escape_key(self):
        """Handle escape key press"""
        if self.current_state == GameState.PLAYING:
            self.pause_game()
        elif self.current_state == GameState.PAUSED:
            self.resume_game()
        elif self.current_state == GameState.TUTORIAL:
            self.tutorial.completed = True
            self._transition_to_gameplay()
    
    def _handle_space_key(self):
        """Handle space key press for interactions"""
        if self.current_state == GameState.PLAYING and self.player and self.current_level:
            self._handle_player_interactions()
        elif self.current_state == GameState.TUTORIAL:
            self.tutorial.advance_step()
    
    def _handle_player_interactions(self):
        """Handle player interactions with game objects"""
        # Check candy collection
        for candy in self.current_level.candies:
            if not candy.collected:
                distance = math.sqrt(
                    (self.player.x - candy.x) ** 2 + (self.player.y - candy.y) ** 2
                )
                if distance <= 25:  # Collection radius
                    particles = candy.collect(self.player)
                    self.particles.extend(particles)
                    # Play your custom collect sound
                    self.sound_manager.play_collect_sound()
                    
                    # Check if we have enough candies
                    if self.player.candies_collected >= CANDIES_TO_COLLECT:
                        self.show_message("Return to house to complete the level!")
        
        # Check cemetery gate interaction
        player_tile_x = int(self.player.x // TILE_SIZE)
        player_tile_y = int(self.player.y // TILE_SIZE)
        if self.current_level.tile_map.get_tile(player_tile_x, player_tile_y) == TileType.CEMETERY_GATE:
            if not hasattr(self, '_cemetery_entered'):
                self.show_message("Press SPACE to enter the cemetery...")
                self._cemetery_entered = False
            if self.keys_pressed[pygame.K_SPACE] and not self._cemetery_entered:
                self._enter_cemetery(self.player.x, self.player.y)
                self._cemetery_entered = True
        elif hasattr(self, '_cemetery_entered'):
            # Reset when leaving cemetery area
            delattr(self, '_cemetery_entered')
        
        # Check Easter egg interactions
        for egg in self.current_level.easter_eggs:
            if not egg.activated:
                success, message, particles = egg.interact(self.player)
                if success:
                    self.particles.extend(particles)
                    self.sound_manager.play_sound("easter_egg")
                    self.show_message(message)
        
        # Handle special feature interactions
        special_particles, special_message = self.special_features.handle_interactions(self.player)
        self.particles.extend(special_particles)
        if special_message:
            self.show_message(special_message)
    
    def update(self, dt: float):
        """Update game state"""
        # Update input state at the beginning of each frame
        self.keys_pressed = pygame.key.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        
        # Update based on current state
        if self.current_state == GameState.MAIN_MENU:
            # Quick start with ENTER key for testing
            if self.keys_pressed[pygame.K_RETURN]:
                self.start_new_game()
                return
            self.main_menu.update(self.mouse_pos, self.mouse_clicked)
        
        elif self.current_state == GameState.TUTORIAL:
            if self.tutorial.update(self.mouse_pos, self.mouse_clicked):
                self._transition_to_gameplay()
            else:
                self._update_gameplay_entities()
        
        elif self.current_state == GameState.PLAYING:
            self._update_gameplay()
        
        elif self.current_state == GameState.CEMETERY:
            self._update_cemetery()
        
        elif self.current_state == GameState.PAUSED:
            self.pause_menu.update(self.mouse_pos, self.mouse_clicked)
        
        elif self.current_state == GameState.GAME_OVER:
            self.game_over_screen.update(self.mouse_pos, self.mouse_clicked)
        
        elif self.current_state == GameState.VICTORY:
            self.victory_screen.update(self.mouse_pos, self.mouse_clicked)
        
        elif self.current_state == GameState.SETTINGS:
            self.settings_menu.update(self.mouse_pos, self.mouse_clicked)
        
        # Update visual effects
        self._update_particles()
        self._update_screen_shake()
        self._update_message_timer()
        
        # Reset mouse click state
        if self.mouse_clicked:
            self.mouse_clicked = False
    
    def _update_gameplay(self):
        """Update gameplay-specific logic"""
        if not self.player or not self.current_level:
            return
        
        self._update_gameplay_entities()
        self._check_collisions()
        self._update_day_night_cycle()
        self._check_level_completion()
    
    def _update_gameplay_entities(self):
        """Update all gameplay entities"""
        if not self.player or not self.current_level:
            return
        
        # Update player
        self.player.update(self.keys_pressed, self.current_level.tile_map)
        
        # Update level entities and handle events
        chase_events = self.current_level.update(self.player)
        
        # Play ghost sound when chasing starts
        if chase_events:
            self.sound_manager.play_ghost_sound()
        
        # Update special features
        special_particles, special_message = self.special_features.update(
            self.player, self.keys_pressed, 
            getattr(self, '_space_pressed', False)
        )
        self.particles.extend(special_particles)
        if special_message:
            self.show_message(special_message)
        
        # Update camera to follow player
        camera.update(self.player.x, self.player.y)
        
        # Apply candy magnet power-up
        for powerup in self.player.active_powerups:
            if powerup.type.name == "CANDY_MAGNET":
                self._apply_candy_magnet()
        
        # Store space state for next frame
        if not hasattr(self, '_last_space_state'):
            self._last_space_state = False
        current_space = self.keys_pressed[pygame.K_SPACE]
        self._space_pressed = current_space and not self._last_space_state
        self._last_space_state = current_space
    
    def _apply_candy_magnet(self):
        """Apply candy magnet effect"""
        magnet_radius = 50
        
        for candy in self.current_level.candies:
            if not candy.collected:
                distance = math.sqrt(
                    (self.player.x - candy.x) ** 2 + (self.player.y - candy.y) ** 2
                )
                
                if distance <= magnet_radius:
                    # Auto-collect candy
                    particles = candy.collect(self.player)
                    self.particles.extend(particles)
                    # Play collect sound (quieter for auto-collect)
                    self.sound_manager.play_sound("collect", 0.5)
    
    def _check_collisions(self):
        """Check for collisions between entities"""
        if not self.player or not self.current_level:
            return
        
        # Check ghost collisions
        for ghost in self.current_level.ghosts:
            if self.player.rect.colliderect(ghost.rect):
                # Check if player has ghost repel power-up
                has_repel = any(p.type.name == "GHOST_REPEL" for p in self.player.active_powerups)
                
                if not has_repel and self.player.take_damage():
                    # Play your custom hit sound
                    self.sound_manager.play_hit_sound()
                    self._trigger_screen_shake(10, 5)
                    
                    # Check for game over
                    if self.player.health <= 0:
                        self._game_over()
    
    def _update_day_night_cycle(self):
        """Update day/night cycle"""
        if not self.current_level:
            return
        
        # Only apply cycle to levels that don't have permanent night mode
        if not self.current_level.night_mode:
            self.night_mode_timer += 1
            
            if self.night_mode_timer >= self.day_night_cycle_duration:
                if not self.night_mode_active:
                    self.night_mode_active = True
                    self.show_message("Night has fallen... more ghosts appear!")
                    
                    # Spawn additional ghosts
                    self._spawn_night_ghosts()
        else:
            # Permanent night mode for higher levels
            self.night_mode_active = True
    
    def _spawn_night_ghosts(self):
        """Spawn additional ghosts during night mode"""
        if not self.current_level:
            return
        
        # Add 2 more ghosts
        for _ in range(2):
            attempts = 0
            while attempts < 50:
                x = random.randint(2, 28) * 32 + 16
                y = random.randint(2, 18) * 32 + 16
                
                # Check if position is valid and away from player
                tile_x, tile_y = int(x // 32), int(y // 32)
                distance_to_player = math.sqrt(
                    (x - self.player.x) ** 2 + (y - self.player.y) ** 2
                )
                
                if (not self.current_level.tile_map.is_solid_tile(tile_x, tile_y) and
                    distance_to_player > 160):  # 5 tiles away
                    
                    patrol_route = [(x, y), (x + 64, y), (x, y + 64), (x - 64, y)]
                    night_ghost = Ghost(x, y, patrol_route)
                    self.current_level.ghosts.append(night_ghost)
                    break
                
                attempts += 1
    
    def _update_cemetery(self):
        """Update cemetery-specific logic"""
        if not self.player or not self.cemetery_area:
            return
        
        # Update player movement in cemetery
        self.player.update(self.keys_pressed, self.cemetery_area.tile_map)
        
        # Update cemetery entities
        chase_events = self.cemetery_area.update(self.player)
        
        # Play ghost sound when chasing starts
        if chase_events:
            self.sound_manager.play_ghost_sound()
        
        # Check collisions with cemetery ghosts
        for ghost in self.cemetery_area.ghosts:
            if self.player.rect.colliderect(ghost.rect):
                has_repel = any(p.type.name == "GHOST_REPEL" for p in self.player.active_powerups)
                has_zombie = any(p.type.name == "ZOMBIE_POWER" for p in self.player.active_powerups)
                
                if not has_repel and not has_zombie and self.player.take_damage():
                    self.sound_manager.play_hit_sound()
                    self._trigger_screen_shake(10, 5)
                    
                    # Check for game over
                    if self.player.health <= 0:
                        self._game_over()
        
        # Check if player wants to exit cemetery
        if self.cemetery_area.check_exit(self.player.x, self.player.y):
            if not hasattr(self, '_exit_message_shown'):
                self.show_message("Press SPACE to exit the cemetery")
                self._exit_message_shown = True
            if self.keys_pressed[pygame.K_SPACE]:
                self._exit_cemetery()
        elif hasattr(self, '_exit_message_shown'):
            delattr(self, '_exit_message_shown')
        
        # Update camera
        camera.update(self.player.x, self.player.y)
    
    def _complete_level(self):
        """Handle level completion"""
        self.sound_manager.play_sound("win")
        
        # Calculate completion bonus
        time_bonus = max(0, 300 - (self.night_mode_timer // 60))  # Bonus for speed
        health_bonus = self.player.health * 50  # Bonus for remaining health
        total_bonus = time_bonus + health_bonus
        
        self.player.score += total_bonus
        
        # Save progress
        save_manager.save_progress(
            self.level_manager.current_level_number + 1,
            self.player.score,
            self.tutorial.completed
        )
        
        # Check if this was the final level
        if self.level_manager.is_final_level():
            self._show_victory()
        else:
            self._advance_to_next_level()
    
    def _advance_to_next_level(self):
        """Advance to the next level"""
        next_level = self.level_manager.next_level()
        if next_level:
            self.current_level = next_level
            
            # Setup special features for new level
            self._setup_special_features()
            
            # Reset player position and some stats
            spawn_x, spawn_y = next_level.get_spawn_position()
            self.player.x = spawn_x
            self.player.y = spawn_y
            self.player.candies_collected = 0
            
            # Reset timers
            self.night_mode_timer = 0
            self.night_mode_active = False
            
            self.show_message(f"Level {self.level_manager.current_level_number} - Good luck!")
    
    def _game_over(self):
        """Handle game over"""
        self.current_state = GameState.GAME_OVER
        
        # Check if this is a high score
        high_scores = save_manager.load_high_scores()
        is_high_score = len(high_scores) < 5 or self.player.score > high_scores[-1]["score"]
        
        if is_high_score:
            # This would trigger name input in the game over screen
            pass
    
    def _show_victory(self):
        """Show victory screen"""
        self.current_state = GameState.VICTORY
        
        # Save final score as high score
        save_manager.save_high_score("Champion", self.player.score)
    
    def _transition_to_gameplay(self):
        """Transition from tutorial to main gameplay"""
        self.current_state = GameState.PLAYING
        save_manager.save_progress(1, 0, True)  # Mark tutorial as completed
    
    def _update_particles(self):
        """Update particle effects"""
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()
    
    def _update_screen_shake(self):
        """Update screen shake effect"""
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= 1
    
    def _update_message_timer(self):
        """Update message display timer"""
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message_text = ""
    
    def _trigger_screen_shake(self, intensity: int, duration: int):
        """Trigger screen shake effect"""
        self.screen_shake_intensity = intensity
        self.screen_shake_timer = duration
    
    def show_message(self, text: str, duration: int = 180):
        """Show a message to the player"""
        self.message_text = text
        self.message_timer = duration
    
    def _exit_cemetery(self):
        """Exit the cemetery area back to main level"""
        self.current_state = GameState.PLAYING
        self.cemetery_area = None
        self.show_message("Exited the cemetery")
        
        # Resume normal gameplay music
        self.sound_manager.play_gameplay_music()
    
    def draw(self):
        """Draw the current game state"""
        # Calculate screen shake offset
        shake_x = 0
        shake_y = 0
        if self.screen_shake_timer > 0:
            shake_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            shake_y = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
        
        # Clear screen
        self.screen.fill((20, 20, 40))  # Dark blue-gray background
        
        # Draw based on current state
        if self.current_state == GameState.MAIN_MENU:
            self.main_menu.draw(self.screen)
        
        elif self.current_state in [GameState.PLAYING, GameState.TUTORIAL]:
            self._draw_gameplay()
            
            if self.current_state == GameState.TUTORIAL:
                self.tutorial.draw(self.screen)
        
        elif self.current_state == GameState.CEMETERY:
            self._draw_cemetery()
        
        elif self.current_state == GameState.PAUSED:
            self._draw_gameplay()  # Draw game behind pause menu
            self.pause_menu.draw(self.screen)
        
        elif self.current_state == GameState.GAME_OVER:
            score = self.player.score if self.player else 0
            self.game_over_screen.draw(self.screen, score)
        
        elif self.current_state == GameState.VICTORY:
            score = self.player.score if self.player else 0
            self.victory_screen.draw(self.screen, score)
        
        elif self.current_state == GameState.SETTINGS:
            self.settings_menu.draw(self.screen)
    
    def _draw_gameplay(self):
        """Draw gameplay elements"""
        if not self.current_level or not self.player:
            return
        
        # Draw level with house highlighting if player has enough candies
        highlight_house = self.player.candies_collected >= CANDIES_TO_COLLECT
        self.current_level.draw(self.screen, highlight_house)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw HUD
        level_info = {
            "number": self.level_manager.current_level_number,
            "night_mode": self.night_mode_active
        }
        self.hud.draw(self.screen, self.player, level_info, self.message_text)
    
    # Public methods for UI callbacks
    def start_new_game(self):
        """Start a new game"""
        # Create new player
        self.player = Player(0, 0)  # Position will be set by level
        
        # Load first level
        self.current_level = self.level_manager.load_level(1)
        spawn_x, spawn_y = self.current_level.get_spawn_position()
        self.player.x = spawn_x
        self.player.y = spawn_y
        

        
        # Setup special features for this level
        self._setup_special_features()
        
        # Reset game state
        self.night_mode_timer = 0
        self.night_mode_active = False
        self.particles.clear()
        
        # Start with tutorial if not completed
        if not self.tutorial.completed:
            self.current_state = GameState.TUTORIAL
        else:
            self.current_state = GameState.PLAYING
            
        # Switch to gameplay music
        self.sound_manager.play_gameplay_music()
    
    def load_game(self):
        """Load saved game"""
        save_data = save_manager.load_progress()
        level_number = save_data.get("level", 1)
        
        # Create player with saved data
        self.player = Player(0, 0)
        self.player.score = save_data.get("score", 0)
        
        # Load saved level
        self.current_level = self.level_manager.load_level(level_number)
        spawn_x, spawn_y = self.current_level.get_spawn_position()
        self.player.x = spawn_x
        self.player.y = spawn_y
        
        # Setup special features for loaded level
        self._setup_special_features()
        
        self.current_state = GameState.PLAYING
        
        # Switch to gameplay music
        self.sound_manager.play_gameplay_music()
    
    def pause_game(self):
        """Pause the game"""
        if self.current_state == GameState.PLAYING:
            self.previous_state = self.current_state
            self.current_state = GameState.PAUSED
    
    def resume_game(self):
        """Resume the game"""
        if self.current_state == GameState.PAUSED:
            self.current_state = self.previous_state
    
    def restart_level(self):
        """Restart the current level"""
        if self.current_level:
            # Reload current level
            self.current_level = self.level_manager.restart_current_level()
            
            # Setup special features for restarted level
            self._setup_special_features()
            
            # Reset player
            spawn_x, spawn_y = self.current_level.get_spawn_position()
            self.player.x = spawn_x
            self.player.y = spawn_y
            self.player.health = 3
            self.player.candies_collected = 0
            
            # Reset timers
            self.night_mode_timer = 0
            self.night_mode_active = False
            self.particles.clear()
            
            self.current_state = GameState.PLAYING
    
    def return_to_main_menu(self):
        """Return to main menu"""
        self.current_state = GameState.MAIN_MENU
        
        # Switch to menu music
        self.sound_manager.play_menu_music()
        
        # Save progress if in game
        if self.player and self.current_level:
            save_manager.save_progress(
                self.level_manager.current_level_number,
                self.player.score,
                self.tutorial.completed
            )
    
    def show_settings(self):
        """Show settings menu"""
        self.previous_state = self.current_state
        self.current_state = GameState.SETTINGS
    
    def return_from_settings(self):
        """Return from settings menu"""
        self.current_state = self.previous_state
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def start_endless_mode(self):
        """Start endless mode (scaling difficulty)"""
        # For now, just restart from level 1 with increased difficulty
        self.level_manager.current_level_number = 1
        self.start_new_game()
    
    def _check_level_completion(self):
        """Check if level completion conditions are met"""
        if not self.player or not self.current_level:
            return
        
        if self.player.candies_collected >= CANDIES_TO_COLLECT:
            # Check if player is near the house
            house_x, house_y = self.current_level.get_house_position()
            distance_to_house = math.sqrt(
                (self.player.x - house_x) ** 2 + (self.player.y - house_y) ** 2
            )
            
            if distance_to_house <= TILE_SIZE * 1.5:
                self._complete_level()
    
    def _setup_special_features(self):
        """Setup special features for the current level"""
        # This method can be expanded to setup level-specific special features
        # For now, it's a placeholder
        pass
    
    def quit_game(self):
        """Quit the game"""
        # Save progress before quitting
        if self.player and self.current_level:
            save_manager.save_progress(
                self.level_manager.current_level_number,
                self.player.score,
                self.tutorial.completed
            )
        
        pygame.quit()
        exit()