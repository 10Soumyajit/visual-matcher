import streamlit as st
import torch
from PIL import Image
import os
import json
from transformers import CLIPProcessor, CLIPModel
import numpy as np
import io
import requests
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Visual Product Matcher",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'model' not in st.session_state:
    st.session_state.model = None
if 'processor' not in st.session_state:
    st.session_state.processor = None

@st.cache_resource(show_spinner="Loading CLIP model...")
def load_model():
    try:
        # Force CPU to avoid GPU memory issues in cloud deployment
        device = "cpu"
        model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32",
            local_files_only=False,
            resume_download=True,
            low_cpu_mem_usage=True,
            torch_dtype=torch.float32
        ).to(device)
        processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32",
            local_files_only=False,
            resume_download=True
        )
        return model, processor, device
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None, None

@st.cache_data
def load_product_data():
    try:
        data_path = Path("data/products_metadata.csv")
        if not data_path.exists():
            st.error("Products metadata file not found!")
            return {}
        
        products_metadata = {}
        with open(data_path, 'r', encoding='utf-8') as f:
            next(f)  # Skip header
            for line in f:
                try:
                    pid, title, desc = line.strip().split(',', 2)
                    products_metadata[pid] = {'title': title, 'description': desc}
                except ValueError:
                    continue  # Skip malformed lines
        return products_metadata
    except Exception as e:
        st.error(f"Error loading product data: {str(e)}")
        return {}

@st.cache_data
def compute_similarity(_image_features, _text_features):
    with torch.no_grad():
        image_features = _image_features / _image_features.norm(dim=-1, keepdim=True)
        text_features = _text_features / _text_features.norm(dim=-1, keepdim=True)
        similarity = torch.matmul(image_features, text_features.T)
    return similarity.cpu().numpy()

def main():
    st.title("Visual Product Matcher 🔍")
    st.write("Upload an image to find similar products!")

    # Load model and data
    try:
        if st.session_state.model is None:
            model, processor, device = load_model()
            if model is None:
                st.error("Failed to load the model. Please try again.")
                return
            st.session_state.model = model
            st.session_state.processor = processor
            st.session_state.device = device
        
        products_metadata = load_product_data()
        if not products_metadata:
            st.error("No product data available.")
            return
        
        # File uploader
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            try:
                # Display uploaded image
                col1, col2 = st.columns(2)
                with col1:
                    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
                
                # Process image
                image = Image.open(uploaded_file).convert('RGB')
                image_inputs = st.session_state.processor(
                    images=image, 
                    return_tensors="pt"
                ).to(st.session_state.device)
                
                with torch.no_grad():
                    image_features = st.session_state.model.get_image_features(**image_inputs)
                
                # Process all product descriptions
                texts = [data['description'] for data in products_metadata.values()]
                text_inputs = st.session_state.processor(
                    text=texts,
                    padding=True,
                    truncation=True,
                    return_tensors="pt"
                ).to(st.session_state.device)
                
                with torch.no_grad():
                    text_features = st.session_state.model.get_text_features(**text_inputs)
                
                # Calculate similarities
                similarities = compute_similarity(image_features, text_features)
                
                # Get top 5 matches
                top_k = min(5, len(products_metadata))
                top_indices = np.argsort(similarities[0])[-top_k:][::-1]
                
                with col2:
                    st.subheader("Top Matches:")
                    for idx in top_indices:
                        pid = list(products_metadata.keys())[idx]
                        product = products_metadata[pid]
                        similarity_score = similarities[0][idx]
                        
                        st.write(f"**{product['title']}**")
                        st.write(f"Similarity: {similarity_score:.2%}")
                        
                        # Display product image if available
                        product_img_path = Path(f"data/product_images/{pid}.jpg")
                        if product_img_path.exists():
                            st.image(str(product_img_path), width=200)
                        st.write("---")
            
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()