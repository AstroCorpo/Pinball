import pygame
import sys
import json

# Inicjalizacja Pygame
pygame.init()

# Ustawienia ekranu
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Leaderboard")

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
BLUE = (0, 0, 255)

# Czcionka
font = pygame.font.Font(None, 40)
title_font = pygame.font.Font(None, 60)


# Funkcja do ładowania danych z pliku JSON
def load_scores_from_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    scores = data['SCORES']
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_scores


# Przykładowe dane do leaderboarda
leaderboard_data = load_scores_from_json('leaderboard.json')


# Funkcja do rysowania leaderboarda
def draw_leaderboard(screen, data):
    screen.fill(WHITE)

    # Tytuł
    title_text = title_font.render("Leaderboard", True, BLUE)
    title_rect = title_text.get_rect(center=(screen_width // 2, 50))
    screen.blit(title_text, title_rect)

    # Wysokość jednego wiersza
    row_height = 60

    # Rysowanie wierszy z danymi
    for index, (name, score) in enumerate(data):
        y_position = 150 + index * row_height

        # Tło wiersza
        if index % 2 == 0:
            row_color = GREY
        else:
            row_color = WHITE

        pygame.draw.rect(screen, row_color, (100, y_position, 600, row_height))

        # Nazwa gracza
        name_text = font.render(name, True, BLACK)
        name_rect = name_text.get_rect(midleft=(150, y_position + row_height // 2))
        screen.blit(name_text, name_rect)

        # Wynik gracza
        score_text = font.render(str(score), True, BLACK)
        score_rect = score_text.get_rect(midright=(650, y_position + row_height // 2))
        screen.blit(score_text, score_rect)


# Główna pętla gry
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_leaderboard(screen, leaderboard_data)
    pygame.display.flip()

# Zakończenie Pygame
pygame.quit()
sys.exit()
