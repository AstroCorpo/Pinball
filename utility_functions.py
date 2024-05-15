import numpy as np
from collections import deque
import random
import pymunk

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

def shortest_distance_between_shapes(shape1, shape2):
    # Initialize variables to store the minimum distance and the closest points
    min_distance = float('inf')
    closest_point_shape1 = None
    closest_point_shape2 = None

    # Get the position of the bodies associated with the shapes
    body1 = shape1.body
    body2 = shape2.body

    # Determine the type of each shape and compute the shortest distance accordingly
    if isinstance(shape1, pymunk.Circle) and isinstance(shape2, pymunk.Circle):
        # If both shapes are circles
        closest_point_shape1 = body1.position
        closest_point_shape2 = body2.position
        min_distance = body1.position.get_distance(body2.position)
    elif isinstance(shape1, pymunk.Circle) and isinstance(shape2, pymunk.Poly):
        # If shape1 is a circle and shape2 is a polygon
        min_distance = float('inf')
        for vertex in shape2.get_vertices():
            distance = body1.position.get_distance(vertex)
            if distance < min_distance:
                min_distance = distance
                closest_point_shape1 = body1.position
                closest_point_shape2 = vertex[0] + body2.position[0], vertex[1] + body2.position[1]
    elif isinstance(shape1, pymunk.Poly) and isinstance(shape2, pymunk.Circle):
        # If shape1 is a polygon and shape2 is a circle
        min_distance = float('inf')
        for vertex in shape1.get_vertices():
            distance = body2.position.get_distance(vertex)
            if distance < min_distance:
                min_distance = distance
                closest_point_shape1 = vertex[0] + body1.position[0], vertex[1] + body1.position[1]
                closest_point_shape2 = body2.position
    elif isinstance(shape1, pymunk.Poly) and isinstance(shape2, pymunk.Poly):
        # If both shapes are polygons
        min_distance = float('inf')
        for vertex1 in shape1.get_vertices():
            for vertex2 in shape2.get_vertices():
                distance = vertex1.get_distance(vertex2)
                if distance < min_distance:
                    min_distance = distance
                    closest_point_shape1 = vertex1[0] + body1.position[0], vertex1[1] + body1.position[1]
                    closest_point_shape2 = vertex2[0] + body2.position[0], vertex2[1] + body2.position[1]
    return closest_point_shape1, closest_point_shape2, min_distance