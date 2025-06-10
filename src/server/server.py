import uuid
import argparse
from flask import Flask, Request, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from server.model import SnakePit, World
from server.model.snake import SnakeId
from server.pit_manager import SnakePitManager
from server.webrtc_manager import WebRtcManager
from server.logger import get_logger

_logger = get_logger(__name__)
app = Flask(__name__)
CORS(app, resources=r"/*", origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

SocketId = str
world = World()
pit_manager = SnakePitManager(world)
web_rtc_manager = WebRtcManager(world)

# hardcode a pit for testing
pit = SnakePit(uuid.UUID("697d8c94-cee3-4a99-a3b6-b7cced7927fc"))
world.pits[pit.id] = pit


def get_connection_id(request: Request) -> SocketId:
    return request.sid  # type: ignore


def parse_pit_id(pit_id: str) -> uuid.UUID:
    try:
        return uuid.UUID(pit_id)
    except ValueError:
        raise ValueError("Invalid pit ID")


def parse_snake_id(snake_id: str) -> SnakeId:
    # socket.io sids are alphanumeric outside of - and _ characters
    if (
        not snake_id
        or not snake_id.replace("-", "").replace("_", "").isalnum()
    ):
        raise ValueError("Invalid snake ID")

    return SnakeId(snake_id)


@socketio.on_error()
def error_handler(e):
    _logger.error(f"Socket.IO error occurred: {str(e)}")
    emit("error", {"message": str(e)})


@socketio.on("connect")
def on_connect():
    pit_manager.handle_connect(get_connection_id(request))


@socketio.on("disconnect")
def on_disconnect(reason):
    _logger.info(f"Peer disconnected with reason: {reason}")
    pit_manager.handle_disconnect(get_connection_id(request))


@socketio.on("create_snake_pit")
def on_create_pit(pit_id):
    pit_id = parse_pit_id(pit_id)
    pit_manager.handle_create_pit(pit_id)


@socketio.on("join_snake_pit")
def on_join_pit(pit_id):
    pit_id = parse_pit_id(pit_id)
    pit_manager.handle_join_pit(get_connection_id(request), pit_id)


@socketio.on("leave_snake_pit")
def on_leave_pit():
    pit_manager.handle_leave_pit(get_connection_id(request))


@socketio.on("send_offer")
def on_send_offer(to_peer_id, offer):
    from_peer_id = get_connection_id(request)
    to_peer_id = parse_snake_id(to_peer_id)
    web_rtc_manager.send_offer(from_peer_id, to_peer_id, offer)


@socketio.on("send_answer")
def on_send_answer(to_peer_id, answer):
    from_peer_id = get_connection_id(request)
    to_peer_id = parse_snake_id(to_peer_id)
    web_rtc_manager.send_answer(from_peer_id, to_peer_id, answer)


@socketio.on("send_ice_candidate")
def on_send_ice_candidate(to_peer_id, ice_candidate):
    from_peer_id = get_connection_id(request)
    to_peer_id = parse_snake_id(to_peer_id)
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
    _logger.info(f"Server initialized with world state: {str(world)}")


def main(debug=False, host="0.0.0.0", port=5678):
    print_server_init_header()
    socketio.run(app, debug=debug, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    main(args.debug)
