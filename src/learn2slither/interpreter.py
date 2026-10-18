from learn2slither.board import Board
from learn2slither.constants import DIRECTIONS, DOWN, LEFT, RIGHT, UP
from learn2slither.types import State

REWARDS = {
    "red_apple": -10,
    "green_apple": 10,
    "empty": -1,
    "wall_collision": -30,
    "self_collision": -30,
}


class Interpreter:
    def get_reward(self, step_event: str) -> int:
        return REWARDS[step_event]

    def get_state(self, board: Board) -> State:
        return (
            self._get_line_of_sight(board, UP),
            self._get_line_of_sight(board, DOWN),
            self._get_line_of_sight(board, LEFT),
            self._get_line_of_sight(board, RIGHT),
        )

    def _get_line_of_sight(self, board: Board, direction: int) -> str:
        dr, dc = DIRECTIONS[direction]
        r, c = board.snake[0][0] + dr, board.snake[0][1] + dc
        max_r, max_c = board.board_size

        green_apples_pos = board.green_apples
        red_apple_pos = board.red_apple
        snake_body = board.snake[1:]

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
        return "1" if distance > 1 else "0"
