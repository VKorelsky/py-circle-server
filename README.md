# sss

**S**imple **S**ignaling **S**erver for P2P webRTC snake.

## Usage

1. Install [UV](https://docs.astral.sh/uv/)
2. `$ uv run server`

### Socket.io events

### Client to server

##### Pit management

- `{"action": "create_pit" }`
- `{"action": "join_pit", "pit_id": "1234567" }`
- `{"action": "leave_pit" }`

##### WebRTC

- `{"action": "send_offer", "to_peer_id": "peer_id", "payload": <offer_payload> }`
- `{"action": "send_answer", "to_peer_id": "peer_id", "payload": <answer_payload> }`
- `{"action": "send_ice_candidate", "to_peer_id": "peer_id", "payload": <ice_candidate_payload> }`

### Server to client

##### Pit management
- `{"event": "new_room_member", "new_peer_id": "peer_id" }`
- `{"event": "room_member_left", "leaving_peer_id": "peer_id" }`

##### WebRTC

- `{"event": "newOffer", "fromPeerId": "peer_id", "offer": <offer_payload> }`
- `{"event": "newAnswer", "fromPeerId": "peer_id", "answer": <answer_payload> }`
- `{"event": "newIceCandidate", "fromPeerId": "peer_id", "newIceCandidate": <ice_candidate_payload> }`
