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
    def __init__(self, x, y, width, height, image,dead_image):
        super().__init__(x, y, width, height)
        self.image = image
        self.dead_image = dead_image

    def draw(self):
        if self.image:
            screen.blit(self.image, (int(self.x - (self.width / 2)), int(self.y - (self.height / 2))))


class Player(VisibleOnMap):
    def __init__(self, x, y, width, height, image, speed):
        super().__init__(x, y, width, height, image)
        self.speed = speed
        self.health = 100
        self.damage = 10

    def give(self):
        pass

    def take(self):
        pass

    def have(self):
        pass


class Enemy(VisibleOnMap):
    def __init__(self, x, y, width, height, image):
        super().__init__(x, y, width, height, image)
        self.health = 25
        self.damage = 10
        self.alive = True

    def attack(self, player):
        self.health -= player.damage
        if self.health <= 0:
            self.kill()
        player.health -= self.damage

    def kill(self):
        alive = False

    def draw(self):
        if self.image:
            if self.alive:
                screen.blit(self.image, (int(self.x - (self.width / 2)), int(self.y - (self.height / 2))))
            else:
                screen.blit(self.dead_image, (int(self.x - (self.width / 2)), int(self.y - (self.height / 2))))


class Chest(VisibleOnMap):
    def __init__(self, x, y, width, height, image):
        super().__init__(x, y, width, height, image)
        self.open = False

    def interact(self):
        self.open_chest()

    def open_chest(self):
        if self.open:
            print("Closing chest")
            self.open = False
        else:
            print("Opening chest")
            self.open = True

    def close_chest(self):
        pass

    def give(self):
        pass

    def take(self):
        pass

    def have(self):
        pass


class Campfire(VisibleOnMap):
    def __init__(self, x, y, width, height, image, ):
        super().__init__(x, y, width, height, image)
        self.lit = False

    def interact(self):
        if self.lit is True:
            closest.image = unlit_campfireImage
            closest.lit = False
        elif self.lit is False:
            closest.image = lit_campfireImage
            closest.lit = True


def is_collision(A, B):
    if abs(A.x - B.x) < abs(A.width + B.width) / 2.0 and abs(A.y - B.y) < abs(A.height + B.height) / 2.0:
        return True
    else:
        return False


def is_nearby(A, B):
    if abs(A.x - B.x) < abs(A.width + B.width) and abs(A.y - B.y) < abs(A.height + B.height):
        return True
    else:
        return False


def correct_collision(A, B):
    if abs(A.x - B.x) < abs(A.width + B.width) / 2.0:
        # B.move()
        pass
    if abs(A.y - B.y) < abs(A.height + B.height) / 2.0:
        # B.move()
        pass


def closest_object(A):
    curr_min = float("Inf")
    closest_objet = None
    for close_object in A:
        distance = math.sqrt((player.x - close_object.x) ** 2 + (player.y - close_object.y) ** 2)
        if distance < curr_min:
            curr_min = distance
            closest_objet = close_object
    return closest_objet


room = Room(600, 600)

playerImg = None

try:
    playerImg = pygame.image.load('player.png')
except OSError:
    print("No player")
player = Player(screen_width / 2.0, screen_height / 2.0, 32, 32, playerImg, 0.1)

# Enemies
enemyImg = None

try:
    enemyImg = pygame.image.load('enemy.png')
except OSError:
    print("No enemy")
try:
    dead_imageImg = pygame.image.load('dead enemy.png')
except OSError:
    print("No dead enemy")
enemies = [Enemy(300, 300, 16, 16, enemyImg, dead_imageImg)]

chestImage = None
lit_campfireImage = None
unlit_campfireImage = None
try:
    chestImage = pygame.image.load('chest.png')
    unlit_campfireImage = pygame.image.load('unlit_campfire.png')
    lit_campfireImage = pygame.image.load('lit_campfire.png')
except OSError:
    print('No object image')
objects = [Chest(450, 300, 32, 20, chestImage), Campfire(500, 300, 32, 10, unlit_campfireImage)]


# Game Loop
running = True
left = False
right = False
up = False
down = False
interact = False
opened = []
game_font = pygame.font.SysFont("monospace", 15)
interact_label = game_font.render("press E to interact", True, (255, 255, 255))

clock = pygame.time.Clock()
while running:
    interact = False
    # RGB = Red, Green, Blue
    screen.fill((25, 25, 25))

    # Background Image
    if background:
        screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                left = True
            if event.key == pygame.K_RIGHT:
                right = True
            if event.key == pygame.K_UP:
                up = True
            if event.key == pygame.K_DOWN:
                down = True
            if event.key == pygame.K_e:
                interact = True

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
            dy = player.speed / math.sqrt(2)
        else:
            dy = -player.speed / math.sqrt(2)
        if right:
            dx = player.speed / math.sqrt(2)
        else:
            dx = -player.speed / math.sqrt(2)
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
    for o in objects:
        o.draw()
    player.draw()
    dt = clock.tick(fps)
    player.move(dx * dt, dy * dt)
    for e in enemies:
        if is_collision(e, player):
            # print(str(player.x)+" "+str(player.y)+" "+str(e.x)+" "+str(e.y))
            player.move(-dx * dt, -dy * dt)
    for o in objects:
        if is_collision(o, player):
            player.move(-dx * dt, -dy * dt)
    closest = closest_object(objects)
    if is_nearby(closest, player):
        screen.blit(interact_label, (closest.x + closest.width, closest.y - closest.height))
        if interact:
            closest.interact()

    if room:
        if room.out_of(player):
            room.correct(player)
    pygame.display.update()
