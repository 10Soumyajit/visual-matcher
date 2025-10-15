import os
import pandas as pd
import requests
from pathlib import Path
import build_index

def download_sample_images():
    """Download sample product images from a public URL"""
    # Create directories if they don't exist
    Path("data/product_images").mkdir(parents=True, exist_ok=True)
    Path("static/uploads").mkdir(parents=True, exist_ok=True)

    # Read product metadata
    df = pd.read_csv("data/products_metadata.csv")
    
    # Example image URL pattern - replace with your actual image source
    base_url = "https://raw.githubusercontent.com/10Soumyajit/sample-product-images/main/"
    
    for _, row in df.iterrows():
        image_id = str(row['id'])
        image_path = f"data/product_images/{image_id}.jpg"
        
        if not os.path.exists(image_path):
            try:
                response = requests.get(f"{base_url}{image_id}.jpg")
                if response.status_code == 200:
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded {image_id}.jpg")
            except Exception as e:
                print(f"Error downloading {image_id}.jpg: {e}")

def setup():
    """Setup the application data"""
    print("Setting up sample data...")
    download_sample_images()
    print("Building product index...")
    build_index.main()
    print("Setup complete!")

if __name__ == "__main__":
    setup()