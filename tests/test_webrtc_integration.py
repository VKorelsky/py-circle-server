import time
from typing import Any, TypedDict

from server.server import app, socketio

NEW_ROOM_MEMBER_MESSAGE_NAME = "newRoomMember"
JOIN_PIT_MESSAGE_NAME = "joinSnakePit"
SEND_OFFER_MESSAGE_NAME = "sendOffer"
NEW_OFFER_MESSAGE_NAME = "newOffer"
SEND_ANSWER_MESSAGE_NAME = "sendAnswer"
NEW_ANSWER_MESSAGE_NAME = "newAnswer"
SEND_ICE_CANDIDATE_MESSAGE_NAME = "sendIceCandidate"
NEW_ICE_CANDIDATE_MESSAGE_NAME = "newIceCandidate"


class SocketIOMessage(TypedDict):
    name: str
    args: list[dict[str, Any]]
    namespace: str


class TestWebRtcIntegration:
    PIT_ID = "697d8c94-cee3-4a99-a3b6-b7cced7927fc"

    def _get_peer_ids_from_events(self, events):
        return [
            event["args"][0]["new_peer_id"]
            for event in events
            if event["name"] == NEW_ROOM_MEMBER_MESSAGE_NAME
        ]

    def _create_and_connect_client(self):
        client = socketio.test_client(app)
        client.get_received()  # Clear initial connection events to avoid interference with test assertions
        return client

    def _join_pit(self, client, pit_id):
        client.emit(JOIN_PIT_MESSAGE_NAME, pit_id)

    def _get_events_by_name(self, client, event_name):
        """Get all events of a specific type from a client."""
        return [event for event in client.get_received() if event["name"] == event_name]

    def test_exchange_offer_answer(self):
        # setup
        client1 = self._create_and_connect_client()
        client2 = self._create_and_connect_client()

        self._join_pit(client1, self.PIT_ID)
        time.sleep(0.01)  # avoid out of order joining
        self._join_pit(client2, self.PIT_ID)
        time.sleep(0.01)

        client1_events = client1.get_received()
        peer_ids = self._get_peer_ids_from_events(client1_events)

        assert (
            len(peer_ids) == 1
        ), f"Expected 1 peer ID, got {len(peer_ids)}: {peer_ids}"
        client2_peer_id = peer_ids[0]

        # send offer
        offer_data = {"type": "offer", "sdp": "test-sdp-content"}
        client1.emit(SEND_OFFER_MESSAGE_NAME, client2_peer_id, offer_data)

        # verify
        offer_events = self._get_events_by_name(client2, NEW_OFFER_MESSAGE_NAME)
        assert len(offer_events) == 1

        event_data = offer_events[0]["args"][0]
        assert event_data["offer"] == offer_data
        # we can't access socket io assigned ids in the tests, and tbh we shouldn't rely on them
        # until we implement a mechanism to get a stable id, we can only really assert this
        assert "fromPeerId" in event_data

        # Send answer
        answer_data = {"type": "answer", "sdp": "test-answer-sdp"}
        client2.emit(SEND_ANSWER_MESSAGE_NAME, event_data["fromPeerId"], answer_data)

        # verify
        answer_events = self._get_events_by_name(client1, NEW_ANSWER_MESSAGE_NAME)
        assert len(answer_events) == 1

        expected_event = {"fromPeerId": client2_peer_id, "answer": answer_data}
        answer_data_received = answer_events[0]["args"][0]
        assert expected_event == answer_data_received

    def test_ice_candidate_exchange(self):
        # setup
        client1 = self._create_and_connect_client()
        client2 = self._create_and_connect_client()

        self._join_pit(client1, self.PIT_ID)
        time.sleep(0.01)
        self._join_pit(client2, self.PIT_ID)
        time.sleep(0.01)

        peer_ids = self._get_peer_ids_from_events(client1.get_received())
        assert len(peer_ids) == 1, f"Expected 1 peer ID, got {len(peer_ids)}"
        client2_peer_id = peer_ids[0]

        # Send ICE candidate
        ice_candidate_data = {
            "candidate": "candidate:1 1 UDP 2113667326 192.168.1.100 54400 typ host",
            "sdpMLineIndex": 0,
            "sdpMid": "0",
        }

        client1.emit(
            SEND_ICE_CANDIDATE_MESSAGE_NAME, client2_peer_id, ice_candidate_data
        )

        # Verify
        ice_events = self._get_events_by_name(client2, NEW_ICE_CANDIDATE_MESSAGE_NAME)
        assert len(ice_events) == 1

        event_data = ice_events[0]["args"][0]
        assert event_data["newIceCandidate"] == ice_candidate_data
        assert "fromPeerId" in event_data

    def test_webrtc_messages_only_sent_to_target_peer(self):
        # setup
        client1 = self._create_and_connect_client()
        client2 = self._create_and_connect_client()
        client3 = self._create_and_connect_client()

        self._join_pit(client1, self.PIT_ID)
        time.sleep(0.01)
        self._join_pit(client2, self.PIT_ID)
        time.sleep(0.01)
        self._join_pit(client3, self.PIT_ID)
        time.sleep(0.01)

        peer_ids = self._get_peer_ids_from_events(client1.get_received())

        assert (
            len(peer_ids) == 2
        ), f"Expected 2 peer IDs, got {len(peer_ids)}: {peer_ids}"

        client2_peer_id = peer_ids[0]  # First to join after client1

        # Send offer from client1 to client2 only
        offer_data = {"type": "offer", "sdp": "test-sdp"}
        client1.emit(SEND_OFFER_MESSAGE_NAME, client2_peer_id, offer_data)

        # Verify
        client2_offers = self._get_events_by_name(client2, NEW_OFFER_MESSAGE_NAME)
        client3_offers = self._get_events_by_name(client3, NEW_OFFER_MESSAGE_NAME)

        assert len(client2_offers) == 1
        assert len(client3_offers) == 0
        assert client2_offers[0]["args"][0]["offer"] == offer_data

    def test_webrtc_error_handling_for_invalid_peer(self):
        # setup
        client1 = self._create_and_connect_client()

        self._join_pit(client1, self.PIT_ID)
        time.sleep(0.01)
        client1.get_received()  # Clear join events

        # Send offer to non-existent peer
        offer_data = {"type": "offer", "sdp": "test-sdp"}
        client1.emit(SEND_OFFER_MESSAGE_NAME, "non-existent-peer-id", offer_data)

        # verify
        error_events = self._get_events_by_name(client1, "error")
        print(f"ERROR EVENTS: {error_events}")
        assert len(error_events) == 1

    def test_webrtc_error_handling_for_invalid_peer_id(self):
        # setup
        client1 = self._create_and_connect_client()

        self._join_pit(client1, self.PIT_ID)
        time.sleep(0.01)
        client1.get_received()  # Clear join events

        # Send offer to badly formatted peer id
        offer_data = {"type": "offer", "sdp": "test-sdp"}
        client1.emit(
            SEND_OFFER_MESSAGE_NAME,
            '{"this is not valid": "invalid-peer-id"}',
            offer_data,
        )

        # verify
        error_events = self._get_events_by_name(client1, "error")
        assert len(error_events) == 1
        assert error_events[0]["args"][0]["message"] == "Invalid snake ID"
