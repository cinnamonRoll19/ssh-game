#!/usr/bin/env python3
"""
SSH Keys Educational Game Launcher
Запускатель обучающей игры о SSH-ключах
"""

import os
import sys
import pygame

# Make sure we're in the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the current directory to Python path
sys.path.insert(0, script_dir)

# Check if required modules are installed
required_modules = ['pygame', 'cryptography', 'pyOpenSSL']
missing_modules = []

for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print("Отсутствуют необходимые модули. Установите их с помощью команды:")
    print(f"pip install {' '.join(missing_modules)}")
    print("\nAborting game launch.")
    sys.exit(1)

# Initialize pygame
pygame.init()

# Import and run the game
try:
    from main import Game
    game = Game()
    game.run()
except Exception as e:
    print(f"Error launching game: {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit(1) 