print("running menu.py")
import pygame, os
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
LEADERBOARD_PATH = os.path.join(SCRIPT_PATH, "layouts", "leaderboard.json")
from layouts.main_menu import generate_main_menu_layout
import main
import json

RUNNING = True
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
WIDTH, HEIGHT = 800, 1000
BACKGROUND_COLOR = (52, 78, 91)
screen = None

class Button:
    def __init__(self, image, x, y, action=None):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.action = action

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def handle_event(self, event, screen, background_color):
        if event.type == pygame.MOUSEBUTTONDOWN:
            screen.fill(background_color)
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

def quit_menu():
    global RUNNING
    RUNNING = False

def key_bindings():
    global LAYOUT
    from layouts.controls_menu import generate_controls_menu_layout
    new_layout = generate_controls_menu_layout({"back": options_menu})
    LAYOUT = new_layout

def back_to_main_menu():
    global LAYOUT
    from layouts.main_menu import generate_main_menu_layout
    new_layout = generate_main_menu_layout({"play": nick_input_menu, "options": options_menu, "quit": quit_menu})
    LAYOUT = new_layout

def options_menu():
    global LAYOUT
    from layouts.options_menu import generate_options_menu_layout
    new_layout = generate_options_menu_layout({"back": back_to_main_menu, "keys": key_bindings, "change_color": change_color})
    LAYOUT = new_layout

def nick_input_menu():
    global LAYOUT
    from layouts.nick_input_menu import generate_nick_input_menu_layout
    new_layout = generate_nick_input_menu_layout({"confirm": selection_menu})
    LAYOUT = new_layout

def selection_menu():
    global LAYOUT
    from layouts.selection_menu import generate_selection_menu_layout
    new_layout = generate_selection_menu_layout({"map1": run_map1, "map2": run_map2, "map3": run_map3, "back": back_to_main_menu})
    LAYOUT = new_layout

def change_color():
    global BACKGROUND_COLOR
    if BACKGROUND_COLOR == (52, 78, 91):
        BACKGROUND_COLOR = (37, 232, 128)
    else:
        BACKGROUND_COLOR = (52, 78, 91)

def run_map1():
    global screen
    
    with open(LEADERBOARD_PATH, 'r') as file :
        leaderboard = json.load(file)
        
    main.run("default",leaderboard["PREVIOUS_PLAYER"], screen)

def run_map2():
    global screen
    with open(LEADERBOARD_PATH, 'r') as file :
        leaderboard = json.load(file)
        
    main.run("fancy",leaderboard["PREVIOUS_PLAYER"], screen)

def run_map3():
    global screen
    with open(LEADERBOARD_PATH, 'r') as file :
        leaderboard = json.load(file)
        
    main.run("third",leaderboard["PREVIOUS_PLAYER"], screen)

def scoreboard_menu():
    from leaderboard import run_leaderboard
    run_leaderboard()

def run_menu(type='main'):
    global screen
    global RUNNING, WIDTH, HEIGHT, LAYOUT, BACKGROUND_COLOR

    LAYOUT = generate_main_menu_layout({"quit": quit_menu, "play": nick_input_menu, "options": options_menu, "leader": scoreboard_menu})

    flags = pygame.NOFRAME if type != 'main' else 0

    info = pygame.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
    x = (SCREEN_WIDTH - WIDTH) // 2
    y = (SCREEN_HEIGHT - HEIGHT) // 2
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (x,0)
    os.environ['SDL_VIDEO_CENTERED'] = '0'

    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)

    pygame.display.set_caption("Flipper Main Menu")

    background_image = pygame.image.load("layouts/images/background.png")

    background_image = pygame.transform.scale(background_image, (800, 1000))

    screen.blit(background_image, (0, 0))

    while RUNNING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_menu()
                break
            for button in LAYOUT.values():
                button.handle_event(event, screen, BACKGROUND_COLOR)
        if not RUNNING:
            break

        for button in LAYOUT.values():
            button.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    from initialize import main_run
    main_run()