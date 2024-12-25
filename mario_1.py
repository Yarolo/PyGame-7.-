import pygame
import os
import sys


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


pygame.init()
screen_size = (500, 500)
screen = pygame.display.set_mode(screen_size)
FPS = 50

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Camera:

    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, x, y):
        self.dx = x
        self.dy = y


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        self.pos = (x, y)
        self.rect = self.image.get_rect().move(
            tile_width * self.pos[0] + 15, tile_height * self.pos[1] + 5)


player = None
running = True
clock = pygame.time.Clock()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


# "аварийное завершение" программы в виде отдельной функции
def terminate():
    pygame.quit()
    sys.exit


def start_screen():
    pygame.display.set_caption('Начальный экран')
    intro_text = ["Перемещение героя", "",
                  "Герой двигается",
                  "Карта на месте"]

    fon = pygame.transform.scale(load_image('fon.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = "."
    return new_player, x, y


def move(hero, movement):
    x, y = hero.pos
    if movement == "up":
        if y > 0 and level_map[y - 1][x] == ".":
            camera.update(0, 50)
            hero.pos = x, y - 1
    elif movement == "down":
        if y < max_y - 1 and level_map[y + 1][x] == ".":
            camera.update(0, -50)
            hero.pos = x, y + 1
    elif movement == "left":
        if x > 0 and level_map[y][x - 1] == ".":
            camera.update(50, 0)
            hero.pos = x - 1, y
    elif movement == "right":
        if x < max_x - 1 and level_map[y][x + 1] == ".":
            camera.update(-50, 0)
            hero.pos = x + 1, y


start_screen()
pygame.display.set_caption('Перемещение героя. Камера')
level_map = load_level("map.map")

hero, max_x, max_y = generate_level(level_map)
while running:
    camera = Camera()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move(hero, "up")
            elif event.key == pygame.K_DOWN:
                move(hero, "down")
            elif event.key == pygame.K_LEFT:
                move(hero, "left")
            elif event.key == pygame.K_RIGHT:
                move(hero, "right")
    screen.fill(pygame.Color("black"))
    for sprite in tiles_group:
        camera.apply(sprite)
    tiles_group.draw(screen)
    player_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
