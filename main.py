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
renderer.add_object(Sphere(0.4, Vector3(-0.6, 0.6, 1), (0, 0, 255)))
renderer.add_object(Sphere(0.2, Vector3(-0.6, -1.6, 1), (0, 0, 255)))
#renderer.add_object(Cube(Vector3(0.5, 0.5, 0.5), Vector3(-0.5, 0.5, -1), (255, 255, 255)))

controls = [
    False, False, # key A and D
    False, False  # key W and S
]

frame = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                controls[0] = True
            if event.key == pygame.K_d:
                controls[1] = True
            if event.key == pygame.K_w:
                controls[2] = True
            if event.key == pygame.K_s:
                controls[3] = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                controls[0] = False
            if event.key == pygame.K_d:
                controls[1] = False
            if event.key == pygame.K_w:
                controls[2] = False
            if event.key == pygame.K_s:
                controls[3] = False

    screen.fill("white")

    if controls[0]: player.rotation.y -= 5
    if controls[1]: player.rotation.y += 5

    forwards = player.get_forward(player.rotation.x, player.rotation.y)
    if controls[2]:
        player.position.x += forwards.x / 10
        player.position.y += forwards.y / 10
        player.position.z += forwards.z / 10
    if controls[3]:
        player.position.x -= forwards.x / 10
        player.position.y -= forwards.y / 10
        player.position.z -= forwards.z / 10

    renderer.objects[0].position.y = math.sin(frame / 10) / 5
    renderer.objects[1].position.y = math.cos(frame / 10) / 5
    renderer.objects[3].position.x = math.cos(frame / 10) / 2

    try:
        renderer.render()
    except Exception as e:
        print(e)
        
    pygame.display.flip()

    frame += 1
    clock.tick(60)

pygame.quit()