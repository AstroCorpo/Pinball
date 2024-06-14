import pygame


def generate_image(name, width=600, height=200, margin=8, font_size=60):
    font = pygame.font.SysFont(None, font_size)
    lines = name.split('\n')  # Podziel tekst na linie
    text_surfaces = []
    for line in lines:
        words = line.strip().split()
        capitalized_words = [word.capitalize() for word in words]  # Kapitalizuj każde słowo
        capitalized_line = ' '.join(capitalized_words)
        text_surfaces.append(font.render(capitalized_line, True, (255, 255, 255)))

    max_width = max(surface.get_width() for surface in text_surfaces)
    total_height = sum(surface.get_height() for surface in text_surfaces)

    total_margin = margin + 5
    img_width = width
    img_height = height
    img = pygame.Surface((img_width, img_height), pygame.SRCALPHA)  # Ustaw SRCALPHA dla przezroczystości
    pygame.draw.rect(img, (0, 0, 0, 100), img.get_rect(), border_radius=10)  # Dodaj gradient lub cień do tła

    # Rysuj tekst w kolejnych wierszach
    y_offset = (img_height - total_height) // 2
    for surface in text_surfaces:
        x_offset = (img_width - surface.get_width()) // 2
        img.blit(surface, (x_offset, y_offset))
        y_offset += surface.get_height()

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
