# Visual Product Matcher 🔍

This Space demonstrates a visual similarity search system for fashion products using CLIP (Contrastive Language-Image Pre-Training) model. The system helps users find visually similar fashion products from our curated database.

## 🌟 Features

- **Visual Search**: Upload images or provide URLs to find similar products
- **Pre-indexed Database**: Fast similarity search using pre-computed CLIP embeddings
- **Rich Metadata**: Detailed product information including category, type, and color
- **Real-time Processing**: Instant results using efficient image processing

## 🎯 How to Use

1. Visit the web interface
2. Choose your search method:
   - 📤 **Upload an Image**: Click "Choose File" to upload from your device
   - 🔗 **Image URL**: Paste a direct link to any fashion image
3. Click "Search" to discover similar products
4. Browse results sorted by similarity score

## 🛍️ Product Categories

Our database includes various fashion items:
- 👟 Footwear (Sports shoes, Casual shoes)
- 👕 Apparel (T-shirts, Shirts, Pants)
- 👜 Accessories

## 🔧 Technical Stack

- **ML Model**: OpenAI's CLIP (clip-vit-base-patch32)
- **Framework**: Flask with Waitress WSGI server
- **Image Processing**: PIL (Python Imaging Library)
- **Database**: SQLite3 with optimized embeddings
- **Deployment**: Docker container on Hugging Face Spaces

## 📝 Note

This demo uses a curated dataset of fashion products with pre-computed embeddings for optimal performance.

## 📜 License
MIT License