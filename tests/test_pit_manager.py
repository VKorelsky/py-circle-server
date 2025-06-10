import time

from server.server import app, socketio

NEW_ROOM_MEMBER_MESSAGE_NAME = "newRoomMember"
JOIN_PIT_MESSAGE_NAME = "joinPit"


class TestPitManager:
    def _join_pit(self, client, pit_id):
        client.emit(JOIN_PIT_MESSAGE_NAME, pit_id)

    def test_receive_id_upon_connection(self):
        client = socketio.test_client(app)
        received = client.get_received()
        
        print(received)
