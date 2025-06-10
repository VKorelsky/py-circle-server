from flask_socketio import emit

from server.model import World
from server.logger import get_logger
from server.model.snake import SnakeId

_logger = get_logger(__name__)


class WebRtcManager:
    def __init__(self, world: World):
        self.world = world

    def send_offer(self, from_peer_id: SnakeId, to_peer_id: SnakeId, offer):
        _logger.info(
            f"Peer with id {from_peer_id} sending offer to peer with id {to_peer_id}"
        )

        self._assert_peers_in_same_pit(from_peer_id, to_peer_id)
        emit("newOffer", {"fromPeerId": from_peer_id, "offer": offer}, to=to_peer_id)

    def send_answer(self, from_peer_id: SnakeId, to_peer_id: SnakeId, answer):
        _logger.info(
            f"Peer with id {from_peer_id} sending answer to peer with id {to_peer_id}"
        )

        self._assert_peers_in_same_pit(from_peer_id, to_peer_id)
        emit("newAnswer", {"fromPeerId": from_peer_id, "answer": answer}, to=to_peer_id)

    def send_ice_candidate(
        self, from_peer_id: SnakeId, to_peer_id: SnakeId, ice_candidate
    ):
        _logger.info(
            f"Peer with id {from_peer_id} sending ice candidate to peer with id {to_peer_id}"
        )

        self._assert_peers_in_same_pit(from_peer_id, to_peer_id)
        emit(
            "newIceCandidate",
            {"fromPeerId": from_peer_id, "newIceCandidate": ice_candidate},
            to=to_peer_id,
        )

    def _assert_peers_in_same_pit(self, from_peer_id: SnakeId, to_peer_id: SnakeId):
        if from_peer_id not in self.world.snakes:
            raise ValueError("Source peer not found in world")

        if to_peer_id not in self.world.snakes:
            raise ValueError("Target peer not found in world")

        snake1, pit1 = self.world.snakes[from_peer_id]
        snake2, pit2 = self.world.snakes[to_peer_id]

        if pit1 is None or pit2 is None:
            raise ValueError(
                f"One or both peers not in a pit: {snake1.display_name} in {str(pit1)}, {snake2.display_name} in {str(pit2)}"
            )

        if pit1 is not pit2:
            raise ValueError(
                f"Peers are in different pits: {snake1.display_name} in {str(pit1)}, {snake2.display_name} in {str(pit2)}"
            )
