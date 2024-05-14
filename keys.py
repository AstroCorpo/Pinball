print("running keys.py")
import pygame, os

RUNNING = True
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
KEYS_WIDTH, KEYS_HEIGHT = 400, 200
KEYS_IMAGE_NAMES = ["back"]

class Button:
    def __init__(self, image, x, y, action=None):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.action = action

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def event_handler(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

def back_to_options():
    from options import run_options_menu
    run_options_menu()

def generate_leyout(icons, spacing = 10):
    global KEYS_WIDTH, KEYS_HEIGHT, KEYS_IMAGE_NAMES

    actions = {"back": back_to_options}

    collective_height = spacing
    max_width = 0
    layout = {}

    # Wklejanie zdjęcia i sprawdzanie wymiarów
    for name in icons:
        filename = name + ".png"
        image_path = os.path.join(SCRIPT_PATH, 'images', filename)
        image = pygame.image.load(image_path)

        image_width, image_height = image.get_width(), image.get_height()
        layout[name] = image
        collective_height += image_height + spacing
        max_width = max(max_width, image_width)

    max_width += 2 * spacing

    KEYS_WIDTH = max(KEYS_WIDTH, max_width)
    KEYS_HEIGHT = max(KEYS_HEIGHT, collective_height)

    start = spacing
    for name in icons:
        image = layout[name]
        image_width, image_height = image.get_width(), image.get_height()
        layout[name] = Button(image, (KEYS_WIDTH // 2) - (image_width // 2), start, action=actions.get(name))
        start += image_height + spacing

    return layout

def run_keys_menu():

    with open('globals.py', 'r') as file:
        lines = file.readlines()

    BACKGROUND_COLOR = eval(lines[0])

    global RUNNING, KEYS_WIDTH, KEYS_HEIGHT, KEYS_IMAGE_NAMES

    pygame.init()

    layout = generate_leyout(KEYS_IMAGE_NAMES)

    screen = pygame.display.set_mode((KEYS_WIDTH, KEYS_HEIGHT), 0)

    pygame.display.set_caption("Key Bindings Menu")

    while RUNNING:
        for event in pygame.event.get():
            for button in layout.values():
                button.event_handler(event)
        if not RUNNING:
            break

        screen.fill(BACKGROUND_COLOR)

        font = pygame.font.Font(None, 36)
        text1 = font.render("Space - Shoot ball", True, (0, 0, 0))
        text2 = font.render("Left arrow - Left flipper", True, (0, 0, 0))
        text3 = font.render("Right arrow - Right flipper", True, (0, 0, 0))

        text_rect = text1.get_rect()
        text_rect.center = (KEYS_WIDTH // 2, KEYS_HEIGHT // 2 + 10)
        screen.blit(text1, text_rect)

        text_rect = text2.get_rect()
        text_rect.center = (KEYS_WIDTH // 2, KEYS_HEIGHT // 2 + 40)
        screen.blit(text2, text_rect)

        text_rect = text3.get_rect()
        text_rect.center = (KEYS_WIDTH // 2, KEYS_HEIGHT // 2 + 70)
        screen.blit(text3, text_rect)

        for button in layout.values():
            button.draw(screen)

        pygame.display.flip()

    pygame.quit()