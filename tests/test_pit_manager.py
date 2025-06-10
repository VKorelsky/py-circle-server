import uuid
from server.server import app, socketio
from typing import Any, TypedDict

CONNECTED_MESSAGE_NAME = "connected"
CREATE_SNAKE_PIT_MESSAGE_NAME = "createSnakePit"
ERROR_MESSAGE_NAME = "error"
JOIN_PIT_MESSAGE_NAME = "joinSnakePit"
NEW_ROOM_MEMBER_MESSAGE_NAME = "newRoomMember"
PIT_CREATED_MESSAGE_NAME = "pit_created"
ROOM_MEMBER_LEFT_MESSAGE_NAME = "room_member_left"


class SocketIOMessage(TypedDict):
    name: str
    args: list[dict[str, Any]]
    namespace: str


class TestSnakePitManager:
    def _join_pit(self, client, pit_id):
        client.emit(JOIN_PIT_MESSAGE_NAME, pit_id)

    def _create_pit(self, client, pit_id=str(uuid.uuid4())):
        client.emit(CREATE_SNAKE_PIT_MESSAGE_NAME, pit_id)

    def _client(self):
        return socketio.test_client(app)

    def _get_events_by_name(self, client, event_name) -> list[SocketIOMessage]:
        return [event for event in client.get_received() if event["name"] == event_name]

    def test_id_assigned_upon_connection(self):
        client = self._client()
        connected_events = self._get_events_by_name(client, CONNECTED_MESSAGE_NAME)

        assert len(connected_events) == 1
        assert "display_name" in connected_events[0]["args"][0].keys()

    def test_create_pit(self):
        client = self._client()
        client.get_received().clear()

        self._create_pit(client)
        pit_created_events = self._get_events_by_name(client, PIT_CREATED_MESSAGE_NAME)

        assert len(pit_created_events) == 1
        assert "pit_id" in pit_created_events[0]["args"][0].keys()

    def test_create_pit_with_invalid_pit_id(self):
        client = self._client()
        client.get_received().clear()

        self._create_pit(client, "invalid-pit-id")
        notifs = self._get_events_by_name(client, ERROR_MESSAGE_NAME)
        assert len(notifs) == 1
        assert notifs[0]["args"][0]["message"] == "Invalid pit ID"

    def test_join_pit(self):
        # client 1
        client1 = self._client()

        self._create_pit(client1)
        pit_created_events = self._get_events_by_name(client1, PIT_CREATED_MESSAGE_NAME)

        # join created pit
        assert len(pit_created_events) == 1
        pit_id = pit_created_events[0]["args"][0]["pit_id"]
        self._join_pit(client1, pit_id)

        # new client
        client2 = self._client()
        client2_notifs = self._get_events_by_name(client2, CONNECTED_MESSAGE_NAME)
        assert len(client2_notifs) == 1
        client2_display_name = client2_notifs[0]["args"][0]["display_name"]

        self._join_pit(client2, pit_id)

        # check that new client info was properly communicated
        client1_notifs = self._get_events_by_name(client1, NEW_ROOM_MEMBER_MESSAGE_NAME)
        client2_notifs = self._get_events_by_name(client2, NEW_ROOM_MEMBER_MESSAGE_NAME)

        assert len(client1_notifs) == 1
        assert len(client2_notifs) == 0

        assert "new_peer_display_name" in client1_notifs[0]["args"][0].keys()
        assert (
            client1_notifs[0]["args"][0]["new_peer_display_name"]
            == client2_display_name
        )

    def test_join_pit_with_invalid_pit_id(self):
        client = self._client()
        client.get_received().clear()

        self._join_pit(client, "invalid-pit-id")
        notifs = self._get_events_by_name(client, ERROR_MESSAGE_NAME)
        assert len(notifs) == 1

    def test_client_disconnect(self):
        # Setup: Create a pit and join it
        client = self._client()
        self._create_pit(client)
        pit_created_events = self._get_events_by_name(client, PIT_CREATED_MESSAGE_NAME)
        pit_id = pit_created_events[0]["args"][0]["pit_id"]
        self._join_pit(client, pit_id)

        # Create second client and join pit
        client2 = self._client()
        self._join_pit(client2, pit_id)

        # Disconnect first client
        client.disconnect()

        # Verify second client received room_member_left notification
        client2_notifs = self._get_events_by_name(
            client2, ROOM_MEMBER_LEFT_MESSAGE_NAME
        )
        assert len(client2_notifs) == 1
        assert "leaving_peer_id" in client2_notifs[0]["args"][0]
