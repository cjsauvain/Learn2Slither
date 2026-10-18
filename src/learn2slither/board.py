import random

from learn2slither.constants import DIRECTIONS


class Board:
    def __init__(self, board_size: tuple[int, int], max_snake_length: int):
        self.board_size: tuple[int, int] = board_size
        self.occupied: set[tuple[int, int]] = set()
        self.max_snake_length: int = max_snake_length
        self.max_duration: int = 0
        # Generate Snake, Green Apples, and Red Apple
        self._build_snake()
        self.green_apples = [self.generate_apple() for _ in range(2)]
        self.red_apple = self.generate_apple()

    def step(self, action: int) -> tuple[bool, str]:
        dr, dc = DIRECTIONS[action]
        snake = self.snake

        # Build New Snake
        new_snake_head = (snake[0][0] + dr, snake[0][1] + dc)
        old_tail = snake[-1]
        if len(snake) > 1:
            snake[1:] = snake[:-1]
        snake[0] = new_snake_head

        self.occupied.discard(old_tail)
        self.occupied.add(new_snake_head)
        self.max_duration += 1

        return self._update_snake(old_tail)

    def grow_snake(self, old_tail: tuple[int, int]):
        self.occupied.add(old_tail)
        self.snake.append(old_tail)
        self.max_snake_length = max(self.max_snake_length, len(self.snake))

    def shrink_snake(self):
        tail = self.snake.pop()
        self.occupied.discard(tail)

    def generate_apple(self) -> tuple[int, int]:
        apple = self._random_position(exclude=self.occupied)
        self.occupied.add(apple)

        return apple

    def _build_snake(self):
        # Head
        head = self._random_position()
        self.occupied.add(head)

        # Body
        first_body_cell = self._random_position(next_to_square=head)
        second_body_cell = self._random_position(
            exclude=self.occupied, next_to_square=first_body_cell
        )
        body = [first_body_cell, second_body_cell]
        self.occupied.add(body[0])
        self.occupied.add(body[1])

        # Build Snake
        self.snake = [head, *body]

    def _update_snake(self, old_tail: tuple[int, int]) -> tuple[bool, str]:
        snake = self.snake

        # Self Collision
        if snake[0] in snake[1:]:
            return True, "self_collision"
        # Green Apple
        elif snake[0] in self.green_apples:
            self.grow_snake(old_tail)
            self.green_apples.remove(snake[0])
            if len(self.occupied) >= self.board_size[0] * self.board_size[1]:
                return True, "green_apple"
            self.green_apples.append(self.generate_apple())
            return False, "green_apple"
        # Red Apple
        elif snake[0] == self.red_apple:
            if len(snake) == 1:
                return True, "red_apple"
            self.shrink_snake()
            self.red_apple = self.generate_apple()
            return False, "red_apple"
        # Wall Collision
        elif snake[0][0] in (-1, self.board_size[0]) or snake[0][1] in (
            -1,
            self.board_size[1],
        ):
            return True, "wall_collision"
        return False, "empty"

    def _random_position(
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

    def _adjacent_position(self, square: tuple[int, int]) -> tuple[int, int]:
        axis = random.choice([0, 1])
        x, y = square

        if axis == 0:
            x += self._bounce_offset(x, self.board_size[0])
        else:
            y += self._bounce_offset(y, self.board_size[1])

        return (x, y)

    def _bounce_offset(self, next_to: int, axis_size: int) -> int:
        if next_to == 0:
            return 1
        elif next_to == axis_size - 1:
            return -1
        return random.choice([-1, 1])
