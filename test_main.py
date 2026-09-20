from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }

def test_reject_pdf_file():
    response = client.post(
        "/api/v1/rooms/analyze",
        files={
            "image": (
                "test.pdf",
                b"fake pdf content",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only JPEG and PNG images are allowed"

def test_reject_invalid_image():
    response = client.post(
        "/api/v1/rooms/analyze",
        files={
            "image": (
                "fake.jpg",
                b"this is not a real image",
                "image/jpeg"
            )
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded file is not a valid image"

def test_analyze_room():
    with open("test_room.jpg.jpeg", "rb") as image_file:

        response = client.post(
            "/api/v1/rooms/analyze",
            files={
                "image": (
                    "test_room.jpg.jpeg",
                    image_file,
                    "image/jpeg"
                )
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert "room_id" in data
    assert "filename" in data
    assert "detections" in data

    assert len(data["detections"]) > 0