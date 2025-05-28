import uuid

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

from server.model import Pit, PitMember, get_pit, get_pit_member, world

app = Flask(__name__)
CORS(app, resources=r"/*", origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on_error()
def error_handler(e):
    print(f"Socket.IO error occurred: {str(e)}")
    pass


@socketio.on("connect")
def on_connect():
    peer_sid = request.sid
    print(f"Peer {peer_sid} connected")


@socketio.on("disconnect")
def on_disconnect():
    peer_sid = request.sid
    print(f"Peer {peer_sid} disconnected")

    # Remove from all pits
    for pit in world:
        if any(member.id == peer_sid for member in pit.members):
            pit.remove_member(peer_sid)
            room_id = str(pit.id)
            leave_room(room_id)
            emit("room_member_left", {"leaving_peer_id": peer_sid}, to=room_id)


# Pit Management Events
@socketio.on("message")
def handle_message(data):
    """Handle Socket.IO messages with action-based routing"""
    action = data.get("action")
    peer_sid = request.sid

    if action == "create_pit":
        handle_create_pit(peer_sid)
    elif action == "join_pit":
        pit_id = data.get("pit_id")
        handle_join_pit(peer_sid, pit_id)
    elif action == "leave_pit":
        handle_leave_pit(peer_sid)
    elif action == "send_offer":
        to_peer_id = data.get("to_peer_id")
        payload = data.get("payload")
        handle_send_offer(peer_sid, to_peer_id, payload)
    elif action == "send_answer":
        to_peer_id = data.get("to_peer_id")
        payload = data.get("payload")
        handle_send_answer(peer_sid, to_peer_id, payload)
    elif action == "send_ice_candidate":
        to_peer_id = data.get("to_peer_id")
        payload = data.get("payload")
        handle_send_ice_candidate(peer_sid, to_peer_id, payload)
    else:
        print(f"Unknown action: {action}")


def handle_create_pit(peer_sid: str):
    """Create a new pit and join the creator to it"""
    new_pit = Pit()
    world.append(new_pit)

    new_member = PitMember(peer_sid)
    new_pit.add_member(new_member)

    room_id = str(new_pit.id)
    join_room(room_id)

    print(f"Created new pit {new_pit.id} with creator {peer_sid}")

    # Send pit_id back to creator
    emit("pit_created", {"pit_id": str(new_pit.id)})


def handle_join_pit(peer_sid: str, pit_id: str):
    """Join an existing pit"""
    if not pit_id:
        emit("error", {"message": "pit_id is required"})
        return

    try:
        requested_pit_id = uuid.UUID(pit_id)
    except ValueError:
        emit("error", {"message": "Invalid pit_id format"})
        return

    pit = get_pit(requested_pit_id)
    if not pit:
        emit("error", {"message": "Pit not found"})
        return

    # Check if already in pit
    if any(member.id == peer_sid for member in pit.members):
        emit("error", {"message": "Already in pit"})
        return

    new_member = PitMember(peer_sid)
    pit.add_member(new_member)

    room_id = str(pit.id)
    join_room(room_id)

    print(f"Peer {peer_sid} joined pit {pit_id}")

    # Notify others in the pit
    emit("new_room_member", {"new_peer_id": peer_sid}, to=room_id, include_self=False)

    # Confirm join to the joiner
    emit("pit_joined", {"pit_id": pit_id})


def handle_leave_pit(peer_sid: str):
    """Leave current pit"""
    # Find which pit the peer is in
    current_pit = None
    for pit in world:
        if any(member.id == peer_sid for member in pit.members):
            current_pit = pit
            break

    if not current_pit:
        emit("error", {"message": "Not in any pit"})
        return

    current_pit.remove_member(peer_sid)
    room_id = str(current_pit.id)
    leave_room(room_id)

    print(f"Peer {peer_sid} left pit {current_pit.id}")

    # Notify others in the pit
    emit("room_member_left", {"leaving_peer_id": peer_sid}, to=room_id)

    # Confirm leave to the leaver
    emit("pit_left", {"pit_id": str(current_pit.id)})


# WebRTC Event Handlers
def handle_send_offer(from_peer_id: str, to_peer_id: str, payload):
    """Handle WebRTC offer"""
    if not to_peer_id or not payload:
        emit("error", {"message": "to_peer_id and payload are required"})
        return

    # Find pit containing both peers
    pit = find_pit_with_peer(from_peer_id)
    if not pit or not get_pit_member(pit.id, to_peer_id):
        emit("error", {"message": "Peers not in same pit"})
        return

    print(f"Peer {from_peer_id} sending offer to {to_peer_id}")
    emit("newOffer", {"fromPeerId": from_peer_id, "offer": payload}, to=to_peer_id)


def handle_send_answer(from_peer_id: str, to_peer_id: str, payload):
    """Handle WebRTC answer"""
    if not to_peer_id or not payload:
        emit("error", {"message": "to_peer_id and payload are required"})
        return

    # Find pit containing both peers
    pit = find_pit_with_peer(from_peer_id)
    if not pit or not get_pit_member(pit.id, to_peer_id):
        emit("error", {"message": "Peers not in same pit"})
        return

    print(f"Peer {from_peer_id} sending answer to {to_peer_id}")
    emit("newAnswer", {"fromPeerId": from_peer_id, "answer": payload}, to=to_peer_id)


def handle_send_ice_candidate(from_peer_id: str, to_peer_id: str, payload):
    """Handle WebRTC ICE candidate"""
    if not to_peer_id or not payload:
        emit("error", {"message": "to_peer_id and payload are required"})
        return

    # Find pit containing both peers
    pit = find_pit_with_peer(from_peer_id)
    if not pit or not get_pit_member(pit.id, to_peer_id):
        emit("error", {"message": "Peers not in same pit"})
        return

    print(f"Peer {from_peer_id} sending ICE candidate to {to_peer_id}")
    emit(
        "newIceCandidate",
        {"fromPeerId": from_peer_id, "newIceCandidate": payload},
        to=to_peer_id,
    )


def find_pit_with_peer(peer_id: str) -> Pit | None:
    """Find the pit containing the given peer"""
    for pit in world:
        if any(member.id == peer_id for member in pit.members):
            return pit
    return None


def main():
    socketio.run(app, debug=True, host="0.0.0.0", port=5678)


if __name__ == "__main__":
    main()
