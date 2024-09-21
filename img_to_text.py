import pytesseract
from PIL import Image

def image_to_text(image_path):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

print(image_to_text("How-to-Create-Image-Inside-Text-3057872416.jpg"))