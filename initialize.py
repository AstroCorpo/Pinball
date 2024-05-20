print("running whole initialize.py")
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

from menu import run_menu
import pygame


if __name__ == "__main__":
    pygame.init()
    run_menu()
