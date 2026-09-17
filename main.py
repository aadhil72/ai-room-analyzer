from fastapi import FastAPI,UploadFile,File,HTTPException
from PIL import Image,UnidentifiedImageError
from io import BytesIO

app = FastAPI()

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

    return {
        "filename":image.filename,
        "content_type":image.content_type,
        "format":room_image.format,
        "size":room_image.size,
        "mode":room_image.mode
        }