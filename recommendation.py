import os
import faiss
import numpy as np
import torch

from PIL import Image
from transformers import CLIPModel, CLIPProcessor
from ultralytics import YOLO

from database import SessionLocal
from models import FurnitureProduct

# 1. Load CLIP model

model_name = "openai/clip-vit-base-patch32"

processor = CLIPProcessor.from_pretrained(model_name)
model = CLIPModel.from_pretrained(model_name)
yolo_model = YOLO("yolo11n.pt")

# 2. Furniture catalog

db = SessionLocal()
products = db.query(FurnitureProduct).all()
db.close()

furniture_catalog = {}

for product in products:
    furniture_catalog[product.image_filename] = {
        "name": product.name,
        "category": product.category,
        "price": product.price
    }


# 3. Convert image to embedding

def get_embedding(image):

    if isinstance(image, str):
        image = Image.open(image)

    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():

        features = model.get_image_features(
            **inputs
        ).pooler_output

    return features


# 4. Build furniture embeddings


folder = "furniture_images"

embeddings = []
filenames = []

for filename in os.listdir(folder):

    image_path = os.path.join(
        folder,
        filename
    )

    embedding = get_embedding(image_path)

    embeddings.append(embedding)
    filenames.append(filename)


embeddings = torch.cat(embeddings)

embeddings = embeddings.numpy().astype("float32")


# 5. Create FAISS index

index = faiss.IndexFlatL2(512)
index.add(embeddings)


# 6. Find similar furniture


def find_similar_furniture(image, category):

    query_embedding = get_embedding(image)

    query_embedding = query_embedding.numpy().astype(
        "float32"
    )

    best_distance = None
    best_filename = None

    for i, filename in enumerate(filenames):

        product = furniture_catalog[filename]

        if product["category"] != category:
            continue

        product_embedding = embeddings[i:i + 1]

        distance = float(
            np.linalg.norm(
                query_embedding - product_embedding
            )
        )

        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_filename = filename

    if best_filename is None:
        return None

    product = furniture_catalog[best_filename]

    return {
        "name": product["name"],
        "category": product["category"],
        "price": product["price"],
        "distance": best_distance
    }

def analyze_room(image):

    results = yolo_model(image)

    detected_objects = []

    for box, class_id, confidence in zip(
        results[0].boxes.xyxy,
        results[0].boxes.cls,
        results[0].boxes.conf
    ):

        name = results[0].names[int(class_id)]

        x1, y1, x2, y2 = map(
            int,
            box.tolist()
        )

        cropped_object = image.crop(
            (x1, y1, x2, y2)
        )

        recommendation = find_similar_furniture(
        cropped_object,name)
        

        detected_objects.append({
            "object": name,
            "confidence": round(
                confidence.item(),
                2
            ),
            "recommendation": recommendation
        })

    return detected_objects

if __name__ == "__main__":
    image = Image.open("test_room.jpg.jpeg")
    results = analyze_room(image)

    print(results)