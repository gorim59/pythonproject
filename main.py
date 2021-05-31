import math
import random

import pygame
from enum import Enum

pygame.init()
screen_width = 1000
screen_height = 800
screen = pygame.display.set_mode([screen_width, screen_height])

inventory_width = 400
inventory_height = 300
inventory_x = screen_width // 2 - inventory_width // 2
inventory_y = screen_height // 2 - inventory_height // 2

pygame.display.set_caption("Game")
fps = 60


def load_image(name):
    try:
        return pygame.image.load(name)
    except OSError:
        print("No", name)
        return None


looting = False
playerImg = load_image('player.png')
enemyImg = load_image('enemy.png')
dead_imageImg = load_image('dead enemy.png')
door_image = load_image('door.png')
chestImage = load_image('chest.png')
unlit_campfire_image = load_image('unlit_campfire.png')
lit_campfire_image = load_image('lit_campfire.png')
used_shrine_image = load_image('used_shrine_image.png')
unused_shrine_image = load_image('unused_shrine_image.png')
background = load_image('background.png')


class Room:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.objects = []
        self.enemies = []

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
        self.collisional = True

    def move(self, delta_x, delta_y):
        self.x += delta_x
        self.y += delta_y


class Looting:
    def __init__(self, items, enemy):
        self.rect = pygame.Rect(
            inventory_x, inventory_y, inventory_width, inventory_height
        )
        self.items = items
        self.player = player
        self.enemy = enemy
        self.current_item = 0

    def update(self, key_event):
        if key_event.key == pygame.K_DOWN:
            if self.current_item + 1 == len(self.items):
                self.current_item = 0
            else:
                self.current_item += 1
        elif key_event.key == pygame.K_UP:
            if self.current_item == 0:
                self.current_item = len(self.items) - 1
            else:
                self.current_item += -1
        elif key_event.key == pygame.K_e and len(self.enemy.items) != 0:
            player.give(self.items[self.current_item])
            self.enemy.take(self.items[self.current_item])
        elif key_event.key == pygame.K_r and len(self.enemy.items) != 0:
            for i in self.items:
                player.give(i)
                self.enemy.take(i)

    def draw(self):
        pygame.draw.rect(screen, (172, 237, 182), self.rect)
        item_rect = self.rect.copy()
        item_rect.size = 150, 150
        item_rect.x = self.rect.x + 15
        item_rect.y = self.rect.y + 50
        pygame.draw.rect(screen, (255, 0, 0), item_rect)
        info = None
        if len(self.items) == 0:
            info = game_font.render("Empty", True, (255, 255, 255))
            screen.blit(info, (item_rect.x + 165, item_rect.y + 5))
        else:
            info = self.items[self.current_item].get_info()
            for i in range(len(info)):
                screen.blit(info[i], (item_rect.x + 165, item_rect.y + ((i + 1) * 12)))
        screen.blit(game_font.render("E: pick one, R: pick all, Esc: leave", True, (255, 255, 255)),
                    (self.rect.x + 15, self.rect.y + 280))


class Inventory:
    def __init__(self):
        self.rect = pygame.Rect(
            inventory_x, inventory_y, inventory_width, inventory_height
        )
        self.items = []
        self.gold = 0
        self.current_item = 0

    def update(self, key_event):
        if key_event.key == pygame.K_DOWN:
            if self.current_item + 1 == len(self.items):
                self.current_item = 0
            else:
                self.current_item += 1
        elif key_event.key == pygame.K_UP:
            if self.current_item == 0:
                self.current_item = len(self.items) - 1
            else:
                self.current_item += -1

    def draw(self):
        pygame.draw.rect(screen, (172, 237, 182), self.rect)
        item_rect = self.rect.copy()
        item_rect.size = 150, 150
        item_rect.x = self.rect.x + 15
        item_rect.y = self.rect.y + 50
        pygame.draw.rect(screen, (255, 0, 0), item_rect)
        gold_label = game_font.render("Gold: {}".format(self.gold), True, (255, 255, 255))
        screen.blit(gold_label, (self.rect.x + 15, self.rect.y + 5))
        info = None
        if len(self.items) == 0:
            info = game_font.render("Empty", True, (255, 255, 255))
            screen.blit(info, (item_rect.x + 165, item_rect.y + 5))
        else:
            info = self.items[self.current_item].get_info()
            for i in range(len(info)):
                screen.blit(info[i], (item_rect.x + 165, item_rect.y + ((i + 1) * 12)))


class VisibleOnMap(ObjectOnMap):
    def __init__(self, x, y, width, height, image):
        super().__init__(x, y, width, height)
        self.image = image

    def draw(self):
        if self.image:
            screen.blit(self.image, (int(self.x - (self.width / 2)), int(self.y - (self.height / 2))))


class Item:
    def __init__(self, item_id, value, name):
        self.id = item_id
        self.value = value
        self.name = name

    def __str__(self):
        return "{} (id:{} gold:{})".format(self.name, self.id, self.value)

    def __repr__(self):
        return str(self)

    def get_info(self):
        lines = []
        lines.append(game_font.render("{}".format(self.name), True, (255, 255, 255)))
        lines.append(game_font.render("Value: {}".format(self.value), True, (255, 255, 255)))
        return lines


class Player(VisibleOnMap):
    def __init__(self, x, y, width, height, image, speed, loc):
        super().__init__(x, y, width, height, image)
        self.speed = speed
        self.health = 100
        self.max_health = self.health  ###
        self.damage = 10
        self.items = [Item(1, 30, "sword"), Item(1, 30, "shield")]
        self.evasion = 0
        self.location = loc
        self.inventory = Inventory()
        self.inventory.items = self.items

    def give(self, item):
        self.items.append(item)
        self.inventory.items.append(item)

    def take(self, item):
        if self.have(item):
            self.items.remove(item)

    def have(self, item):
        return item in self.items

    def draw(self):
        super().draw()
        pygame.draw.rect(screen, (255, 0, 0),
                         (0 + 10, screen_height - 20, 100, 15))
        pygame.draw.rect(screen, (0, 128, 0),
                         (0 + 10, screen_height - 20, int(100 - (50 * (1 - (self.health / self.max_health)))), 15))


class Enemy(VisibleOnMap):
    def __init__(self, x, y, width, height, alive_image, dead_image):
        super().__init__(x, y, width, height, alive_image)
        self.dead_image = dead_image
        self.health = 25
        self.max_health = self.health
        self.damage = 10
        self.alive = True
        self.items = [Item(5, 30, "loot 3"), Item(5, 30, "loot 4")]
        self.loot = Looting(self.items, self)
        self.patrol_instructions = None
        self.speed = 0.0

    def interact(self, curr_player):
        if self.alive:
            self.get_attacked(curr_player)
        return not self.alive

    def get_attacked(self, curr_player):
        print("Fight player({} hp) against enemy({} hp).".format(curr_player.health, self.health))
        self.health -= curr_player.damage
        if self.health <= 0:
            self.kill()
            print(self.items)
            self.health = 0
        else:
            self.attack(curr_player)
        print("After fight player({} hp) against enemy({} hp).".format(curr_player.health, self.health))

    def attack(self, curr_player):
        if random.randrange(1, 100) <= curr_player.evasion:
            print("Hit evaded!")
        else:
            curr_player.health -= self.damage

    def kill(self):
        print("Dead.")
        self.image, self.dead_image = self.dead_image, self.image
        self.alive = False
        self.collisional = False

    def patrol(self, time):
        if self.patrol_instructions is not None:
            if time * self.speed:
                pass

    def draw(self):
        if self.image:
            if self.alive:
                if self.health < self.max_health:
                    pygame.draw.rect(screen, (255, 0, 0),
                                     (self.x - 25, self.y - self.height, 50, 5))
                    pygame.draw.rect(screen, (0, 128, 0),
                                     (self.x - 25, self.y - self.height,
                                      int(50 - (50 * (1 - (self.health / self.max_health)))), 5))
        super().draw()
        #     screen.blit(self.image, (int(self.x - (self.width / 2)), int(self.y - (self.height / 2))))
        # else:
        #     screen.blit(self.dead_image, (int(self.x - (self.width / 2)), int(self.y - (self.height / 2))))

    def give(self, item):
        self.items.append(item)

    def take(self, item):
        if self.have(item):
            self.items.remove(item)

    def have(self, item):
        return item in self.items


class Chest(VisibleOnMap):
    def __init__(self, x, y, width=32, height=20, image=chestImage):
        super().__init__(x, y, width, height, image)
        self.open = False
        self.opener = None
        self.items = [Item(3, 30, "loot 1"), Item(4, 30, "loot 2")]

    def interact(self, player):
        if self.open:
            while len(self.items) > 0:
                temp = self.items[0]
                self.take(temp)
                player.give(temp)
            self.close_chest()
        else:
            self.open_chest(player)

    def open_chest(self, player):
        if not self.open:
            print("Opening chest")
            print(self.items)
            self.open = True
            self.opener = player

    def close_chest(self):
        if self.open:
            print("Closing chest")
            self.open = False

    def give(self, item):
        self.items.append(item)

    def take(self, item):
        if self.have(item):
            self.items.remove(item)

    def have(self, item):
        return item in self.items


class Campfire(VisibleOnMap):
    def __init__(self, x, y, width=32, height=10, image=unlit_campfire_image):
        super().__init__(x, y, width, height, image)
        self.lit = False

    def interact(self, player):
        if self.lit is True:
            closest.image = unlit_campfire_image
            closest.lit = False
        elif self.lit is False:
            closest.image = lit_campfire_image
            closest.lit = True


class ShrineTypes(Enum):
    HEALING = 1
    HASTE = 2
    DAMAGE = 3
    EVASION = 4


class Shrine(VisibleOnMap):
    def __init__(self, x, y, type, width=32, height=32, image=unused_shrine_image):
        super().__init__(x, y, width, height, image)
        self.used = False
        self.type = type

    def bonus(self, receiving_player):
        if self.type == ShrineTypes.HASTE:
            receiving_player.speed += 0.02
            print("Movement speed increased")
        elif self.type == ShrineTypes.HEALTH:
            receiving_player.max_health += 20
            print("Maximum health increased")
        elif self.type == ShrineTypes.DAMAGE:
            receiving_player.damage += 2
            print("Damage increased")
        elif self.type == ShrineTypes.EVASION:
            receiving_player.damage += 2
            print("EVASION increased")

    def interact(self, player):
        if self.used is False:
            closest.image = used_shrine_image
            closest.used = True
            self.bonus(player)
        elif self.used is True:
            print("Shrine was drained out of power")


class Door(VisibleOnMap):
    def __init__(self, x, y, width=32, height=32, whereTo=None, image=None):
        super().__init__(x, y, width, height, image)
        self.direction = whereTo
        self.collisional = False

    def interact(self, opening_player):
        opening_player.x = screen_width / 2.0
        opening_player.y = screen_height / 2.0
        for objects in self.direction.objects:
            if isinstance(objects, Door):
                if objects.direction is opening_player.location:
                    opening_player.x = objects.x
                    opening_player.y = objects.y
        opening_player.location = self.direction


def X_collision(A, B):
    if abs(A.x - B.x) < (A.width + B.width) / 2.0:
        if B.x > A.x:
            return ((A.width + B.width) / 2.0) - (B.x - A.x)
        else:
            return (A.x - B.x) - ((A.width + B.width) / 2.0)
    else:
        return 0


def Y_collision(A, B):
    if abs(A.y - B.y) < (A.height + B.height) / 2.0:
        if B.y > A.y:
            return ((A.height + B.height) / 2.0) - (B.y - A.y)
        else:
            return (A.y - B.y) - ((A.height + B.height) / 2.0)
    else:
        return 0


def is_collision(A, B):
    if (not B.collisional) or (not A.collisional):
        return False
    if abs(X_collision(A, B)) > 0 and abs(Y_collision(A, B)) > 0:
        print(X_collision(A, B))
        print(Y_collision(A, B))
        return True
    else:
        return False


def correct_collision(A, B):
    x_dif = X_collision(A, B)
    y_dif = Y_collision(A, B)
    print(X_collision(A, B))
    print(Y_collision(A, B))
    print("from ({}, {}),({}, {})".format(A.x, A.y, B.x, B.y))
    if abs(x_dif) > 0 and abs(y_dif) > 0:
        if abs(x_dif) < abs(y_dif):
            print("X in both")
            B.move(x_dif, 0)
        else:
            print("Y in both")
            B.move(0, y_dif)
    print("to   ({}, {}),({}, {})".format(A.x, A.y, B.x, B.y))


def is_nearby(A, B):
    if abs(A.x - B.x) < abs(A.width + B.width) and abs(A.y - B.y) < abs(A.height + B.height):
        return True
    else:
        return False


def closest_object(A):
    curr_min = float("Inf")
    closest_objet = None
    for close_object in A:
        distance = math.sqrt((player.x - close_object.x) ** 2 + (player.y - close_object.y) ** 2)
        if distance < curr_min:
            curr_min = distance
            closest_objet = close_object
    return closest_objet


room1 = Room(600, 600)
room2 = Room(600, 600)

player = Player(screen_width / 2.0, screen_height / 2.0, 32, 32, playerImg, 0.1, room1)

room1.enemies = [Enemy(300, 300, 16, 16, enemyImg, dead_imageImg)]

room1.objects = [Chest(450, 300, 32, 20, chestImage),
                 Campfire(500, 300, 32, 10, unlit_campfire_image),
                 Shrine(x=600, y=300, type=ShrineTypes.HASTE, width=32, height=32, image=unused_shrine_image),
                 Door((screen_width + 32 - room1.width) / 2.0, screen_height / 2.0, 32, 32, room2, door_image)]

room2.objects = [Door((screen_width - 32 + room2.width) / 2.0, screen_height / 2.0, 32, 32, room1, door_image)]
moving_enemy = Enemy(300, 300, 16, 16, enemyImg, dead_imageImg)
moving_enemy.patrol_instructions = [(0, 0), (0, 0)]
moving_enemy.speed = 0.05


# try:
#     playerImg = pygame.image.load('player.png')
# except OSError:
#     print("No player")

# Enemies
# enemyImg = None
# dead_imageImg = None
#
# try:
#     enemyImg = pygame.image.load('enemy.png')
# except OSError:
#     print("No enemy")
# try:
#     dead_imageImg = pygame.image.load('dead enemy.png')
# except OSError:
#     print("No dead enemy")

# chestImage = None
# lit_campfire_image = None
# unlit_campfire_image = None
# used_shrine_image = None
# unused_shrine_image = None
# door_image = None
# try:
#     door_image = pygame.image.load('door.png')
#     chestImage = pygame.image.load('chest.png')
#     unlit_campfire_image = pygame.image.load('unlit_campfire.png')
#     lit_campfire_image = pygame.image.load('lit_campfire.png')
#     used_shrine_image = pygame.image.load('used_shrine_image.png')
#     unused_shrine_image = pygame.image.load('unused_shrine_image.png')
# except OSError:
#     print('No object image')


def out_of(self, map_object):
    return (screen_width + map_object.width - self.width) / 2.0 > map_object.x or \
           (screen_width - map_object.width + self.width) / 2.0 < map_object.x or \
           (screen_height + map_object.height - self.height) / 2.0 > map_object.y or \
           (screen_height - map_object.height + self.height) / 2.0 < map_object.y


# Game Loop
running = True
left = False
right = False
up = False
down = False
interact_E = False
interact_R = False
inventory = False
loot_window = None
game_font = pygame.font.SysFont("monospace", 15)
interact_label = game_font.render("press E to interact", True, (255, 255, 255))
attack_label = game_font.render("press E to atack", True, (255, 255, 255))

clock = pygame.time.Clock()
while running:
    interact_E = False
    interact_R = False
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
                if inventory:
                    player.inventory.update(event)
                elif looting:
                    loot_window.update(event)
                else:
                    up = True
            if event.key == pygame.K_DOWN:
                if inventory:
                    player.inventory.update(event)
                elif looting:
                    loot_window.update(event)
                else:
                    down = True
            if event.key == pygame.K_e:
                interact_E = True
                if looting:
                    loot_window.update(event)
            if event.key == pygame.K_r:
                interact_R = True
                if looting:
                    loot_window.update(event)
            if event.key == pygame.K_i:
                if inventory is False:
                    inventory = True
                else:
                    inventory = False
            if event.key == pygame.K_ESCAPE:
                if inventory:
                    inventory = False
                if looting:
                    looting = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left = False
            if event.key == pygame.K_RIGHT:
                right = False
            if event.key == pygame.K_UP:
                up = False
            if event.key == pygame.K_DOWN:
                down = False

    if inventory or looting:
        down = False
        up = False
        left = False
        right = False

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

    for e in player.location.enemies:
        e.draw()
    for o in player.location.objects:
        o.draw()
    player.draw()
    if inventory:
        player.inventory.draw()
    if looting:
        loot_window.draw()
    # moving player
    dt = clock.tick(fps)
    player.move(dx * dt, dy * dt)
    for e in player.location.enemies:
        if is_collision(e, player):
            correct_collision(e, player)
    for o in player.location.objects:
        if is_collision(o, player):
            correct_collision(o, player)
    for o in player.location.objects:
        if isinstance(o, Chest):
            if o.open:
                if not is_nearby(o, player):
                    o.close_chest()
    # interacting
    closest = closest_object(player.location.objects + player.location.enemies)
    if is_nearby(closest, player):
        if isinstance(closest, Enemy):
            loot_window = closest.loot
            if closest.alive:
                screen.blit(attack_label, (closest.x + closest.width, closest.y - closest.height))
            else:
                screen.blit(interact_label, (closest.x + closest.width, closest.y - closest.height))
        elif closest:
            screen.blit(interact_label, (closest.x + closest.width, closest.y - closest.height))
        if interact_E:
            looting = closest.interact(player) or False

    if inventory:
        print(player.items)
    if player.location:
        if player.location.out_of(player):
            player.location.correct(player)
    pygame.display.update()
