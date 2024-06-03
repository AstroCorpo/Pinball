print("running whole main.py")
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import random
import pymunk
import numpy as np
import menu
import pygame
from utility_functions import *
from copy import deepcopy
import json
import pause_menu as pause

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
SOUND_PATH = os.path.join(SCRIPT_PATH, "sounds")
LEADERBOARD_PATH = os.path.join(SCRIPT_PATH, "layouts", "leaderboard.json")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def create_ball(r, position, static = False, mass = None, color = rand_color(), elast = 0.5, collision_sound_file = None, action_sound_file = None, space = None) :
    return Ball(r = r, position = position, static = static, mass = mass, color = color, elast = elast, collision_sound_file = collision_sound_file, action_sound_file = action_sound_file, space = space)

class Ball :
    def __init__(self, r, position, static = False, mass = None, color = rand_color(), elast = 0.5, collision_sound_file = None, action_sound_file = None, space = None) :
        body = None
        if static : body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else : body = pymunk.Body()
        body.position = position
        shape = pymunk.Circle(body, r)
        if mass is not None :
            shape.mass = mass
        else :
            shape.mass = shape.area/20
        shape.elasticity = elast
        self.color = color
        
        self.body = body
        self.shape = shape
        self.shape.data = self
        
        self.space = space
        self.add()
        
        self.collision_sound = None
        if collision_sound_file is not None :
            self.collision_sound = pygame.mixer.Sound(os.path.join(SOUND_PATH, collision_sound_file))
        
        self.action_sound = None
        if action_sound_file is not None :
            self.action_sound = pygame.mixer.Sound(os.path.join(SOUND_PATH, action_sound_file))
        
    def add_to_space(self, space = None) :
        if space is None : space = self.space
        space.add(self.body, self.shape)
    
    def destroy(self) :
        self.space.remove(self.body)
        self.space.remove(self.shape)
        
    def draw(self, screen, rainbow_mode = False) :
        color = self.color
        if rainbow_mode : color = rand_color()
        pos = self.body.position
        radius = self.shape.radius
        pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), int(radius), 0)
        
    def play_collision_sound(self) :
        sound = self.collision_sound
        if sound is not None :
            sound.play()

    def play_action_sound(self) :
        sound = self.action_sound
        if sound is not None :
            sound.play()

    def action(self, energy_stored) :
        self.body.apply_impulse_at_local_point((0, -1_000*energy_stored))
        self.play_action_sound()
        
        

        
def create_wall(start_pos, end_pos, color = rand_color(), width = 10, frict = 0.5, elast = 0.5, static = True, object_colors = None, space = None) :
    w = width // 2
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
    shape.elasticity = elast
    shape.friction = frict
    shape.filter = pymunk.ShapeFilter(categories=0x1)
    space.add(body, shape)

    object_colors[shape] = color

    return (body, shape), object_colors, space

def create_triangle(points, color, static = True, elast = 0.5, object_colors = None, space = None) :
    mass = poly_field(points)
    moment = pymunk.moment_for_poly(mass, points)

    body = pymunk.Body(mass, moment)
    if static :
        body.body_type=pymunk.Body.STATIC
    body.position = points[0]
    
    new_points = deepcopy(points)
    
    new_points[1] = (new_points[1][0] - new_points[0][0], new_points[1][1] - new_points[0][1])
    new_points[2] = (new_points[2][0] - new_points[0][0], new_points[2][1] - new_points[0][1])
    new_points[0] = (0,0)
    
    shape = pymunk.Poly(body, new_points)
    shape.elasticity = elast
    shape.filter = pymunk.ShapeFilter(categories=0x1)
    space.add(body, shape)
    object_colors[shape] = color
    
    return (body, shape), object_colors, space


def create_flipper(length, angle, position, side, color, elast, object_colors = None, space = None) :
    
    points = generate_flipper_points(length, angle)
    
    mass = poly_field(points)
    moment = pymunk.moment_for_poly(mass, points)

    if side == 'left' :
        for i in range(len(points)) : points[i] = (-points[i][0],points[i][1])
    
    flipper_body = pymunk.Body(mass, moment)
    flipper_body.position = position
    flipper_shape = pymunk.Poly(flipper_body, points)
    flipper_shape.elasticity = elast
    flipper_shape.filter = pymunk.ShapeFilter(categories=0x2)
    space.add(flipper_body, flipper_shape)

    object_colors[flipper_shape] = color

    return (flipper_body, flipper_shape), object_colors, space


circle_field = lambda r : np.pi * r**2

def run(preset="fancy", player_name = "Unknown", screen = None) :
    
    print("RUNNING WITH PRESET", preset)

    with open(os.path.join(SCRIPT_PATH, "maps", preset + ".json"), 'r') as file :
        config = json.load(file)

    BASE_WIDTH = config["BASE_WIDTH"]
    WIDTH = config["WIDTH"]
    HEIGHT = config["HEIGHT"]
    NO_BALLS = config["NO_BALLS"]
    TARGET_ANGLE = config["TARGET_ANGLE"]
    BALL_RADIUS = config["BALL_RADIUS"]
    WALL_WIDTH = config["WALL_WIDTH"]
    TARGET_HEIGHT = config["TARGET_HEIGHT"]
    REACTION_TIME = config["REACTION_TIME"]
    
    POINTS = 0
    
    RUNNING = True
    rainbow_mode = False
    epilepsy_mode = False

    space = pymunk.Space()
    space.gravity = config["GRAVITY"]
    
    object_colors = {}

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    field_max = float('-inf')
    field_min = float('inf')
    
    OBSTACLES = []
    for arguments in config["OBSTACLES"] :
        data = create_ball(*arguments, space)
        OBSTACLES.append(data)
        field = circle_field(arguments[0])
        field_max = max(field_max, field)
        field_min = min(field_min, field)
    field_min = max(field_min, 100)
    
    point_function = lambda x : (field_min + field_max - x) / 10
        
    BALLS = []
    for arguments in config["BALLS"] :
        data, space = create_ball(*arguments, object_colors, space)
        BALLS.append(data)
        
    WALLS = []
    for arguments in config["WALLS"] :
        data, object_colors, space = create_wall(*arguments, object_colors, space)
        WALLS.append(data)
        
    TRIANGLES = []
    for arguments in config["TRIANGLES"] :
        data, object_colors, space = create_triangle(*arguments, object_colors, space)
        TRIANGLES.append(data)
        
    RIGHT_FLIPPERS = []
    for arguments in config["RIGHT_FLIPPERS"] :
        data, object_colors, space = create_flipper(*arguments, object_colors, space)
        RIGHT_FLIPPERS.append(data)
        
    LEFT_FLIPPERS = []
    for arguments in config["LEFT_FLIPPERS"] :
        data, object_colors, space = create_flipper(*arguments, object_colors, space)
        LEFT_FLIPPERS.append(data)

    INITIAL_HEIGHT = 0
    
    POINTERS = []
    for arguments in config["POINTERS"] :
        data, object_colors, space = create_ball(*arguments, object_colors, space)
        INITIAL_HEIGHT = arguments[1][1]
        POINTERS.append(data)
        
    BALL_PARAMS = config["MAIN_BALL"]
    (BALL, BALL_SHAPE), object_colors, space = create_ball(*BALL_PARAMS, object_colors, space)
        
    BLOCKADE_PARAMS = config["BLOCKADE"]
    (BLOCKADE, BLOCKADE_SHAPE), object_colors, space = create_wall(*BLOCKADE_PARAMS, object_colors, space)
    
    def draw_circle(body, shape) :
        nonlocal screen, object_colors, rainbow_mode
        color = object_colors[shape]
        if rainbow_mode : color = rand_color()
        pos = body.position
        radius = shape.radius
        pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), int(radius), 0)

    def draw_polygon(body, shape):
        nonlocal screen, object_colors, rainbow_mode, WALLS
        color = object_colors[shape]
        if rainbow_mode and (tuple(color) != WHITE) : color = rand_color()
        vertices = shape.get_vertices()
        transformed_vertices = [body.local_to_world(vertex) for vertex in vertices]
        pygame.draw.polygon(screen, color, transformed_vertices, 0)

    def draw_text(surface, text, pos, color, font_size=24):
        nonlocal rainbow_mode, WIDTH, HEIGHT
        if rainbow_mode:
            color = rand_color()
        font = pygame.font.SysFont(None, font_size)
        text_surface = font.render(text, True, color)
        text_width, text_height = text_surface.get_size()
        x,y = pos
        
        x = min(max(x, text_width // 2), WIDTH - (text_width // 2))
        y = min(max(y, text_height // 2), HEIGHT - (text_height // 2))
        
        pos = (x,y)
        text_rect = text_surface.get_rect()
        text_rect.center = pos  # Ustawienie środka tekstu na pozycji pos
        surface.blit(text_surface, text_rect.topleft)
                
    def destroy_blockade() :
        nonlocal BLOCKADE, BLOCKADE_SHAPE, space
        if BLOCKADE is not None:
            space.remove(BLOCKADE)
            BLOCKADE = None
        if BLOCKADE_SHAPE is not None:
            space.remove(BLOCKADE_SHAPE)
            BLOCKADE_SHAPE = None
        return space

    def summon_blockade() :
        nonlocal BLOCKADE, BLOCKADE_SHAPE, BLOCKADE_PARAMS, object_colors, space
        (BLOCKADE, BLOCKADE_SHAPE), object_colors, space = create_wall(*BLOCKADE_PARAMS, object_colors, space)
        return BLOCKADE, BLOCKADE_SHAPE, object_colors, space

    def spawn_ball() :
        nonlocal BALL_PARAMS, object_colors, space
        
        space = destroy_blockade()
        return create_ball(*BALL_PARAMS, object_colors, space)

    def is_inside(wid = WIDTH, hei = HEIGHT) :
        nonlocal BALL
        x,y = BALL.position
        if x < BALL_RADIUS : return False
        if x > wid - BALL_RADIUS : return False
        if y < BALL_RADIUS : return False
        if y > hei + 2*BALL_RADIUS : return False
        return True


    def in_tunnel() :
        nonlocal BALL, BASE_WIDTH
        if BASE_WIDTH - 2*BALL_RADIUS - WALL_WIDTH < BALL.position[0] : return True
        return False
    
    def at_start() :
        nonlocal BALL, config
        
        if distance_points(config["BALL_POSITION"], BALL.position) > config["TUNNEL_SIZE"] :
            return False
        return True
    
    def add_points(val) :
        nonlocal POINTS
        POINTS += val
        print("+", val, "POINTS!!")
    
    
    for _, shape in WALLS + TRIANGLES:
        shape.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS() & ~0x2)
        
    def not_paused() :
        nonlocal paused
        paused = False
        
    # PAUSE_LAYOUT = pause.generate_pause_menu_layout({"continue": not_paused, "options": pause.options_menu, "menu": menu.run_menu}, BASE_WIDTH, HEIGHT)

    PAUSE_LAYOUT = pause.generate_pause_menu_layout({"continue": not_paused, "menu": menu.run_menu}, BASE_WIDTH, HEIGHT)

    removed = 0
    
    display_fire = False

    pygame.display.set_caption("Pinball")
    clock = pygame.time.Clock()

    model_fps = float('inf')
    # model_fps = 60

    i = 0
    avg_time = 0
    avg_fps = 0
    val = 1/model_fps

    right_flipper_pressed = False
    left_flipper_pressed = False
    space_pressed = False

    max_energy = config["LAUNCH_ENERGY"]
    min_energy = config["MINIMAL_ENERGY"]
    energy_stored = 0
    energy_direction = 1
    time_passed = 0
    max_time_passing = 1
    
    paused = False  
    speed = 1
    
    blocked = False
    destroy_blockade()
    
    while RUNNING :
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and not paused:
                    right_flipper_pressed = True
                elif event.key == pygame.K_LEFT and not paused:
                    left_flipper_pressed = True
                elif event.key == pygame.K_SPACE and not paused:
                    if at_start() :
                        space_pressed = True
                        energy_direction = 1
                elif event.key == pygame.K_ESCAPE :
                    paused = not paused
            elif event.type == pygame.KEYUP and not paused:
                if event.key == pygame.K_RIGHT:
                    right_flipper_pressed = False
                elif event.key == pygame.K_LEFT:
                    left_flipper_pressed = False
                elif event.key == pygame.K_SPACE:
                    if at_start() :
                        BALL.action(energy_stored)
                    space_pressed = False
                    display_fire = False
                elif event.key == pygame.K_c:
                    object_colors[BALL_SHAPE] = rand_color()
                    BALL_PARAMS[4] = object_colors[BALL_SHAPE]
                elif event.key == pygame.K_r:
                    rainbow_mode = not rainbow_mode
                elif event.key == pygame.K_t:
                    epilepsy_mode = not epilepsy_mode
                elif event.key == pygame.K_q:
                    speed *= 2
                elif event.key == pygame.K_e:
                    speed /= 2 
                elif event.key == pygame.K_f:
                    speed = -speed
            if paused :
                for button in PAUSE_LAYOUT.values():
                    button.handle_event(event, screen, pause.BACKGROUND_COLOR)
        if not RUNNING : break
        
        # Wyczyszczenie ekranu
        if epilepsy_mode : screen.fill(random.choice([WHITE, BLACK]))
        else : screen.fill(BLACK)
        
        # Ustawienie limitu FPS
        clock.tick(model_fps)
        fps = clock.get_fps()
        val = 1 / model_fps
        if fps > 0:
            val = 1 / fps

        avg_time = ((avg_time * i) + val) / (i + 1)
        avg_fps = ((avg_fps * i) + fps) / (i + 1)

        # Symulacja
        if not paused :
            val *= speed
            space.step(val)
        else :
            for button in PAUSE_LAYOUT.values():
                button.draw(screen)
        
        value = avg_time / (REACTION_TIME / speed)
        energy_stored = max(energy_stored, 0)
        energy_stored = min(energy_stored, max_energy)
        if space_pressed :
            if energy_stored >= min_energy :
                display_fire = True
            else : display_fire = False
            
            print(energy_stored)
            energy_part = energy_stored / max_energy
            pointer_height = INITIAL_HEIGHT - ((INITIAL_HEIGHT - TARGET_HEIGHT))*energy_part
            
            for pointer,_ in POINTERS :
                pointer.position = (pointer.position[0], pointer_height)
                
            energy_stored += max_energy * value * energy_direction
            
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
        else :
            if energy_stored > 0 :
                energy_direction = -1
                energy_stored += max_energy * value * energy_direction
                energy_part = energy_stored / max_energy
                pointer_height = INITIAL_HEIGHT - ((INITIAL_HEIGHT - TARGET_HEIGHT))*energy_part
                
                for pointer,_ in POINTERS :
                    pointer.position =    (pointer.position[0], pointer_height)
    
        right_flipper_target_angle = TARGET_ANGLE if right_flipper_pressed else 0
        left_flipper_target_angle = -TARGET_ANGLE if left_flipper_pressed else 0
    

        for right_flipper_body, _ in RIGHT_FLIPPERS:
            right_flipper_body.velocity = 0, 0
            right_flipper_body.angular_velocity = (right_flipper_target_angle - right_flipper_body.angle) * 30
        for left_flipper_body, _ in LEFT_FLIPPERS:
            left_flipper_body.velocity = 0, 0
            left_flipper_body.angular_velocity = (left_flipper_target_angle - left_flipper_body.angle) * 30  
        
        
        if not in_tunnel() and not blocked :
            add_points(int(round(energy_stored*10)))
            summon_blockade()
            blocked = True
        if not is_inside() :
            space.remove(BALL)
            space.remove(BALL_SHAPE)
            removed += 1
            if removed == NO_BALLS : RUNNING = False
            (BALL, BALL_SHAPE), object_colors, space = spawn_ball()
            blocked = False
        if not RUNNING : break
            
        
        # Rysowanie obiektów
        for body in space.bodies:
            for shape in body.shapes:
                shape.data.draw()
                
                if isinstance(shape, pymunk.Poly):
                    draw_polygon(body, shape)

                # Check for collisions with the ball
                if (body, shape) in OBSTACLES :
                    if in_tunnel() : continue
                    dist = shortest_distance(BALL_SHAPE, shape)
                    if dist <= BALL_RADIUS//10 :
                        add_points(int(round(point_function(circle_field(shape.radius)))))
            

        # Wyświetlanie licznika FPS
        text_fps = ""
        if fps == float('inf') : text_fps = "inf"
        else : text_fps = int(round(fps))
        
        draw_text(screen, f"FPS: {text_fps}", (0, 0), BLACK)
        draw_text(screen, f"Balls left: {NO_BALLS - removed}", (0, HEIGHT), BLACK)
        draw_text(screen, f"{POINTS}", (WIDTH // 2, 0), BLACK)
        draw_text(screen, f"Game speed: {speed}", (WIDTH, HEIGHT), BLACK)

        if display_fire :
            draw_text(screen, "FIRE!", (WIDTH//2, HEIGHT//2), rand_color(), font_size=80)

        pygame.display.flip()

    
    if removed == NO_BALLS :
        print()
        print("avg_frametime", avg_time)
        print("avg_fps", round(avg_fps))
        print("POINTS:", POINTS)
        
        with open(LEADERBOARD_PATH, 'r') as file :
            leaderboard = json.load(file)
            
        leaderboard["PREVIOUS_PLAYER"] = player_name

        if player_name in leaderboard["SCORES"] :
            leaderboard["SCORES"][player_name] = max(leaderboard["SCORES"][player_name], POINTS)
        else :
            leaderboard["SCORES"][player_name] = POINTS
            
        with open(LEADERBOARD_PATH, 'w') as FILE:
            json.dump(leaderboard, FILE, indent=4)

        menu.run_menu()
    else :
        pygame.quit()

if __name__ == "__main__":
    from initialize import main_run
    main_run()