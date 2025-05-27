from server.server import socketio, app

def test_create_pit():
    client = get_flask_client()
    # POST request to create a pit on the server
    res = client.post("/pit/create")
    assert res.status_code == 200
    pit_id = res.json["pitId"]
    
    get_res = client.get(f"/pit/{pit_id}")
    assert get_res.status_code == 200
    assert get_res.json["pitId"] == pit_id



def test_join_pit():
    pit_id = "697d8c94-cee3-4a99-a3b6-b7cced7927fc"
    client = get_socket_io_client(pit_id)
    

    assert client.is_connected()


def get_flask_client():
    return app.test_client()


def get_socket_io_client(pit_id: str):
    flask_test_client = get_flask_client()
    return socketio.test_client(
        app, query_string=f"circleId={pit_id}", flask_test_client=flask_test_client
    )
