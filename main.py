import math
import pygame

pygame.init()
screen_width = 1000
screen_height = 800
screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.set_caption("Game")
fps = 60
background = None
try:
    background = pygame.image.load('background.png')
except OSError:
    print("No background")


class Room:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def out_of(self, map_object):
        return (screen_width + map_object.width - self.width) / 2.0 > map_object.x or \
               (screen_width - map_object.width + self.width) / 2.0 < map_object.x or \
               (screen_height + map_object.height - self.height) / 2.0 > map_object.y or \
               (screen_height - map_object.height + self.height) / 2.0 < map_object.y

    def correct(self, map_object):
        if (screen_width + map_object.width - self.width) / 2.0 > map_object.x:
            map_object.move((screen_width + map_object.width - self.width) / 2.0 - map_object.x, 0)
        if (screen_width - map_object.width + self.width) / 2.0 < map_object.x:
            map_object.move((screen_width - map_object.width + self.width) / 2.0 - map_object.x, 0)
        if (screen_height + map_object.height - self.height) / 2.0 > map_object.y:
            map_object.move(0, (screen_height + map_object.height - self.height) / 2.0 - map_object.y)
        if (screen_height - map_object.height + self.height) / 2.0 < map_object.y:
            map_object.move(0, (screen_height - map_object.height + self.height) / 2.0 - map_object.y)


class ObjectOnMap:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def move(self, delta_x, delta_y):
        self.x += delta_x
        self.y += delta_y


class VisibleOnMap(ObjectOnMap):
    def __init__(self, x, y, width, height, image):
        super().__init__(x, y, width, height)
        self.image = image

    def draw(self):
        if self.image:
            screen.blit(self.image, (int(self.x - (self.width / 2)), int(self.y - (self.height / 2))))


class Player(VisibleOnMap):
    def __init__(self, x, y, width, height, image, speed):
        super().__init__(x, y, width, height, image)
        self.speed = speed


class Enemy(VisibleOnMap):
    def __init__(self, x, y, width, height, image):
        super().__init__(x, y, width, height, image)


room = Room(600, 600)

playerImg = None

try:
    playerImg = pygame.image.load('player.png')
except OSError:
    print("No player")
player = Player(screen_width / 2.0, screen_height / 2.0, 32, 32, playerImg, 0.5)

# Enemies
enemyImg = None

try:
    enemyImg = pygame.image.load('enemy.png')
except OSError:
    print("No enemy")
enemies = [Enemy(300, 300, 16, 16, enemyImg)]


def isCollision(A, B):
    if abs(A.x - B.x) < abs(A.width - B.width) and abs(A.y - B.y) < abs(A.height - B.height):
        return True
    else:
        return False


# Game Loop
running = True
left = False
right = False
up = False
down = False
clock = pygame.time.Clock()
while running:

    # RGB = Red, Green, Blue
    screen.fill((25, 25, 25))
    # Background Image
    if background:
        screen.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # if keystroke is pressed check whether its right or left
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                left = True
            if event.key == pygame.K_RIGHT:
                right = True
            if event.key == pygame.K_UP:
                up = True
            if event.key == pygame.K_DOWN:
                down = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left = False
            if event.key == pygame.K_RIGHT:
                right = False
            if event.key == pygame.K_UP:
                up = False
            if event.key == pygame.K_DOWN:
                down = False

    horizontal_move = left != right
    vertical_move = up != down
    dx = 0
    dy = 0
    if horizontal_move and vertical_move:
        if down:
            dy = player.speed/math.sqrt(2)
        else:
            dy = -player.speed/math.sqrt(2)
        if right:
            dx = player.speed/math.sqrt(2)
        else:
            dx = -player.speed/math.sqrt(2)
    elif horizontal_move:
        if right:
            dx = player.speed
        else:
            dx = -player.speed
    elif vertical_move:
        if down:
            dy = player.speed
        else:
            dy = -player.speed

    for e in enemies:
        e.draw()
    player.draw()
    pygame.display.update()
    dt = clock.tick(fps)
    player.move(dx*dt, dy*dt)
    for e in enemies:
        if isCollision(e, player):
            player.move(-dx * dt, -dy * dt)
    if room:
        if room.out_of(player):
            room.correct(player)
