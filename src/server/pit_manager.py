from tokenize import maybe
from flask_socketio import emit, join_room, leave_room
from server.model import SnakePit, SnakePitId, Snake, Snake, World
from server.logger import get_logger
from server.model.snake import SnakeId

_logger = get_logger(__name__)


class SnakePitManager:
    def __init__(self, world: World):
        self.world = world

    def handle_connect(self, new_snake_id: SnakeId):
        if new_snake_id in self.world.snakes:
            self._emit_error("Connection already established")
            return

        new_snake = Snake(new_snake_id)
        self._add_snake_to_world(new_snake)
        emit("connected", {"display_name": new_snake.display_name})

    def handle_create_pit(self, pit_id: SnakePitId):
        self.world.create_pit(pit_id)
        emit("pit_created", {"pit_id": str(pit_id)})

    def handle_join_pit(self, snake_id: SnakeId, pit_id: SnakePitId):
        if snake_id not in self.world.snakes:
            self._emit_error("Peer either already in a room or somehow not connected")
            return

        if pit_id not in self.world.pits:
            self._emit_error("Pit does not exist")
            return

        snake, maybe_pit = self.world.snakes[snake_id]

        if maybe_pit is not None:
            self._emit_error(f"Snake is already in pit with id {maybe_pit.id}")
            return

        pit = self.world.pits[pit_id]  # read

        _logger.info(f"Peer {snake.display_name} joining pit {pit_id}")
        self._add_snake_to_pit(snake, pit)

        try:
            room_id = str(pit_id)
            join_room(room_id)

            emit(
                "newRoomMember",
                {"new_peer_id": snake_id, "new_peer_display_name": snake.display_name},
                to=room_id,
                include_self=False,
            )
        except Exception as e:
            _logger.error(f"Error joining room: {str(e)}")
            self._remove_snake_from_pit(snake, pit)
            self._emit_error(f"Error joining room: {str(e)}")

        _logger.info(f"World state after join: {str(self.world)}")

    def handle_disconnect(self, snake_id: SnakeId):
        if not snake_id in self.world.snakes:
            return None

        snake, maybe_pit = self.world.snakes[snake_id]
        _logger.info(f"Peer {snake.display_name} with id {snake.id} disconnected")

        if maybe_pit is not None:
            self._remove_snake_from_pit(snake, maybe_pit)

            room_id = str(maybe_pit.id)
            leave_room(room_id)
            emit("room_member_left", {"leaving_peer_id": snake_id}, to=room_id)

            if len(maybe_pit) == 0:
                del self.world.pits[maybe_pit.id]

        _logger.debug(f"World state after disconnect: {str(self.world)}")

    def _add_snake_to_world(self, snake: Snake):
        self.world.snakes[snake.id] = (snake, None)

    def _add_snake_to_pit(self, snake: Snake, pit: SnakePit):
        pit.add_snake(snake)
        self.world.snakes[snake.id] = (snake, pit)

    def _remove_snake_from_pit(self, snake: Snake, pit: SnakePit):
        pit.remove_snake(snake)
        self.world.snakes[snake.id] = (snake, None)

    def _emit_error(self, error_message: str):
        emit(
            "error",
            {"message": error_message},
        )
