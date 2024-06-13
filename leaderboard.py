import pygame
import sys
import json
def run_leaderboard():
    pygame.init()

    screen_width = 800
    screen_height = 1000
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Scoreboard")

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    font = pygame.font.Font(None, 36)
    header_font = pygame.font.Font(None, 48)

    button_image = pygame.image.load("layouts/images/back.png")
    button_image = pygame.transform.scale(button_image, (100, 50))

    def load_scores_from_json(filename):
        with open(filename, "r") as file:
            data = json.load(file)
            previous_player = data["PREVIOUS_PLAYER"]
            scores = data["SCORES"]
        return previous_player, scores

    def draw_scoreboard(scores):
        background_image = pygame.image.load("layouts/images/background.png")

        background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

        screen.blit(background_image, (0, 0))

        table_height = len(scores) * 50

        pygame.draw.rect(screen, WHITE, (50, 50, 700, 50))
        pygame.draw.rect(screen, (52, 78, 91), (50, 50, 700, table_height + 70))

        col_width = 350

        header_name = header_font.render("PLAYER", True, BLACK)
        header_score = header_font.render("SCORE", True, BLACK)

        screen.blit(header_name,
                    (50 + col_width // 2 - header_name.get_width() // 2, 75 - header_name.get_height() // 2))
        screen.blit(header_score,
                    (400 + col_width // 2 - header_score.get_width() // 2, 75 - header_score.get_height() // 2))

        pygame.draw.line(screen, BLACK, (50, 100), (750, 100), 2)

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

        pygame.draw.line(screen, BLACK, (50, 50), (50, 100 + table_height + 20), 2)
        pygame.draw.line(screen, BLACK, (750, 50), (750, 100 + table_height + 20), 2)
        pygame.draw.line(screen, BLACK, (400, 50), (400, 100 + table_height + 20), 2)

        pygame.draw.line(screen, BLACK, (50, 50), (750, 50), 2)
        pygame.draw.line(screen, BLACK, (50, 100 + table_height + 20), (750, 100 + table_height + 20), 2)

        button_rect = button_image.get_rect(center=(screen_width // 2, 675))
        screen.blit(button_image, button_rect)

    def handle_button_click():
        from menu import run_menu
        run_menu()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                handle_button_click()

        previous_player, scores = load_scores_from_json("layouts/leaderboard.json")

        draw_scoreboard(scores)

        pygame.display.flip()

    pygame.quit()
    # sys.exit()