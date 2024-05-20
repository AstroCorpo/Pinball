import numpy as np
from collections import deque
import random
import pygame
import ctypes
from Xlib import display

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

def poly_field(points):
    n = len(points)
    field = 0
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        field += (x1 * y2 - x2 * y1)
    return abs(field) / 2


def rand_color() :
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))

def distance_points(point_a,point_b) :
    return np.sqrt((point_a[0] - point_b[0])**2 + (point_a[1] - point_b[1])**2)


def shortest_distance(shape1, shape2) :
    
    body1 = shape1.body
    body2 = shape2.body
    
    pos1 = body1.position
    pos2 = body2.position
    
    rad1 = shape1.radius
    rad2 = shape2.radius
    
    return distance_points(pos1, pos2) - rad1 - rad2

def distance_line_point(line, point_c) :
    point_a, point_b = line
    a_x, a_y = point_a
    b_x, b_y = point_b
    c_x, c_y = point_c
    
    t = -( ( ( (b_x - a_x) * (a_x - c_x) ) + ( (b_y - a_y) * (a_y - c_y) ) ) / ( ( (b_x - a_x)**2 ) + ( (b_y - a_y)**2 )) )
    
    point_d = (a_x + (b_x - a_x)*t, a_y + (b_y - a_y)*t)
    
    return distance_points(point_c, point_d)

def shortest_in_triangle(triangle, point) :
    point_a, point_b, point_c = triangle
    dist = distance_line_point((point_a, point_b), point)
    dist = min(dist, distance_line_point((point_b, point_c), point))
    dist = min(dist, distance_line_point((point_c, point_a), point))
    return dist

