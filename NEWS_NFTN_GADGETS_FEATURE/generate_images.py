from PIL import Image, ImageDraw, ImageFont
import os

def create_image(filename, text, size=(200, 200), bg_color='white', text_color='black'):
    # Create a new image with a white background
    image = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(image)
    
    # Add text to the image
    text_width = draw.textlength(text, font=None)
    text_x = (size[0] - text_width) // 2
    text_y = size[1] // 2
    draw.text((text_x, text_y), text, fill=text_color)
    
    # Save the image
    image.save(f'static/images/{filename}')

# Create directory if it doesn't exist
os.makedirs('static/images', exist_ok=True)

# Create badge images
badges = [
    ('safety_shield.png', 'Safety Shield'),
    ('golden_trophy.png', 'Golden Trophy'),
    ('rising_star.png', 'Rising Star'),
    ('guardian_angel.png', 'Guardian Angel')
]

# Create gadget images
gadgets = [
    ('alarm.jpg', 'Safety Alarm'),
    ('watch.jpg', 'GPS Watch'),
    ('spray.jpg', 'Pepper Spray'),
    ('keychain.jpg', 'Safety Keychain')
]

# Generate all images
for filename, text in badges + gadgets:
    create_image(filename, text)

print("All images have been generated successfully!")
