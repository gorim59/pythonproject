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


class ObjectOnMap:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def move(self, dx, dy):
        self.x += dx
        self.y += dy


class VisibleOnMap(ObjectOnMap):
    def __init__(self, x, y, width, height, image):
        super().__init__(x, y, width, height)
        self.image = image

    def draw(self):
        if self.image:
            screen.blit(self.image, (int(self.x + (self.width / 2)), int(self.y + (self.height / 2))))


class Player(VisibleOnMap):
    def __init__(self, x, y, width, height, image, speed):
        super().__init__(x, y, width, height, image)
        self.speed = speed


class Enemy(VisibleOnMap):
    def __init__(self, x, y, width, height, image):
        super().__init__(x, y, width, height, image)


playerImg = None

try:
    playerImg = pygame.image.load('player.png')
except OSError:
    print("No player")
player = Player(screen_width / 2.0, screen_height / 2.0, 32, 32, playerImg, 0.5)

# Enemies
enemies = []


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
    screen.fill((0, 0, 0))
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

    player.draw()
    pygame.display.update()
    dt = clock.tick(fps)
    player.move(dx*dt, dy*dt)
