# Learn2Slither

A snake that learns to play through reinforcement learning (Q-learning).

The snake only sees in the 4 directions from its head (`W` wall, `S` body, `G` green apple, `R` red apple, `0` empty).  
A Q-table maps what it sees to the value of each action (UP, DOWN, LEFT, RIGHT) and is updated after every move.

## Requirements

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/)

## Install

```bash
uv sync
```

## Usage

```bash
uv run learn2slither --sessions <N> [options]
```

| Option | Description | Default |
|---|---|---|
| `--sessions <N>` | Number of sessions (required) | |
| `--load <file>` | Load a model (`.json`, `.pkl`, `.pickle`) | |
| `--save <file>` | Save the model at the end | |
| `--dont-learn` | Evaluate a model without updating it | off |
| `--fps <N>` | Display speed | 5 |
| `--board-size <rows> <cols>` | Board size (5 to 25 per side) | 10 10 |
| `--board-display-off` | Hide the graphical board | off |
| `--terminal-display-off` | Hide the terminal output | off |
| `--step-by-step` | Advance one move per key press (`Space`) | off |
| `--learning-rate <0-1>` | Learning rate | 0.5 |
| `--gamma <0-1>` | Discount factor | 0.9 |

Controls in the board window: `Space` to step (with `--step-by-step`), `Esc` to quit.

`--step-by-step` needs the graphical board, so it cannot be combined with `--board-display-off`.

## Examples

Train 100 sessions without display and save the model:

```bash
uv run learn2slither --sessions 100 --board-display-off --terminal-display-off --save models/100sess.json
```

Watch a trained model play, without learning:

```bash
uv run learn2slither --sessions 10 --load models/100sess.json --dont-learn
```

Same, step by step:

```bash
uv run learn2slither --sessions 10 --load models/100sess.json --dont-learn --step-by-step
```

At the end, the best result over all sessions is printed:

```text
Game over, max length = 7, max duration = 32
```

## Models

Trained models are in `models/` (`1sess`, `10sess`, `100sess`, ...). A model is the Q-table stored as JSON or pickle.

## Project layout

```text
src/learn2slither/
  main.py         entry point and game loop
  parsing.py      command line arguments
  board.py        environment (snake, apples, rewards)
  agent_snake.py  state, Q-table, action choice, import/export
  renderer.py     pygame board and terminal display
  constants.py    sizes, colors, rewards, actions
```
