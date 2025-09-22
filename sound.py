"""
Sound system for Halloween Haunt: Candy Quest
Handles music and sound effects with graceful fallbacks
"""

import pygame
import os
from typing import Dict, Optional
from halloween_haunt import asset_manager

class SoundManager:
    """Manages all game audio"""
    
    def __init__(self):
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.music_playing = False
        self.current_music_type = None  # Track current music type
        
        # Sound effects dictionary
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        
        # Music paths
        self.music_paths = {
            "menu": "assets/music/main-menu.mp3",
            "gameplay": "assets/music/Game-time.mp3"
        }
        
        # Load sounds
        self._load_sounds()
        
        # Start with menu music
        self.play_menu_music()
    
    def _load_sounds(self):
        """Load all sound effects"""
        sound_files = {
            # Your custom sounds
            "collect": "assets/sfx/collect.mp3",
            "hit": "assets/sfx/hit.mp3", 
            "ghost": "assets/sfx/ghost.m4a",  # Fallback to boo if m4a fails
            
            # Fallback sounds (if available)
            "pickup": "assets/sfx/pickup.wav",
            "boo": "assets/sfx/boo.wav", 
            "win": "assets/sfx/win.wav",
            "hurt": "assets/sfx/hurt.wav",
            "powerup": "assets/sfx/powerup.wav",
            "easter_egg": "assets/sfx/easter_egg.wav",
            "menu_select": "assets/sfx/menu_select.wav",
            "menu_hover": "assets/sfx/menu_hover.wav"
        }
        
        for sound_name, file_path in sound_files.items():
            self.sounds[sound_name] = asset_manager.load_sound(file_path)
    
    def play_menu_music(self):
        """Play main menu music"""
        if self.current_music_type == "menu":
            return  # Already playing menu music
            
        self._switch_music("menu")
    
    def play_gameplay_music(self):
        """Play gameplay music"""
        if self.current_music_type == "gameplay":
            return  # Already playing gameplay music
            
        self._switch_music("gameplay")
    
    def _switch_music(self, music_type: str):
        """Switch to a different music track"""
        if music_type not in self.music_paths:
            return
            
        # Stop current music
        if self.music_playing:
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass
        
        # Load and play new music
        music_path = self.music_paths[music_type]
        if asset_manager.load_music(music_path):
            try:
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)  # Loop indefinitely
                self.music_playing = True
                self.current_music_type = music_type
            except pygame.error:
                self.music_playing = False
                self.current_music_type = None
    
    def play_sound(self, sound_name: str, volume_override: Optional[float] = None):
        """Play a sound effect"""
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                volume = volume_override if volume_override is not None else self.sfx_volume
                sound.set_volume(volume)
                sound.play()
            except pygame.error:
                pass  # Fail silently if sound can't play
    
    def set_music_volume(self, volume: float):
        """Set background music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except pygame.error:
            pass
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
        # Update volume for all loaded sounds
        for sound in self.sounds.values():
            if sound:
                try:
                    sound.set_volume(self.sfx_volume)
                except pygame.error:
                    pass
    
    def toggle_music(self):
        """Toggle background music on/off"""
        if self.music_playing:
            try:
                pygame.mixer.music.pause()
                self.music_playing = False
            except pygame.error:
                pass
        else:
            try:
                pygame.mixer.music.unpause()
                self.music_playing = True
            except pygame.error:
                pass
    
    def stop_music(self):
        """Stop background music"""
        try:
            pygame.mixer.music.stop()
            self.music_playing = False
        except pygame.error:
            pass
    
    def fade_out_music(self, fade_time_ms: int = 1000):
        """Fade out background music"""
        try:
            pygame.mixer.music.fadeout(fade_time_ms)
            self.music_playing = False
        except pygame.error:
            pass
    
    # Convenience methods for specific game events
    def play_collect_sound(self):
        """Play candy collection sound"""
        self.play_sound("collect")
    
    def play_hit_sound(self):
        """Play player hit sound"""
        self.play_sound("hit")
    
    def play_ghost_sound(self):
        """Play ghost chase sound"""
        # Try ghost sound first, fallback to boo if not available
        if self.sounds.get("ghost"):
            self.play_sound("ghost")
        else:
            self.play_sound("boo")
    
    def play_menu_select_sound(self):
        """Play menu selection sound"""
        self.play_sound("menu_select")
    
    def play_menu_hover_sound(self):
        """Play menu hover sound"""
        self.play_sound("menu_hover")