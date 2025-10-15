# app.py (Updated to use transformers directly)
import os
import io
import sqlite3
import time
import requests
import torch
import numpy as np
from flask import Flask, request, render_template, jsonify, send_from_directory
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# ---- Configuration ----
UPLOAD_DIR = "static/uploads"
DB = "data/products.db"
MODEL_ID = "openai/clip-vit-base-patch32"

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")

# ---- Load model ----
print("Loading CLIP model...")
import sys
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

try:
    device_type = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device_type}")
    print(f"Cache directory: {os.getenv('TRANSFORMERS_CACHE', 'default cache location')}")
    
    model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32', 
                                    local_files_only=False, 
                                    cache_dir='/cache')
    processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32',
                                            local_files_only=False,
                                            cache_dir='/cache')
    print(f"Model loaded successfully on {device_type}.")
except Exception as e:
    print(f"Error loading model: {str(e)}", file=sys.stderr)
    raise

# ---- Utility functions ----
def blob_to_np(blob):
    mem = io.BytesIO(blob)
    mem.seek(0)
    return np.load(mem, allow_pickle=False)

def load_indexed_products():
    """Load all product entries from DB (id, name, category, path, embedding)."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, name, category, image_path, embedding FROM products")
    rows = c.fetchall()
    conn.close()
    products = []
    for pid, name, category, image_path, emb_blob in rows:
        emb = blob_to_np(emb_blob)
        emb = emb / (np.linalg.norm(emb) + 1e-10)
        products.append({
            "id": pid,
            "name": name,
            "category": category,
            "image_path": image_path,
            "embedding": emb
        })
    return products

# Load all products into memory
products = load_indexed_products()
print(f"Loaded {len(products)} products from DB.")

def compute_similarities(query_emb, top_k=10):
    mats = np.stack([p["embedding"] for p in products], axis=0)
    q = query_emb / (np.linalg.norm(query_emb) + 1e-10)
    sims = mats @ q
    idxs = np.argsort(-sims)[:top_k]
    results = []
    for i in idxs:
        p = products[i]
        results.append({
            "id": p["id"],
            "name": p["name"],
            "category": p["category"],
            "image_path": p["image_path"],
            "score": float(sims[i])
        })
    return results

# ---- Routes ----
@app.route("/")
def index():
    return render_template("index.html")

def save_uploaded_file(file_storage):
    ts = int(time.time() * 1000)
    fname = f"q_{ts}_{file_storage.filename}"
    path = os.path.join(UPLOAD_DIR, fname)
    file_storage.save(path)
    return path, fname

def download_image_from_url(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        content_type = r.headers.get("content-type", "")
        if "image" not in content_type:
            raise ValueError("URL does not point to an image")
        ext = content_type.split("/")[-1].split(";")[0]
        if ext not in ["jpeg", "jpg", "png", "webp"]:
            ext = "jpg"
        ts = int(time.time() * 1000)
        fname = f"q_{ts}.{ext}"
        path = os.path.join(UPLOAD_DIR, fname)
        with open(path, "wb") as f:
            f.write(r.content)
        return path, fname
    except Exception as e:
        raise

@app.route("/upload", methods=["POST"])
def upload():
    try:
        if "file" in request.files and request.files["file"].filename != "":
            uploaded = request.files["file"]
            qpath, qname = save_uploaded_file(uploaded)
        elif request.form.get("image_url"):
            url = request.form.get("image_url")
            qpath, qname = download_image_from_url(url)
        else:
            return jsonify({"error": "No file or URL provided"}), 400

        img = Image.open(qpath).convert("RGB")
        # Process image through CLIP
        pixel_values = processor.feature_extractor(img, return_tensors="pt")["pixel_values"]
        if torch.cuda.is_available():
            pixel_values = pixel_values.cuda()
        # Get image features and normalize
        image_features = model.vision_model(pixel_values)[1]
        qemb = image_features.detach().cpu().numpy()[0]
        qemb = qemb / np.linalg.norm(qemb)
        results = compute_similarities(qemb, top_k=10)

        for r in results:
            r["image_url"] = f"/product_image?path={r['image_path']}"

        query_public_url = f"/static/uploads/{qname}"
        return jsonify({"query_image": query_public_url, "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/product_image")
def product_image():
    path = request.args.get("path")
    if not path:
        return "Missing path", 400
    safe_root = os.path.abspath("data/product_images")
    req_path = os.path.abspath(path)
    if not req_path.startswith(safe_root):
        return "Not allowed", 403
    directory, filename = os.path.split(req_path)
    return send_from_directory(directory, filename)

# ---- Run ----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
