from fastapi import FastAPI,UploadFile,File,HTTPException
from PIL import Image,UnidentifiedImageError
from io import BytesIO
from ultralytics import YOLO

app = FastAPI()

model = YOLO("yolo11n.pt")

@app.get("/health")
def health_check():
    return {"status":"ok"}

@app.post("/api/v1/rooms/analyze")
async def analyze_room(image:UploadFile=File(...)):

    if image.content_type not in ["image/jpeg","image/png"]:
        raise HTTPException(status_code=400,detail="Only jpeg and png images are allowed")

    image_data = await image.read()
    try:
        room_image = Image.open(BytesIO(image_data))
        room_image.load()
        
    except UnidentifiedImageError:
        raise HTTPException(status_code=400,detail="The uploaded file is not a valid image")

    results = model(room_image)
    class_ids = results[0].boxes.cls
    confidences = results[0].boxes.conf
    detections = []
    for class_id,confidence in zip(class_ids,confidences):
        name = results[0].names[int(class_id)]
        detection = {
            "object":name,
            "confidence":round(confidence.item(),2)
        }
        detections.append(detection)
    return {
        "filename":image.filename,
        "detections":detections
        }

