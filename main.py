import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
# os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
import pymunk
from utility_functions import *
import pause_menu as pause
import menu
import json

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
SOUND_PATH = os.path.join(SCRIPT_PATH, "sounds")
LEADERBOARD_PATH = os.path.join(SCRIPT_PATH, "layouts", "leaderboard.json")

# Definicja kolorów
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
POINTS = 0

VOLUME = 0.5

BALL_COLLISION_TYPE = 1
OBSTACLE_COLLISTION_TYPE = 2
POLY_COLLISION_TYPE = 2

def create_sound(filename, percentage = 1) :
    sound = pygame.mixer.Sound(os.path.join(SOUND_PATH, filename))
    sound.set_volume(VOLUME * percentage)
    return sound

class Object:
    def __init__(self, color=rand_color(), game_points = 0, collision_sound_file=None, space=None):
        self.color = color
        self.game_points = game_points
        self.body = None
        self.shape = None
        self.space = space
        self.collision_sound = None
        if collision_sound_file is not None:
            self.collision_sound = create_sound(collision_sound_file)
        
            
    
    def summon(self, space=None):
        if space is None:
            space = self.space
        try :
            space.add(self.body, self.shape)
        except :
            print("Couldn't add this to space")
    def destroy(self):
        try :
            self.space.remove(self.body)
        except :
            print("Exception occured while trying to destroy object", self.body)
        try :
            self.space.remove(self.shape)
        except :
            print("Exception occured while trying to destroy object", self.shape)
            

    def draw(self, screen, rainbow_mode=False):
        color = self.color
        if rainbow_mode:
            color = rand_color()
        if isinstance(self.shape, pymunk.Circle):
            pos = self.body.position
            radius = self.shape.radius
            pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), int(radius), 0)
        elif isinstance(self.shape, pymunk.Poly):
            vertices = self.shape.get_vertices()
            transformed_vertices = [self.body.local_to_world(vertex) for vertex in vertices]
            pygame.draw.polygon(screen, self.color, transformed_vertices, 0)

    def play_collision_sound(self):
        sound = self.collision_sound
        if sound is not None:
            sound.play()

    def collision(self) :
        global POINTS
        self.play_collision_sound()
        if self.game_points == 0 : return
        POINTS += self.game_points
        print("+", self.game_points, "POINTS!!  -> now having", POINTS, "POINTS")


class Ball(Object):
    def __init__(self, r, position, static=False, mass=None, color=rand_color(), game_points = 0, elast=0.5, collision_sound_file=None, effects = [], add = True, space=None):
        super().__init__(color, game_points, collision_sound_file, space)
        if static:
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            self.body = pymunk.Body()
        self.body.position = position
        self.shape = pymunk.Circle(self.body, r)
        if mass is not None:
            self.shape.mass = mass
        else:
            self.shape.mass = self.shape.area / 20
        self.shape.elasticity = elast
        self.shape.data = self    
        self.shape.collision_type = BALL_COLLISION_TYPE
        if add :
            self.shape.collision_type = OBSTACLE_COLLISTION_TYPE
        
        self.effects = {}
        
        self.effects["slow"] = [-float('inf'), 2]
        self.effects["epilepsy"] = [-float('inf')]
        self.effects["rainbow"] = [-float('inf')]
        
        for effect in effects :
            self.effects[effect[0]] = effect[1]
            
        self.summon()


class Poly(Object):
    def __init__(self, points, position = None, mass=None, moment=None, color=rand_color(), game_points = 0, frict=0.5, elast=0.5, static=True, collision_sound_file=None, addition = False, space=None):
        super().__init__(color, game_points, collision_sound_file, space)
        if position == None :
            position = (sum([point[0] for point in points]) / len(points), sum([point[1] for point in points]) / len(points))
            points = [(point[0] - position[0], point[1] - position[1]) for point in points]
            
        mass = pymunk.moment_for_poly(1, points) if mass is None else mass
        moment = pymunk.moment_for_poly(mass, points) if moment is None else moment
        
        if static:
            self.body = pymunk.Body(mass, moment, body_type=pymunk.Body.STATIC)
        else:
            self.body = pymunk.Body(mass, moment)
        
        self.body.position = position
        self.shape = pymunk.Poly(self.body, points)
        self.shape.elasticity = elast
        self.shape.friction = frict
        self.shape.collision_type = POLY_COLLISION_TYPE
        self.shape.data = self
        if addition :
            self.summon()
        
    def draw(self, screen, rainbow_mode = False) :
        color = self.color
        if rainbow_mode:
            color = rand_color()
        vertices = self.shape.get_vertices()
        transformed_vertices = [self.body.local_to_world(vertex) for vertex in vertices]
        pygame.draw.polygon(screen, color, transformed_vertices, 0)


class Wall(Poly):
    def __init__(self, start_pos, end_pos, color=rand_color(), game_points = 0, width=10, frict=0.5, elast=0.5, static=True, collision_sound_file=None, add = True, space=None):
        w = width // 2
        a_x, a_y = start_pos
        b_x, b_y = end_pos
        v_l = ((b_x - a_x) ** 2 + (b_y - a_y) ** 2) ** 0.5
        v_x, v_y = (b_x - a_x), (b_y - a_y)
        points = [(a_x - w * (v_y / v_l), a_y + w * (v_x / v_l)),
                  (a_x + w * (v_y / v_l), a_y - w * (v_x / v_l)),
                  (b_x + w * (v_y / v_l), b_y - w * (v_x / v_l)),
                  (b_x - w * (v_y / v_l), b_y + w * (v_x / v_l))]

        super().__init__(points = points, color=color, game_points = game_points, frict=frict, elast=elast, static=static, collision_sound_file=collision_sound_file, space=space)
        self.summon()

class Flipper(Poly):
    def __init__(self, length, angle, position, side = "right", color = rand_color(), game_points = 0, elast = 0.7, collision_sound_file = None, space=None):
        points = generate_flipper_points(length, angle)
        self.side = side
        if side == "left":
            points = [(-point[0], point[1]) for point in points]
        
        mass = poly_field(points)
        moment = pymunk.moment_for_poly(mass, points)
        
        super().__init__(points = points, position = position, mass=mass, moment=moment, color=color, game_points = game_points, elast=elast, static=False, collision_sound_file = collision_sound_file, space=space)
        self.body.position = position
        self.shape.filter = pymunk.ShapeFilter(categories=0x2)
        self.summon()


def run(preset="fancy", player_name = "Unknown", screen = None):
    global POINTS, WALLS, FLIPPERS, BALLS, POLYS
    
    print("RUNNING WITH PRESET", preset)

    with open(os.path.join(SCRIPT_PATH, "maps", preset + ".json"), 'r') as file :
        config = json.load(file)
        
    HEIGHT = config["HEIGHT"]
    BALL_RADIUS = config["BALL_RADIUS"]
    NO_BALLS = config["NO_BALLS"]
    WALL_WIDTH = config["WALL_WIDTH"]
    TARGET_HEIGHT = config["TARGET_HEIGHT"]
    TARGET_ANGLE = config["TARGET_ANGLE"]
    REACTION_TIME = config["REACTION_TIME"]
    BASE_WIDTH = config["BASE_WIDTH"]
    WIDTH = config["WIDTH"]
    TUNNEL_SIZE = config["TUNNEL_SIZE"]
    BALL_POSITION = config["BALL_POSITION"]
    INITIAL_HEIGHT = HEIGHT - TARGET_HEIGHT
    
    
    pygame.mixer.music.set_volume(0.2)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    space = pymunk.Space()
    space.gravity = config["GRAVITY"]


    BALL_START = create_sound('ball_start.wav')
    FLIPPER_MOVE = create_sound('flipper_move.wav', percentage = 0.5)

    for PARAMS in config["WALLS"] :
        Wall(*PARAMS, add = True, space = space)
        
    for PARAMS in config["BALLS"] :
        Ball(*PARAMS, add = True, space = space)
        
    for PARAMS in config["POLYS"] :
        Poly(*PARAMS, addition = True, space = space)

    flippers = []
    for PARAMS in config["FLIPPERS"] :
        flippers.append(Flipper(*PARAMS, space = space))

    BALL = Ball(*config["BALL_PARAMS"], add = False, space = space)
    POINTER = Ball(*config["POINTER_PARAMS"], add = False, space = space)
    BLOCKADE = Wall(*config["BLOCKADE_PARAMS"], add = False, space = space)
    

    def ball_collision_handler(arbiter, space, data):
        other_shape = arbiter.shapes[1]
        other_shape.data.collision()
        return True

    def poly_collision_handler(arbiter, space, data):
        return False
    
    handler = space.add_collision_handler(BALL_COLLISION_TYPE, POLY_COLLISION_TYPE)
    handler.begin = ball_collision_handler
    
    poly_handler = space.add_collision_handler(POLY_COLLISION_TYPE, POLY_COLLISION_TYPE)
    poly_handler.begin = poly_collision_handler


    def at_start() :
        nonlocal BALL
        
        if distance_points(BALL_POSITION, BALL.body.position) > TUNNEL_SIZE :
            return False
        return True
    
    def is_inside(shape, wid = WIDTH, hei = HEIGHT) :
        x,y = shape.position
        eps = 2*BALL_RADIUS
        if x < - eps : return False
        if x > wid + eps : return False
        if y < - eps : return False
        if y > hei + eps : return False
        return True
    
    
    def not_paused() :
        nonlocal paused
        paused = False
        
    def in_tunnel() :
        nonlocal BALL, BASE_WIDTH
        if BASE_WIDTH - 2*BALL_RADIUS - WALL_WIDTH < BALL.body.position[0] : return True
        return False
    
    
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

    right_pressed = False
    left_pressed = False
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
    BLOCKADE.destroy()
    epilepsy_mode = False
    rainbow_mode = False
    
    RUNNING = True
    
    while RUNNING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and not paused:
                    right_pressed = True
                    FLIPPER_MOVE.play()
                elif event.key == pygame.K_LEFT and not paused:
                    left_pressed = True
                    FLIPPER_MOVE.play()
                elif event.key == pygame.K_SPACE and not paused:
                    if at_start() :
                        space_pressed = True
                        energy_direction = 1
                elif event.key == pygame.K_ESCAPE :
                    paused = not paused
            elif event.type == pygame.KEYUP and not paused:
                if event.key == pygame.K_RIGHT:
                    right_pressed = False
                elif event.key == pygame.K_LEFT:
                    left_pressed = False
                elif event.key == pygame.K_SPACE:
                    if at_start() :
                        BALL.body.apply_impulse_at_local_point((0, -1_000*energy_stored))
                        BALL_START.play()
                    space_pressed = False
                    display_fire = False
                elif event.key == pygame.K_c:
                    BALL.color = rand_color() 
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

        if epilepsy_mode : screen.fill(random.choice([WHITE, BLACK]))
        else : screen.fill(BLACK)

        clock.tick(model_fps)
        fps = clock.get_fps()
        val = 1 / model_fps
        if fps > 0:
            val = 1 / fps

        avg_time = ((avg_time * i) + val) / (i + 1)
        avg_fps = ((avg_fps * i) + fps) / (i + 1)

        

        epilepsy_possibility = False
        slow_possibility = False
        slow_value = 1
        rainbow_possibility = False
        for body in space.bodies:
            if not is_inside(body) :
                shape.data.destroy()
                del(shape.data)
            for shape in body.shapes:
                shape.data.draw(screen, rainbow_mode)
                if not isinstance(shape, pymunk.Circle) : continue
                if shape == BALL.shape : continue
                dist = shortest_distance(shape, BALL.shape)
                for effect in shape.data.effects :
                    effect_dist = shape.data.effects[effect][0]
                    if effect == "epilepsy" :
                        if dist <= effect_dist :
                            epilepsy_possibility = True
                    elif effect == "slow" : 
                        if dist <= effect_dist :
                            slow_possibility = True
                            slow_value = shape.data.effects[effect][1]
                    elif effect == "rainbow" : 
                        if dist <= effect_dist :
                            rainbow_possibility = True
                    
        epilepsy_mode = epilepsy_possibility
        rainbow_mode = rainbow_possibility
        if slow_possibility : speed = slow_value
        else : speed = 1
                
        # Symulacja
        if not paused :
            val *= speed
            space.step(val)
        else :
            for button in PAUSE_LAYOUT.values():
                button.draw(screen)
                continue
                
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
            
            POINTER.body.position = (POINTER.body.position[0], pointer_height)
                
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
                
                POINTER.body.position = (POINTER.body.position[0], pointer_height)

        for flipper in flippers :
            flipper.body.velocity = (0, 0)
            target_angle = 0
            if flipper.side == "right" :
                if right_pressed :
                    target_angle = TARGET_ANGLE
                flipper.body.angular_velocity = (target_angle - flipper.body.angle) * 30
            elif flipper.side == "left" :
                if left_pressed :
                    target_angle = -TARGET_ANGLE
                flipper.body.angular_velocity = (target_angle - flipper.body.angle) * 30
        
        if not is_inside(BALL.body) :
            BALL.destroy()
            removed += 1
            if removed == NO_BALLS : RUNNING = False
            BALL.body.velocity = (0,0)
            BALL.body.position = BALL_POSITION
            BALL.summon()
            blocked = False
            BLOCKADE.destroy()
        if not in_tunnel() and not blocked :
            BLOCKADE.summon()
            blocked = True
        if not RUNNING : break
        
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
    