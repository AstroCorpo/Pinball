import pygame
import os
from layouts.button import Button
from layouts.tools import generate_image


BUTTONS = ["continue", "options", "menu"]
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


def generate_pause_menu_layout(actions, WIDTH = 600, HEIGHT = 1000, spacing=10):
    

    global BUTTONS, SCRIPT_PATH

    max_width = 0
    collective_height = spacing
    layout = {}
    for name in BUTTONS:
        filename = name + '.png'
        img_path = os.path.join(SCRIPT_PATH, 'images', filename)
        img = None
        if os.path.exists(img_path):
            img = pygame.image.load(img_path)
        else:
            img = generate_image(name)

        img_width, img_height = img.get_width(), img.get_height()
        collective_height += img_height + spacing
        layout[name] = img
        max_width = max(max_width, img_width)

    max_width += 2 * spacing

    WIDTH = max(WIDTH, max_width)

    start = ((HEIGHT - collective_height) // 2)
    for name in BUTTONS:
        img = layout[name]
        img_width, img_height = img.get_width(), img.get_height()
        layout[name] = Button(img, ((WIDTH - img_width) // 2), start, action=actions.get(name))
        start += img_height + spacing

    return layout