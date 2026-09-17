from fastapi import FastAPI,UploadFile,File,HTTPException

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status":"ok"}

@app.post("/api/v1/rooms/analyze")
async def analyze_room(image:UploadFile=File(...)):

    if image.content_type not in ["image/jpeg","image/png"]:
        raise HTTPException(status_code=400,detail="Only jpeg,jpg and png images are allowed")
    return {
        "filename":image.filename,
        "content_type":image.content_type
        }