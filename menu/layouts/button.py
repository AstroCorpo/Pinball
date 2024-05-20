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
            screen.fill(BACKGROUND_COLOR)
            if self.rect.collidepoint(event.pos) :
                if self.action:
                    self.action()