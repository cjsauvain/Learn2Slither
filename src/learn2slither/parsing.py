import argparse
from pathlib import Path

MIN_BOARD_SIZE = 5
MAX_BOARD_SIZE = 25


def _positive_integer(value: str) -> int:
    i = int(value)

    if i <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer")

    return i


def _between_0_and_1(value: str) -> float:
    try:
        f = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a float")

    if not (0 <= f <= 1):
        raise argparse.ArgumentTypeError(f"{value} must be in range [0, 1]")

    return f


def _check_board_side(value: str) -> int:
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{value} is not an integer."
        ) from None

    if n < MIN_BOARD_SIZE or n > MAX_BOARD_SIZE:
        raise argparse.ArgumentTypeError(
            f"board side must be between {MIN_BOARD_SIZE} "
            f"and {MAX_BOARD_SIZE}, got {value}"
        )

    return n


def parse_command_line() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False
    )

    parser.add_argument(
        "--load",
        help="File containing the q-table to load",
    )
    parser.add_argument(
        "--save",
        help="File to save the q-table to",
    )
    parser.add_argument(
        "--sessions",
        help="Number of training sessions",
        type=_positive_integer,
        required=True,
        metavar="<N>",
    )
    parser.add_argument(
        "--fps",
        help="Frames per second for the display",
        type=_positive_integer,
        default=5,
        metavar="<N>",
    )
    parser.add_argument(
        "--board-size",
        help="Size of the board",
        type=_check_board_side,
        nargs=2,
        default=(10, 10),
        metavar=("<nrows>", "<ncols>"),
    )
    parser.add_argument(
        "--board-display-off",
        help="Turn off board display",
        action="store_true",
    )
    parser.add_argument(
        "--terminal-display-off",
        help="Turn off terminal display",
        action="store_true",
    )
    parser.add_argument(
        "--dont-learn",
        help="Turn off learning phase",
        action="store_true",
    )
    parser.add_argument(
        "--step-by-step",
        help="Enable step by step actions triggered by a user key",
        action="store_true",
    )
    parser.add_argument(
        "--learning-rate",
        help="Learning rate during training",
        type=_between_0_and_1,
        default=0.5,
    )
    parser.add_argument(
        "--gamma",
        help="Gamma used during training",
        type=_between_0_and_1,
        default=0.95,
    )

    args = parser.parse_args()

    # Parse q-table file extension
    SUPPORTED = {".json", ".pkl", ".pickle"}
    for name in ("load", "save"):
        value = getattr(args, name)
        if value and Path(value).suffix.lower() not in SUPPORTED:
            parser.error(
                f"--{name.replace('_', '-')}: "
                "expected a .json, .pkl or .pickle file"
            )

    # Validate the compatibility of
    # --step-by-step and --board-display-off options
    if args.step_by_step and args.board_display_off:
        parser.error("--step-by-step cannot be used with --board-display-off")

    return args
