import os
import json
import pygame as pg

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
LEADERBOARD_PATH = os.path.join(SCRIPT_PATH, "leaderboard.json")

COLOR_INACTIVE = pg.Color('black')
COLOR_ACTIVE = pg.Color('dodgerblue2')
INPUT_BACKGROUND_COLOR = pg.Color('white')  # White background color for the input box

class InputBox:
    def __init__(self, x, y, action=None, text=''):
        pg.font.init()
        self.FONT = pg.font.SysFont("Comic Sans MS", 50)
        self.backtext = "Here type your nickname!"
        self.color = COLOR_INACTIVE
        self.txt_surface = self.FONT.render(text, True, self.color)
        self.rect = pg.Rect(x - 110, y + 80, 600, 200)
        self.text = ''
        self.active = False
        self.action = action

    def handle_event(self, event, screen, BACKGROUND_COLOR):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    player_name = self.text

                    with open(LEADERBOARD_PATH, 'r') as file:
                        leaderboard = json.load(file)

                    leaderboard["PREVIOUS_PLAYER"] = player_name

                    with open(LEADERBOARD_PATH, 'w') as FILE:
                        json.dump(leaderboard, FILE, indent=4)

                    background_image = pg.image.load("layouts/images/background.png")
                    background_image = pg.transform.scale(background_image, (800, 1000))
                    screen.blit(background_image, (0, 0))
                    self.text = ''
                    if self.action:
                        self.action()
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

        if event.type == pg.KEYUP and self.active:
            self.txt_surface = self.FONT.render(self.backtext if len(self.text) == 0 else self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Fill the input box with white background
        pg.draw.rect(screen, INPUT_BACKGROUND_COLOR, self.rect, border_radius=10)
        # Calculate position to center the text
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        # Draw the text surface
        screen.blit(self.txt_surface, (text_rect.x, text_rect.y))
        # Draw the border of the input box
        pg.draw.rect(screen, self.color, self.rect, 2, border_radius=10)