# Visual Product Matcher

This Space demonstrates a visual similarity search system for fashion products using the CLIP model.

## Features

- Upload your own image or provide an image URL
- Find visually similar products from the database
- View product details and metadata
- Real-time image processing and similarity search

## How to Use

1. Open the web interface
2. Choose one of two options:
   - Upload an image file from your device
   - Enter the URL of an image
3. Click "Search" to find similar products
4. View the results with similarity scores and product details

## Technical Details

- **Model**: OpenAI's CLIP (clip-vit-base-patch32)
- **Backend**: Flask + Waitress
- **Image Processing**: PIL
- **Similarity Search**: Cosine similarity on CLIP embeddings
- **Database**: SQLite with pre-computed embeddings

## Example Queries

Try searching with:
- Pictures of shoes
- Clothing items
- Fashion accessories

## License
MIT License