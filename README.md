# sss

**S**imple **S**ignaling **S**erver for P2P webRTC snake.

## Usage

1. Install [UV](https://docs.astral.sh/uv/)
2. `$ uv run serve`

### Socket.io events

### Client to server

##### Connection

- Connect with query param: `?pitId=<uuid>` (auto-joins pit)

##### Pit management

- `joinPit` with pit_id parameter
- `leavePit`

##### WebRTC

- `sendOffer` with parameters: to_peer_id, offer
- `sendAnswer` with parameters: to_peer_id, answer  
- `sendIceCandidate` with parameters: to_peer_id, ice_candidate

### Server to client

##### Pit management
- `newRoomMember` with new_peer_id
- `room_member_left` with leaving_peer_id object

##### WebRTC

- `newOffer` with fromPeerId and offer
- `newAnswer` with fromPeerId and answer
- `newIceCandidate` with fromPeerId and newIceCandidate

##### Errors
- `{"event": "error", "message": "<error_message>" }` 