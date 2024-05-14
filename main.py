print("running whole main.py")
import os
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

import random
import pymunk
import numpy as np
import menu
import pygame
from utility_functions import *

RUNNING = False
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
SPACE = pymunk.Space()
OBJECT_COLORS = {}
POINTS = 0

# Global variables
WIDTH = 100
HEIGHT = 100
ELASTICITY = 1
BALL_RADIUS = 1
NO_BALLS = 1
FRICTION = 1
WALL_WIDTH = 1
TARGET_ANGLE = 1
FLIPPER_LENGTH = 1
FLIPPER_ANGLE = 1
FLIPPER_X = 1
FLIPPER_Y = 1
GRAVITY_X = 1
GRAVITY_Y = 1
BALL_POSITION_X = 1
BALL_POSITION_Y = 1
LAUNCH_ENERGY = 1
MODEL_FPS = float('inf')
POINTS_SET = {}
WALLS = []
BALLS = []
OBSTACLES = []
RIGHT_FLIPPERS = []
LEFT_FLIPPERS = []
BASE_FLIPPERS = []
BLOCKADE, BLOCKADE_SHAPE, BLOCKADE_PARAMS = None, None, None
BALL, BALL_SHAPE, BALL_PARAMS = None, None, None


BASE_WIDTH = WIDTH
TUNNEL_SIZE = (2.2*BALL_RADIUS)
WIDTH = int(round(WIDTH + (3/2) * WALL_WIDTH + TUNNEL_SIZE))
breaking_point = (BASE_WIDTH, 2 * WALL_WIDTH + 3 * BALL_RADIUS)

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

def rand_pos() :
    global WALL_WIDTH, WIDTH, HEIGHT
    return (random.randint(WALL_WIDTH,WIDTH-WALL_WIDTH),random.randint(WALL_WIDTH,HEIGHT-WALL_WIDTH))

def create_ball(r = BALL_RADIUS, position_x = None, position_y = None, static = False, mass = None, red = None, green = None, blue = None, elasticity = ELASTICITY, points = None, collision = None) :
    global OBJECT_COLORS, SPACE
    
    position = (position_x, position_y)
    if any(pos is None for pos in position) : position = rand_pos()
    color = (red, green, blue)
    if any(col is None for col in color) : color = rand_color()
    
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
    
    if collision is not None :
        ball_shape.collision_type = collision
    if points is not None :
        POINTS_SET[ball_shape] = points
    
    OBJECT_COLORS[ball_shape] = color
    SPACE.add(ball, ball_shape)
    return ball,ball_shape

def create_wall(start_x = None, start_y = None, end_x = None, end_y = None, red = None, green = None, blue = None, segment_width = WALL_WIDTH, friction = FRICTION, elasticity = ELASTICITY, static = True, points_gain = None, collision = None) :
    global OBJECT_COLORS, SPACE
    
    start_pos = (start_x, start_y)
    if any(pos is None for pos in start_pos) : start_pos = rand_pos()
    end_pos = (end_x, end_y)
    if any(pos is None for pos in end_pos) : end_pos = rand_pos()
    color = (red, green, blue)
    if any(col is None for col in color) : color = rand_color()
    
    w = segment_width // 2
    a_x, a_y = start_pos
    b_x, b_y = end_pos
    c_x, c_y = (a_x + b_x) // 2, (a_y + b_y) // 2
    v_l = np.sqrt(((b_x - a_x)**2) + ((b_y - a_y)**2))
    v_x, v_y = (b_x - a_x), (b_y - a_y)
    points = [(-(v_x/2) - w * (v_y/v_l), -(v_y/2) + w * (v_x/v_l)), (-(v_x/2) + w * (v_y/v_l), -(v_y/2) - w * (v_x/v_l)), ((v_x/2) + w * (v_y/v_l), (v_y/2) - w * (v_x/v_l)), ((v_x/2) - w * (v_y/v_l), (v_y/2) + w * (v_x/v_l))]


    position = (c_x, c_y)
    mass = poly_field(points)
    moment = pymunk.moment_for_poly(mass, points)
    
    body = None
    if static :
        body = pymunk.Body(mass, moment, body_type=pymunk.Body.STATIC)
    else :
        body = pymunk.Body(mass, moment)
    body.position = position
    shape = pymunk.Poly(body, points)
    shape.elasticity = ELASTICITY
    
    if collision is not None :
        shape.collision_type = collision
    if points is not None :
        POINTS_SET[shape] = points_gain
        
    shape.filter = pymunk.ShapeFilter(categories=0x1)
    SPACE.add(body, shape)

    OBJECT_COLORS[shape] = color

    return body, shape


def create_flipper(length = FLIPPER_LENGTH, angle = FLIPPER_ANGLE, position_x = None, position_y = None, side = 'right', red = None, green = None, blue = None) :
    global OBJECT_COLORS, SPACE
    
    position = position_x, position_y
    if any(pos is None for pos in position) : position = rand_pos()
    color = (red, green, blue)
    if any(col is None for col in color) : color = rand_color()
    
    
    points = generate_flipper_points(length, angle)
    
    mass = poly_field(points)
    moment = pymunk.moment_for_poly(mass, points)

    # init_angle = 0

    if side == 'left' :
        for i in range(len(points)) : points[i] = (-points[i][0],points[i][1])
        # init_angle = -init_angle
    
    flipper_body = pymunk.Body(mass, moment)
    flipper_body.position = position
    flipper_shape = pymunk.Poly(flipper_body, points)
    flipper_shape.elasticity = ELASTICITY
    flipper_shape.filter = pymunk.ShapeFilter(categories=0x2)
    SPACE.add(flipper_body, flipper_shape)

    OBJECT_COLORS[flipper_shape] = color

    return flipper_body, flipper_shape


# Load global variables
def load_map(name) :
    global WALLS, BALLS, BALL, BALL_SHAPE, BALL_PARAMS, RIGHT_FLIPPERS, LEFT_FLIPPERS, BASE_FLIPPERS, BLOCKADE, BLOCKADE_SHAPE, BLOCKADE_PARAMS
    with open(os.path.join(SCRIPT_PATH, 'maps', name + '.txt'), 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line[0] == '-' :
                parts = line.split(' ')
                function_name = parts[1]
                parameters = [eval(param) for param in parts[2].split(',')]
                if function_name == "create_wall":
                    WALLS.append(create_wall(*parameters))
                elif function_name == "create_flipper":
                    checker = parameters.pop()
                    data = create_flipper(*parameters)
                    data = (data[0], data[1], parameters)
                    if checker == 'right_flipper' :
                        RIGHT_FLIPPERS.append(data)
                    elif checker == 'left_flipper' :
                        LEFT_FLIPPERS.append(data)
                    else :
                        BASE_FLIPPERS.append(data)
                elif function_name == "create_ball":
                    BALLS.append(create_ball(*parameters))
            elif line[0] == "#" :
                parts = line.split(" ")
                if parts[1] == 'BLOCKADE' :
                    function_name = parts[3]
                    parameters = [eval(param) for param in parts[4].split(',')]
                    BLOCKADE_PARAMS = parameters + [2]
                    BLOCKADE, BLOCKADE_SHAPE = create_wall(*BLOCKADE_PARAMS)
                    WALLS.append((BLOCKADE, BLOCKADE_SHAPE))
                if parts[1] == 'BALL' :
                    function_name = parts[3]
                    parameters = [eval(param) for param in parts[4].split(',')]
                    BALL_PARAMS = parameters + [1]
                    BALL, BALL_SHAPE = create_ball(*BALL_PARAMS)
                    BALLS.append((BALL, BALL_SHAPE))
                if parts[1] == 'OBSTACLE' :
                    function_name = parts[3]
                    parameters = [eval(param) for param in parts[4].split(',')]
                    data = None
                    if function_name == "create_wall":
                        print(parameters[-1])
                        data = create_wall(*parameters)
                        WALLS.append(data)
                    if function_name == "create_ball":
                        data = create_ball(*parameters)
                        BALLS.append(data)
                    OBSTACLES.append(data)
            else :
                parts = line.split('#')
                if parts[0] == ' \n' or parts[0] == '\n' : continue
                var_value = 0
                if parts[0] == 'inf ' :
                    var_value = float('inf')
                else : var_value = eval(parts[0])
                var_name = parts[1].split(' ')[-2]
                globals()[var_name] = var_value
                


def replace_base_flippers() :
    global BASE_FLIPPERS
    
    for i in range(len(BASE_FLIPPERS)) :
        BASE_FLIPPER, BASE_FLIPPER_SHAPE, BASE_FLIPPER_PARAMS = BASE_FLIPPERS[i]
        SPACE.remove(BASE_FLIPPER)
        SPACE.remove(BASE_FLIPPER_SHAPE)
        BASE_FLIPPER, BASE_FLIPPER_SHAPE = create_flipper(*BASE_FLIPPER_PARAMS)
        BASE_FLIPPERS[i] = BASE_FLIPPER, BASE_FLIPPER_SHAPE, BASE_FLIPPER_PARAMS
    
    return BASE_FLIPPERS
    
    # return base_right_flipper_body, base_right_flipper_shape, base_left_flipper_body, base_left_flipper_shape

def destroy_blockade() :
    global BLOCKADE, BLOCKADE_SHAPE, SPACE
    if BLOCKADE is not None:
        SPACE.remove(BLOCKADE)
        BLOCKADE = None
    if BLOCKADE_SHAPE is not None:
        SPACE.remove(BLOCKADE_SHAPE)
        BLOCKADE_SHAPE = None


    # return create_wall(start_pos = (base_width, 0), end_pos = breaking_point,color = WHITE)

def summon_blockade() :
    global BLOCKADE, BLOCKADE_SHAPE, BLOCKADE_PARAMS
    BLOCKADE, BLOCKADE_SHAPE = create_wall(*BLOCKADE_PARAMS)
    return BLOCKADE, BLOCKADE_SHAPE

def spawn_ball() :
    global BALL_PARAMS, BASE_FLIPPERS
    destroy_blockade()
    BASE_FLIPPERS = replace_base_flippers()
    return create_ball(*BALL_PARAMS)

def draw_circle(body, shape) :
    pos = body.position
    radius = shape.radius
    pygame.draw.circle(SCREEN, OBJECT_COLORS[shape], (int(pos.x), int(pos.y)), int(radius), 0)

def draw_segment(body,shape) :
    a = shape.a
    b = shape.b
    w = int(shape.radius)
    pygame.draw.line(SCREEN, OBJECT_COLORS[shape], a, b, 2*w + 1)

def draw_polygon(body, shape):
    vertices = shape.get_vertices()
    transformed_vertices = [body.local_to_world(vertex) for vertex in vertices]
    pygame.draw.polygon(SCREEN, OBJECT_COLORS[shape], transformed_vertices, 0)

def draw_text_inside(surface, text, pos, color, font_size=24):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)
    
def is_inside(position,wid = WIDTH, hei = HEIGHT) :
    x,y = position
    if x < BALL_RADIUS : return False
    if x > wid - BALL_RADIUS : return False
    if y < BALL_RADIUS : return False
    if y > hei - BALL_RADIUS : return False
    return True


    
def run(preset="default"):
    global BALL, BALL_SHAPE, BLOCKADE, BLOCKADE_SHAPE, POINTS, BASE_WIDTH, TUNNEL_SIZE, WIDTH, breaking_point, BASE_FLIPPERS, WALLS, OBSTACLES, LAUNCH_ENERGY
    print("RUNNING WITH PRESET", preset)
    menu.quit_menu()
    load_map(preset)
    SPACE.gravity = GRAVITY_X, GRAVITY_Y
    destroy_blockade()
    BASE_WIDTH = WIDTH
    TUNNEL_SIZE = (2.2 * BALL_RADIUS)
    WIDTH = int(round(WIDTH + (3 / 2) * WALL_WIDTH + TUNNEL_SIZE))
    breaking_point = (BASE_WIDTH, 2 * WALL_WIDTH + 3 * BALL_RADIUS)
    
    pygame.init()
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

    for _, shape in WALLS:
        shape.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS() & ~0x2)

    removed = 0

    pygame.display.set_caption("Pinball")
    clock = pygame.time.Clock()

    model_fps = float('inf')
    # model_fps = 60

    i = 0
    avg_time = 0
    avg_fps = 0

    right_flipper_pressed = False
    left_flipper_pressed = False
    base_flipper_pressed = False

    max_energy = LAUNCH_ENERGY
    energy_stored = 0
    energy_direction = 1
    time_passed = 0
    max_time_passing = 1
    shoot = False

    inside = False

    RUNNING = True
    while RUNNING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    right_flipper_pressed = True
                elif event.key == pygame.K_LEFT:
                    left_flipper_pressed = True
                elif event.key == pygame.K_SPACE:
                    base_flipper_pressed = True
                    energy_stored = 0
                # elif event.key == pygame.K_ESCAPE :
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    right_flipper_pressed = False
                elif event.key == pygame.K_LEFT:
                    left_flipper_pressed = False
                elif event.key == pygame.K_SPACE:
                    base_flipper_pressed = False
                    shoot = True
                    print(shoot)

        # Wyczyszczenie ekranu
        SCREEN.fill(BLACK)

        if base_flipper_pressed:
            print(energy_stored)
            val = avg_time / 0.75
            energy_stored += max_energy * val * energy_direction
            if energy_stored >= max_energy:
                energy_stored = max_energy
                time_passed += avg_time
                if time_passed >= max_time_passing:
                    time_passed = 0
                    energy_direction = -1
            if energy_stored <= 0:
                energy_stored = 0
                time_passed += avg_time
                if time_passed >= max_time_passing:
                    time_passed = 0
                    energy_direction = 1

        right_flipper_target_angle = TARGET_ANGLE if right_flipper_pressed else 0
        left_flipper_target_angle = -TARGET_ANGLE if left_flipper_pressed else 0
        base_flipper_target_angle = TARGET_ANGLE if shoot else 0

        if shoot:
            time_passed += avg_time
            if time_passed >= 0.5:
                shoot = False
                BASE_FLIPPERS = replace_base_flippers()
                for _, shape in WALLS:
                    shape.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS() & ~0x2)
                time_passed = 0

        for right_flipper_body, _, _ in RIGHT_FLIPPERS:
            right_flipper_body.velocity = 0, 0
            right_flipper_body.angular_velocity = (right_flipper_target_angle - right_flipper_body.angle) * 30
        for left_flipper_body, _, _ in LEFT_FLIPPERS:
            left_flipper_body.velocity = 0, 0
            left_flipper_body.angular_velocity = (left_flipper_target_angle - left_flipper_body.angle) * 30
        for base_flipper_body, _, _ in BASE_FLIPPERS:
            base_flipper_body.velocity = 0, 0
            base_flipper_body.angular_velocity = (base_flipper_target_angle - base_flipper_body.angle) * (energy_stored)

        # Ustawienie limitu FPS
        clock.tick(model_fps)
        fps = clock.get_fps()
        val = 1 / model_fps
        if fps > 0:
            val = 1 / fps

        avg_time = ((avg_time * i) + val) / (i + 1)
        avg_fps = ((avg_fps * i) + fps) / (i + 1)

        # Symulacja
        SPACE.step(val)

        # Rysowanie obiektów
        for body in SPACE.bodies:
            if any(body in data for data in BASE_FLIPPERS) : continue
            for shape in body.shapes:
                if isinstance(shape, pymunk.Circle):
                    pos = body.position
                    if not inside and body == BALL:
                        if is_inside(pos, BASE_WIDTH):
                            BLOCKADE, BLOCKADE_SHAPE = summon_blockade()
                            POINTS += round(energy_stored)
                            inside = True
                    if not is_inside(pos, wid=WIDTH, hei=HEIGHT):
                        SPACE.remove(body)
                        SPACE.remove(shape)
                        print("REMOVED")
                        removed += 1
                        inside = False
                        BALL, BALL_SHAPE = spawn_ball()
                        if removed == NO_BALLS:
                            print("ALL GONE")
                            RUNNING = False
                    draw_circle(body, shape)
                elif isinstance(shape, pymunk.Segment):
                    draw_segment(body, shape)
                elif isinstance(shape, pymunk.Poly):
                    draw_polygon(body, shape)

                # Check for collisions with the ball
                if (body, shape) in OBSTACLES :
                    # print(BALL_SHAPE)
                    _,_,dist = shortest_distance_between_shapes(BALL_SHAPE, shape)
                    if dist < 50 :
                        print("+",POINTS_SET[shape],"POINTS!")
                        POINTS += POINTS_SET[shape]

        # Wyświetlanie licznika FPS
        draw_text_inside(SCREEN, f"FPS: {int(clock.get_fps())}", (0, 0), BLACK)
        draw_text_inside(SCREEN, f"Balls left: {NO_BALLS - removed}", (0, HEIGHT - 14), BLACK)
        draw_text_inside(SCREEN, f"{POINTS}", (WIDTH // 2, 0), BLACK)
        # draw_text(screen, f"AVG_FPS: {int(avg_fps)}", (200,0), BLACK)

        # Odświeżenie ekranu
        pygame.display.flip()

    # Wyjście z Pygame
    pygame.quit()

    print("avg_frametime", avg_time)
    print("avg_fps", round(avg_fps))
    print("POINTS: ", POINTS)


if __name__ == "__main__":
    run()

