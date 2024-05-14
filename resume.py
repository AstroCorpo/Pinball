print("running whole menu.py")
import pygame, os

# Global variables
RUNNING = True
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
RESUME_WIDTH, RESUME_HEIGHT = 300, 200
RESUME_IMAGE_NAMES = ["resume", "options", "back_to_menu"]


class Button:
    def __init__(self, image, x, y, action=None):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.action = action

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()


def continue_game():
    exit(0)
    # odpauzowanie, wrócenie do gry

def options_menu():
    from resume_options import run_resume_options_menu
    run_resume_options_menu()

def back_to_main_menu():
    from menu import run_main_menu
    run_main_menu()
    # I tu chyba jeszcze quit z maina

def generate_image(name):
    img = pygame.Surface((100, 50))
    img.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 24)
    text = font.render(name.capitalize(), True, (255, 255, 255))
    text_rect = text.get_rect(center=(img.get_width() // 2, img.get_height() // 2))
    img.blit(text, text_rect)
    return img


def generate_layout(icons, spacing=10):
    global RESUME_WIDTH, RESUME_HEIGHT, SCRIPT_PATH

    actions = {"resume": continue_game, "options": options_menu, "back_to_menu": back_to_main_menu}

    collective_height = spacing
    max_width = 0
    layout = {}
    for name in icons:
        filename = name + '.png'
        img_path = os.path.join(SCRIPT_PATH, 'images', filename)
        img = None
        if os.path.exists(img_path):
            img = pygame.image.load(img_path)
        else:
            img = generate_image(name)

        img_width, img_height = img.get_width(), img.get_height()
        layout[name] = img
        collective_height += img_height + spacing
        max_width = max(max_width, img_width)

    max_width += 2 * spacing

    RESUME_WIDTH = max(RESUME_WIDTH, max_width)
    RESUME_HEIGHT = max(RESUME_HEIGHT, collective_height)

    start = spacing
    for name in icons:
        img = layout[name]
        img_width, img_height = img.get_width(), img.get_height()
        layout[name] = Button(img, (RESUME_WIDTH // 2) - (img_width // 2), start, action=actions.get(name))
        start += img_height + spacing

    return layout


def run_resume_menu(dimensions=None, type='main'):
    with open('globals.py', 'r') as file:
        lines = file.readlines()

    BACKGROUND_COLOR = eval(lines[0])

    global RUNNING, RESUME_WIDTH, RESUME_HEIGHT, RESUME_IMAGE_NAMES

    if dimensions != None: RESUME_WIDTH, RESUME_HEIGHT = dimensions

    image_names = RESUME_IMAGE_NAMES

    pygame.init()

    layout = generate_layout(image_names)

    # Set up the screen
    flags = pygame.NOFRAME if type != 'main' else 0
    screen = pygame.display.set_mode((RESUME_WIDTH, RESUME_HEIGHT), flags)

    pygame.display.set_caption("Flipper Main Menu")

    while RUNNING:
        for event in pygame.event.get():
            for button in layout.values():
                button.handle_event(event)
        if not RUNNING: break

        screen.fill(BACKGROUND_COLOR)

        for button in layout.values():
            button.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_resume_menu()
