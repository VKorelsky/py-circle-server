from flask_socketio import emit, join_room, leave_room
from server.model import SnakePit, SnakePitId, Snake, SnakeId, World
from server.logger import get_logger

_logger = get_logger(__name__)


class SnakePitManager:
    def __init__(self, world: World):
        self.world = world
        self.holding_area: dict[SnakeId, Snake] = dict()

    def handle_connect(self, new_snake_id: SnakeId):
        if new_snake_id in self.holding_area:
            emit("error", {"message": "Connection already established"})
            return

        new_snake = Snake(new_snake_id)
        self._add_to_holding_area(new_snake)
        emit("connection_success", {"id": new_snake.display_name})

    def handle_create_pit(self, pit_id: SnakePitId):
        new_pit = SnakePit(pit_id)
        self.world.add_pit(new_pit)
        emit("pit_created", {"pit_id": str(pit_id)})

    def handle_join_pit(self, snake_id: SnakeId, pit_id: SnakePitId):
        if snake_id not in self.holding_area:
            emit(
                "error",
                {"message": "Peer either already in a room or somehow not connected"},
            )
            return

        # also need to check for pit existence here
        snake = self._remove_from_holding_area(snake_id)

        _logger.info(f"Peer {snake.display_name} joining pit {pit_id}")
        self.world.add_member_to_pit(pit_id, snake)

        try:
            self._join_socket_io_room(pit_id, snake_id)
        except Exception as e:
            _logger.error(f"Error joining room: {str(e)}")
            self.world.remove_member_from_pit(snake_id)
            self._add_to_holding_area(snake)
            raise e

        _logger.debug(f"World state after join: {str(self.world)}")

    def handle_disconnect(self, snake_id: SnakeId):
        _logger.info(f"Peer {snake_id} disconnected")

        if snake_id in self.holding_area:
            self._remove_from_holding_area(snake_id)

        for pit in self.world:
            if pit.get_member(snake_id):
                _logger.info(f"Peer {snake_id} leaving pit {pit.id}")

                pit.remove_member(snake_id)
                self._leave_socket_io_room(pit.id, snake_id)

                if len(pit) == 0:
                    self.world.remove_pit(pit)

        _logger.debug(f"World state after disconnect: {str(self.world)}")

    def _add_to_holding_area(self, snake: Snake) -> None:
        self.holding_area[snake.id] = snake

    def _remove_from_holding_area(self, snake_id: SnakeId) -> Snake:
        snake = self.holding_area.get(snake_id)

        if snake is None:
            raise ValueError(f"Snake with id {snake_id} not found in holding area")

        del self.holding_area[snake_id]
        _logger.debug(f"Removed snake with name {snake.display_name} from holding area")

        return snake

    def _join_socket_io_room(self, pit_id: SnakePitId, new_peer_id: SnakeId):
        room_id = str(pit_id)
        join_room(room_id)
        emit("newRoomMember", new_peer_id, to=room_id, include_self=False)

    def _leave_socket_io_room(self, pit_id: SnakePitId, peer_id: SnakeId):
        room_id = str(pit_id)
        leave_room(room_id)
        emit("room_member_left", {"leaving_peer_id": peer_id}, to=room_id)
