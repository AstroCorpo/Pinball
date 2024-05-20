import pygame

def generate_image(name, margin=8):
    
    font = pygame.font.SysFont(None, 24)
    text = font.render(name.capitalize(), True, (255, 255, 255))
    
    text_width, text_height = text.get_size()
    
    total_margin = margin + 5
    img_width = text_width + 2 * total_margin
    img_height = text_height + 2 * total_margin
    img = pygame.Surface((img_width, img_height))
    img.fill((255, 255, 255))
    inner_rect = pygame.Rect(5, 5, img_width - 10, img_height - 10)
    pygame.draw.rect(img, (0, 0, 0), inner_rect)
    text_rect = text.get_rect(center=(img_width // 2, img_height // 2))
    img.blit(text, text_rect)
    
    return img
