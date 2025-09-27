import pygame
import numpy as np
import time

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from concurrent.futures import ProcessPoolExecutor, as_completed

from objects.vector3 import Vector3

class Renderer:
    def __init__(self, screen, screen_size, player):
        self.screen = screen
        self.screen_size = screen_size
        self.player = player

        self.objects = []
        self.light_position = Vector3(0, 10, 2)

        self.resolution = 100
        self.ray_resolution = 5
        self.ray_distance = 5
        self.cell_size = round(self.screen_size[0] / self.resolution)
    
    def add_object(self, object_adding):
        self.objects.append(object_adding)

    def render(self):
        render_time_start = time.time()

        with ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(
                    self.render_pixel, 
                    y, self.player, self.light_position, self.resolution, 
                    self.ray_distance, self.ray_resolution, self.objects
                    )
                for y in range(self.resolution)
            ]

            for future in as_completed(futures):
                row_colors, y = future.result()
                for x, color in enumerate(row_colors):
                    pygame.draw.rect(
                        self.screen,
                        color,
                        (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                    )

        print(f"finished render in {(time.time() - render_time_start) * 1000}ms")

    @staticmethod
    def render_pixel(y, player, light_position, resolution, ray_distance, ray_resolution, objects):
        results = []
        for x in range(resolution):
            forwards = player.get_forward(
                (y - resolution / 2) + player.rotation.x,
                (x - resolution / 2) + player.rotation.y
            )

            color, position, position_object = trace_ray(
                player.position.x,
                player.position.y,
                player.position.z,
                forwards.x, forwards.y, forwards.z, # direction
                ray_distance,
                ray_resolution,
                objects
            )

            light = 0.5
            if position != [0, 0, 0] and position_object != [0, 0, 0]:
                light = trace_ray_to(
                    position[0],
                    position[1],
                    position[2],
                    light_position.x,
                    -light_position.y,
                    light_position.z,
                    100,
                    position_object,
                    objects
                )

            results.append((int(color[0] * (1 - light)), int(color[1] * (1 - light)), int(color[2] * (1 - light))))
        return (results, y)

def distance(x1, x2, y1, y2, z1, z2):
    dx = x1 - x2
    dy = y1 - y2
    dz = z1 - z2
    return (dx*dx + dy*dy + dz*dz) ** 0.5

def distance_inaccurate(x1, x2, y1, y2, z1, z2):
    dx = x1 - x2
    dy = y1 - y2
    dz = z1 - z2
    return dx*dx + dy*dy + dz*dz

def trace_ray_to(x, y, z, xl, yl, zl, ray_resolution, position_object, objects):
    difference_x = xl - x
    difference_y = yl - y
    difference_z = zl - z

    for i in range(ray_resolution):
        increment_x = (difference_x / ray_resolution) * (i + 1)
        increment_y = (difference_y / ray_resolution) * (i + 1)
        increment_z = (difference_z / ray_resolution) * (i + 1)
        position = [
            x + increment_x, 
            y + increment_y, 
            z + increment_z
        ]

        for object_checking in objects:
            object_position = object_checking.position
            object_type = object_checking.object_type
            if object_type == 1:
                object_radius = object_checking.radius
                if distance(
                    object_position.x, position[0],
                    object_position.y, position[1],
                    object_position.z, position[2]
                    ) <= object_radius:
                    return 1

    direction_to_light = np.array([xl - x, yl - y, zl - z])
    direction_to_object = np.array([
        position_object[0] - x,
        position_object[1] - y,
        position_object[2] - z
    ])
    N = direction_to_object / np.linalg.norm(direction_to_object)
    L = direction_to_light / np.linalg.norm(direction_to_light)
    intensity = max(0, np.dot(N, L)) * 2
    return min(1, intensity)

def check_ray_intersects_sphere(ray_distance, ray_resolution, i, x, y, z, rx, ry, rz, object_radius, object_position, j, n, back_tracking):
    increment = (ray_distance / ray_resolution) * (i + j)
    position = [
        x + rx * increment, 
        y + ry * increment, 
        z + rz * increment
    ]
    
    if n >= 255:
        print(j)
        return position

    if distance(
        object_position.x, position[0],
        object_position.y, position[1],
        object_position.z, position[2]
        ) <= object_radius:
        if not back_tracking:
            return check_ray_intersects_sphere(
                    ray_distance, ray_resolution, i, x, y, z, rx, ry, rz, object_radius, object_position, j - 0.005, n + 1, False
                )
        else:
            return position
    return check_ray_intersects_sphere(
                ray_distance, ray_resolution, i, x, y, z, rx, ry, rz, object_radius, object_position, j + 0.001, n + 1, True
            )

def check_ray_intersects_cube(ray_distance, ray_resolution, i, x, y, z, rx, ry, rz, object_size, object_position, j, n, back_tracking):
    increment = (ray_distance / ray_resolution) * (i + j)
    position = [
        x + rx * increment, 
        y + ry * increment, 
        z + rz * increment
    ]
    
    if n >= 255:
        print(j)
        return position

    if position[0] >= object_position.x - object_size.x / 2 and position[0] <= object_position.x + object_size.x / 2 and \
        position[1] >= object_position.y - object_size.y / 2 and position[1] <= object_position.y + object_size.y / 2 and \
        position[2] >= object_position.z - object_size.z / 2 and position[2] <= object_position.z + object_size.z / 2:
        if not back_tracking:
            return self.check_ray_intersects_cube(
                            ray_distance, ray_resolution, i, x, y, z, rx, ry, rz, object_size, object_position, j - 0.005, n + 1, False
                        )
        else:
            return position

    return self.check_ray_intersects_cube(
                        ray_distance, ray_resolution, i, x, y, z, rx, ry, rz, object_size, object_position, j + 0.001, n + 1, True
                    )

def trace_ray(x, y, z, rx, ry, rz, ray_distance, ray_resolution, objects):
    for i in range(ray_resolution):
        increment = (ray_distance / ray_resolution) * (i + 1)
        position = [
            x + rx * increment, 
            y + ry * increment, 
            z + rz * increment
        ]

        closest_object = [False, float('inf')]
        for object_checking in objects:
            object_position = object_checking.position
            object_type = object_checking.object_type
            if object_type == 1:
                object_radius = object_checking.radius
                distance_checked = distance_inaccurate(
                    object_position.x, position[0],
                    object_position.y, position[1],
                    object_position.z, position[2])
                if distance_checked <= object_radius*object_radius and distance_checked < closest_object[1]:
                    closest_object = [object_checking, distance_checked]
            elif object_type == 2:
                object_size = object_checking.size
                distance_checked = distance_inaccurate(
                    object_position.x, position[0],
                    object_position.y, position[1],
                    object_position.z, position[2])
                if position[0] >= object_position.x - object_size.x / 2 and position[0] <= object_position.x + object_size.x / 2 and \
                    position[1] >= object_position.y - object_size.y / 2 and position[1] <= object_position.y + object_size.y / 2 and \
                    position[2] >= object_position.z - object_size.z / 2 and position[2] <= object_position.z + object_size.z / 2:
                    if distance_checked < closest_object[1]:
                        closest_object = [object_checking, distance_checked]
        
        if closest_object[0] == False:
            continue

        object_checking = closest_object[0]
        object_position = object_checking.position
        object_type = object_checking.object_type
        if object_type == 1:
            object_radius = object_checking.radius
            if closest_object[1] <= object_radius*object_radius:
                    position_new = check_ray_intersects_sphere(
                        ray_distance, ray_resolution, i, x, y, z, rx, ry, rz, object_radius, object_position, 1, 0, False
                    )
                    return object_checking.color, position_new, [object_position.x, object_position.y, object_position.z]
        elif object_type == 2:
            object_size = object_checking.size
            position_new = check_ray_intersects_cube(
                ray_distance, ray_resolution, i, x, y, z, rx, ry, rz, object_size, object_position, 1, 0, False
            )
            return object_checking.color, position, [object_position.x, object_position.y, object_position.z]
    
    return (255, 255, 255), [0, 0, 0], [0, 0, 0]