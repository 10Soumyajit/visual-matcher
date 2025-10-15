---
title: Visual Product Matcher
emoji: 🔍
colorFrom: purple
colorTo: blue
sdk: docker
sdk_version: 3.0.0
app_file: app.py
pinned: false
---

# Visual Matcher

A Flask-based web application that uses CLIP (Contrastive Language-Image Pre-Training) to perform visual similarity search across a product database. The application allows users to find visually similar products by either uploading an image or providing an image URL.

## Features

- Image similarity search using CLIP model
- Support for both file upload and image URL input
- Product categorization and metadata display
- RESTful API endpoints for image processing
- Efficient in-memory similarity computation
- Secure image serving with path validation

## Tech Stack

- **Backend**: Python 3.x, Flask
- **ML Model**: CLIP (OpenAI's clip-vit-base-patch32)
- **Database**: SQLite3
- **Image Processing**: Pillow
- **ML Framework**: PyTorch, Transformers
- **WSGI Server**: Waitress

## Project Structure

```
visual-matcher/
├── app.py                 # Main Flask application
├── build_index.py         # Script to build product embeddings database
├── server.py              # Production server configuration
├── requirements.txt       # Python dependencies
├── data/
│   ├── products.db        # SQLite database with product embeddings
│   ├── products_metadata.csv  # Product metadata
│   └── product_images/    # Product image files
├── static/
│   ├── uploads/          # Temporary storage for uploaded query images
│   └── main.js          # Frontend JavaScript
└── templates/
    └── index.html       # Main application template
```

## Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Build the product database:
   ```bash
   python build_index.py
   ```

## Running the Application

### Development Mode
```bash
python app.py
```

### Production Mode
```bash
python server.py
```
or
```bash
waitress-serve --host=0.0.0.0 --port=10000 --call app:app
```

The application will be available at http://localhost:5000 (development) or http://localhost:10000 (production).

## API Endpoints

### `GET /`
- Returns the main application page

### `POST /upload`
- Accepts form data with either:
  - `file`: An image file upload
  - `image_url`: URL of an image
- Returns JSON with similar products:
  ```json
  {
    "query_image": "/static/uploads/q_123.jpg",
    "results": [
      {
        "id": 1234,
        "name": "Product Name",
        "category": "Category",
        "image_url": "/product_image?path=...",
        "score": 0.95
      }
    ]
  }
  ```

### `GET /product_image`
- Parameters:
  - `path`: Path to the product image
- Returns the product image file with proper content type

## Security

- Input validation for image uploads and URLs
- Path traversal prevention in image serving
- Secure file handling and storage
- CORS and content type validation

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
