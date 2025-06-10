import uuid
from server.logger import get_logger

from server.model.snake import Snake, SnakeId
from server.model.snake_pit import SnakePit, SnakePitId

_logger = get_logger(__name__)


class World:
    def __init__(self):
        self.pits: dict[SnakePitId, SnakePit] = dict()
        self.memberships: dict[SnakeId, SnakePit] = dict()

    def add_pit(self, pit: SnakePit) -> None:
        self.pits[pit.id] = pit

    def remove_pit(self, pit: SnakePit) -> None:
        if pit.id in self.pits:
            del self.pits[pit.id]

    def add_member_to_pit(self, pit_id: SnakePitId, member: Snake) -> None:
        pit = self.get_pit(pit_id)

        _logger.debug(f"Adding member to pit: {pit}")

        if pit is None:
            raise ValueError(f"SnakePit with id {pit_id} not found")

        pit.add_member(member)
        self.memberships[member.display_name] = pit

    def remove_member_from_pit(self, member_id: SnakeId) -> None:
        if not member_id in self.memberships:
            return None

        pit = self.memberships[member_id]
        pit.remove_member(member_id)

        del self.memberships[member_id]

    def get_pit(self, requested_pit_id: SnakePitId) -> SnakePit | None:
        return self.pits.get(requested_pit_id)

    def get_pit_by_pit_member(self, member_id: SnakeId) -> SnakePit | None:
        return self.memberships.get(member_id)

    def __str__(self):
        return (
            f"World(pits="
            + str([str(pit) for pit in self.pits.values()])
            + ", memberships="
            + str(
                [
                    f"{member_id}: {str(pit.id)}"
                    for member_id, pit in self.memberships.items()
                ]
            )
            + ")"
        )

    def __iter__(self):
        return iter(self.pits.values())

    def __len__(self):
        return len(self.pits)

    def __contains__(self, pit_id: SnakePitId):
        return pit_id in self.pits
