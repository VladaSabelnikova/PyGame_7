import logging
import sys
from pathlib import Path
from typing import List, Tuple

import pygame

FPS = 50


def terminate():
    pygame.quit()
    sys.exit()


def create_logger(
    name: str,
    format_line: str = '%(levelname)s — %(message)s',
    stream_out: sys = sys.stderr,
    level: str = 'INFO'
) -> logging:
    """
    Функция генерирует лог.
    """
    logger = logging.getLogger(name)
    formatter = logging.Formatter(format_line)
    handler = logging.StreamHandler(stream=stream_out)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def load_image(name: str, colorkey=None) -> pygame.image:
    """
    Вернёт surface на котором расположено изображение.
    """
    fullname = Path(f'src/{name}')
    if not fullname.is_file():
        logger.error(f"Файл с изображением '{fullname}' не найден")
    image = pygame.image.load(fullname)
    return image


def load_level(file_name: str) -> List[str]:
    file_name = Path(f'src/{file_name}')
    # читаем уровень, убирая символы перевода строки
    level_map = [line for line in file_name.read_text('utf-8').split('\n')]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(
    all_sprites: pygame.sprite.Group,
    tiles_group: pygame.sprite.Group,
    player_group: pygame.sprite.Group,
    level: List[str],
) -> Tuple:
    new_player, x_hero, y_hero = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile(tiles_group, all_sprites, 'empty', x, y)
            elif level[y][x] == '#':
                Tile(tiles_group, all_sprites, 'wall', x, y)
            elif level[y][x] == '@':
                Tile(tiles_group, all_sprites, 'empty', x, y)
                new_player = Player(player_group, all_sprites, x, y)
                x_hero, y_hero = x, y
    # вернет игрока, а также размер поля в клетках
    return new_player, x_hero, y_hero


def start_screen() -> None:
    screen = pygame.display.set_mode((300, 300))
    fon = pygame.transform.scale(load_image('fon.png'), (300, 300))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mario.png')

tile_width = tile_height = 50

MOVE = {
    1073741906: (0, -1),
    1073741905: (0, 1),
    1073741904: (-1, 0),
    1073741903: (1, 0)
}


class Tile(pygame.sprite.Sprite):
    def __init__(
        self,
        tiles_group: pygame.sprite.Group,
        all_sprites: pygame.sprite.Group,
        tile_type: str,
        pos_x: int,
        pos_y: int
    ) -> None:
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    player_image = tile_images

    def __init__(
        self,
        player_group: pygame.sprite.Group,
        all_sprites: pygame.sprite.Group,
        pos_x: int,
        pos_y: int
    ) -> None:
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


def move(level_x, level_y, coeff):
    map = load_level('map.txt')
    new_map = []
    for elem in map:
        line = [el for el in elem]
        new_map.append(line)
    if level_y + coeff[1] in range(12) and level_x + coeff[0] in range(12):
        for i, elem in enumerate(new_map):
            if new_map[level_y + coeff[1]][level_x + coeff[0]] != '#':
                new_map[i] = [el.replace('@', '.') for el in elem]
                new_map[level_y + coeff[1]][level_x + coeff[0]] = '@'
    return [''.join(line) for line in new_map]


def generated_group():
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    return all_sprites, tiles_group, player_group


def main():
    start_screen()
    pygame.init()
    pygame.display.set_caption('Перемещение героя')
    screen = pygame.display.set_mode((300, 300))
    # основной персонаж
    player = None
    # группы спрайтов
    all_sprites, tiles_group, player_group = generated_group()

    player, level_x, level_y = generate_level(
        all_sprites,
        tiles_group,
        player_group,
        load_level('map.txt'),
    )
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in MOVE:
                    all_sprites, tiles_group, player_group = generated_group()
                    player, level_x, level_y = generate_level(
                        all_sprites,
                        tiles_group,
                        player_group,
                        move(level_x, level_y, MOVE[event.key]),
                    )
        screen.fill((255, 255, 255))
        all_sprites.draw(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    logger = create_logger(__name__)
    main()
