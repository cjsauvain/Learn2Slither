from abc import ABC, abstractmethod

import pygame

from learn2slither.board import Board
from learn2slither.constants import DOWN, LEFT, RIGHT, UP

SQUARE_SIZE = 40
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (100, 149, 237)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

ACTIONS = {UP: "UP", DOWN: "DOWN", LEFT: "LEFT", RIGHT: "RIGHT"}


class Renderer(ABC):
    @abstractmethod
    def draw(self, board: Board):
        pass


class TerminalRenderer(Renderer):
    def draw(self, board: Board, action: int | None):
        if action is not None:
            print("\n" + ACTIONS[action])

        nrows, ncols = board.board_size
        head_row, head_col = board.snake[0]

        # Build Grid Skeleton
        grid = [["W"] * (ncols + 2)]
        grid += [["W"] + ["0"] * ncols + ["W"] for _ in range(nrows)]
        grid += [["W"] * (ncols + 2)]

        # Head
        grid[head_row + 1][head_col + 1] = "H"
        # Body
        for row, col in board.snake[1:]:
            grid[row + 1][col + 1] = "S"
        # Green Apples
        for row, col in board.green_apples:
            grid[row + 1][col + 1] = "G"
        # Red Apple
        row, col = board.red_apple
        grid[row + 1][col + 1] = "R"

        # Draw
        for r, line in enumerate(grid):
            if r == head_row + 1:
                print("".join(line))
            else:
                print(" " * (head_col + 1) + line[head_col + 1])


class BoardRenderer(Renderer):
    def __init__(self, board_size: tuple[int, int]):
        self.win = self._create_window(board_size)

    def _create_window(self, board_size: tuple[int, int]) -> pygame.Surface:
        WIDTH = board_size[1] * SQUARE_SIZE
        HEIGHT = board_size[0] * SQUARE_SIZE

        pygame.init()
        pygame.display.set_caption("Agent Snake")
        win = pygame.display.set_mode((WIDTH, HEIGHT))

        return win

    def _draw_square(self, color: tuple[int, int, int], x: int, y: int):
        pygame.draw.rect(
            self.win,
            color,
            (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
        )

    def draw(self, board: Board):
        self.win.fill(WHITE)

        # Green Apples
        for green_apple in board.green_apples:
            self._draw_square(GREEN, green_apple[1], green_apple[0])

        # Red Apples
        self._draw_square(RED, board.red_apple[1], board.red_apple[0])

        # Snake
        self._draw_square(BLUE, board.snake[0][1], board.snake[0][0])
        for body_part in board.snake[1:]:
            self._draw_square(LIGHT_BLUE, body_part[1], body_part[0])

        # Horizontal Grid
        width = board.board_size[1] * SQUARE_SIZE
        for row in range(board.board_size[0]):
            pygame.draw.rect(self.win, BLACK, (0, row * SQUARE_SIZE, width, 1))

        # Vertical Grid
        height = board.board_size[0] * SQUARE_SIZE
        for col in range(board.board_size[1]):
            pygame.draw.rect(
                self.win,
                BLACK,
                (col * SQUARE_SIZE, 0, 1, height)
            )

        pygame.display.update()
