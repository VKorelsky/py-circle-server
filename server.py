import uuid
from dataclasses import dataclass

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

circles = []


class CircleMember:
    id: uuid

    def __init__(self, id):
        self.id = id


class Circle:
    id: uuid
    members: list[CircleMember]

    def __init__(self):
        self.id = uuid.uuid4()
        self.members = []

    def add_member(self, new_member: CircleMember):
        self.members.append(new_member)

    def remove_member(self, member_id: str):
        self.members = [m for m in self.members if str(m.id) != member_id]


def get_circle(requested_circle_id: str) -> Circle | None:
    for circle in circles:
        if str(circle.id) == requested_circle_id:
            return circle

    return None


@socketio.on("joinCircle")
def on_join(new_peer_id, requested_circle_id):
    print(
        f"Peer with id {new_peer_id} requested to join circle with id {requested_circle_id}"
    )

    circle = get_circle(requested_circle_id)

    if circle is None:
        raise Exception("No circle found")

    join_room(circle.id)
    circle.add_member(CircleMember(new_peer_id))


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


# messages that can be received
#   sendOffer
#   sendAnswer
#   broadcastIceCandidate

# messages that can be sent
#   newOffer
#   newAnswer
#   newIceCandidate


# ADMIN ENDPOINTS
@app.post("/circle/new")
def create_circle():
    circle = Circle()
    circles.append(circle)

    print(f"creating new circle {circle}")
    print(circles)

    return {"circle_id": circle.id}


@app.get("/circle/<circle_id>")
def show_circle(circle_id):
    print(f"requested circle with id {circle_id}")
    print(circles)
    circle = get_circle(circle_id)

    if circle is None:
        return {}, 404

    return {"circle_id": circle.id, "members": [member.id for member in circle.members]}


if __name__ == "__main__":
    socketio.run(app, debug=True)
