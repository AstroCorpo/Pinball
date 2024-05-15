print("running whole menu.py")
import pygame, os

RUNNING = True
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
MENU_WIDTH, MENU_HEIGHT = 300, 200
PAUSE_MENU_IMAGE_NAMES = ["keys", "options", "quit"]
MAIN_MENU_IMAGE_NAMES = ["logo", "select_map", "options", "quit"]

class Button:
    def __init__(self, image, x, y, action=None):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.action = action

    def draw(self, surface) :
        surface.blit(self.image, self.rect)

    def handle_event(self, event) :
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) :
                if self.action:
                    self.action()

def quit_menu() :
    global RUNNING
    RUNNING = False
    
def select_map():
    from map_selection import run_map_menu
    run_map_menu()

def options_menu():
    from options import run_options_menu
    run_options_menu()

def generate_image(name) :
    img = pygame.Surface((100, 50))
    img.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 24)
    text = font.render(name.capitalize(), True, (255, 255, 255))
    text_rect = text.get_rect(center=(img.get_width() // 2, img.get_height() // 2))
    img.blit(text, text_rect)
    return img
    
def generate_layout(icons, spacing=10) :
    global MENU_WIDTH, MENU_HEIGHT, SCRIPT_PATH

    actions = {"quit": quit_menu, "select_map": select_map, "options": options_menu}

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

    MENU_WIDTH = max(MENU_WIDTH, max_width)
    MENU_HEIGHT = max(MENU_HEIGHT, collective_height)

    start = spacing
    for name in icons:
        img = layout[name]
        img_width, img_height = img.get_width(), img.get_height()
        layout[name] = Button(img, (MENU_WIDTH // 2) - (img_width // 2), start, action=actions.get(name))
        start += img_height + spacing

    return layout


def run_main_menu(dimensions = None, type = 'main'):

    with open('globals.py', 'r') as file:
        lines = file.readlines()

    BACKGROUND_COLOR = eval(lines[0])

    global RUNNING, MENU_WIDTH, MENU_HEIGHT, PAUSE_MENU_IMAGE_NAMES, MAIN_MENU_IMAGE_NAMES

    if dimensions != None : MENU_WIDTH, MENU_HEIGHT = dimensions
    
    image_names = PAUSE_MENU_IMAGE_NAMES if type != 'main' else MAIN_MENU_IMAGE_NAMES

    pygame.init()

    layout = generate_layout(image_names)

    flags = pygame.NOFRAME if type != 'main' else 0
    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT), flags)

    pygame.display.set_caption("Flipper Main Menu")

    screen.fill(BACKGROUND_COLOR)

    while RUNNING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_menu()
                break
            for button in layout.values():
                button.handle_event(event)
        if not RUNNING: break

        for button in layout.values():
            button.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    run_main_menu()
