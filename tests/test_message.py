
import pytest
from fastapi.testclient import TestClient

from task_api.main import app
from task_api import storage

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_messages():
    storage.messages.clear()
    storage.next_message_id = 1


def test_create_message():
    response = client.post(
        "/api/v1/messages",
        json={"role": "user", "content": "Hello"}
    )

    assert response.status_code == 201
    assert response.json()["content"] == "Hello"
    assert response.json()["id"] == 1


def test_reject_empty_message():
    response = client.post(
        "/api/v1/messages",
        json={"role": "user", "content": "   "}
    )

    assert response.status_code == 422


def test_list_messages_with_pagination_and_role():
    client.post("/api/v1/messages", json={
        "role": "user", "content": "First"
    })
    client.post("/api/v1/messages", json={
        "role": "assistant", "content": "Second"
    })
    client.post("/api/v1/messages", json={
        "role": "user", "content": "Third"
    })

    response = client.get(
        "/api/v1/messages?limit=1&offset=1&role=user"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["content"] == "Third"


def test_retrieve_existing_message():
    created = client.post(
        "/api/v1/messages",
        json={"role": "user", "content": "Hello"}
    )

    message_id = created.json()["id"]
    response = client.get(f"/api/v1/messages/{message_id}")

    assert response.status_code == 200
    assert response.json()["content"] == "Hello"


def test_missing_message_returns_404():
    response = client.get("/api/v1/messages/999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "message_not_found"


def test_update_message():
    created = client.post(
        "/api/v1/messages",
        json={"role": "user", "content": "Old content"}
    )

    message_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/messages/{message_id}",
        json={"content": "Updated content"}
    )

    assert response.status_code == 200
    assert response.json()["content"] == "Updated content"


def test_delete_message():
    created = client.post(
        "/api/v1/messages",
        json={"role": "user", "content": "Delete me"}
    )

    message_id = created.json()["id"]

    response = client.delete(f"/api/v1/messages/{message_id}")

    assert response.status_code == 204
    assert response.content == b""

    verify = client.get(f"/api/v1/messages/{message_id}")
    assert verify.status_code == 404
