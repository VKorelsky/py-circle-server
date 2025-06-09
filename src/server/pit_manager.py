from flask_socketio import emit, join_room, leave_room
from server.model import PitId, PitMember, PitMemberId, World


class PitManager:
    def __init__(self, world: World):
        self.world = world

    def handle_join_pit(self, new_peer_id: PitMemberId, pit_id: PitId):
        print(f"Peer {new_peer_id} joining pit {pit_id}")
        new_pit_member = PitMember(new_peer_id)
        self.world.add_member_to_pit(pit_id, new_pit_member)

        try:
            self._join_socket_io_room(pit_id, new_peer_id)
        except Exception as e:
            print(f"Error joining room: {str(e)}")
            self.world.remove_member_from_pit(new_peer_id)
            raise e

        print("SOW: " + str(self.world))

    def handle_disconnect(self, peer_id: PitMemberId):
        print(f"Peer {peer_id} disconnected")

        for pit in self.world:
            if pit.get_member(peer_id):
                print(f"Peer {peer_id} leaving pit {pit.id}")

                pit.remove_member(peer_id)
                self._leave_socket_io_room(pit.id, peer_id)
                
        print("SOW: " + str(self.world))

    def _join_socket_io_room(self, pit_id: PitId, new_peer_id: PitMemberId):
        room_id = str(pit_id)
        join_room(room_id)
        emit("newRoomMember", new_peer_id, to=room_id, include_self=False)

    def _leave_socket_io_room(self, pit_id: PitId, peer_id: PitMemberId):
        room_id = str(pit_id)
        leave_room(room_id)
        emit("room_member_left", {"leaving_peer_id": peer_id}, to=room_id)
