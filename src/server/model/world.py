from server.logger import get_logger

from server.model.snake import Snake, Snake, SnakeId
from server.model.snake_pit import SnakePit, SnakePitId
from typing import Tuple

_logger = get_logger(__name__)


SnakePitState = Tuple[Snake, SnakePit | None]


class World:
    def __init__(self):
        # bookeeping for easier querying of pits and snakes
        self.pits: dict[SnakePitId, SnakePit] = dict()
        self.snakes: dict[SnakeId, SnakePitState] = dict()

    def create_pit(self, pit_id: SnakePitId) -> None:
        new_pit = SnakePit(pit_id)
        self.pits[pit_id] = new_pit

    def destroy_pit(self, pit: SnakePit) -> None:
        if pit.id in self.pits and len(pit) == 0:
            del self.pits[pit.id]

    def get_pit(self, requested_pit_id: SnakePitId) -> SnakePit | None:
        return self.pits.get(requested_pit_id)

    def __str__(self):
        return (
            f"World(pits="
            + str([str(pit) for pit in self.pits.values()])
            + ", snakes="
            + str([f"{snake.id}: {str(pit)}" for snake, pit in self.snakes.values()])
            + ")"
        )

    def each_pit(self):
        return iter(self.pits.values())

    def __len__(self):
        return len(self.pits)

    def __contains__(self, pit_id: SnakePitId):
        return pit_id in self.pits
