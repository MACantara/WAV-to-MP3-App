from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a new image with a white background
    size = (256, 256)
    image = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a circle background
    circle_bbox = (20, 20, 236, 236)
    draw.ellipse(circle_bbox, fill='#2196F3')
    
    # Draw the text
    text = "WAV\nMP3"
    try:
        # Try to use Arial font, fall back to default if not available
        font = ImageFont.truetype("arial.ttf", 72)
    except:
        font = ImageFont.load_default()
    
    # Center the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) / 2
    y = (size[1] - text_height) / 2
    
    # Draw the text in white
    draw.text((x, y), text, fill='white', font=font, align='center')
    
    # Save as ICO
    image.save('app_icon.ico', format='ICO', sizes=[(256, 256)])

if __name__ == '__main__':
    create_icon()
