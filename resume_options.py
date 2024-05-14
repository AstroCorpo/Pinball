print("running resume options.py")
import pygame, os

RUNNING = True
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
SETTINGS_WIDTH, SETTINGS_HEIGHT = 300, 200
SETTINGS_MENU_IMAGE_NAMES = ["back", "change color", "keys"]

class Button:
    def __init__(self, image, x, y, action=None) :
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.action = action

    def draw(self, surface) :
        surface.blit(self.image, self.rect)

    def handle_event(self, event) :
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

def generate_image(name) :
    img = pygame.Surface((100, 50))
    img.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 24)
    text = font.render(name.capitalize(), True, (255, 255, 255))
    text_rect = text.get_rect(center=(img.get_width() // 2, img.get_height() // 2))
    img.blit(text, text_rect)
    return img

def back_to_main_menu():
    from menu import run_main_menu
    run_main_menu()

def back_to_resume():
    from resume import run_resume_menu
    run_resume_menu()

def change_color():
    with open('globals.py', 'r') as file:
        lines = file.readlines()

    first = "(52, 78, 91)"
    second = "(37, 232, 128)"

    with open('globals.py', 'w') as file:
        if lines[0] == first:
            lines[0] = second
            file.writelines(lines)
        elif lines[0] == second:
            lines[0] = first
            file.writelines(lines)

def key_bindings():
    from keys import run_keys_menu
    run_keys_menu()

def generate_layout(icons, spacing=10):
    global SETTINGS_WIDTH, SETTINGS_HEIGHT, SCRIPT_PATH

    actions = {"back": back_to_resume, "keys": key_bindings, "change color": change_color}

    collective_height = spacing
    max_width = 0
    layout = {}
    for name in icons:
        filename = name + '.png'
        img_path = os.path.join(SCRIPT_PATH, 'images', filename)
        if os.path.exists(img_path):
            img = pygame.image.load(img_path)
        else:
            img = generate_image(name)

        img_width, img_height = img.get_width(), img.get_height()
        layout[name] = img
        collective_height += img_height + spacing
        max_width = max(max_width, img_width)

    max_width += 2 * spacing

    SETTINGS_WIDTH = max(SETTINGS_WIDTH, max_width)
    SETTINGS_HEIGHT = max(SETTINGS_HEIGHT, collective_height)

    start = spacing
    for name in icons:
        img = layout[name]
        img_width, img_height = img.get_width(), img.get_height()
        layout[name] = Button(img, (SETTINGS_WIDTH // 2) - (img_width // 2), start, action=actions.get(name))
        start += img_height + spacing

    return layout


def run_resume_options_menu(dimensions=None, type='main_menu'):

    global RUNNING, SETTINGS_WIDTH, SETTINGS_HEIGHT, SETTINGS_MENU_IMAGE_NAMES

    if dimensions != None:
        SETTINGS_WIDTH, SETTINGS_HEIGHT = dimensions

    image_names = SETTINGS_MENU_IMAGE_NAMES

    pygame.init()

    layout = generate_layout(image_names)

    flags = pygame.NOFRAME if type != 'main_menu' else 0
    screen = pygame.display.set_mode((SETTINGS_WIDTH, SETTINGS_HEIGHT), flags)

    pygame.display.set_caption("Flipper Main Menu")

    while RUNNING:
        with open('globals.py', 'r') as file:
            lines = file.readlines()

        BACKGROUND_COLOR = eval(lines[0])
        for event in pygame.event.get():
            for button in layout.values():
                button.handle_event(event)
        if not RUNNING: break

        screen.fill(BACKGROUND_COLOR)

        for button in layout.values():
            button.draw(screen)

        pygame.display.flip()

    pygame.quit()