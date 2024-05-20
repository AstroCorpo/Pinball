print("running menu.py")
import pygame, os
from layouts.pause_menu import generate_pause_menu_layout

RUNNING = True
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
WIDTH, HEIGHT = 620, 640
BACKGROUND_COLOR = (52, 78, 91)

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

def back_to_pause_menu():
    global LAYOUT
    from layouts.pause_menu import generate_pause_menu_layout
    new_layout = generate_pause_menu_layout({"menu": back_to_main_menu, "continue": select_map, "options": options_menu})
    LAYOUT = new_layout

def back_to_main_menu():
    global LAYOUT
    from layouts.main_menu import generate_main_menu_layout
    new_layout = generate_main_menu_layout({"quit": quit_menu, "play": select_map, "options": options_menu})
    LAYOUT = new_layout

def change_color():
    global BACKGROUND_COLOR
    if BACKGROUND_COLOR == (52, 78, 91):
        BACKGROUND_COLOR = (37, 232, 128)
    else:
        BACKGROUND_COLOR = (52, 78, 91)

def options_menu():
    global LAYOUT
    from layouts.options_menu import generate_options_menu_layout
    new_layout = generate_options_menu_layout({"back": back_to_pause_menu, "keys": key_bindings, "change_color": change_color})
    LAYOUT = new_layout

def select_map():
    global LAYOUT
    from layouts.selection_menu import generate_selection_menu_layout
    new_layout = generate_selection_menu_layout({"map1": run_map1, "map2": run_map2, "map3": run_map3, "back": back_to_pause_menu})
    LAYOUT = new_layout

def run_map1():
    import main
    main.run("default")

def run_map2():
    import main
    main.run("fancy")

def run_map3():
    import main
    main.run("third")

def run_pause_menu(type='main'):
    global RUNNING, WIDTH, HEIGHT, LAYOUT, BACKGROUND_COLOR
     
    pygame.init()

    LAYOUT = generate_pause_menu_layout({"continue": None, "options": options_menu, "menu": back_to_main_menu})

    flags = pygame.NOFRAME if type != 'main' else 0
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)

    pygame.display.set_caption("Flipper Main Menu")

    screen.fill(BACKGROUND_COLOR)

    while RUNNING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_menu()
                break
            for button in LAYOUT.values():
                button.handle_event(event, screen, BACKGROUND_COLOR)
        if not RUNNING: break

        for button in LAYOUT.values():
            button.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    run_pause_menu()