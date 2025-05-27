import uuid
from server.server import app, socketio

def test_create_circle():
    client = socketio.test_client(app)
    response = client.get_received()
    assert len(response) == 0  # No messages received yet
    
    # Test HTTP endpoint
    with app.test_client() as http_client:
        response = http_client.post("/circle/new")
        assert response.status_code == 200
        data = response.get_json()
        assert "circle_id" in data
        circle_id = uuid.UUID(data["circle_id"])
        
        # Test socket connection to the new circle
        client.connect(app, query_string=f"circleId={circle_id}")
        response = client.get_received()
        assert len(response) == 0  # No messages on connect

