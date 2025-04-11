import uuid

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, send

app = Flask(__name__)
CORS(app, resources=r"/*", origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")


class CircleMember:
    id: str

    def __init__(self, socket_id):
        self.id = socket_id

    def __str__(self):
        return f"CircleMember(id={self.id})"


class Circle:
    id: uuid.UUID
    members: list[CircleMember]

    def __init__(self, id=uuid.uuid4()):
        self.id = id
        self.members = []

    def add_member(self, new_member: CircleMember):
        self.members.append(new_member)

    def remove_member(self, member_id: str):
        self.members = [m for m in self.members if str(m.id) != member_id]

    def __str__(self):
        return (
            f"Circle(id={str(self.id)}, members="
            + str([str(member) for member in self.members])
            + ")"
        )


circles = [Circle(uuid.UUID("697d8c94-cee3-4a99-a3b6-b7cced7927fc"))]


# this should really be hashmaps
def get_circle(requested_circle_id: uuid.UUID) -> Circle | None:
    for circle in circles:
        if circle.id == requested_circle_id:
            return circle

    return None


def find_peer(circle_id: uuid.UUID, member_id: str) -> CircleMember | None:
    circle = get_circle(circle_id)

    if not circle:
        return None

    for member in circle.members:
        if str(member.id) == member_id:
            return member

    return None


@socketio.on_error()
def error_handler(e):
    pass


@socketio.on("connect")
def on_join():
    query_params = request.args
    requested_circle_id = uuid.UUID(query_params.get("circleId"))
    peer_sid = request.sid  # type: ignore

    print(
        f"Peer with id {peer_sid} requested to join circle with id {requested_circle_id}"
    )

    circle = get_circle(requested_circle_id)

    if circle is None:
        # question around exception handling in the websockets - how does that work?
        raise Exception("No circle found")

    new_member = CircleMember(peer_sid)

    room_id = str(circle.id)
    join_room(room_id)
    circle.add_member(new_member)

    emit("newRoomMember", new_member.id, to=room_id, include_self=False)


@socketio.on("disconnect")
def on_disconnect():
    query_params = request.args
    print(f"received connection request with query_params {query_params}")


@socketio.on("leaveCircle")
def on_leave(leaving_peer_id, requested_circle_id):
    print(
        f"Peer with id {leaving_peer_id} requested to leave circle with id {requested_circle_id}"
    )

    circle = get_circle(requested_circle_id)

    if circle is None:
        raise Exception("No circle found")

    leave_room(circle.id)
    circle.remove_member(leaving_peer_id)


# ADMIN ENDPOINTS
@app.post("/circle/new")
def create_circle():
    circle = Circle()
    circles.append(circle)

    print(f"creating new circle {circle}")
    print(circles)

    return {"circle_id": circle.id}


@app.post("/circle/<circle_id>/broadcast")
def broadcast(circle_id: str):
    circle = get_circle(uuid.UUID(circle_id))

    if circle is None:
        return {}, 404

    emit("newRoomMember", {"new_member_id": 123}, to=str(circle.id))
    return {}, 200


@app.get("/circle/<circle_id>")
def show_circle(circle_id: str):
    print(f"requested circle with id {circle_id}")
    circle = get_circle(uuid.UUID(circle_id))

    if circle is None:
        return {}, 404

    return {"circle_id": circle.id, "members": [member.id for member in circle.members]}


if __name__ == "__main__":
    socketio.run(app, debug=True)
