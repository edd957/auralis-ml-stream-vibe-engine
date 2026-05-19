from fastapi.testclient import TestClient

from auralis_ml.api.app import create_app


def test_chat_ingest_and_energy_endpoint() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/chat",
        json={"author": "viewer", "message": "this is fire, go faster", "platform": "demo"},
    )
    assert response.status_code == 200

    energy = client.get("/energy")
    assert energy.status_code == 200
    assert energy.json()["message_count"] == 1


def test_batch_ingest_and_profile_endpoint() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/chat/batch",
        json=[
            {"author": "viewer1", "message": "wild drop", "platform": "demo"},
            {"author": "viewer2", "message": "bass is fire", "platform": "demo"},
        ],
    )
    assert response.status_code == 200
    assert len(response.json()) == 2

    profile = client.get("/engine/profile")
    assert profile.status_code == 200
    assert profile.json()["name"] in {"cooldown", "steady", "lift", "surge"}
