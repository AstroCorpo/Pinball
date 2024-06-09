import pygame
import os
from layouts.button import Button
from layouts.input import InputBox
from layouts.tools import generate_image

INPUTS = ["input"]
BUTTONS = ["What's your name?"]
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
BUTTONS2 = ["confirm"]

def generate_nick_input_menu_layout(actions, spacing=10):
    WIDTH = 600

    global BUTTONS, SCRIPT_PATH

    max_width = 0
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
        layout[name] = img
        max_width = max(max_width, img_width)

    for name in BUTTONS2:
        filename = name + '.png'
        img_path = os.path.join(SCRIPT_PATH, 'images', filename)
        img = None
        if os.path.exists(img_path):
            img = pygame.image.load(img_path)
        else:
            img = generate_image(name)

        img_width, img_height = img.get_width(), img.get_height()
        layout[name] = img
        max_width = max(max_width, img_width)

    max_width += 2 * spacing

    WIDTH = max(WIDTH, max_width)

    start = spacing + 90

    for name in BUTTONS:
        img = layout[name]
        img_width, img_height = img.get_width(), img.get_height()
        layout[name] = Button(img, (WIDTH // 2) - (img_width // 2) + 90, start, action=actions.get(name))
        start += img_height + spacing

    for name in INPUTS:
        layout[name] = InputBox(WIDTH // 2 - 100, start, action=actions.get("box"))
        start += 10 + spacing

    start = spacing + 510

    for name in BUTTONS2:
        img = layout[name]
        img_width, img_height = img.get_width(), img.get_height()
        layout[name] = Button(img, (WIDTH // 2) - (img_width // 2) + 90, start, action=actions.get(name))
        start += img_height + spacing

    return layout