import pymunk
import pygame
import random
import numpy as np
from pygame.locals import *


width, height = 600,1000

ELASTICITY = 0.95
BALL_RADIUS = 10
NO_BALLS = 20
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

wall_width = 10

# Floor
left_floor = pymunk.Body(body_type=pymunk.Body.STATIC)
left_floor_shape = pymunk.Segment(left_floor, (0, 0.9*height), (width // 2 - BALL_RADIUS*2 - FLIPPER_HOR, 0.99*height - FLIPPER_VERT), wall_width)
left_floor_shape.friction = 0.5
left_floor_shape.elasticity = ELASTICITY
space.add(left_floor, left_floor_shape)

right_floor = pymunk.Body(body_type=pymunk.Body.STATIC)
right_floor_shape = pymunk.Segment(right_floor, (width, 0.9*height), (width // 2 + BALL_RADIUS*2 + FLIPPER_VERT, 0.99*height - FLIPPER_VERT), wall_width)
right_floor_shape.friction = 0.5
right_floor_shape.elasticity = ELASTICITY
space.add(right_floor, right_floor_shape)



# Ceiling
ceil = pymunk.Body(body_type=pymunk.Body.STATIC)
ceil_shape = pymunk.Segment(ceil, (0, wall_width//2), (width, wall_width//2), wall_width)
ceil_shape.friction = 0.5
ceil_shape.elasticity = ELASTICITY
space.add(ceil, ceil_shape)


# Left Wall
left_wall = pymunk.Body(body_type=pymunk.Body.STATIC)
left_wall_shape = pymunk.Segment(left_wall, (wall_width//2, 0), (wall_width//2, height), wall_width)
left_wall_shape.friction = 0.5
left_wall_shape.elasticity = ELASTICITY
space.add(left_wall, left_wall_shape)

# Right Wall
right_wall = pymunk.Body(body_type=pymunk.Body.STATIC)
right_wall_shape = pymunk.Segment(right_wall, (width - wall_width//2, 0), (width - wall_width//2, height), wall_width)
right_wall_shape.friction = 0.5
right_wall_shape.elasticity = ELASTICITY
space.add(right_wall, right_wall_shape)


colors = {}

# ball = pymunk.Body()
# ball.position = 100, int(0.8*height)
# radius = BALL_RADIUS
# ball_shape = pymunk.Circle(ball, radius)
# ball_shape.mass = ball_shape.area
# colors[ball_shape] = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
# space.add(ball, ball_shape)

# ball2 = pymunk.Body()
# ball2.position = 105, 105
# radius = BALL_RADIUS
# ball2_shape = pymunk.Circle(ball2, radius)
# ball2_shape.mass = ball2_shape.area
# space.add(ball2, ball2_shape)



for i in range(NO_BALLS) :
    ball = pymunk.Body()
    ball.position = random.randint(10,width-10),random.randint(10,0.9*height-10)
    radius = BALL_RADIUS
    ball_shape = pymunk.Circle(ball, radius)
    ball_shape.mass = ball_shape.area
    colors[ball_shape] = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    space.add(ball, ball_shape)




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

right_rotating = 0
left_rotating = 0


running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_RIGHT:  # Sprawdzenie, czy wciśnięto strzałkę w prawo
                print("RIGHT PRESESED")
                right_up = True
       
       
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
            shape.elasticity = ELASTICITY
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
                pygame.draw.circle(screen, colors[shape], (int(pos.x), int(pos.y)), int(radius), 0)
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