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


POINTS = 0

VOLUME = 0.5

# Set up constants
BALLS = []
WALLS = []
POLYS = []
FLIPPERS = []

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
    global BALLS
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
            BALLS.append((r, position, static, mass, color, game_points, elast, collision_sound_file, effects))
        
        self.effects = {}
        
        self.effects["slow"] = [-float('inf'), 2]
        self.effects["epilepsy"] = [-float('inf')]
        self.effects["rainbow"] = [-float('inf')]
        
        for effect in effects :
            print(effect[1])
            self.effects[effect[0]] = effect[1]
        if effects != [] :
            print(self.effects)
            
        self.summon()


class Poly(Object):
    global POLYS
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
            POLYS.append((points, position, mass, moment, color, game_points, frict, elast, static, collision_sound_file))
        
    def draw(self, screen, rainbow_mode = False) :
        color = self.color
        if rainbow_mode:
            color = rand_color()
        vertices = self.shape.get_vertices()
        transformed_vertices = [self.body.local_to_world(vertex) for vertex in vertices]
        pygame.draw.polygon(screen, color, transformed_vertices, 0)


class Wall(Poly):
    global WALLS
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
        if add :
            WALLS.append((start_pos, end_pos, color, game_points, width, frict, elast, static, collision_sound_file))

class Flipper(Poly):
    global FLIPPERS
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
        FLIPPERS.append((length, angle, position, side, color, game_points, elast))


def run(preset_name = "third"):
    global POINTS, WALLS, FLIPPERS, BALLS, POLYS
    WIDTH, HEIGHT = 800, 1440
    ELASTICITY = 0.7
    BALL_RADIUS = 15
    NO_BALLS = 3
    FRICTION = 0.5
    WALL_WIDTH = 20
    # Definicja kolorów
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    FLIPPER_LENGTH = 60
    POINTS = 0
    LAUNCH_ENERGY = 75
    MINIMAL_ENERGY = 53
    TUNNEL_SIZE = 2.2*BALL_RADIUS
    TARGET_ANGLE = np.pi/3
    REACTION_TIME = 0.75
    BASE_WIDTH = WIDTH
    GRAVITY = (0, 981)
    WIDTH = int(round(WIDTH + WALL_WIDTH + 2.2 * BALL_RADIUS))
    breaking_point = (BASE_WIDTH - WALL_WIDTH//2,2 * WALL_WIDTH + BALL_RADIUS * 3)

    BALL_POSITION = (WIDTH - WALL_WIDTH - 1.1 * BALL_RADIUS, HEIGHT - WALL_WIDTH - 1.5 * BALL_RADIUS)

    FLIPPER_ANGLE = -np.pi/12
    FLIPPER_X = np.abs(FLIPPER_LENGTH * np.cos(FLIPPER_ANGLE))
    FLIPPER_Y = np.abs(FLIPPER_LENGTH * np.sin(FLIPPER_ANGLE))
    
    
    
    def symmetry(point) :
        if isinstance(point, list) :
            points = []
            for poin in point :
                points.append((BASE_WIDTH - poin[0], poin[1]))
            return points
        return BASE_WIDTH - point[0], point[1]
    
    pygame.init()
    pygame.mixer.music.set_volume(0.2)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    space = pymunk.Space()
    space.gravity = GRAVITY


    BALL_START = create_sound('ball_start.wav')
    FLIPPER_MOVE = create_sound('flipper_move.wav', percentage = 0.5)

    wall_color = rand_color()
    # Left flipper position
    position_left = (BASE_WIDTH // 2 - 2 * BALL_RADIUS - FLIPPER_X, 0.95 * HEIGHT - FLIPPER_Y)
    # right flipper position
    position_right = symmetry(position_left)
    
    # WALL args
    # start_pos, end_pos, color, game_points, width, frict, elast, static, collision_sound_file, add, space
    Wall(start_pos = (0, WALL_WIDTH//2), end_pos = (WIDTH, WALL_WIDTH//2), color = wall_color, game_points = 0, width = WALL_WIDTH, frict = FRICTION, elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    Wall(start_pos = (WALL_WIDTH//2, 0), end_pos = (WALL_WIDTH//2, HEIGHT), color = wall_color, game_points = 0, width = WALL_WIDTH, frict = FRICTION, elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    Wall(start_pos = (WIDTH - WALL_WIDTH//2, 0), end_pos = (WIDTH - WALL_WIDTH//2, HEIGHT), color = wall_color, game_points = 0, width = WALL_WIDTH, frict = FRICTION, elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    Wall(start_pos = (BASE_WIDTH - WALL_WIDTH//2, breaking_point[1]), end_pos = (BASE_WIDTH - WALL_WIDTH//2, HEIGHT), color = wall_color, game_points = 0, width = WALL_WIDTH, frict = FRICTION, elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    Wall(start_pos = (BASE_WIDTH, HEIGHT - WALL_WIDTH//2), end_pos = (WIDTH, HEIGHT - WALL_WIDTH//2), color = wall_color, game_points = 0, width = WALL_WIDTH, frict = FRICTION, elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    Wall(start_pos = (WIDTH - 2.5*WALL_WIDTH, 0), end_pos = (WIDTH, 2.5*WALL_WIDTH), color = wall_color, game_points = 0, width = WALL_WIDTH, frict = FRICTION, elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    Wall(start_pos = (WIDTH - 2.5*WALL_WIDTH, 0), end_pos = (WIDTH, 2.5*WALL_WIDTH), color = wall_color, game_points = 0, width = WALL_WIDTH, frict = FRICTION, elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    poin = [(0, HEIGHT), ((BASE_WIDTH // 2) - BALL_RADIUS, HEIGHT), (0, HEIGHT - 3*BALL_RADIUS)]
    Poly(points = poin, position = None, mass = None, moment = None, color = wall_color, game_points = 0, frict = FRICTION, elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", addition = True, space = space)
    Poly(points = symmetry(poin), position = None, mass = None, moment = None, color = wall_color, game_points = 0, frict = FRICTION, elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", addition = True, space = space)

    poin = [(WALL_WIDTH, 6*HEIGHT // 12),
            (7*WALL_WIDTH, 5.75*HEIGHT // 12),
            (WALL_WIDTH, 5*HEIGHT // 12)]
    Poly(points = poin, position = None, mass = None, moment = None, color = wall_color, game_points = 0, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", addition = True, space = space)
    poin = symmetry(poin)
    Poly(points = poin, position = None, mass = None, moment = None, color = wall_color, game_points = 0, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", addition = True, space = space)

    poin = [(WALL_WIDTH, 9*HEIGHT // 12),
            (3*WALL_WIDTH, 8.25*HEIGHT // 12),
            (WALL_WIDTH, 8*HEIGHT // 12)]
    Poly(points = poin, position = None, mass = None, moment = None, color = wall_color, game_points = 0, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", addition = True, space = space)
    poin = symmetry(poin)
    Poly(points = poin, position = None, mass = None, moment = None, color = wall_color, game_points = 0, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", addition = True, space = space)

    # START Left Castle
    # Left Tower
    poin = [(WALL_WIDTH, 3.25*HEIGHT // 12),
            (2*WALL_WIDTH, 3.25*HEIGHT // 12),
            (WALL_WIDTH, 3*HEIGHT // 12)]
    Poly(points = poin, position = None, mass = None, moment = None, color = wall_color, game_points = 0, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", addition = True, space = space)
    poin = [(1 * WALL_WIDTH, 4.25 * HEIGHT // 12),
            (1 * WALL_WIDTH, 4.5 * HEIGHT // 12),
            (2 * WALL_WIDTH, 4.25 * HEIGHT // 12)]
    Poly(points=poin, position=None, mass=None, moment=None, color=wall_color, game_points=0, frict=FRICTION,
         elast=ELASTICITY, static=True, collision_sound_file="wall_hit.wav", addition=True, space=space)
    # Right Tower
    poin = [(2*WALL_WIDTH + 2.2*BALL_RADIUS, 3.5*HEIGHT // 12),
            (4*WALL_WIDTH + 2.2*BALL_RADIUS, 3.5*HEIGHT // 12),
            (3*WALL_WIDTH + 2.2*BALL_RADIUS, 3.25*HEIGHT // 12)]
    Poly(points = poin, position = None, mass = None, moment = None, color = wall_color, game_points = 0, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", addition = True, space = space)
    poin = [(2*WALL_WIDTH + 2.2*BALL_RADIUS, 4.75*HEIGHT // 12),
            (3*WALL_WIDTH + 2.2*BALL_RADIUS, 5*HEIGHT // 12),
            (4*WALL_WIDTH + 2.2*BALL_RADIUS, 4.75*HEIGHT // 12)]
    Poly(points = poin, position = None, mass = None, moment = None, color = wall_color, game_points = 0, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", addition = True, space = space)
    # Castle Walls
    Wall(start_pos=(3*WALL_WIDTH + 2.25*BALL_RADIUS, 4.75*HEIGHT//12), end_pos=(3*WALL_WIDTH + 2.25*BALL_RADIUS, 3.5 * HEIGHT // 12), color = wall_color, game_points = 0, width=2* WALL_WIDTH, frict = FRICTION, elast=ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    Wall(start_pos=(1*WALL_WIDTH, 4.25*HEIGHT//12), end_pos=(1*WALL_WIDTH, 3.25 * HEIGHT // 12), color = wall_color, game_points = 0, width=2* WALL_WIDTH, frict = FRICTION, elast=ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    # END Left Castle

    # START Right Castle
    # Left Tower
    poin = [(WALL_WIDTH, 3.25*HEIGHT // 12),
            (2*WALL_WIDTH, 3.25*HEIGHT // 12),
            (WALL_WIDTH, 3*HEIGHT // 12)]
    poin = symmetry(poin)
    Poly(points = poin, position = None, mass = None, moment = None, color = wall_color, game_points = 0, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", addition = True, space = space)
    poin = [(1 * WALL_WIDTH, 4.25 * HEIGHT // 12),
            (1 * WALL_WIDTH, 4.5 * HEIGHT // 12),
            (2 * WALL_WIDTH, 4.25 * HEIGHT // 12)]
    poin = symmetry(poin)
    Poly(points=poin, position=None, mass=None, moment=None, color=wall_color, game_points=0, frict=FRICTION,
         elast=ELASTICITY, static=True, collision_sound_file="wall_hit.wav", addition=True, space=space)
    # Right Tower
    poin = [(2*WALL_WIDTH + 2.2*BALL_RADIUS, 3.5*HEIGHT // 12),
            (4*WALL_WIDTH + 2.2*BALL_RADIUS, 3.5*HEIGHT // 12),
            (3*WALL_WIDTH + 2.2*BALL_RADIUS, 3.25*HEIGHT // 12)]
    poin = symmetry(poin)
    Poly(points = poin, position = None, mass = None, moment = None, color = wall_color, game_points = 0, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", addition = True, space = space)
    poin = [(2*WALL_WIDTH + 2.2*BALL_RADIUS, 4.75*HEIGHT // 12),
            (3*WALL_WIDTH + 2.2*BALL_RADIUS, 5*HEIGHT // 12),
            (4*WALL_WIDTH + 2.2*BALL_RADIUS, 4.75*HEIGHT // 12)]
    poin = symmetry(poin)
    Poly(points = poin, position = None, mass = None, moment = None, color = wall_color, game_points = 0, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", addition = True, space = space)
    # Castle Walls
    Wall(start_pos=symmetry((3*WALL_WIDTH + 2.25*BALL_RADIUS, 4.75*HEIGHT//12)), end_pos=symmetry((3*WALL_WIDTH + 2.25*BALL_RADIUS, 3.5 * HEIGHT // 12)), color = wall_color, game_points = 0, width=2* WALL_WIDTH, frict = FRICTION, elast=ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    Wall(start_pos=symmetry((1*WALL_WIDTH, 4.25*HEIGHT//12)), end_pos=symmetry((1*WALL_WIDTH, 3.25 * HEIGHT // 12)), color = wall_color, game_points = 0, width=2* WALL_WIDTH, frict = FRICTION, elast=ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    # END Right Castle

    # START Basket
    leng_w = 200
    leng_h = 100

    poin = [(BASE_WIDTH // 5 + 80, 10.75 * HEIGHT // 12 - 60),
            (BASE_WIDTH // 5 + 80, 10.75 * HEIGHT // 12 - 20),
            (BASE_WIDTH // 5, 10 * HEIGHT // 12 - 30)]
    Poly(points=poin, position=None, mass=None, moment=None, color=wall_color, game_points=0, frict=FRICTION,
         elast=ELASTICITY, static=True, collision_sound_file="wall_hit.wav", addition=True, space=space)
    poin = symmetry(poin)
    Poly(points=poin, position=None, mass=None, moment=None, color=wall_color, game_points=0, frict=FRICTION,
         elast=ELASTICITY, static=True, collision_sound_file="wall_hit.wav", addition=True, space=space)

    position_left_2 = (position_left[0] - np.cos(FLIPPER_ANGLE)*leng_w,
                       position_left[1] + np.sin(FLIPPER_ANGLE)*leng_h)
    position_right_2 = symmetry(position_left_2)
    Wall(start_pos = position_left, end_pos = position_left_2, color = wall_color, game_points = 0, width = WALL_WIDTH*0.65, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    Wall(start_pos = position_right, end_pos = position_right_2, color = wall_color, game_points = 0, width = WALL_WIDTH*0.65, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    s_p = (position_left_2[0],
           position_left_2[1] + 5)
    e_p = (position_left_2[0],
           position_left_2[1] - 1.5*leng_h)
    Wall(start_pos = s_p, end_pos = e_p, color = wall_color, game_points = 0, width = WALL_WIDTH*0.65, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    Wall(start_pos=symmetry(s_p), end_pos=symmetry(e_p), color = wall_color, game_points = 0, width = WALL_WIDTH*0.65,
         frict = FRICTION, elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    s_p = (position_left_2[0] - 30,
           position_left_2[1] - 1.5*leng_w + 30)
    e_p = (position_left_2[0],
           position_left_2[1] - 1.5*leng_h)
    Wall(start_pos = s_p, end_pos = e_p, color = wall_color, game_points = 0, width = WALL_WIDTH*0.65, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    Wall(start_pos=symmetry(s_p), end_pos=symmetry(e_p), color = wall_color, game_points = 0, width = WALL_WIDTH*0.65, frict = FRICTION,
         elast = ELASTICITY, static = True, collision_sound_file = "wall_hit.wav", space=space)
    # END Basket
    
    flipper_color = rand_color()
    # Flipper args
    # length, angle, position, side, color, game_points, elast, collision_sound_file, space
    # flippers must be in table for proper demo
    flippers = []
    flippers.append(Flipper(FLIPPER_LENGTH, FLIPPER_ANGLE, position_right, 'right', flipper_color, space = space))
    flippers.append(Flipper(FLIPPER_LENGTH, FLIPPER_ANGLE, position_left, 'left', flipper_color, space = space))
    # Left flipper position
    position_left = (7*WALL_WIDTH - 10, 5.75*HEIGHT // 12)
    # right flipper position
    position_right = symmetry(position_left)
    flippers.append(Flipper(1.5*FLIPPER_LENGTH, FLIPPER_ANGLE, position_right, 'right', flipper_color, space = space))
    flippers.append(Flipper(1.5*FLIPPER_LENGTH, FLIPPER_ANGLE, position_left, 'left', flipper_color, space = space))

    # Ball args
    # r, position, static, mass, color, game_points, elast, collision_sound_file, add
    ball_color = rand_color()
    BALL_PARAMS = (BALL_RADIUS, BALL_POSITION, False, None, ball_color, 0, ELASTICITY, None)
    BALL = Ball(*BALL_PARAMS, add = False, space = space)


    TARGET_HEIGHT = WALL_WIDTH*(3/2)
    INITIAL_HEIGHT = HEIGHT - TARGET_HEIGHT
    
    POINTER_PARAMS = (WALL_WIDTH//4, (WIDTH - WALL_WIDTH//2, INITIAL_HEIGHT), True, None, ball_color, 0, ELASTICITY, None)
    
    POINTER = Ball(*POINTER_PARAMS, add = False, space = space)
    
    BLOCKADE_PARAMS = ((BASE_WIDTH - WALL_WIDTH//2, 0), breaking_point, wall_color, 0, WALL_WIDTH, FRICTION, ELASTICITY, True, "wall_hit.wav")
    BLOCKADE = Wall(*BLOCKADE_PARAMS, add = False, space = space)
    BLOCKADE.destroy()

    obstacle_color = rand_color()

    poin = (BASE_WIDTH // 5, 3 * HEIGHT // 4)
    effects_table = [("slow", (50, 0.5))]
    Ball(position = poin, r = 2*BALL_RADIUS, color = obstacle_color, static = True, elast= 2*ELASTICITY, game_points = 400, collision_sound_file = "bell.wav", effects = effects_table, space = space)
    Ball(position = symmetry(poin), r = 2*BALL_RADIUS, color = obstacle_color, static = True, elast= 2*ELASTICITY, game_points = 400, collision_sound_file = "bell.wav", effects = effects_table, space = space)

    poin = (BASE_WIDTH // 5 * 2, 1.75 * HEIGHT // 4)
    effects_table = [("slow", (50, 0.5))]
    Ball(position = poin, r = 2*BALL_RADIUS, color = obstacle_color, static = True, elast= 2*ELASTICITY, game_points = 400, collision_sound_file = "bell.wav", effects = effects_table, space = space)
    Ball(position = symmetry(poin), r = 2*BALL_RADIUS, color = obstacle_color, static = True, elast= 2*ELASTICITY, game_points = 400, collision_sound_file = "bell.wav", effects = effects_table, space = space)

    poin = (BASE_WIDTH // 2, HEIGHT // 7)
    Ball(position = poin, r = 2*BALL_RADIUS, color = obstacle_color, static = True, elast = 2*ELASTICITY, game_points = 400, collision_sound_file="bell.wav", effects = effects_table, space = space)

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
        text_rect.center = pos
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

    max_energy = LAUNCH_ENERGY
    min_energy = MINIMAL_ENERGY
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
    
    eps = 0.001
    
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
        if speed >= 0 :
            speed = max(speed, eps)
        else :
            speed = min(speed, eps)
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

    pygame.quit()
    
    print("json saving")
    DATA = {}
    
    DATA["HEIGHT"] = HEIGHT
    DATA["ELASTICITY"] = ELASTICITY
    DATA["BALL_RADIUS"] = BALL_RADIUS
    DATA["NO_BALLS"] = NO_BALLS
    DATA["WALL_WIDTH"] = WALL_WIDTH
    DATA["FLIPPER_LENGTH"] = FLIPPER_LENGTH
    DATA["LAUNCH_ENERGY"] = LAUNCH_ENERGY
    DATA["MINIMAL_ENERGY"] =  MINIMAL_ENERGY
    DATA["TUNNEL_SIZE"] = TUNNEL_SIZE
    DATA["REACTION_TIME"] = REACTION_TIME
    DATA["BASE_WIDTH"] = BASE_WIDTH
    DATA["WIDTH"] = WIDTH
    DATA["BREAKING_POINT"] = breaking_point
    DATA["FLIPPER_ANGLE"] = FLIPPER_ANGLE
    DATA["FLIPPER_X"] = FLIPPER_X
    DATA["FLIPPER_Y"] = FLIPPER_Y
    DATA["BALL_POSITION"] = BALL_POSITION
    DATA["GRAVITY"] = space.gravity
    DATA["TARGET_HEIGHT"] = TARGET_HEIGHT
    DATA["TARGET_ANGLE"] = TARGET_ANGLE
    DATA["WALLS"] = WALLS
    DATA["BALLS"] = BALLS
    DATA["FLIPPERS"] = FLIPPERS
    DATA["POLYS"] = POLYS
    DATA["POINTER_PARAMS"] = POINTER_PARAMS
    DATA["BALL_PARAMS"] = BALL_PARAMS
    DATA["BLOCKADE_PARAMS"] = BLOCKADE_PARAMS
    DATA["BALL_POSITION"] = BALL_POSITION
    
    
    with open(os.path.join(SCRIPT_PATH, "maps", preset_name + ".json"), 'w') as FILE:
        json.dump(DATA, FILE, indent=4)

    print("json saving completed")
if __name__ == "__main__":
    run()
    
