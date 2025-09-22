#!/usr/bin/env python3
"""
Halloween Haunt: Candy Quest - Demo Launcher
A simple script to demonstrate how to run the game

This script checks for dependencies and provides helpful error messages.
"""

import sys
import os

def check_python_version():
    """Check if Python version is sufficient"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required.")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python: https://python.org/downloads/")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_pygame():
    """Check if Pygame is installed and working"""
    try:
        import pygame
        pygame.init()
        print(f"✅ Pygame {pygame.version.ver} is ready")
        return True
    except ImportError:
        print("❌ Error: Pygame is not installed")
        print("   Install with: pip install pygame")
        print("   Or: python -m pip install pygame")
        return False
    except Exception as e:
        print(f"❌ Error initializing Pygame: {e}")
        return False

def check_game_files():
    """Check if all required game files exist"""
    required_files = [
        'halloween_haunt.py',
        'entities.py', 
        'levels.py',
        'ui.py',
        'sound.py',
        'game_manager.py',
        'special_features.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file} found")
    
    if missing_files:
        print(f"❌ Error: Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def create_assets_folder():
    """Create assets folder structure if it doesn't exist"""
    asset_dirs = [
        'assets',
        'assets/sprites',
        'assets/tiles', 
        'assets/music',
        'assets/sfx',
        'assets/ui',
        'assets/fonts'
    ]
    
    created_dirs = []
    for dir_path in asset_dirs:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                created_dirs.append(dir_path)
            except OSError as e:
                print(f"⚠️  Warning: Could not create {dir_path}: {e}")
    
    if created_dirs:
        print(f"📁 Created asset directories: {', '.join(created_dirs)}")
        print("   Add custom sprites, sounds, and fonts to enhance the game!")
    else:
        print("📁 Asset directories already exist")

def run_game():
    """Run the main game"""
    try:
        print("\n🎮 Starting Halloween Haunt: Candy Quest...")
        print("   Press F11 for fullscreen, ESC for pause menu")
        print("   Use WASD/arrows to move, SPACE to interact")
        print("   Collect 15 candies and return home to win each level!")
        print("\n" + "="*50)
        
        # Import and run the main game
        from halloween_haunt import main
        main()
        
    except ImportError as e:
        print(f"❌ Error importing game modules: {e}")
        print("   Make sure all game files are in the same directory")
        return False
    except Exception as e:
        print(f"❌ Error running game: {e}")
        return False
    
    return True

def main():
    """Main demo launcher"""
    print("🎃 Halloween Haunt: Candy Quest - Demo Launcher 🎃")
    print("                    BETA VERSION")
    print("="*50)
    
    # Check system requirements
    print("\n🔍 Checking system requirements...")
    
    if not check_python_version():
        return
    
    if not check_pygame():
        return
    
    print("\n📋 Checking game files...")
    
    if not check_game_files():
        return
    
    print("\n📁 Setting up assets...")
    create_assets_folder()
    
    print("\n✅ All checks passed! Ready to play!")
    
    # Ask user if they want to start the game
    try:
        response = input("\n🎮 Start the game now? (y/n): ").lower().strip()
        if response in ['y', 'yes', '']:
            run_game()
        else:
            print("🎃 Run 'python halloween_haunt.py' when you're ready to play!")
    except KeyboardInterrupt:
        print("\n👻 See you later! Happy Halloween!")

if __name__ == "__main__":
    main()