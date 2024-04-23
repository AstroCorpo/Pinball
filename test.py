import pymunk
import pygame
import random
import numpy as np
from pygame.locals import *
import pymunk.pygame_util
from collections import deque


# Ustawienie wymiarów okna
# width, height = 2550, 1340
width, height = 600,1000

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
FLIPPER_ANGLE = -np.pi/6
FLIPPER_X = np.abs(FLIPPER_LENGTH*np.cos(FLIPPER_ANGLE))
FLIPPER_Y = np.abs(FLIPPER_LENGTH*np.sin(FLIPPER_ANGLE))

base_width = width
width = width + 3*WALL_WIDTH + 2*BALL_RADIUS

# Inicjalizacja Pygame
pygame.init()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pinball")

# Stworzenie obiektu Clock do kontrolowania FPS
clock = pygame.time.Clock()

space = pymunk.Space()      # Create a Space which contain the simulation
space.gravity = 0, 981     # Set its gravity



object_colors = {}

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

position_left = (base_width//2 - 3*BALL_RADIUS - FLIPPER_X,0.9*height - FLIPPER_Y)
position_right = base_width - position_left[0],position_left[1]

right_wall, right_wall_shape = create_wall(start_pos = (width - WALL_WIDTH//2, 0), end_pos = (width - WALL_WIDTH//2, height),color = WHITE)
left_wall, left_wall_shape = create_wall(start_pos = (WALL_WIDTH//2, 0), end_pos = (WALL_WIDTH//2, height),color = WHITE)
ceil, ceil_shape = create_wall(start_pos = (0, WALL_WIDTH//2), end_pos = (width, WALL_WIDTH//2),color = WHITE)


floor1, floor1_shape = create_wall(start_pos = (width - 3*WALL_WIDTH - BALL_RADIUS*2, height), end_pos = (width, height),color = WHITE)
floor1, floor1_shape = create_wall(start_pos = (0, 0.9*height), end_pos = ((5/12)*base_width, height),color = WHITE)
floor2, floor2_shape = create_wall(start_pos = (width - 3*WALL_WIDTH - BALL_RADIUS*2, 0.9*height), end_pos = ((7/12)*base_width, height),color = WHITE)

floor3, floor3_shape = create_wall(start_pos = (WALL_WIDTH + 3*BALL_RADIUS, 0.8*height), end_pos = position_left,color = WHITE)

floor4, floor4_shape = create_wall(start_pos = (base_width - (WALL_WIDTH + 3*BALL_RADIUS), 0.8*height), end_pos = position_right,color = WHITE)


divide, divide_shape = create_wall(start_pos = (width - 3*WALL_WIDTH - BALL_RADIUS*2, 4*WALL_WIDTH + BALL_RADIUS*2), end_pos = (width - 3*WALL_WIDTH - BALL_RADIUS*2, height),color = WHITE)
divide2, divide2_shape = create_wall(start_pos = (width, 5*WALL_WIDTH), end_pos = (width - 5*WALL_WIDTH, 0),color = WHITE)



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

flipper_points = generate_flipper_points(60, -np.pi/6)
base_points = generate_flipper_points(2*BALL_RADIUS)

flipper_color = rand_color()

right_flipper_body, right_flipper_shape = create_flipper(flipper_points, position_right, 'right', flipper_color)
left_flipper_body, left_flipper_shape = create_flipper(flipper_points, position_left, 'left', flipper_color)
base_flipper_body, base_flipper_shape = create_flipper(base_points, (width - 2*WALL_WIDTH, height - 2*WALL_WIDTH), 'right', flipper_color)

# Ustawienie maski kolizji dla flipperów
right_flipper_shape.filter = pymunk.ShapeFilter(categories=0x2)
left_flipper_shape.filter = pymunk.ShapeFilter(categories=0x2)
base_flipper_shape.filter = pymunk.ShapeFilter(categories=0x2)

# Ustawienie maski kolizji dla ścian
right_wall_shape.filter = pymunk.ShapeFilter(categories=0x1)
left_wall_shape.filter = pymunk.ShapeFilter(categories=0x1)
ceil_shape.filter = pymunk.ShapeFilter(categories=0x1)
floor1_shape.filter = pymunk.ShapeFilter(categories=0x1)
floor2_shape.filter = pymunk.ShapeFilter(categories=0x1)
floor3_shape.filter = pymunk.ShapeFilter(categories=0x1)
floor4_shape.filter = pymunk.ShapeFilter(categories=0x1)
divide_shape.filter = pymunk.ShapeFilter(categories=0x1)
divide2_shape.filter = pymunk.ShapeFilter(categories=0x1)

# Ustawienie maski kolizji dla ścian i flipperów
for shape in [right_wall_shape, left_wall_shape, ceil_shape, floor1_shape, floor2_shape, floor3_shape, floor4_shape, divide_shape, divide2_shape]:
    shape.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS() & ~0x2)  # Wyłączenie maski flipperów

    
    
# ball_1 = create_ball(r = 1.5*BALL_RADIUS, position = (width//2,height//2 - 4*BALL_RADIUS), static = False, mass = None, color = (random.randint(0,255),random.randint(0,255),random.randint(0,255)), elasticity = ELASTICITY)
# static_1 = create_wall(start_pos = (width//2,height//2), end_pos = (width//2,height//3), color = rand_color(), width = WALL_WIDTH, friction = FRICTION, elasticity = 1.5*ELASTICITY, static = True)
# static_2 = create_ball(r = 2*BALL_RADIUS, position = (width//3,height//4), static = True, mass = None, color = rand_color(), elasticity = 1.5*ELASTICITY)
# static_3 = create_ball(r = 2*BALL_RADIUS, position = (2*width//3,height//4), static = True, mass = None, color = rand_color(), elasticity = 1.5*ELASTICITY)

def spawn_ball() :
    ball,ball_shape = create_ball(r = BALL_RADIUS, position = (width - WALL_WIDTH//2 - BALL_RADIUS, height - 2*WALL_WIDTH - 2*BALL_RADIUS), static = False, mass = None, color = rand_color(), elasticity = ELASTICITY)

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

def inside(position) :
    x,y = position
    if x < 0 : return False
    if x > width : return False
    if y < 0 : return False
    if y > height : return False
    return True

def distance(point_a,point_b) :
    return np.sqrt((point_a[0] - point_b[0])**2 + (point_a[1] - point_b[1])**2)


spawn_ball()
removed = 0


model_fps = float('inf')
# model_fps = 60
    
i = 0
avg_time = 0
avg_fps = 0

right_flipper_pressed = False
left_flipper_pressed = False
base_flipper_pressed = False

target_angle = np.pi/3

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            pygame.image.save(screen, "flipper.png")
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                right_flipper_pressed = False
            elif event.key == pygame.K_LEFT:
                left_flipper_pressed = False
            elif event.key == pygame.K_SPACE:
                base_flipper_pressed = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                right_flipper_pressed = True
            elif event.key == pygame.K_LEFT:
                left_flipper_pressed = True
            elif event.key == pygame.K_SPACE:
                base_flipper_pressed = True
    
       
    # Wyczyszczenie ekranu
    screen.fill(BLACK)
    
    
    right_flipper_body.velocity = left_flipper_body.velocity = base_flipper_body.velocity = 0, 0

    right_flipper_target_angle = target_angle if right_flipper_pressed else 0
    left_flipper_target_angle = -target_angle if left_flipper_pressed else 0
    base_flipper_target_angle = target_angle if base_flipper_pressed else 0

    right_flipper_body.angular_velocity = (right_flipper_target_angle - right_flipper_body.angle) * 30
    left_flipper_body.angular_velocity = (left_flipper_target_angle - left_flipper_body.angle) * 30
    base_flipper_body.angular_velocity = (base_flipper_target_angle - base_flipper_body.angle) * 100
    
    
    
    # Ustawienie limitu FPS
    clock.tick(model_fps)
    fps = clock.get_fps()
    val = 1/model_fps
    if fps > 0 :
        val = 1/fps
    
    avg_time = ((avg_time*i) + val)/ (i+1)
    avg_fps = ((avg_fps*i) + fps)/ (i+1)
    
    # Symulacja   
    space.step(val)
    
    # Rysowanie obiektów
    for body in space.bodies:
        for shape in body.shapes:
            if isinstance(shape, pymunk.Circle):
                pos = body.position
                if not inside(pos) :
                    space.remove(body)
                    print("REMOVED")
                    removed += 1
                    spawn_ball()
                    if removed == NO_BALLS :
                        print("ALL GONE")
                        running = False
                draw_circle(body,shape)
            elif isinstance(shape, pymunk.Segment):
                draw_segment(body,shape)
            elif isinstance(shape, pymunk.Poly):
                draw_polygon(body, shape)
                    
    # Wyświetlanie licznika FPS
    draw_text(screen, f"FPS: {int(clock.get_fps())}", (0,0), BLACK)
    # draw_text(screen, f"AVG_FPS: {int(avg_fps)}", (200,0), BLACK)

    # Odświeżenie ekranu
    pygame.display.flip()


# Wyjście z Pygame
pygame.quit()

print("avg_frametime",avg_time)
print("avg_fps",round(avg_fps))