# sss

**S**imple **S**ignaling **S**erver for P2P webRTC snake.

## Usage

1. Install [UV](https://docs.astral.sh/uv/)
2. `$ uv run serve`

### Testing

- Run all tests: `uv run pytest`
- Run specific test: `uv run pytest tests/test_pit_manager.py`

### Socket.io events

### Client to server

##### Connection Management

- **connect**: Automatically assigns unique snake ID and display name
- **create_snake_pit**, payload: `{"pit_id": "697d8c94-cee3-4a99-a3b6-b7cced7927fc"}`
- **join_snake_pit**, payload: `{"pit_id": "697d8c94-cee3-4a99-a3b6-b7cced7927fc"}`  
- **leave_snake_pit**: No payload (leaves current pit)

##### WebRTC Signaling

- **send_offer**, payload: `{"to_peer_id": "socket_id_123", "offer": {...}}`
- **send_answer**, payload: `{"to_peer_id": "socket_id_123", "answer": {...}}`
- **send_ice_candidate**, payload: `{"to_peer_id": "socket_id_123", "ice_candidate": {...}}`

### Server to client

##### Connection & Pit Management

- **connected**, payload: `{"display_name": "striped-sahara-cobra"}`
- **pit_created**, payload: `{"pit_id": "697d8c94-cee3-4a99-a3b6-b7cced7927fc"}`
- **new_room_member**, payload: `{"new_peer_id": "socket_id_123", "new_peer_display_name": "glossy-amazon-viper"}`
- **room_member_left**, payload: `{"leaving_peer_id": "socket_id_123"}`

##### WebRTC Signaling

- **new_offer**, payload: `{"fromPeerId": "socket_id_123", "offer": {...}}`
- **new_answer**, payload: `{"fromPeerId": "socket_id_123", "answer": {...}}`
- **new_ice_candidate**, payload: `{"fromPeerId": "socket_id_123", "newIceCandidate": {...}}`

##### Errors

- **error**, payload: `{"message": "Pit does not exist"}`
