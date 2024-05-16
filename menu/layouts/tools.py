import pygame

def generate_image(name) :
    img = pygame.Surface((100, 50))
    img.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 24)
    text = font.render(name.capitalize(), True, (255, 255, 255))
    text_rect = text.get_rect(center=(img.get_width() // 2, img.get_height() // 2))
    img.blit(text, text_rect)
    return img