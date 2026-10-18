import json
import pickle
import random
from collections import defaultdict
from pathlib import Path

from learn2slither.types import State


class AgentSnake:
    def __init__(
        self,
        load: str,
        save: str,
        learning_rate: float,
        gamma: float,
        sessions: int,
        dont_learn: bool,
    ):
        self.load = load
        self.save = save
        self.q_table = self._load_q_table()
        self.learning_rate = learning_rate
        self.learning_rate_decay = learning_rate / sessions
        self.gamma = gamma
        self.epsilon = 1.0 if not dont_learn else 0.0
        self.epsilon_decay = 1.0 / sessions

    def update_q_value(
        self,
        state: State,
        next_state: State,
        action: int,
        reward: int,
        dead: bool
    ):
        max_future_q = 0.0 if dead else max(self.q_table[next_state])
        current_q = self.q_table[state][action]

        self.q_table[state][action] = current_q + self.learning_rate * (
            reward + self.gamma * max_future_q - current_q
        )

    def choose_action(
        self,
        state: State,
    ) -> int:
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, 3)

        q_values = self.q_table[state]
        best = max(q_values)
        return random.choice([a for a, q in enumerate(q_values) if q == best])

    def update_epsilon(self):
        self.epsilon = max(0.1, self.epsilon - self.epsilon_decay)

    def update_learning_rate(self):
        self.learning_rate = max(
            0.01,
            self.learning_rate - self.learning_rate_decay
        )

    def save_q_table(self):
        print(f"\nSave learning model into {self.save}")
        path = Path(self.save)
        path.parent.mkdir(parents=True, exist_ok=True)

        dumpers = {
            ".json": self._dump_json,
            ".pkl": self._dump_pickle,
            ".pickle": self._dump_pickle,
        }
        dumper = dumpers.get(path.suffix.lower())
        if dumper is None:
            raise ValueError(f"Unsupported file extension {path.suffix}")
        dumper(path)

    def _load_q_table(self) -> defaultdict:
        def default() -> list[float]:
            return [0.0, 0.0, 0.0, 0.0]

        if not self.load:
            return defaultdict(default)

        print(f"\nLoad trained model from {self.load}\n")
        path = Path(self.load)

        loaders = {
            ".json": self._load_json,
            ".pkl": self._load_pickle,
            ".pickle": self._load_pickle,
        }
        loader = loaders.get(path.suffix.lower())
        if loader is None:
            raise ValueError(f"Unsupported file extension {path.suffix}")

        return defaultdict(default, loader(path))

    def _load_json(
        self, path: Path
    ) -> dict[
        State,
        list[float],
    ]:
        try:
            with open(path, "r") as f:
                q_table = json.load(f)
        except ValueError as e:
            raise ValueError(f"{path} is not a valid JSON file: {e}") from e
        return {
            self._decode_state(key): value
            for key, value in q_table.items()
        }

    def _load_pickle(
        self, path: Path
    ) -> dict[
        State,
        list[float],
    ]:
        try:
            with open(path, "rb") as f:
                q_table = pickle.load(f)
        except (ValueError, EOFError, pickle.UnpicklingError) as e:
            raise ValueError(f"{path} is not a valid pickle file: {e}") from e
        return {
            self._decode_state(key): value
            for key, value in q_table.items()
        }

    def _dump_json(self, path: Path):
        data = {
            self._encode_state(state): value
            for state, value in self.q_table.items()
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    def _dump_pickle(self, path: Path):
        data = {
            self._encode_state(state): value
            for state, value in self.q_table.items()
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)

    def _encode_state(
        self,
        state: State,
    ) -> str:
        return "|".join(sight for sight in state)

    def _decode_state(self, key: str) -> State:
        key_split = key.split("|")
        if len(key_split) != 4:
            raise ValueError(f"Invalid state: {key}")
        if any(len(sight) != 2 for sight in key_split):
            raise ValueError(f"Invalid state: {key}")

        return tuple(key_split)
