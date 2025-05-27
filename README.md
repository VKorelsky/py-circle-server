# sss 

**S**imple **S**ignaling **S**erver for P2P webRTC snake.

## Usage

1. Install [UV](https://docs.astral.sh/uv/)
2. `$ uv run server.py`

#### Websocket events
##### Pit management
- `create_pit`
- `join_pit`, requires the `pit_id` to be passed
- `leave_pit`

##### WebRTC 
- `sendOffer` - Send WebRTC offer to peer
- `sendAnswer` - Send WebRTC answer to peer
- `sendIceCandidate` - Send ICE candidate to peer

<!-- goal of today is -->
<!-- simplify the code of the signaling server into something that will support room creation -->
<!-- and properly implements room leaving and rejoining -->
<!-- and is called snake pit instead of circle -->
<!-- and a CI/CD flow -->

<!-- THEN -->
<!-- fix the snake implementation and make it run properly -->
<!-- type everything -->
<!-- split the lib into a typescript raft implementation? -->


