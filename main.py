import pygame
import math

from objects.player import Player
from objects.sphere import Sphere
from objects.cube import Cube
from objects.vector3 import Vector3
from renderer import Renderer

pygame.init()
screen_size = (500, 500)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('SmallRayTracer')
clock = pygame.time.Clock()
running = True

player = Player()
renderer = Renderer(screen, screen_size, player)
renderer.add_object(Sphere(0.4, Vector3(0, 0, 2), (255, 0, 0)))
renderer.add_object(Sphere(0.4, Vector3(0.5, 0, 1), (0, 255, 0)))
#renderer.add_object(Cube(Vector3(1, 1, 1), Vector3(0, 0, 1), (255, 255, 255)))

frame = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill("white")

    #renderer.player.rotation.add(0, 1, 0)

    #renderer.objects[0].position.y = math.sin(frame / 10) / 5
    renderer.objects[1].position.y = math.sin(frame / 10) / 5

    renderer.render()
    pygame.display.flip()

    frame += 1
    clock.tick(60)

pygame.quit()