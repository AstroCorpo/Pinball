print("running whole initialize.py")
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
os.environ['SDL_AUDIODRIVER'] = 'dummy'


from menu import run_main_menu

import pygame
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = min(400, info.current_w), min(500,info.current_h)
pygame.quit()


if __name__ == "__main__":
    # menu.MENU_WIDTH, menu.MENU_HEIGHT = WIDTH, HEIGHT
    
    run_main_menu((WIDTH, HEIGHT))
