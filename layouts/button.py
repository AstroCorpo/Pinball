import pygame

class Button:
    def __init__(self, image, x, y, action=None):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.action = action

    def draw(self, surface) :
        surface.blit(self.image, self.rect)

    def handle_event(self, event, screen, BACKGROUND_COLOR) :
        if event.type == pygame.MOUSEBUTTONDOWN:
            background_image = pygame.image.load("layouts/images/background.jpg")

            # Dostosuj rozmiar obrazu do rozmiaru ekranu
            background_image = pygame.transform.scale(background_image, (800, 1000))

            # Wypełnij ekran za pomocą obrazu
            screen.blit(background_image, (0, 0))
            if self.rect.collidepoint(event.pos) :
                if self.action:
                    self.action()