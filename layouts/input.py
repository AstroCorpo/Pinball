import os
import json
import pygame as pg

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
LEADERBOARD_PATH = os.path.join(SCRIPT_PATH, "leaderboard.json")

COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')

class InputBox:
    def __init__(self, x, y, action=None, text=''):
        pg.font.init()
        self.FONT = pg.font.SysFont("Comic Sans MS", 16)
        self.backtext = "Here type your nickname!"
        self.color = COLOR_INACTIVE
        self.txt_surface = self.FONT.render(text, True, self.color)
        self.txt_surface = self.FONT.render(self.backtext, True, self.color)
        self.rect = pg.Rect(x, y, 200, 32)  # Initial width and height
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

                    screen.fill(BACKGROUND_COLOR)
                    self.text = ''
                    self.action()
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                    screen.fill(BACKGROUND_COLOR)
                else:
                    screen.fill(BACKGROUND_COLOR)
                    self.text += event.unicode
                    self.draw(screen)
        if event.type == pg.KEYUP:
            if self.active:
                screen.fill(BACKGROUND_COLOR)
                if len(self.text) == 0:
                    self.txt_surface = self.FONT.render(self.backtext, True, self.color)
                if len(self.text) > 0:
                    self.txt_surface = self.FONT.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pg.draw.rect(screen, self.color, self.rect, 2)