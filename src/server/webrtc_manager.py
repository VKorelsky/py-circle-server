from flask_socketio import emit

from server.model import World, PitMemberId
from server.logger import get_logger

_logger = get_logger(__name__)


class WebRtcManager:
    def __init__(self, world: World):
        self.world = world

    def send_offer(self, from_peer_id: PitMemberId, to_peer_id: PitMemberId, offer):
        _logger.info(f"Peer with id {from_peer_id} sending offer to peer with id {to_peer_id}")

        self._assert_peers_in_same_pit(from_peer_id, to_peer_id)
        emit("newOffer", {"fromPeerId": from_peer_id, "offer": offer}, to=to_peer_id)

    def send_answer(self, from_peer_id: PitMemberId, to_peer_id: PitMemberId, answer):
        _logger.info(f"Peer with id {from_peer_id} sending answer to peer with id {to_peer_id}")

        self._assert_peers_in_same_pit(from_peer_id, to_peer_id)
        emit("newAnswer", {"fromPeerId": from_peer_id, "answer": answer}, to=to_peer_id)

    def send_ice_candidate(
        self, from_peer_id: PitMemberId, to_peer_id: PitMemberId, ice_candidate
    ):
        _logger.info(f"Peer with id {from_peer_id} sending ice candidate to peer with id {to_peer_id}")

        self._assert_peers_in_same_pit(from_peer_id, to_peer_id)
        emit(
            "newIceCandidate",
            {"fromPeerId": from_peer_id, "newIceCandidate": ice_candidate},
            to=to_peer_id,
        )

    def _assert_peers_in_same_pit(
        self, from_peer_id: PitMemberId, to_peer_id: PitMemberId
    ):
        pit = self.world.get_pit_by_pit_member(from_peer_id)

        if pit is None:
            _logger.error(f"No pit found for peer {from_peer_id}")
            raise ValueError(f"No pit found for peer {from_peer_id}")

        if not to_peer_id in pit:
            _logger.error(f"Target peer {to_peer_id} not found in pit {pit.id}")
            raise Exception(f"Target peer {to_peer_id} not found in pit {pit.id}")
