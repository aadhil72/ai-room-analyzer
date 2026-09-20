# AI Room Analyzer & Furniture Recommendation API

A beginner-friendly FastAPI project that analyzes a room image, detects furniture with YOLO, compares detected objects with a small furniture catalog using CLIP embeddings, and stores the analysis in MySQL.

The project is intentionally small and focused: it demonstrates an end-to-end AI API without adding unnecessary features.

## What it does

1. Accepts a JPEG or PNG room image.
2. Detects objects such as chairs, beds, and tables with YOLO11.
3. Creates CLIP embeddings for detected object crops and catalog images.
4. Finds the closest catalog item in the same category using FAISS/Euclidean distance.
5. Saves the room and its detected objects in MySQL.
6. Returns the detections and recommendations as JSON.

## Tech stack

- Python 3.11
- FastAPI and Uvicorn
- Ultralytics YOLO11
- Hugging Face CLIP, PyTorch, NumPy, and FAISS
- MySQL, SQLAlchemy, and PyMySQL
- Docker and pytest

## Project layout

```text
main.py                 FastAPI routes and upload validation
recommendation.py       YOLO detection and CLIP/FAISS matching
database.py             MySQL connection setup
models.py               SQLAlchemy models
create_tables.py        Creates the database tables
seed_database.py        Adds the starter furniture catalog records
furniture_images/       Versioned catalog images used for recommendations
test_main.py            API tests
```

## Prerequisites

- Python 3.11
- MySQL Server 8 (or compatible)
- Git
- Docker Desktop (optional, for the container workflow)

## Local setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a MySQL database:

```sql
CREATE DATABASE room_analyzer;
```

Copy `.env.example` to `.env` and enter your local MySQL password. The expected variables are:

```env
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=room_analyzer
```

Create the tables and seed the starter products:

```powershell
python create_tables.py
python seed_database.py
```

Then start the API:

```powershell
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## Docker

Build the image from the project folder:

```powershell
docker build -t ai-room-analyzer .
```

Run it with a reachable MySQL instance. On Windows with MySQL running on the host, use `host.docker.internal` for `DB_HOST`:

```powershell
docker run --rm -p 8000:8000 `
  -e DB_USER=root `
  -e DB_PASSWORD=your_mysql_password `
  -e DB_HOST=host.docker.internal `
  -e DB_PORT=3306 `
  -e DB_NAME=room_analyzer `
  ai-room-analyzer
```

Run `python create_tables.py` and `python seed_database.py` once against that MySQL database before calling the analysis route. The first model load may download the YOLO and CLIP weights if they are not already cached.

## API usage

Health check:

```powershell
curl.exe http://localhost:8000/health
```

Analyze a room image:

```powershell
curl.exe -X POST "http://localhost:8000/api/v1/rooms/analyze" -F "image=@test_room.jpg.jpeg"
```

Example response:

```json
{
  "room_id": 5,
  "filename": "test_room.jpg.jpeg",
  "detections": [
    {
      "object": "chair",
      "confidence": 0.9,
      "recommendation": {
        "name": "Modern Wooden Chair",
        "category": "chair",
        "price": 4999,
        "distance": 8.260498046875
      }
    },
    {
      "object": "bed",
      "confidence": 0.69,
      "recommendation": {
        "name": "King Size Bed",
        "category": "bed",
        "price": 19999,
        "distance": 9.57346248626709
      }
    }
  ]
}
```

Only `image/jpeg` and `image/png` uploads are accepted. Invalid image content returns HTTP 400.

## Architecture

```text
Room image
    |
    v
FastAPI upload validation
    |
    v
YOLO11 object detection --> crop each detected object
    |                                |
    |                                v
    |                       CLIP image embeddings
    |                                |
    v                                v
MySQL room/detection records <-- category-matched catalog recommendation
    |
    v
JSON response
```

The `furniture_images/` folder is intentionally committed because it is the small, required reference catalog. Downloaded YOLO weight files (`*.pt`), local credentials, and temporary test images are excluded from Git.

## Tests

With MySQL configured and the starter catalog seeded, run:

```powershell
pytest -q
```

The test suite checks the health endpoint, rejects non-image and corrupt uploads, and exercises a real image-analysis request.

## Notes

- Recommendation distance is a similarity signal, not a price or quality score; lower is closer.
- The starter seed script inserts its five catalog records each time it is run. For a fresh database, run it once.
- This project is intended for learning and as a portfolio foundation; production deployment would need authentication, migrations, logging, and background model loading.
