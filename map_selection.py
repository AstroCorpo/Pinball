print("running map_selection.py")
import pygame, os

RUNNING = True
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
MAP_WIDTH, MAP_HEIGHT = 300, 200
MAP_IMAGE_NAMES = ["map1", "map2", "map3", "back"]

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


def quit_menu():
    global RUNNING
    RUNNING = False

def run_map1():
    import main, threading
    thread = threading.Thread(target=main.run("default"))
    thread.start()
    thread.join()


def run_map2():
    import main
    main.run("fancy")

def run_map3():
    import main
    main.run("third")

def back_to_main_menu():
    from menu import run_main_menu
    run_main_menu()


def generate_image(name):
    img = pygame.Surface((100, 50))
    img.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 24)
    text = font.render(name.capitalize(), True, (255, 255, 255))
    text_rect = text.get_rect(center=(img.get_width() // 2, img.get_height() // 2))
    img.blit(text, text_rect)
    return img


def generate_layout(icons, spacing=10):
    global MAP_WIDTH, MAP_HEIGHT, SCRIPT_PATH

    actions = {"map1": run_map1, "map2": run_map2, "map3": run_map3, "back": back_to_main_menu}

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

    MAP_WIDTH = max(MAP_WIDTH, max_width)
    MAP_HEIGHT = max(MAP_HEIGHT, collective_height)

    start = spacing
    for name in icons:
        img = layout[name]
        img_width, img_height = img.get_width(), img.get_height()
        layout[name] = Button(img, (MAP_WIDTH // 2) - (img_width // 2), start, action=actions.get(name))
        start += img_height + spacing

    return layout


def run_map_menu(dimensions=None, type='main'):
    with open('globals.py', 'r') as file:
        lines = file.readlines()

    BACKGROUND_COLOR = eval(lines[0])

    global RUNNING, MAP_WIDTH, MAP_HEIGHT, MAP_IMAGE_NAMES

    if dimensions != None: MENU_WIDTH, MENU_HEIGHT = dimensions

    image_names = MAP_IMAGE_NAMES

    pygame.init()

    layout = generate_layout(image_names)

    flags = pygame.NOFRAME if type != 'main' else 0
    screen = pygame.display.set_mode((MAP_WIDTH, MAP_HEIGHT), flags)

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
    run_map_menu()
