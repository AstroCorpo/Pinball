import pymunk
import pygame
import random
import numpy as np
from pygame.locals import *
from copy import deepcopy


width, height = 600,1000

ELASTICITY = 1.001
BALL_RADIUS = 10
NO_BALLS = 20
FRICTION = 0.5
# Definicja kolorów
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
FLIPPER_HOR = width//10
FLIPPER_VERT = height//20

# Inicjalizacja Pygame
pygame.init()
# Ustawienie wymiarów okna
# width, height = 2550, 1340
width, height = 600,1000

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pymunk Simulation")

# Stworzenie obiektu Clock do kontrolowania FPS
clock = pygame.time.Clock()

space = pymunk.Space()      # Create a Space which contain the simulation
space.gravity = 0, 981     # Set its gravity

WALL_WIDTH = 10


object_colors = {}

def create_wall(start_pos = (random.randint(WALL_WIDTH,width-WALL_WIDTH),random.randint(WALL_WIDTH,height-WALL_WIDTH)), end_pos = (random.randint(WALL_WIDTH,width-WALL_WIDTH),random.randint(WALL_WIDTH,height-WALL_WIDTH)), color = (random.randint(0,255),random.randint(0,255),random.randint(0,255)), width = WALL_WIDTH, friction = FRICTION, elasticity = ELASTICITY, static = True) :
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

right_wall, right_wall_shape = create_wall(start_pos = (width - WALL_WIDTH//2, 0), end_pos = (width - WALL_WIDTH//2, height),color = WHITE)
left_wall, left_wall_shape = create_wall(start_pos = (WALL_WIDTH//2, 0), end_pos = (WALL_WIDTH//2, height),color = WHITE)
ceil, ceil_shape = create_wall(start_pos = (0, WALL_WIDTH//2), end_pos = (width, WALL_WIDTH//2),color = WHITE)
floor, floor_shape = create_wall(start_pos = (0, height - WALL_WIDTH//2), end_pos = (width, height - WALL_WIDTH//2),color = WHITE)


def create_ball(r = BALL_RADIUS, position = (random.randint(WALL_WIDTH,width-WALL_WIDTH),random.randint(WALL_WIDTH,height-WALL_WIDTH)), static = False, mass = None, color = (random.randint(0,255),random.randint(0,255),random.randint(0,255)), elasticity = ELASTICITY) :
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
        ball_shape.mass = ball_shape.area
    ball_shape.elasticity = elasticity
    object_colors[ball_shape] = color
    space.add(ball, ball_shape)
    return ball,ball_shape
    

for i in range(NO_BALLS) :
    
    ball,ball_shape = create_ball(r = BALL_RADIUS, position = (random.randint(WALL_WIDTH,width-WALL_WIDTH),random.randint(WALL_WIDTH,height-WALL_WIDTH)), static = False, mass = None, color = (random.randint(0,255),random.randint(0,255),random.randint(0,255)), elasticity = ELASTICITY)


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

removed = 0


model_fps = float('inf')
# model_fps = 60
    
i = 0
avg_time = 0
avg_fps = 0


running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        # elif event.type == KEYDOWN:
        #     if event.key == K_RIGHT:  # Sprawdzenie, czy wciśnięto strzałkę w prawo
        #         print("RIGHT PRESESED")
       
       
    # Wyczyszczenie ekranu
    screen.fill(BLACK)
    
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
                radius = shape.radius
                if not inside(pos) :
                    space.remove(body)
                    print("REMOVED")
                    removed += 1
                    if removed == NO_BALLS :
                        print("ALL GONE")
                        running = False
                pygame.draw.circle(screen, object_colors[shape], (int(pos.x), int(pos.y)), int(radius), 0)
            elif isinstance(shape, pymunk.Segment):
                a = shape.a
                b = shape.b
                w = int(shape.radius)
                pygame.draw.line(screen, WHITE, a, b, 2*w + 1)
                
    # Wyświetlanie licznika FPS
    draw_text(screen, f"FPS: {int(clock.get_fps())}", (0,0), BLACK)
    # draw_text(screen, f"AVG_FPS: {int(avg_fps)}", (200,0), BLACK)

    # Odświeżenie ekranu
    pygame.display.flip()


# Wyjście z Pygame
pygame.quit()

print("avg_frametime",avg_time)
print("avg_fps",round(avg_fps))