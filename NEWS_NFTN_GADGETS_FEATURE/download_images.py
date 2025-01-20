import requests
from PIL import Image
from io import BytesIO
import os

# Create the images directory if it doesn't exist
os.makedirs('static/images', exist_ok=True)

# Image URLs and their corresponding filenames
images = {
    'safety_shield.png': 'https://img.freepik.com/premium-photo/shield-with-shield-that-says-god-it_1172671-19684.jpg',
    'golden_trophy.png': 'https://img.freepik.com/premium-photo/shield-with-star-it-that-says-star_1172671-15912.jpg',
    'rising_star.png': 'https://img.freepik.com/premium-photo/shield-with-star-it-that-says-star_1172671-19898.jpg',
    'guardian_angel.png': 'https://img.freepik.com/premium-photo/shield-with-star-it-that-says-shield_1172671-13009.jpg'
}

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def download_and_save_image(url, filename):
    try:
        # Download the image
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Open the image using PIL
        img = Image.open(BytesIO(response.content))
        
        # Resize the image to a consistent size (e.g., 200x200 pixels)
        img = img.resize((200, 200), Image.Resampling.LANCZOS)
        
        # Save the image
        img.save(f'static/images/{filename}')
        print(f"Successfully downloaded and saved {filename}")
        
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")

# Download each image
for filename, url in images.items():
    download_and_save_image(url, filename)

print("Image download process completed!")
