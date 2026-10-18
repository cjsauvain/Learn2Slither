import sys

import pygame
from tqdm import tqdm

from learn2slither.agent_snake import AgentSnake
from learn2slither.board import Board
from learn2slither.interpreter import Interpreter
from learn2slither.parsing import parse_command_line
from learn2slither.renderer import BoardRenderer, TerminalRenderer


def _check_event() -> bool | None:
    for event in pygame.event.get():
        if (
            event.type == pygame.QUIT
            or event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):
            return True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return False


def _wait_for_step() -> bool:
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True
            elif event.key == pygame.K_SPACE:
                return False


def _event_loop(step_by_step: bool) -> bool:
    if step_by_step:
        return _wait_for_step()
    return _check_event() is True


def _game_loop(
    agentSnake: AgentSnake,
    interpreter: Interpreter,
    terminalRenderer: TerminalRenderer | None,
    boardRenderer: BoardRenderer | None,
    sessions: int,
    board_size: tuple[int, int],
    step_by_step: bool,
    fps: int,
    dont_learn: bool,
):
    best_length = 3
    best_duration = 0
    exit_game = False
    loop_condition = range(sessions) if step_by_step else tqdm(range(sessions))
    if boardRenderer or terminalRenderer:
        clock = pygame.time.Clock()

    for _ in loop_condition:
        if exit_game:
            break

        board = Board(board_size, max_snake_length=best_length)
        dead = False
        state = interpreter.get_state(board)
        empty_steps = 0
        max_empty_steps = 5 * (board_size[0] + board_size[1])
        while not dead:
            if dont_learn and empty_steps >= max_empty_steps:
                break
            action = agentSnake.choose_action(state)
            if terminalRenderer:
                terminalRenderer.draw(board, action)
            if boardRenderer:
                boardRenderer.draw(board)
                if _event_loop(step_by_step):
                    exit_game = True
                    break

            dead, step_event = board.step(action)
            reward = interpreter.get_reward(step_event)
            next_state = interpreter.get_state(board)
            if not dont_learn:
                agentSnake.update_q_value(
                    state, next_state, action, reward, dead
                )
            state = next_state

            if dont_learn:
                empty_steps = empty_steps + 1 if step_event == "empty" else 0
            if boardRenderer or terminalRenderer:
                clock.tick(fps)

        best_length = max(best_length, board.max_snake_length)
        best_duration = max(best_duration, board.max_duration)
        if not dont_learn:
            agentSnake.update_epsilon()
            agentSnake.update_learning_rate()

    print(
        f"Game over, max length = {best_length}, "
        f"max duration = {best_duration}"
    )

    if boardRenderer:
        pygame.quit()


def main():
    try:
        args = parse_command_line()

        agentSnake = AgentSnake(
            args.load,
            args.save,
            args.learning_rate,
            args.gamma,
            args.sessions,
            args.dont_learn,
        )
        interpreter = Interpreter()
        boardRenderer = (
            BoardRenderer(args.board_size)
            if not args.board_display_off else None
        )
        terminalRenderer = (
            TerminalRenderer()
            if not args.terminal_display_off else None
        )

        try:
            _game_loop(
                agentSnake,
                interpreter,
                terminalRenderer,
                boardRenderer,
                args.sessions,
                args.board_size,
                args.step_by_step,
                args.fps,
                args.dont_learn,
            )
        finally:
            if agentSnake.save:
                agentSnake.save_q_table()

    except (OSError, ValueError, pygame.error, TypeError) as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
