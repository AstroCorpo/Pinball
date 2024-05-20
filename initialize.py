print("running whole initialize.py")
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

from menu import run_menu
import pygame

def main_run() :
    pygame.init()
    run_menu()

if __name__ == "__main__":
    main_run()