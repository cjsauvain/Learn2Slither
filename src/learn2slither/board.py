import random

from learn2slither.constants import DIRECTIONS, DOWN, LEFT, RIGHT, UP
from learn2slither.types import State

REWARDS = {
    "red_apple": -10,
    "green_apple": 10,
    "empty": -1,
    "wall_collision": -30,
    "self_collision": -30,
}


class Board:
    def __init__(self, board_size: tuple[int, int], max_snake_length: int):
        self.board_size: tuple[int, int] = board_size
        self.occupied: set[tuple[int, int]] = set()
        self.max_snake_length: int = max_snake_length
        self.max_duration: int = 0
        # Generate Snake, Green Apples, and Red Apple
        self._generate_snake()
        self.green_apples = [self.generate_apple() for _ in range(2)]
        self.red_apple = self.generate_apple()

    def generate_apple(self) -> tuple[int, int]:
        apple = self.random_position(exclude=self.occupied)
        self.occupied.add(apple)

        return apple

    def step(self, action: int) -> tuple[bool, int]:
        self.max_duration += 1
        dr, dc = DIRECTIONS[action]
        snake = self.snake
        old_tail = snake[-1]
        new_snake_head = (snake[0][0] + dr, snake[0][1] + dc)

        # Do step
        if len(snake) > 1:
            snake[1:] = snake[:-1]
        snake[0] = new_snake_head
        self.occupied.discard(old_tail)
        self.occupied.add(new_snake_head)

        board_size = self.board_size
        # Self Collision
        if new_snake_head in snake[1:]:
            return True, REWARDS["self_collision"]
        # Green Apple
        elif new_snake_head in self.green_apples:
            self._grow_snake(old_tail)
            green_apple = self.generate_apple()
            self.green_apples.append(green_apple)
            self.green_apples.remove(new_snake_head)
            return False, REWARDS["green_apple"]
        # Red Apple
        elif new_snake_head == self.red_apple:
            if len(snake) == 1:
                return True, REWARDS["red_apple"]
            self._shrink_snake()
            self.red_apple = self.generate_apple()
            return False, REWARDS["red_apple"]
        # Wall Collision
        elif snake[0][0] in (-1, board_size[0]) or snake[0][1] in (-1, board_size[1]):
            return True, REWARDS["wall_collision"]
        # Empty
        return False, REWARDS["empty"]

    def random_position(
        self,
        exclude: set[tuple[int, int]] | None = None,
        next_to_square: tuple[int, int] | None = None,
    ) -> tuple[int, int]:
        exclude = exclude or set()

        while True:
            if next_to_square is not None:
                pos = self._adjacent_position(next_to_square)
            else:
                pos = (
                    random.randint(0, self.board_size[0] - 1),
                    random.randint(0, self.board_size[1] - 1),
                )

            if pos not in exclude:
                break

        return pos

    def get_state(self) -> State:
        return (
            self._get_line_of_sight(UP),
            self._get_line_of_sight(DOWN),
            self._get_line_of_sight(LEFT),
            self._get_line_of_sight(RIGHT),
        )

    def _get_line_of_sight(self, direction: int) -> str:
        dr, dc = DIRECTIONS[direction]
        r, c = self.snake[0][0] + dr, self.snake[0][1] + dc
        max_r, max_c = self.board_size

        green_apples_pos = set(self.green_apples)
        red_apple_pos = self.red_apple
        snake_body = self.snake[1:]

        distance = 1
        while 0 <= r < max_r and 0 <= c < max_c:
            pos = (r, c)

            if pos in snake_body:
                return "S" + self._append_distance(distance)
            elif pos in green_apples_pos:
                return "G" + self._append_distance(distance)
            elif pos == red_apple_pos:
                return "R" + self._append_distance(distance)

            r += dr
            c += dc
            distance += 1

        return "W" + self._append_distance(distance)

    def _append_distance(self, distance: int) -> str:
        if distance == 1:
            return "0"
        elif 2 <= distance <= 5:
            return "1"
        elif distance > 5:
            return "2"

    def _generate_snake(self):
        # Head
        head = self.random_position()
        self.occupied.add(head)

        # Body
        first_body_cell = self.random_position(next_to_square=head)
        second_body_cell = self.random_position(
            exclude=self.occupied, next_to_square=first_body_cell
        )
        body = [first_body_cell, second_body_cell]
        self.occupied.add(body[0])
        self.occupied.add(body[1])

        # Build Snake
        self.snake = [head, *body]

    def _grow_snake(self, old_tail: tuple[int, int]):
        self.occupied.add(old_tail)
        self.snake.append(old_tail)
        self.max_snake_length = max(self.max_snake_length, len(self.snake))

    def _shrink_snake(self):
        tail = self.snake.pop()
        self.occupied.discard(tail)

    def _bounce_offset(self, next_to: int, axis_size: int) -> int:
        if next_to == 0:
            return 1
        elif next_to == axis_size - 1:
            return -1
        return random.choice([-1, 1])

    def _adjacent_position(self, square: tuple[int, int]) -> tuple[int, int]:
        axis = random.choice([0, 1])
        x, y = square

        if axis == 0:
            x += self._bounce_offset(x, self.board_size[0])
        else:
            y += self._bounce_offset(y, self.board_size[1])

        return (x, y)
