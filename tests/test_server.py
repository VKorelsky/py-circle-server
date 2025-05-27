from server.server import socketio, app

def test_create_pit():
    """Test creating a pit via Socket.IO"""
    client = get_socket_io_client()
    
    # Send create_pit message
    client.emit("message", {"action": "create_pit"})
    
    # Check for pit_created response
    received = client.get_received()
    assert len(received) > 0
    
    pit_created_event = None
    for event in received:
        if event["name"] == "pit_created":
            pit_created_event = event
            break
    
    assert pit_created_event is not None
    assert "pit_id" in pit_created_event["args"][0]
    pit_id = pit_created_event["args"][0]["pit_id"]
    
    # Verify pit_id is a valid UUID string
    import uuid
    uuid.UUID(pit_id)  # This will raise if invalid


def test_join_pit():
    """Test joining an existing pit"""
    # First create a pit
    creator_client = get_socket_io_client()
    creator_client.emit("message", {"action": "create_pit"})
    
    received = creator_client.get_received()
    pit_id = None
    for event in received:
        if event["name"] == "pit_created":
            pit_id = event["args"][0]["pit_id"]
            break
    
    assert pit_id is not None
    
    # Now join with another client
    joiner_client = get_socket_io_client()
    joiner_client.emit("message", {"action": "join_pit", "pit_id": pit_id})
    
    # Check joiner received confirmation
    joiner_received = joiner_client.get_received()
    pit_joined_event = None
    for event in joiner_received:
        if event["name"] == "pit_joined":
            pit_joined_event = event
            break
    
    assert pit_joined_event is not None
    assert pit_joined_event["args"][0]["pit_id"] == pit_id
    
    # Check creator received new_room_member notification
    creator_received = creator_client.get_received()
    new_member_event = None
    for event in creator_received:
        if event["name"] == "new_room_member":
            new_member_event = event
            break
    
    assert new_member_event is not None
    assert "new_peer_id" in new_member_event["args"][0]


def test_leave_pit():
    """Test leaving a pit"""
    # Create pit and join
    client = get_socket_io_client()
    client.emit("message", {"action": "create_pit"})
    
    # Clear received messages
    client.get_received()
    
    # Leave pit
    client.emit("message", {"action": "leave_pit"})
    
    # Check for pit_left confirmation
    received = client.get_received()
    pit_left_event = None
    for event in received:
        if event["name"] == "pit_left":
            pit_left_event = event
            break
    
    assert pit_left_event is not None
    assert "pit_id" in pit_left_event["args"][0]


def test_webrtc_offer():
    """Test WebRTC offer exchange"""
    # Create pit with two clients
    client1 = get_socket_io_client()
    client2 = get_socket_io_client()
    
    # Client1 creates pit
    client1.emit("message", {"action": "create_pit"})
    received = client1.get_received()
    pit_id = None
    for event in received:
        if event["name"] == "pit_created":
            pit_id = event["args"][0]["pit_id"]
            break
    
    # Client2 joins pit
    client2.emit("message", {"action": "join_pit", "pit_id": pit_id})
    
    # Get the new_room_member event to find client2's session ID
    client1_received = client1.get_received()
    client2_session_id = None
    for event in client1_received:
        if event["name"] == "new_room_member":
            client2_session_id = event["args"][0]["new_peer_id"]
            break
    
    # Clear remaining messages
    client2.get_received()
    
    # Client1 sends offer to Client2
    offer_payload = {"type": "offer", "sdp": "fake_sdp"}
    client1.emit("message", {
        "action": "send_offer",
        "to_peer_id": client2_session_id,
        "payload": offer_payload
    })
    
    # Check Client2 received the offer
    received = client2.get_received()
    offer_event = None
    for event in received:
        if event["name"] == "newOffer":
            offer_event = event
            break
    
    assert offer_event is not None
    # Note: fromPeerId should be client1's session ID, which we can get from the server
    assert offer_event["args"][0]["offer"] == offer_payload


def get_flask_client():
    return app.test_client()


def get_socket_io_client():
    flask_test_client = get_flask_client()
    return socketio.test_client(app, flask_test_client=flask_test_client)
