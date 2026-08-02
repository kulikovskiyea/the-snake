"""
Реализация игры 'Змейка'.
Описание игры:
    Игрок управляет змейкой, которая движется по игровому полю.
    Цель игры - собирать яблоки, которые появляются на поле.
    Каждый раз, когда змейка съедает яблоко, она увеличивается в длину.
    Игра заканчивается, если змейка сталкивается с самой собой.
Модуль содержит классы для объектов игры (змейка и яблоко),
а также основную игровую логику.
Реализация с использованием библиотеки pygame.
"""

from collections.abc import Collection
from random import choice
from typing import Optional

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()

Position = tuple[int, int]
Color = tuple[int, int, int]

KEY_DIRECTION: dict[tuple[int, Position], Position] = {
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT
}


class GameObject:
    """Базовый класс для объектов на поле."""

    def __init__(
        self, position: Position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
        body_color: Color = BOARD_BACKGROUND_COLOR
    ) -> None:
        """Задача позиции и цвета объекта."""
        self.position = position
        self.body_color = body_color

    def _draw_cell(self, position: Optional[Position] = None,
                   body_color: Optional[Color] = None) -> None:
        """Отрисовка одной ячейки на экране."""
        position = position or self.position
        body_color = body_color or self.body_color
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self) -> None:
        """Отрисовка объекта для дочерних классов."""
        raise NotImplementedError(
            'Метод draw() должен быть реализован в дочернем классе.'
        )


class Apple(GameObject):
    """Яблоко на поле."""

    def __init__(
            self,
            occupied_positions: Collection[Position] = (),
            body_color: Color = APPLE_COLOR
    ) -> None:
        """Яблоко появляется в случайной позиции, не занятой змейкой."""
        super().__init__(body_color=body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(
            self,
            occupied_positions: Collection[Position]
    ) -> None:
        """Случаное перемещение яблока на экране в свободную клетку."""
        occupied_positions_set = set(occupied_positions)
        free_positions = [
            (column * GRID_SIZE, row * GRID_SIZE)
            for column in range(GRID_WIDTH)
            for row in range(GRID_HEIGHT)
            if (column * GRID_SIZE, row * GRID_SIZE)
            not in occupied_positions_set
        ]
        if not free_positions:
            raise ValueError('Нет свободных позиций для яблока.')
        self.position = (choice(free_positions))

    def draw(self) -> None:
        """Отрисовка яблока на экране."""
        self._draw_cell()


class Snake(GameObject):
    """Змейка на поле."""

    def __init__(self, body_color: Color = SNAKE_COLOR) -> None:
        """Появление змейки с движением вправо."""
        super().__init__(body_color=body_color)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction: Optional[Position] = None
        self.last: Optional[Position] = None

    def update_direction(self) -> None:
        """Обновление направления движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Перемещение змейки по направлению движения."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_head = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head)
        self.position = new_head

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self) -> None:
        """Отрисовать сегменты змейки и стереть удалённый хвост."""
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

        for position in self.positions[:1]:
            self._draw_cell(position)

        self._draw_cell(self.get_head_position())

    def get_head_position(self) -> Position:
        """Возвращает позицию начала змейки."""
        return self.positions[0]

    def reset(self) -> None:
        """Возврат змейки после столкновения."""
        self.length = 1
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [self.position]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None


# Функция обработки действий пользователя
def handle_keys(game_object: Snake) -> None:
    """Закрытие окна. Обработка нажатия."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            key_and_direction = (event.key, game_object.direction)
            game_object.next_direction = KEY_DIRECTION.get(
                key_and_direction, game_object.next_direction
            )


def main() -> None:
    """Запуск основной логики."""
    pygame.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head_position = snake.get_head_position()
        if head_position == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif head_position in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
