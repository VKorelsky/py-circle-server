import pytest
from server.server import socketio, app


def test_join_pit():
    pit_id = "697d8c94-cee3-4a99-a3b6-b7cced7927fc"
    client = get_client(pit_id)

    assert client.is_connected()


def get_client(pit_id: str):
    return socketio.test_client(app, query_string=f"circleId={pit_id}")
