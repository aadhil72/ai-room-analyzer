from fastapi import FastAPI,UploadFile,File

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status":"ok"}

@app.post("/api/v1/rooms/analyze")
async def analyze_room(image:UploadFile=File(...)):
    return {"filename":image.filename}