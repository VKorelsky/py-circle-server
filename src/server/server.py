import uuid
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO

from server.model import World
from server.pit_manager import PitManager
from server.webrtc_manager import WebRtcManager

app = Flask(__name__)
CORS(app, resources=r"/*", origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

world = World()
pit_manager = PitManager(world)
web_rtc_manager = WebRtcManager(world)


@socketio.on_error()
def error_handler(e):
    print(f"Socket.IO error occurred: {str(e)}")
    pass


@socketio.on("connect")
def on_connect():
    peer_sid = request.sid  # type: ignore
    print(f"Peer {peer_sid} connected")


@socketio.on("disconnect")
def on_disconnect():
    pit_manager.handle_disconnect(request.sid)  # type: ignore


@socketio.on("joinPit")
def on_join_pit(pit_id):
    pit_manager.handle_join_pit(request.sid, pit_id)  # type: ignore


@socketio.on("leavePit")
def on_leave_pit(pit_id):
    pit_manager.handle_disconnect(request.sid)  # type: ignore


@socketio.on("sendOffer")
def on_send_offer(to_peer_id, offer):
    from_peer_id = request.sid  # type: ignore
    web_rtc_manager.send_offer(from_peer_id, to_peer_id, offer)


@socketio.on("sendAnswer")
def on_send_answer(to_peer_id, answer):
    from_peer_id = request.sid  # type: ignore
    web_rtc_manager.send_answer(from_peer_id, to_peer_id, answer)


@socketio.on("sendIceCandidate")
def on_send_ice_candidate(to_peer_id, ice_candidate):
    from_peer_id = request.sid  # type: ignore
    web_rtc_manager.send_ice_candidate(from_peer_id, to_peer_id, ice_candidate)


def main():
    socketio.run(app, debug=True, host="0.0.0.0", port=5678)


if __name__ == "__main__":
    main()
