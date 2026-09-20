from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image, UnidentifiedImageError

from recommendation import analyze_room

from database import SessionLocal
from models import Room, DetectedObject


app = FastAPI()


@app.get("/health")
def health_check():

    return {
        "status": "ok"
    }


@app.post("/api/v1/rooms/analyze")
async def analyze_room_api(
    image: UploadFile = File(...)
):

    # Check file type
    if image.content_type not in [
        "image/jpeg",
        "image/png"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG images are allowed"
        )

    # Read uploaded file
    image_data = await image.read()

    # Validate actual image
    try:

        room_image = Image.open(
            BytesIO(image_data)
        )

        room_image.load()

        room_image = room_image.convert("RGB")

    except UnidentifiedImageError:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image"
        )

    # Analyze room
    results = analyze_room(
        room_image
    )

    db = SessionLocal()

    room = Room( image_filename=image.filename)
    db.add(room)
    db.commit()
    db.refresh(room)

    for detection in results:

        recommendation = detection["recommendation"]

        detected_object = DetectedObject(
            room_id=room.id,
            object_name=detection["object"],
            confidence=detection["confidence"],
            recommendation_name=(
                recommendation["name"]
                if recommendation
                else None
            ),
            recommendation_price=(
                recommendation["price"]
                if recommendation
                else None
            )
        )

        db.add(detected_object)

    db.commit()
    room_id = room.id
    db.close()

    return {
    "room_id": room.id,
    "filename": image.filename,
    "detections": results
}