# build_index.py  — Updated for metadata CSV
import os
import io
import sqlite3
import numpy as np
import pandas as pd
from PIL import Image
from sentence_transformers import SentenceTransformer

# ---- Config ----
DB_PATH = "data/products.db"  # Store in data directory
IMAGE_DIR = "data/product_images"
META_CSV = "data/products_metadata.csv"
MODEL_NAME = "clip-ViT-B-32"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# ---- Helpers ----
def create_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            image_path TEXT,
            embedding BLOB
        )
    """)
    conn.commit()
    conn.close()


def np_to_blob(arr: np.ndarray) -> bytes:
    """Serialize numpy array as binary blob for SQLite."""
    mem = io.BytesIO()
    np.save(mem, arr, allow_pickle=False)
    return mem.getvalue()


# ---- Main indexing ----
def build_index():
    # Load metadata
    meta = pd.read_csv(META_CSV)
    if "ProductId" not in meta.columns:
        raise ValueError("Metadata CSV must contain a 'ProductId' column")
    # Rename ProductId to id for consistency
    meta = meta.rename(columns={"ProductId": "id"})

    # Load CLIP model
    print("Loading CLIP model...")
    import torch
    from PIL import Image
    from transformers import CLIPProcessor, CLIPModel
    device_type = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
    processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')
    print(f"Model loaded on {device_type}.")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    inserted = 0
    skipped = 0

    for _, row in meta.iterrows():
        pid = int(row["id"])
        name = str(row["ProductTitle"])  # Use ProductTitle from CSV
        category = str(row["Category"])  # Use Category from CSV
        # Image filename may be id.jpg or have extension in CSV
        possible_names = [
            f"{pid}.jpg",
            f"{pid}.jpeg",
            f"{pid}.png",
            str(row.get("image", ""))  # optional column
        ]
        img_path = None
        for p in possible_names:
            if not p or p == "nan":
                continue
            full = os.path.join(IMAGE_DIR, p)
            if os.path.exists(full):
                img_path = full
                break

        if not img_path:
            print(f"⚠️  Image not found for ID {pid} ({name}); skipped.")
            skipped += 1
            continue

        try:
            img = Image.open(img_path).convert("RGB")
            # Process image through CLIP
            pixel_values = processor.feature_extractor(img, return_tensors="pt")["pixel_values"]
            if torch.cuda.is_available():
                pixel_values = pixel_values.cuda()
            image_features = model.vision_model(pixel_values)[1]
            # Convert to numpy array and normalize
            emb = image_features.detach().cpu().numpy()[0]
            emb = emb / np.linalg.norm(emb)
            blob = np_to_blob(emb)
            c.execute(
                "INSERT OR REPLACE INTO products (id, name, category, image_path, embedding) VALUES (?, ?, ?, ?, ?)",
                (pid, name, category, img_path, sqlite3.Binary(blob))
            )
            inserted += 1
            print(f"✅ Indexed {pid} | {name} | {category}")
        except Exception as e:
            print(f"❌ Failed to process {pid}: {e}")
            skipped += 1

    conn.commit()
    conn.close()
    print(f"\nDone. Indexed {inserted} products, skipped {skipped}.")


if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    create_db()
    build_index()
