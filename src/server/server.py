import uuid
import argparse
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO

from server.model import Pit, World
from server.pit_manager import PitManager
from server.webrtc_manager import WebRtcManager

app = Flask(__name__)
CORS(app, resources=r"/*", origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

world = World()
# hardcode a pit for testing
pit = Pit(uuid.UUID("697d8c94-cee3-4a99-a3b6-b7cced7927fc"))
world.add_pit(pit)

pit_manager = PitManager(world)
web_rtc_manager = WebRtcManager(world)


@socketio.on_error()
def error_handler(e):
    print(f"Socket.IO error occurred: {str(e)}")
    pass


@socketio.on("connect")
def on_connect():
    query_params = request.args

    # until FE renames to pitID, we will have to take params as circle id
    pit_id = uuid.UUID(query_params.get("circleId"))
    pit_manager.handle_join_pit(request.sid, pit_id)  # type: ignore


@socketio.on("disconnect")
def on_disconnect(reason):
    print(f"Peer disconnected with reason: {reason}")
    pit_manager.handle_disconnect(request.sid)  # type: ignore


@socketio.on("joinPit")
def on_join_pit(pit_id):
    pit_id = uuid.UUID(pit_id)
    pit_manager.handle_join_pit(request.sid, pit_id)  # type: ignore


@socketio.on("leavePit")
def on_leave_pit(_pit_id):
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

def print_server_init_header():
    print(
        """
 _____  _____  _____  _____                               
/  ___|/  ___|/  ___|/  ___|                              
\\ `--. \\ `--. \\ `--. \\ `--.   ___  _ __ __   __ ___  _ __ 
 `--. \\ `--. \\ `--. \\ `--. \\ / _ \\| '__|\\ \\ / // _ \\| '__|
/\\__/ //\\__/ //\\__/ //\\__/ /|  __/| |    \\ V /|  __/| |   
\\____/ \\____/ \\____/ \\____/  \\___||_|     \\_/  \\___||_|   
Initializing server...
"""
    )
    print(str(world))


def main(debug=False, host="0.0.0.0", port=5678):
    print_server_init_header()
    socketio.run(app, debug=debug, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    main(args.debug)
