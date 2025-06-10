import uuid

from server.model.snake import Snake, SnakeId

SnakePitId = uuid.UUID


class SnakePit:
    def __init__(self, id=uuid.uuid4()):
        self.id: SnakePitId = id
        self.snakes: dict[SnakeId, Snake] = dict()

    def add_snake(self, new_snake: Snake):
        self.snakes[new_snake.id] = new_snake

    def remove_snake(self, snake: Snake):
        try:
            del self.snakes[snake.id]
        except KeyError as e:
            return None

    def get_snake(self, snake_or_id: Snake | SnakeId) -> Snake | None:
        """Get a snake by Snake object or SnakeId."""
        if isinstance(snake_or_id, Snake):
            return self.snakes.get(snake_or_id.id)
        else:
            return self.snakes.get(snake_or_id)

    def __str__(self):
        return (
            f"SnakePit(id={str(self.id)}, members="
            + str([str(member) for member in self.snakes])
            + ")"
        )

    def __iter__(self):
        return iter(self.snakes.values())

    def __len__(self):
        return len(self.snakes)

    def __contains__(self, member_id: SnakeId):
        return member_id in self.snakes
