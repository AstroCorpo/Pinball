import pygame
import button
import pymunk
import pygame
import random
import numpy as np
from pygame.locals import *
import pymunk.pygame_util
from collections import deque

# Ustawienie wymiarów okna
# width, height = 2550, 1340
width, height = 800, 1000

ELASTICITY = 0.7
BALL_RADIUS = 15
NO_BALLS = 3
FRICTION = 0.5
WALL_WIDTH = 10
# Definicja kolorów
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
FLIPPER_LENGTH = 60
FLIPPER_ANGLE = -np.pi / 6
FLIPPER_X = np.abs(FLIPPER_LENGTH * np.cos(FLIPPER_ANGLE))
FLIPPER_Y = np.abs(FLIPPER_LENGTH * np.sin(FLIPPER_ANGLE))
POINTS = 0

base_width = width
width = width + 3 * WALL_WIDTH + 2 * BALL_RADIUS



def rand_color() :
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))

def rand_pos() :
    global WALL_WIDTH, width, height
    return (random.randint(WALL_WIDTH,width-WALL_WIDTH),random.randint(WALL_WIDTH,height-WALL_WIDTH))

def poly_field(points):
    n = len(points)
    field = 0
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        field += (x1 * y2 - x2 * y1)
    return abs(field) / 2

def create_wall(start_pos = rand_pos(), end_pos = rand_pos(), color = rand_color(), width = WALL_WIDTH, friction = FRICTION, elasticity = ELASTICITY, static = True) :
    global object_colors, space
    if static :
        wall = pymunk.Body(body_type=pymunk.Body.STATIC)
    else :
        wall = pymunk.Body()
    wall_shape = pymunk.Segment(wall, start_pos, end_pos, width)
    wall_shape.friction = friction
    wall_shape.elasticity = elasticity
    object_colors[wall_shape] = color
    space.add(wall, wall_shape)
    return wall, wall_shape



def create_ball(r = BALL_RADIUS, position = rand_pos(), static = False, mass = None, color = rand_color(), elasticity = ELASTICITY) :
    global object_colors, space
    ball = None
    if static : ball = pymunk.Body(body_type=pymunk.Body.STATIC)
    else : ball = pymunk.Body()
    ball.position = position
    radius = r
    ball_shape = pymunk.Circle(ball, radius)
    if mass is not None :
        ball_shape.mass = mass
    else :
        ball_shape.mass = ball_shape.area/20
    ball_shape.elasticity = elasticity
    object_colors[ball_shape] = color
    space.add(ball, ball_shape)
    return ball,ball_shape



# ball2,ball2_shape = create_ball(r = BALL_RADIUS, position = rand_pos(), static = False, mass = None, color = rand_color(), elasticity = ELASTICITY)

def generate_flipper_points(d, posterior_angle = 0, density1 = 0, density2 = 0) :
    c_1 = (0,0)
    c_2 = (-d,0)
    r1 = 4*(d/36)
    r2 = 2.5*(d/36)

    x = np.sqrt(d**2 - (r1 - r2)**2)
    alpha = np.pi - np.arcsin(x/d)

    f1 = lambda x: (c_1[0] + r1*np.cos(x),c_1[1] + r1*np.sin(x))
    f2 = lambda x: (c_2[0] + r2*np.cos(x),c_2[1] + r2*np.sin(x))

    if density1 == 0 : density1 = r1
    if density2 == 0 : density2 = r2

    step = (2*alpha*r1 / density1) / (2*np.pi*r1)

    changed = False

    func = f1
    points = deque()

    angle = 0
    while angle < np.pi :
        point = func(angle)
        points.append(point)
        if point[1] != 0 :
            points.appendleft((point[0],-point[1]))
        if not changed and angle >= alpha :
            func = f2
            step = (2*alpha*r2 / density2) / (2*np.pi*r2)
            changed = True

        else : angle += step


    points = list(points)

    rotation_point = (np.cos(posterior_angle), np.sin(posterior_angle))

    multiply = lambda x,y : (x[0]*y[0] - x[1]*y[1],x[0]*y[1] + x[1]*y[0])

    for i in range(len(points)) :
        points[i] = multiply(points[i],rotation_point)

    return list(points)



def create_flipper(points, position, side, color) :

    mass = poly_field(points)
    moment = pymunk.moment_for_poly(mass, points)

    init_angle = 0

    if side == 'left' :
        for i in range(len(points)) : points[i] = (-points[i][0],points[i][1])
        init_angle = -init_angle
    # right flipper
    flipper_body = pymunk.Body(mass, moment)
    flipper_body.position = position
    flipper_shape = pymunk.Poly(flipper_body, points)
    flipper_shape.elasticity = ELASTICITY
    space.add(flipper_body, flipper_shape)

    object_colors[flipper_shape] = color

    return flipper_body, flipper_shape

def destroy_blockade() :
    space.remove(divide)
    space.remove(divide_shape)

    return create_wall(start_pos = (width - 3*WALL_WIDTH - BALL_RADIUS*2, 4*WALL_WIDTH + BALL_RADIUS*2), end_pos = (width - 3*WALL_WIDTH - BALL_RADIUS*2, height),color = WHITE)

def summon_blockade() :
    space.remove(divide)
    space.remove(divide_shape)
    print("blockade summoned")
    return create_wall(start_pos = (width - 3*WALL_WIDTH - BALL_RADIUS*2, 0), end_pos = (width - 3*WALL_WIDTH - BALL_RADIUS*2, height),color = WHITE)

def spawn_ball() :
    global divide, divide_shape
    divide, divide_shape = destroy_blockade()
    return create_ball(r = BALL_RADIUS, position = (width - WALL_WIDTH//2 - BALL_RADIUS, height - 2*WALL_WIDTH - 2*BALL_RADIUS), static = False, mass = None, color = rand_color(), elasticity = ELASTICITY)

def draw_circle(body, shape) :
    pos = body.position
    radius = shape.radius
    pygame.draw.circle(screen, object_colors[shape], (int(pos.x), int(pos.y)), int(radius), 0)

def draw_segment(body,shape) :
    a = shape.a
    b = shape.b
    w = int(shape.radius)
    pygame.draw.line(screen, object_colors[shape], a, b, 2*w + 1)

def draw_polygon(body, shape):
    vertices = shape.get_vertices()
    transformed_vertices = [body.local_to_world(vertex) for vertex in vertices]
    pygame.draw.polygon(screen, object_colors[shape], transformed_vertices, 0)

# Definicja funkcji renderującej tekst
def draw_text(surface, text, pos, color, font_size=24):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def is_inside(position,wid = width, hei = height) :
    x,y = position
    if x < 0 : return False
    if x > wid : return False
    if y < 0 : return False
    if y > hei : return False
    return True

def distance(point_a,point_b) :
    return np.sqrt((point_a[0] - point_b[0])**2 + (point_a[1] - point_b[1])**2)

def increase_points(arbiter, space, _):
    # Znajdź kolizję
    ball_shape, obstacle_shape = arbiter.shapes

    # Sprawdź, czy przeszkoda jest kołem
    if isinstance(obstacle_shape, pymunk.Circle):
        # Zwiększ wartość POINTS o 100
        global POINTS
        POINTS += 100

pygame.init()

#create game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1000

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Main Menu")

#game variables
game_paused = False
menu_state = "menu"

#define fonts
font = pygame.font.SysFont("arialblack", 40)

#define colours
TEXT_COL = (255, 255, 255)

#load button images
resume_img = pygame.image.load("images/button_resume.png").convert_alpha()
options_img = pygame.image.load("images/button_options.png").convert_alpha()
quit_img = pygame.image.load("images/button_quit.png").convert_alpha()
keys_img = pygame.image.load('images/button_keys.png').convert_alpha()
back_img = pygame.image.load('images/button_back.png').convert_alpha()

#create button instances
resume_button = button.Button(304, 125, resume_img, 1)
options_button = button.Button(297, 250, options_img, 1)
quit_button = button.Button(336, 375, quit_img, 1)
keys_button = button.Button(246, 325, keys_img, 1)
back_button = button.Button(332, 450, back_img, 1)

def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

#game loop
run = True
while run:

  screen.fill((52, 78, 91))

  if game_paused == True:
    if menu_state == "menu":
      if resume_button.draw(screen):
        menu_state = "game"
      if options_button.draw(screen):
        menu_state = "options"
      if quit_button.draw(screen):
        run = False
    if menu_state == "options":
      if keys_button.draw(screen):
        print("Change Key Bindings")
      if back_button.draw(screen):
        menu_state = "menu"
    elif menu_state == "game":


        # Inicjalizacja Pygame
        # pygame.init()

        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pinball")

        # Stworzenie obiektu Clock do kontrolowania FPS
        clock = pygame.time.Clock()

        space = pymunk.Space()  # Create a Space which contain the simulation
        space.gravity = 0, 981  # Set its gravity

        object_colors = {}

        position_left = (base_width // 2 - 2 * BALL_RADIUS - FLIPPER_X, 0.95 * height - FLIPPER_Y)
        position_right = base_width - position_left[0], position_left[1]

        right_wall, right_wall_shape = create_wall(start_pos=(width - WALL_WIDTH // 2, 0),
                                                   end_pos=(width - WALL_WIDTH // 2, height), color=WHITE)
        left_wall, left_wall_shape = create_wall(start_pos=(WALL_WIDTH // 2, 0), end_pos=(WALL_WIDTH // 2, height),
                                                 color=WHITE)
        ceil, ceil_shape = create_wall(start_pos=(0, WALL_WIDTH // 2), end_pos=(width, WALL_WIDTH // 2), color=WHITE)

        floor, floor_shape = create_wall(start_pos=(width - 3 * WALL_WIDTH - BALL_RADIUS * 2, height),
                                         end_pos=(width, height), color=WHITE)
        floor1, floor1_shape = create_wall(start_pos=(0, 0.9 * height), end_pos=((5 / 12) * base_width, height),
                                           color=WHITE)
        floor2, floor2_shape = create_wall(start_pos=(width - 3 * WALL_WIDTH - BALL_RADIUS * 2, 0.9 * height),
                                           end_pos=((7 / 12) * base_width, height), color=WHITE)
        floor3, floor3_shape = create_wall(start_pos=(0, height - WALL_WIDTH // 2),
                                           end_pos=((4.5 / 12) * base_width, height - WALL_WIDTH // 2), color=WHITE)
        floor4, floor4_shape = create_wall(start_pos=(base_width, height - WALL_WIDTH // 2),
                                           end_pos=((7.5 / 12) * base_width, height - WALL_WIDTH // 2), color=WHITE)

        floor5, floor5_shape = create_wall(start_pos=(WALL_WIDTH + 3 * BALL_RADIUS, 0.85 * height),
                                           end_pos=position_left, color=WHITE, width=0.85 * WALL_WIDTH)

        floor6, floor6_shape = create_wall(start_pos=(base_width - (WALL_WIDTH + 3 * BALL_RADIUS), 0.85 * height),
                                           end_pos=position_right, color=WHITE, width=0.85 * WALL_WIDTH)

        divide, divide_shape = create_wall(
            start_pos=(width - 3 * WALL_WIDTH - BALL_RADIUS * 2, 4 * WALL_WIDTH + BALL_RADIUS * 2),
            end_pos=(width - 3 * WALL_WIDTH - BALL_RADIUS * 2, height), color=WHITE)
        divide2, divide2_shape = create_wall(start_pos=(width, 4.5 * WALL_WIDTH), end_pos=(width - 4.5 * WALL_WIDTH, 0),
                                             color=WHITE, width=1.5 * WALL_WIDTH)

        flipper_points = generate_flipper_points(60, -np.pi / 6)
        base_points = generate_flipper_points(BALL_RADIUS)

        flipper_color = rand_color()

        right_flipper_body, right_flipper_shape = create_flipper(flipper_points, position_right, 'right', flipper_color)
        left_flipper_body, left_flipper_shape = create_flipper(flipper_points, position_left, 'left', flipper_color)
        base_right_flipper_body, base_right_flipper_shape = create_flipper(base_points, (
        width - 1.5 * WALL_WIDTH, height - 1.2 * WALL_WIDTH), 'right', WHITE)
        base_left_flipper_body, base_left_flipper_shape = create_flipper(base_points, (
        width - 2 * WALL_WIDTH - 2 * BALL_RADIUS, height - 1.2 * WALL_WIDTH), 'left', WHITE)

        # Ustawienie maski kolizji dla flipperów
        right_flipper_shape.filter = pymunk.ShapeFilter(categories=0x2)
        left_flipper_shape.filter = pymunk.ShapeFilter(categories=0x2)
        base_right_flipper_shape.filter = pymunk.ShapeFilter(categories=0x2)
        base_left_flipper_shape.filter = pymunk.ShapeFilter(categories=0x2)

        # Ustawienie maski kolizji dla ścian
        right_wall_shape.filter = pymunk.ShapeFilter(categories=0x1)
        left_wall_shape.filter = pymunk.ShapeFilter(categories=0x1)
        ceil_shape.filter = pymunk.ShapeFilter(categories=0x1)
        floor1_shape.filter = pymunk.ShapeFilter(categories=0x1)
        floor2_shape.filter = pymunk.ShapeFilter(categories=0x1)
        floor3_shape.filter = pymunk.ShapeFilter(categories=0x1)
        floor4_shape.filter = pymunk.ShapeFilter(categories=0x1)
        floor5_shape.filter = pymunk.ShapeFilter(categories=0x1)
        floor6_shape.filter = pymunk.ShapeFilter(categories=0x1)
        divide_shape.filter = pymunk.ShapeFilter(categories=0x1)
        divide2_shape.filter = pymunk.ShapeFilter(categories=0x1)

        # Ustawienie maski kolizji dla ścian i flipperów
        for shape in [right_wall_shape, left_wall_shape, ceil_shape, floor1_shape, floor2_shape, floor3_shape,
                      floor4_shape, floor5_shape, floor6_shape, divide_shape, divide2_shape]:
            shape.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS() & ~0x2)  # Wyłączenie maski flipperów

        obstacle_color = rand_color()

        # ball_1 = create_ball(r = 1.5*BALL_RADIUS, position = (width//2,height//2 - 4*BALL_RADIUS), static = False, mass = None, color = (random.randint(0,255),random.randint(0,255),random.randint(0,255)), elasticity = ELASTICITY)
        static_1 = create_wall(start_pos=(base_width // 2, height // 2), end_pos=(base_width // 2, height // 3),
                               color=obstacle_color, width=WALL_WIDTH, friction=FRICTION, elasticity=1.5 * ELASTICITY,
                               static=True)
        static_2 = create_ball(r=2 * BALL_RADIUS, position=(base_width // 3, height // 4), static=True, mass=None,
                               color=obstacle_color, elasticity=1.5 * ELASTICITY)
        static_3 = create_ball(r=2 * BALL_RADIUS, position=(2 * base_width // 3, height // 4), static=True, mass=None,
                               color=obstacle_color, elasticity=1.5 * ELASTICITY)
        # Rejestracja funkcji obsługi zdarzeń kolizji
        handler = space.add_collision_handler(1, 2)
        handler.begin = increase_points

        ball, ball_shape = spawn_ball()
        removed = 0

        model_fps = float('inf')
        # model_fps = 60

        i = 0
        avg_time = 0
        avg_fps = 0

        right_flipper_pressed = False
        left_flipper_pressed = False
        base_flipper_pressed = False

        target_angle = np.pi / 3

        max_energy = 200
        energy_stored = 0
        energy_direction = 1
        time_passed = 0
        shoot = False

        inside = False

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    pygame.image.save(screen, "flipper.png")
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        right_flipper_pressed = True
                    elif event.key == pygame.K_LEFT:
                        left_flipper_pressed = True
                    elif event.key == pygame.K_SPACE:
                        base_flipper_pressed = True
                        energy_stored = 0
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT:
                        right_flipper_pressed = False
                    elif event.key == pygame.K_LEFT:
                        left_flipper_pressed = False
                    elif event.key == pygame.K_SPACE:
                        base_flipper_pressed = False
                        base_right_flipper_body.angular_velocity = (
                                                                               base_flipper_target_angle - base_right_flipper_body.angle) * energy_stored
                        base_left_flipper_body.angular_velocity = (
                                                                              -base_flipper_target_angle - base_left_flipper_body.angle) * energy_stored
                        # energy_stored = 0
                        shoot = True
                        print(shoot)

            # Wyczyszczenie ekranu
            screen.fill(BLACK)

            if base_flipper_pressed:
                print(energy_stored)
                val = avg_time / 0.75
                energy_stored += max_energy * val * energy_direction
                if energy_stored >= max_energy:
                    energy_stored = max_energy
                    time_passed += avg_time
                    if time_passed >= 0.25:
                        time_passed = 0
                        energy_direction = -1
                if energy_stored <= 0:
                    energy_stored = 0
                    time_passed += avg_time
                    if time_passed >= 0.25:
                        time_passed = 0
                        energy_direction = 1

            right_flipper_body.velocity = left_flipper_body.velocity = base_right_flipper_body.velocity = base_left_flipper_body.velocity = 0, 0

            right_flipper_target_angle = target_angle if right_flipper_pressed else 0
            left_flipper_target_angle = -target_angle if left_flipper_pressed else 0
            base_flipper_target_angle = target_angle if shoot else 0

            if shoot:
                # print(base_flipper_target_angle)
                time_passed += avg_time
                if time_passed >= 0.3:
                    shoot = False
                    time_passed = 0

            right_flipper_body.angular_velocity = (right_flipper_target_angle - right_flipper_body.angle) * 30
            left_flipper_body.angular_velocity = (left_flipper_target_angle - left_flipper_body.angle) * 30
            base_right_flipper_body.angular_velocity = (
                                                                   base_flipper_target_angle - base_right_flipper_body.angle) * energy_stored
            base_left_flipper_body.angular_velocity = (
                                                                  -base_flipper_target_angle - base_left_flipper_body.angle) * energy_stored

            # Ustawienie limitu FPS
            clock.tick(model_fps)
            fps = clock.get_fps()
            val = 1 / model_fps
            if fps > 0:
                val = 1 / fps

            avg_time = ((avg_time * i) + val) / (i + 1)
            avg_fps = ((avg_fps * i) + fps) / (i + 1)

            # Symulacja
            space.step(val)

            # Rysowanie obiektów
            for body in space.bodies:
                for shape in body.shapes:
                    if isinstance(shape, pymunk.Circle):
                        pos = body.position
                        if not inside and body == ball:
                            if is_inside(pos, base_width):
                                divide, divide_shape = summon_blockade()
                                POINTS += round(energy_stored)
                                inside = True
                        if not is_inside(pos):
                            space.remove(body)
                            print("REMOVED")
                            removed += 1
                            inside = False
                            ball, ball_shape = spawn_ball()
                            if removed == NO_BALLS:
                                print("ALL GONE")
                                running = False
                        draw_circle(body, shape)
                    elif isinstance(shape, pymunk.Segment):
                        draw_segment(body, shape)
                    elif isinstance(shape, pymunk.Poly):
                        draw_polygon(body, shape)

            # Wyświetlanie licznika FPS
            # draw_text(screen, f"FPS: {int(clock.get_fps())}", (0, 0), BLACK)
            # draw_text(screen, f"Balls left: {NO_BALLS - removed}", (0, height - 14), BLACK)
            # draw_text(screen, f"{POINTS}", (width // 2, 0), BLACK)
            # draw_text(screen, f"AVG_FPS: {int(avg_fps)}", (200,0), BLACK)

            # Odświeżenie ekranu
            pygame.display.flip()

        # Wyjście z Pygame
        pygame.quit()

        print("avg_frametime", avg_time)
        print("avg_fps", round(avg_fps))
        print("POINTS: ", POINTS)
    pass
  else:
    draw_text("Press SPACE to start", font, TEXT_COL, 160, 250)

  for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_SPACE:
        game_paused = True
    if event.type == pygame.QUIT:
      run = False

  pygame.display.update()

pygame.quit()
