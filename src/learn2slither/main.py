import sys

import pygame
from tqdm import tqdm

from learn2slither.agent_snake import AgentSnake
from learn2slither.board import Board
from learn2slither.parsing import parse_command_line
from learn2slither.renderer import BoardRenderer, TerminalRenderer

MAX_STEPS = 2000


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
    game_over = False
    if step_by_step:
        loop_condition = range(sessions)
    else:
        loop_condition = tqdm(range(sessions))
    if boardRenderer or terminalRenderer:
        clock = pygame.time.Clock()
    for _ in loop_condition:
        if game_over:
            break

        board = Board(board_size, max_snake_length=best_length)
        dead = False
        state = board.get_state()
        step = 0
        while not dead:
            if dont_learn and step >= MAX_STEPS:
                break
            action = agentSnake.choose_action(state)
            if terminalRenderer:
                terminalRenderer.draw(board, action)
            if boardRenderer:
                boardRenderer.draw(board)
                if _event_loop(step_by_step):
                    game_over = True
                    break

            dead, reward = board.step(action)
            next_state = board.get_state()
            if not dont_learn:
                agentSnake.update_q_value(state, next_state, action, reward, dead)
            state = next_state

            if boardRenderer or terminalRenderer:
                clock.tick(fps)

            step += 1

        best_length = max(best_length, board.max_snake_length)
        if dead:
            best_duration = max(best_duration, board.max_duration)
        if not dont_learn:
            agentSnake.update_epsilon()
            agentSnake.update_learning_rate()

    print(f"Game over, max length = {best_length}, max duration = {best_duration}")

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
        boardRenderer = (
            BoardRenderer(args.board_size) if not args.board_display_off else None
        )
        terminalRenderer = TerminalRenderer() if not args.terminal_display_off else None

        try:
            _game_loop(
                agentSnake,
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
