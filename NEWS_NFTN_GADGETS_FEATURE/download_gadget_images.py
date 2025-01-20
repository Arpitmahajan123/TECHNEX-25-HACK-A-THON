import requests
from PIL import Image
from io import BytesIO
import os

# Create the images directory if it doesn't exist
os.makedirs('static/images', exist_ok=True)

# Image URLs for gadgets
images = {
    'alarm.jpg': 'https://img.freepik.com/free-photo/security-alarm-system_53876-139275.jpg',
    'watch.jpg': 'https://img.freepik.com/free-photo/modern-smartwatch-with-black-screen_23-2147835049.jpg',
    'spray.jpg': 'https://img.freepik.com/free-photo/pepper-spray-self-defense_23-2148383743.jpg',
    'keychain.jpg': 'https://img.freepik.com/free-photo/personal-alarm-keychain-self-defense_23-2148383744.jpg'
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
        
        # Resize the image to a consistent size
        img = img.resize((400, 300), Image.Resampling.LANCZOS)
        
        # Save the image
        img.save(f'static/images/{filename}', quality=90)
        print(f"Successfully downloaded and saved {filename}")
        
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")

# Download each image
for filename, url in images.items():
    download_and_save_image(url, filename)

print("Gadget image download process completed!")
