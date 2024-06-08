import pygame
import sys
import json

# Inicjalizacja Pygame
pygame.init()

# Ustawienia ekranu
screen_width = 800
screen_height = 740
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Scoreboard")

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Czcionka
font = pygame.font.Font(None, 36)
header_font = pygame.font.Font(None, 48)


# Funkcja wczytująca dane z pliku JSON
def load_scores_from_json(filename):
    with open(filename, "r") as file:
        data = json.load(file)
        previous_player = data["PREVIOUS_PLAYER"]
        scores = data["SCORES"]
    return previous_player, scores


# Funkcja rysująca tabelę wyników
def draw_scoreboard(scores):
    background_image = pygame.image.load("layouts/images/background.png")

    # Dostosuj rozmiar obrazu do rozmiaru ekranu
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

    # Wypełnij ekran za pomocą obrazu
    screen.blit(background_image, (0, 0))

    # Obliczanie wysokości tabeli na podstawie liczby wyników
    table_height = len(scores) * 50

    # Narysuj nowe tło tabeli
    pygame.draw.rect(screen, WHITE, (50, 50, 700, 50))
    pygame.draw.rect(screen, (52, 78, 91), (50, 50, 700, table_height + 70))

    # Szerokość kolumn
    col_width = 350

    # Narysowanie nagłówków tabeli
    header_name = header_font.render("PLAYER", True, BLACK)
    header_score = header_font.render("SCORE", True, BLACK)

    screen.blit(header_name, (50 + col_width // 2 - header_name.get_width() // 2, 75 - header_name.get_height() // 2))
    screen.blit(header_score,
                (400 + col_width // 2 - header_score.get_width() // 2, 75 - header_score.get_height() // 2))

    pygame.draw.line(screen, BLACK, (50, 100), (750, 100), 2)

    # Narysowanie wyników graczy
    y_offset = 130
    row_height = 40
    for player, score in scores.items():
        name_text = font.render(player, True, BLACK)
        score_text = font.render(str(score), True, BLACK)

        screen.blit(name_text, (50 + col_width // 2 - name_text.get_width() // 2,
                                y_offset + row_height // 2 - name_text.get_height() // 2 - 10))
        screen.blit(score_text, (400 + col_width // 2 - score_text.get_width() // 2,
                                 y_offset + row_height // 2 - score_text.get_height() // 2 - 10))

        y_offset += 50

    # Linie pionowe tabeli
    pygame.draw.line(screen, BLACK, (50, 50), (50, 100 + table_height + 20), 2)
    pygame.draw.line(screen, BLACK, (750, 50), (750, 100 + table_height + 20), 2)
    pygame.draw.line(screen, BLACK, (400, 50), (400, 100 + table_height + 20), 2)

    # Górna i dolna krawędź tabeli
    pygame.draw.line(screen, BLACK, (50, 50), (750, 50), 2)
    pygame.draw.line(screen, BLACK, (50, 100 + table_height + 20), (750, 100 + table_height + 20), 2)

    # Rysowanie guzika
    pygame.draw.rect(screen, GRAY, (screen_width // 2 - 50, 650, 100, 50))
    button_text = font.render("HELLO", True, BLACK)
    screen.blit(button_text, (screen_width // 2 - button_text.get_width() // 2, 665))


# Funkcja obsługująca kliknięcie przycisku
def handle_button_click():
    from menu import run_menu
    run_menu()


# Pętla gry
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if screen_width // 2 - 50 <= mouse_pos[0] <= screen_width // 2 + 50 and 650 <= mouse_pos[1] <= 700:
                handle_button_click()

    # Wczytaj dane z pliku JSON
    previous_player, scores = load_scores_from_json("layouts/leaderboard.json")

    # Tutaj rysujemy wszystkie elementy na ekranie
    draw_scoreboard(scores)

    # Aktualizujemy ekran
    pygame.display.flip()

pygame.quit()
sys.exit()
