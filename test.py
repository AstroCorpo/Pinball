import pygame
import os
import pymunk.pygame_util
from utility_functions import *
from copy import deepcopy

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

# Ustawienie wymiarów okna
# width, height = 2550, 1340
width, height = 500, 900

DATA = {}


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
REACTION_TIME = 0.75

base_width = width
width = int(round(width + WALL_WIDTH + 2.2 * BALL_RADIUS))
breaking_point = (base_width - WALL_WIDTH//2,2 * WALL_WIDTH + BALL_RADIUS * 3)

a, b, c = [(0,height),((base_width // 2) - BALL_RADIUS,height), (0, height - 3*BALL_RADIUS)]
FLIPPER_ANGLE = -np.arctan( (np.abs(distance_points(a,c))) / (np.abs(distance_points(b,a))) )
FLIPPER_X = np.abs(FLIPPER_LENGTH * np.cos(FLIPPER_ANGLE))
FLIPPER_Y = np.abs(FLIPPER_LENGTH * np.sin(FLIPPER_ANGLE))

BALLS = []
WALLS = []
TRIANGLES = []
RIGHT_FLIPPERS = []
LEFT_FLIPPERS = []
BLOCKADES = []
MAIN_BALLS = []
OBSTACLES = []
POINTERS = []

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


def create_ball(r = BALL_RADIUS, position = rand_pos(), static = False, mass = None, color = rand_color(), elasticity = ELASTICITY, add = True, type = None, second_pos = None) :
    global BALLS
    if add :
        if type == "o" :
            OBSTACLES.append((r, position, static, mass, color, elasticity))
        elif type == "p" :
            POINTERS.append((r, position, static, mass, color, elasticity))
        else :
            BALLS.append((r, position, static, mass, color, elasticity))
        
        # print("-> create_ball", end = " ")
        # print(r, end = ",")
        # print(position[0], end = ",")
        # print(position[1], end = ",")
        # print(static, end = ",")
        # print(mass, end = ",")
        # print(color[0], end = ",")
        # print(color[1], end = ",")
        # print(color[2], end = ",")
        # print(elasticity, end = " \n")
        # print(" ")
    
    
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

def create_wall(start_pos = rand_pos(), end_pos = rand_pos(), color = rand_color(), widt = WALL_WIDTH, friction = FRICTION, elasticity = ELASTICITY, static = True, add = True) :
    global WALLS
    if add :
        WALLS.append((start_pos, end_pos, color, widt, friction, elasticity, static))
        
        # print("-> create_wall", end = " ")
        # print(start_pos[0], end = ",")
        # print(start_pos[1], end = ",")
        # print(end_pos[0], end = ",")
        # print(end_pos[1], end = ",")
        # print(color[0], end = ",")
        # print(color[1], end = ",")
        # print(color[2], end = ",")
        # print(width, end = ",")
        # print(friction, end = ",")
        # print(elasticity, end = ",")
        # print(static, end = " \n")
        # print(" ")
    
    
    w = widt // 2
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
    shape.filter = pymunk.ShapeFilter(categories=0x1)
    space.add(body, shape)

    object_colors[shape] = color

    return body, shape
    



# ball2,ball2_shape = create_ball(r = BALL_RADIUS, position = rand_pos(), static = False, mass = None, color = rand_color(), elasticity = ELASTICITY)

def create_triangle(points, color, static = True, elast = ELASTICITY, add = True) :
    global TRIANGLES
    if add :
        TRIANGLES.append((points, color, static, elast))    
        # print("-> create_triangle", end = " ")
        # print(points[0][0], end = ",")
        # print(points[0][1], end = ",")
        # print(points[1][0], end = ",")
        # print(points[1][1], end = ",")
        # print(points[2][0], end = ",")
        # print(points[2][1], end = ",")
        # print(color[0], end = ",")
        # print(color[1], end = ",")
        # print(color[2], end = ",")
        # print(static, end = ",")
        # print(elast, end = " \n")
        # print(" ")
    
    
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
    
    return body, shape
    

def create_flipper(length, angle, position, side, color, elast = ELASTICITY, name = "", add = True) :
    global RIGHT_FLIPPERS, RIGHT_FLIPPERS
    
    if name == "base_" : add = False
    
    if add :
        if side == "right" :
            RIGHT_FLIPPERS.append((length, angle, position, side, color, elast))
        if side == "left" :
            LEFT_FLIPPERS.append((length, angle, position, side, color, elast))
            
        # print("-> create_flipper", end = " ")
        # print(length, end = ",")
        # print(angle, end = ",")
        # print(position[0], end = ",")
        # print(position[1], end = ",")
        # print("'" + side + "'", end = ",")
        # print(color[0], end = ",")
        # print(color[1], end = ",")
        # print(color[2], end = ",")
        # print("'" + name + side + "_flipper" + "'", end = " \n")
        # print(" ")
    
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
    space.add(flipper_body, flipper_shape)

    object_colors[flipper_shape] = color

    return flipper_body, flipper_shape


def replace_base_flippers() :
    global base_right_flipper_body, base_right_flipper_shape
    space.remove(base_right_flipper_body)
    space.remove(base_right_flipper_shape)
    
    base_right_flipper_body, base_right_flipper_shape = create_flipper(2*BALL_RADIUS, 0, (width - WALL_WIDTH - 2.2*BALL_RADIUS, height - WALL_WIDTH), 'left', WHITE, "base_", add = False)
    
    
    return base_right_flipper_body, base_right_flipper_shape

def destroy_blockade() :
    space.remove(blockade)
    space.remove(blockade_shape)

    # return create_wall(start_pos = (base_width, 0), end_pos = breaking_point,color = WHITE)

def summon_blockade() :
    # # print("# BLOCKADE", end = " ")
    
    BLOCKADES.append(((base_width - WALL_WIDTH//2, 0), breaking_point, WHITE, WALL_WIDTH, FRICTION, ELASTICITY, True))
    
    return create_wall(start_pos = (base_width - WALL_WIDTH//2, 0), end_pos = breaking_point, color = WHITE, widt = WALL_WIDTH, friction = FRICTION, elasticity = ELASTICITY, static = True, add = False)

BALL_POSITION = None

def spawn_ball() :
    global BALL_POSITION
    destroy_blockade()
    replace_base_flippers()
    BALL_POSITION = (width - WALL_WIDTH - 1.1 * BALL_RADIUS, height - WALL_WIDTH - 1.5 * BALL_RADIUS)
    # print(ball_position[0], "# BALL_POSITION_X")
    # print(ball_position[1], "# BALL_POSITION_Y")
    # # print("# BALL", end = " ")
    
    MAIN_BALLS.append((BALL_RADIUS, BALL_POSITION, False, None, rand_color(), ELASTICITY))
    
    return create_ball(r = BALL_RADIUS, position = BALL_POSITION, static = False, mass = None, color = rand_color(), elasticity = ELASTICITY, add = False)

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
def draw_text_inside(surface, text, pos, color, font_size=24):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def is_inside(position,wid = width, hei = height) :
    x,y = position
    if x < BALL_RADIUS : return False
    if x > wid - BALL_RADIUS : return False
    if y < BALL_RADIUS : return False
    if y > hei + 2* BALL_RADIUS : return False
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

# Inicjalizacja Pygame
pygame.init()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pinball")

# Stworzenie obiektu Clock do kontrolowania FPS
clock = pygame.time.Clock()

space = pymunk.Space()  # Create a Space which contain the simulation
space.gravity = 0, 981  # Set its gravity

object_colors = {}
def symmetry(point) :
    if isinstance(point, list) :
        points = []
        for poin in point :
            points.append((base_width - poin[0], poin[1]))
        return points
    return base_width - point[0], point[1]

def baricenter(points) :
    a, b = 0,0
    for c,d in points :
        a += c
        b += d
    return (a/len(points), b/(len(points)))

def shortest(point, points) :
    dist = float('inf')
    for poin in points :
        dist = min(dist,distance_points(point, poin))
    return dist

position_left = (base_width // 2 - 2 * BALL_RADIUS - FLIPPER_X, 0.95 * height - FLIPPER_Y)
position_right = symmetry(position_left)
flipper_color = rand_color()





walls = []

# START


# poin = [(base_width // 5 + 10, 10.75*height // 12 - 10), (base_width // 5 + 30 + 10, 10.75*height // 12 + 7 - 10), (base_width // 5 + 10, 10*height // 12 - 10)]
# center_poin = baricenter(poin)
# radius = shortest_in_triangle(poin, center_poin)
# # # print("# OBSTACLE",end = " ")
# (create_ball(position=center_poin, r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY, add =True, type = "o"))
# # # print("# OBSTACLE",end = " ")
# (create_ball(position=symmetry(center_poin), r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY, add =True, type = "o"))

# for i in range(3) :
#     prev = center_poin
#     for _ in range(10) :
#         vect1 = (poin[i][0] - prev[0], poin[i][1] - prev[1])
#         vect1 /= distance_points((0,0), vect1)
#         vect1 = (vect1[0]*radius + prev[0], vect1[1]*radius + prev[1])
#         radius = shortest_in_triangle(poin, vect1)
#         # # print("# OBSTACLE",end = " ")
#         (create_ball(position=vect1, r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY, add =True, type = "o"))
#         # # print("# OBSTACLE",end = " ")
#         (create_ball(position=symmetry(vect1), r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY, add =True, type = "o"))
#         prev = vect1
        
# walls.append(create_triangle(poin, color = RED, elast = 2*ELASTICITY))
# walls.append(create_triangle(symmetry(poin), color = RED, elast = 2*ELASTICITY))



# poin = [(WALL_WIDTH, 9*height // 12), (2*WALL_WIDTH, 8.75*height // 12), (WALL_WIDTH, 8.5*height // 12)]
# center_poin = baricenter(poin)
# radius = shortest(center_poin, poin)
# # # print("# OBSTACLE",end = " ")
# (create_ball(position=center_poin, r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY, add =True, type = "o"))
# # # print("# OBSTACLE",end = " ")
# (create_ball(position=symmetry(center_poin), r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY,add =True, type = "o"))


# for i in range(3) :
#     prev = center_poin
#     for _ in range(10) :
#         vect1 = (poin[i][0] - prev[0], poin[i][1] - prev[1])
#         vect1 /= distance_points((0,0), vect1)
#         vect1 = (vect1[0]*radius + prev[0], vect1[1]*radius + prev[1])
#         radius = shortest_in_triangle(poin, vect1)
#         # # print("# OBSTACLE",end = " ")
#         (create_ball(position=vect1, r = radius, color=BLUE, static = True, elasticity = 0, add =True, type = "o"))
#         # # print("# OBSTACLE",end = " ")
#         (create_ball(position=symmetry(vect1), r = radius, color=BLUE, static = True, elasticity = 0, add =True, type = "o"))
#         prev = vect1

# walls.append(create_triangle(poin, color = RED, elast = 2*ELASTICITY))
# walls.append(create_triangle(symmetry(poin), color = RED, elast = 2*ELASTICITY))

# poin = [(base_width // 3, 8.75*height // 12)]
# center_poin = baricenter(poin)
# # # print("# OBSTACLE",end = " ")
# (create_ball(position=center_poin, r = 2*BALL_RADIUS, color=BLUE, static = True, elasticity = 2*ELASTICITY, add =True, type = "o"))
# # # print("# OBSTACLE",end = " ")
# (create_ball(position=symmetry(center_poin), r = 2*BALL_RADIUS, color=BLUE, static = True, elasticity = 2*ELASTICITY,add =True, type = "o"))

# poin = [(WALL_WIDTH, 7*height // 12), (4*WALL_WIDTH, 6.5*height // 12), (WALL_WIDTH, 6*height // 12)]
# walls.append(create_triangle(poin, color = WHITE))
# walls.append(create_triangle(symmetry(poin), color = WHITE))


# right_flipper_body2, right_flipper_shape2 = create_flipper(FLIPPER_LENGTH, FLIPPER_ANGLE, symmetry((3.6*WALL_WIDTH, 6.5*height // 12)), 'right', flipper_color)
# left_flipper_body2, left_flipper_shape2 = create_flipper(FLIPPER_LENGTH, FLIPPER_ANGLE, (3.6*WALL_WIDTH, 6.5*height // 12), 'left', flipper_color)

# walls.append(create_wall(start_pos=(WALL_WIDTH + WALL_WIDTH//2, 6.5*height // 12),end_pos=(WALL_WIDTH + WALL_WIDTH//2, 3.25*height // 12), static=True, color=WHITE, widt=WALL_WIDTH))
# walls.append(create_wall(start_pos=symmetry((WALL_WIDTH + WALL_WIDTH//2, 6.5*height // 12)),end_pos=symmetry((WALL_WIDTH + WALL_WIDTH//2, 3.25*height // 12)), static=True, color=WHITE, widt=WALL_WIDTH))

# poin = [(WALL_WIDTH, 3.25*height // 12), (2*WALL_WIDTH, 3.25*height // 12), (WALL_WIDTH, 3*height // 12)]
# center_poin = baricenter(poin)
# radius = shortest(center_poin, poin)
# # # print("# OBSTACLE",end = " ")
# (create_ball(position=center_poin, r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY,add =True, type = "o"))
# # # print("# OBSTACLE",end = " ")
# (create_ball(position=symmetry(center_poin), r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY,add =True, type = "o"))
# walls.append(create_triangle(poin, color = RED, elast = 2*ELASTICITY))
# walls.append(create_triangle(symmetry(poin), color = RED, elast = 2*ELASTICITY))

# poin = [(2*WALL_WIDTH + 2.2*BALL_RADIUS, 5.25*height // 12), (3*WALL_WIDTH + 2.2*BALL_RADIUS, 5.5*height // 12), (3*WALL_WIDTH + 2.2*BALL_RADIUS, 5.25*height // 12)]
# center_poin = baricenter(poin)
# radius = shortest(center_poin, poin)
# # print("# OBSTACLE",end = " ")
# (create_ball(position=center_poin, r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY,add =True, type = "o"))
# # print("# OBSTACLE",end = " ")
# (create_ball(position=symmetry(center_poin), r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY, add =True, type = "o"))
# walls.append(create_triangle(poin, color = RED, elast = 2*ELASTICITY))
# walls.append(create_triangle(symmetry(poin), color = RED, elast = 2*ELASTICITY))


# poin = [(3*WALL_WIDTH + 2.2*BALL_RADIUS, 4.25*height // 12), (3*WALL_WIDTH + 2.2*BALL_RADIUS, 4.5*height // 12), (4*WALL_WIDTH + 2.2*BALL_RADIUS, 4.25*height // 12)]
# center_poin = baricenter(poin)
# radius = shortest(center_poin, poin)
# # print("# OBSTACLE",end = " ")
# (create_ball(position=center_poin, r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY,add =True, type = "o"))
# # print("# OBSTACLE",end = " ")
# (create_ball(position=symmetry(center_poin), r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY, add =True, type = "o"))
# walls.append(create_triangle(poin, color = RED, elast = 2*ELASTICITY))
# walls.append(create_triangle(symmetry(poin), color = RED, elast = 2*ELASTICITY))


# poin = [(2*WALL_WIDTH + 2.2*BALL_RADIUS, 3.25*height // 12), (4*WALL_WIDTH + 2.2*BALL_RADIUS, 3.25*height // 12), (3*WALL_WIDTH + 2.2*BALL_RADIUS, 3*height // 12)]
# center_poin = baricenter(poin)
# radius = shortest(center_poin, poin)
# # print("# OBSTACLE",end = " ")
# (create_ball(position=center_poin, r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY, add =True, type = "o"))
# # print("# OBSTACLE",end = " ")
# (create_ball(position=symmetry(center_poin), r = radius, color=BLUE, static = True, elasticity = 2*ELASTICITY, add =True, type = "o"))
# walls.append(create_triangle(poin, color = RED, elast = 2*ELASTICITY))
# walls.append(create_triangle(symmetry(poin), color = RED, elast = 2*ELASTICITY))

# center_poin = (base_width//2, 3*height // 12) 
# # print("# OBSTACLE",end = " ")
# (create_ball(position=symmetry(center_poin), r = 2*BALL_RADIUS, color=BLUE, static = True, elasticity = 2*ELASTICITY, add =True, type = "o"))

# # walls
# starting = (3*WALL_WIDTH + 2.2*BALL_RADIUS, 4.25*height // 12)
# ending = (3*WALL_WIDTH + 2.2*BALL_RADIUS, 3.25*height // 12)
# walls.append(create_wall(start_pos= starting,end_pos=ending, static=True, color=WHITE, widt=2*WALL_WIDTH))
# walls.append(create_wall(start_pos=symmetry(starting),end_pos=symmetry(ending), static=True, color=WHITE, widt=2*WALL_WIDTH))

# starting = (2.5*WALL_WIDTH + 2.2*BALL_RADIUS, 5.25*height // 12)
# ending = (2.5*WALL_WIDTH + 2.2*BALL_RADIUS, 4.25*height // 12)
# walls.append(create_wall(start_pos= starting,end_pos=ending, static=True, color=WHITE, widt=WALL_WIDTH))
# walls.append(create_wall(start_pos=symmetry(starting),end_pos=symmetry(ending), static=True, color=WHITE, widt=WALL_WIDTH))

obstacle_color = rand_color()

walls.append(create_wall(start_pos = (base_width // 2, height // 3), end_pos = (base_width // 2, 2 * height // 3), static = True, color = obstacle_color, widt = WALL_WIDTH))

poin = (base_width // 3, height // 4)

(create_ball(position=poin, r = 2*BALL_RADIUS, color=obstacle_color, static = True, elasticity = 2*ELASTICITY, add =True, type = "o"))
(create_ball(position=symmetry(poin), r = 2*BALL_RADIUS, color=obstacle_color, static = True, elasticity = 2*ELASTICITY, add =True, type = "o"))

walls.append(create_wall(start_pos=(width - WALL_WIDTH // 2, 0), end_pos=(width - WALL_WIDTH // 2, height), color=WHITE)) # right_wall
walls.append(create_wall(start_pos=(WALL_WIDTH // 2, 0), end_pos=(WALL_WIDTH // 2, height), color=WHITE)) # left_wall
walls.append(create_wall(start_pos=(0, WALL_WIDTH // 2), end_pos=(width, WALL_WIDTH // 2), color=WHITE)) # ceil
walls.append(create_wall(start_pos=(base_width - WALL_WIDTH//2, breaking_point[1]), end_pos=(base_width - WALL_WIDTH//2, height), color=WHITE)) # dividing wall
# print("% tunnel floor")
walls.append(create_wall(start_pos=(base_width, height - WALL_WIDTH // 2), end_pos=(width, height - WALL_WIDTH // 2), color=WHITE)) # tunnel floor
walls.append(create_wall(start_pos=(width - 2.5*WALL_WIDTH, 0), end_pos=(width, 2.5*WALL_WIDTH), color=WHITE, elasticity=2*ELASTICITY)) # tunnel bumper
walls.append(create_triangle([(0,height), ((base_width // 2) - BALL_RADIUS,height), (0, height - 3*BALL_RADIUS)], color = WHITE, static = True))
walls.append(create_triangle([symmetry(((base_width // 2) - BALL_RADIUS,height)), symmetry((0,height)), symmetry((0, height - 3*BALL_RADIUS))], color = WHITE, static = True))
leng = 100
position_left_2 = (position_left[0] - np.cos(FLIPPER_ANGLE)*leng, position_left[1] + np.sin(FLIPPER_ANGLE)*leng)
walls.append(create_wall(start_pos=(position_left), end_pos=position_left_2, widt=WALL_WIDTH*0.65, color=WHITE))
position_right_2 = symmetry(position_left_2)
walls.append(create_wall(start_pos=(position_right), end_pos=position_right_2, widt=WALL_WIDTH*0.65, color=WHITE))


walls.append(create_wall(start_pos=(position_left_2[0], position_left_2[1] + 5), end_pos=(position_left_2[0], position_left_2[1] - 1.5*leng), widt=WALL_WIDTH*0.65, color=WHITE, elasticity=2*ELASTICITY))
walls.append(create_wall(start_pos=symmetry((position_left_2[0], position_left_2[1] + 5)), end_pos=symmetry((position_left_2[0], position_left_2[1] - 1.5*leng)), widt=WALL_WIDTH*0.65, color=WHITE, elasticity=2*ELASTICITY))

walls.append(create_wall(start_pos = (position_left_2[0] - 3, position_left_2[1] - 1.5*leng + 3), end_pos=(position_left_2[0] + 20, position_left_2[1] - 1.5*leng - 20), widt=WALL_WIDTH*0.65, color=WHITE, elasticity=2*ELASTICITY))
walls.append(create_wall(start_pos = symmetry((position_left_2[0] - 3, position_left_2[1] - 1.5*leng + 3)), end_pos=symmetry((position_left_2[0] + 20, position_left_2[1] - 1.5*leng - 20)), widt=WALL_WIDTH*0.65, color=WHITE, elasticity=2*ELASTICITY))

# all kinds of floor

blockade, blockade_shape = summon_blockade()

# create_ball(r = WALL_WIDTH//2, position = rand_pos(), static = True, mass = None, color = rand_color(), elasticity = ELASTICITY, add = True, type = None)

TARGET_HEIGHT = WALL_WIDTH*(3/2)
INITIAL_HEIGHT = height - TARGET_HEIGHT

create_ball(position=(width - WALL_WIDTH//2, INITIAL_HEIGHT), r = WALL_WIDTH // 4, color=rand_color(), static = True, elasticity = 0, add = True, type = "p", second_pos = (width - WALL_WIDTH//2, WALL_WIDTH*(3/2)))


def distance(point_a, point_b) :
    return np.sqrt( ( (point_a[0] + point_b[0])**2 ) + ( (point_a[1] + point_b[1])**2 ) )

def max_dist(points) :
    dist = 0
    for point_a in points :
        for point_b in points :
            dist = max(dist, distance(point_a, point_b))
    return dist

# flipper_points = generate_flipper_points(60, -np.pi / 6)
# base_points = generate_flipper_points(BALL_RADIUS)

right_flipper_body, right_flipper_shape = create_flipper(FLIPPER_LENGTH, FLIPPER_ANGLE, position_right, 'right', flipper_color)
left_flipper_body, left_flipper_shape = create_flipper(FLIPPER_LENGTH, FLIPPER_ANGLE, position_left, 'left', flipper_color)
base_right_flipper_body, base_right_flipper_shape = create_flipper(2*BALL_RADIUS, 0, (width - WALL_WIDTH - 2.2*BALL_RADIUS, height - 0.9*WALL_WIDTH), 'left', WHITE, "base_", add = False)


# END

# Ustawienie maski kolizji dla ścian i flipperów
for _,shape in walls:
    shape.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS() & ~0x2)  # Wyłączenie maski flipperów

obstacle_color = rand_color()


# static_1 = create_wall(start_pos=(base_width // 2, height // 2), end_pos=(base_width // 2, height // 3), color=obstacle_color, widt=WALL_WIDTH, friction=FRICTION, elasticity=1.5 * ELASTICITY, static=True)
# # print("# OBSTACLE",end = " ")
# static_2 = create_ball(r=2 * BALL_RADIUS, position=(base_width // 3, height // 4), static=True, mass=None, color=obstacle_color, elasticity=1.5 * ELASTICITY)
# # print("# OBSTACLE",end = " ")
# static_3 = create_ball(r=2 * BALL_RADIUS, position=(2 * base_width // 3, height // 4), static=True, mass=None, color=obstacle_color, elasticity=1.5 * ELASTICITY)
# Rejestracja funkcji obsługi zdarzeń kolizji
handler = space.add_collision_handler(1, 2)
handler.begin = increase_points

ball, ball_shape = spawn_ball()
# ball, ball_shape = None, None
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




max_energy = LAUNCH_ENERGY
energy_stored = 0
energy_direction = 1
time_passed = 0
max_time_passing = 1
shoot = False

inside = False

running = True
while running:
    
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
                # ball.apply_impulse_at_local_point((0, -5000))
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                right_flipper_pressed = False
            elif event.key == pygame.K_LEFT:
                left_flipper_pressed = False
            elif event.key == pygame.K_SPACE:
                base_flipper_pressed = False
                # base_right_flipper_body.angular_velocity = 100 * (base_flipper_target_angle - base_right_flipper_body.angle) * (energy_stored/max_energy) * np.pi
                # base_left_flipper_body.angular_velocity = 100 * (-base_flipper_target_angle - base_left_flipper_body.angle) * (energy_stored/max_energy) * np.pi
                # energy_stored = 0
                ball.apply_impulse_at_local_point((0, -1_000*energy_stored))
                # shoot = True
                print(shoot)

    # Wyczyszczenie ekranu
    screen.fill(BLACK)

    if base_flipper_pressed:
        print(energy_stored)
        val = avg_time / REACTION_TIME
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

    right_flipper_body.velocity = left_flipper_body.velocity = base_right_flipper_body.velocity = 0, 0

    right_flipper_target_angle = target_angle if right_flipper_pressed else 0
    left_flipper_target_angle = -target_angle if left_flipper_pressed else 0
    base_flipper_target_angle = -target_angle if shoot else 0

    if shoot:
        time_passed += avg_time
        if time_passed >= 0.5:
            shoot = False
            base_right_flipper_body, base_right_flipper_shape = replace_base_flippers()
            time_passed = 0

    right_flipper_body.angular_velocity = (right_flipper_target_angle - right_flipper_body.angle) * 30
    # right_flipper_body2.angular_velocity = (right_flipper_target_angle - right_flipper_body.angle) * 30
    left_flipper_body.angular_velocity = (left_flipper_target_angle - left_flipper_body.angle) * 30
    # left_flipper_body2.angular_velocity = (left_flipper_target_angle - left_flipper_body.angle) * 30
    # base_right_flipper_body.angular_velocity = (base_flipper_target_angle - base_right_flipper_body.angle) * (energy_stored)

    

    # Rysowanie obiektów
    for body in space.bodies:
        for shape in body.shapes:
            if isinstance(shape, pymunk.Circle):
                pos = body.position
                if not inside and body == ball:
                    if is_inside(pos, base_width):
                        blockade, blockade_shape = summon_blockade()
                        POINTS += round(energy_stored)
                        inside = True
                if not is_inside(pos) and body == ball:
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
    draw_text_inside(screen, f"FPS: {int(clock.get_fps())}", (0, 0), BLACK)
    draw_text_inside(screen, f"Balls left: {NO_BALLS - removed}", (0, height - 14), BLACK)
    draw_text_inside(screen, f"{POINTS}", (width // 2, 0), BLACK)
    # draw_text(screen, f"AVG_FPS: {int(avg_fps)}", (200,0), BLACK)

    # Odświeżenie ekranu
    pygame.display.flip()

# Wyjście z Pygame
pygame.quit()
print(LAUNCH_ENERGY, "# LAUNCH_ENERGY \n\n")
print(model_fps, "# MODEL_FPS \n\n")

print("avg_frametime", avg_time)
print("avg_fps", round(avg_fps))
print("POINTS: ", POINTS)



DATA["HEIGHT"] = height
DATA["ELASTICITY"] = ELASTICITY
DATA["BALL_RADIUS"] = BALL_RADIUS
DATA["NO_BALLS"] = NO_BALLS
DATA["WALL_WIDTH"] = WALL_WIDTH
DATA["FLIPPER_LENGTH"] = FLIPPER_LENGTH
DATA["LAUNCH_ENERGY"] = LAUNCH_ENERGY
DATA["MINIMAL_ENERGY"] =  MINIMAL_ENERGY
DATA["TUNNEL_SIZE"] = TUNNEL_SIZE
DATA["REACTION_TIME"] = REACTION_TIME
DATA["BASE_WIDTH"] = base_width
DATA["WIDTH"] = width
DATA["BREAKING_POINT"] = breaking_point
DATA["FLIPPER_ANGLE"] = FLIPPER_ANGLE
DATA["FLIPPER_X"] = FLIPPER_X
DATA["FLIPPER_Y"] = FLIPPER_Y
DATA["BALL_POSITION"] = BALL_POSITION
DATA["GRAVITY"] = space.gravity
DATA["TARGET_HEIGHT"] = TARGET_HEIGHT
DATA["TARGET_ANGLE"] = target_angle
DATA["TRIANGLES"] = TRIANGLES
DATA["WALLS"] = WALLS
DATA["BALLS"] = BALLS
DATA["RIGHT_FLIPPERS"] = RIGHT_FLIPPERS
DATA["LEFT_FLIPPERS"] = LEFT_FLIPPERS
DATA["OBSTACLES"] = OBSTACLES
DATA["POINTERS"] = POINTERS
DATA["MAIN_BALL"] = MAIN_BALLS[0]
DATA["BLOCKADE"] = BLOCKADES[0]

print(DATA)
print(len(DATA))


import json


with open(os.path.join(SCRIPT_PATH, "maps", "default.json"), 'w') as FILE:
    json.dump(DATA, FILE, indent=4)