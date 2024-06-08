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


def generate_text_surface(text, font_size=24, color=(255, 255, 255)):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    return text_surface


import pygame
from pygame.rect import Rect

def draw_table(surface, headers, data, x, y, header_font_size=24, data_font_size=20, header_color=(255, 255, 255), data_color=(200, 200, 200), padding=10, border_color=(255, 255, 255), border_width=2):
    # Ustawiamy fonty
    pygame.font.init()
    header_font = pygame.font.SysFont(None, header_font_size)
    data_font = pygame.font.SysFont(None, data_font_size)

    # Obliczamy wymiary komórek
    cell_widths = []
    for i, header in enumerate(headers):
        header_surface = header_font.render(header, True, header_color)
        cell_widths.append(header_surface.get_width())
    for row in data:
        for i, cell in enumerate(row):
            cell_surface = data_font.render(cell, True, data_color)
            if len(cell_widths) <= i:
                cell_widths.append(cell_surface.get_width())
            else:
                cell_widths[i] = max(cell_widths[i], cell_surface.get_width())

    # Obliczamy wymiary tabeli
    table_width = sum(cell_widths) + (len(cell_widths) - 1) * padding
    table_height = (header_font_size + padding) + (data_font_size + padding) * len(data)

    # Rysujemy ramkę tabeli
    pygame.draw.rect(surface, border_color, (x, y, table_width, table_height), border_width)

    # Rysujemy nagłówki
    cell_x = x
    for i, header in enumerate(headers):
        header_surface = header_font.render(header, True, header_color)
        header_rect = header_surface.get_rect(topleft=(cell_x, y))
        surface.blit(header_surface, header_rect)
        cell_x += cell_widths[i] + padding

    # Rysujemy dane
    cell_y = y + header_font_size + padding
    for row in data:
        cell_x = x
        for i, cell in enumerate(row):
            cell_surface = data_font.render(cell, True, data_color)
            cell_rect = cell_surface.get_rect(topleft=(cell_x, cell_y))
            surface.blit(cell_surface, cell_rect)
            cell_x += cell_widths[i] + padding
        cell_y += data_font_size + padding
