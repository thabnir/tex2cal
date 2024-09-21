import pytesseract
from google.cloud import vision

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

import base64
from PIL import Image
import io

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        # Read the image file in binary mode
        image_data = image_file.read()
        # Encode the binary data to base64
        base64_encoded_data = base64.b64encode(image_data)
        # Convert bytes to string
        base64_string = base64_encoded_data.decode('utf-8')
        return "data:image/png;base64,"+base64_string

def detect_text(path):
    """Detects text in the file."""
    #from google.cloud import vision

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print("Texts:")

    for text in texts:
        print(f'\n"{text.description}"')

        vertices = [
            f"({vertex.x},{vertex.y})" for vertex in text.bounding_poly.vertices
        ]

        print("bounds: {}".format(",".join(vertices)))

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )

import json
import requests

#TODO have a thing that turns pdf into image
#TODO: finetune the model

url = "https://proxy.tune.app/chat/completions"
image_url = "https://d2e931syjhr5o9.cloudfront.net/playground_uploads/e172d34b-97ef-4499-8e43-5c6c18995ad4"


def image_to_text(image_url):
    stream = False
    url = "https://proxy.tune.app/chat/completions"
    headers = {
        "Authorization": "sk-tune-Y9MwiV5Z1gjHPYlrqmDUHZt7GCSfgsxNsBd",
        "Content-Type": "application/json",
    }
    data = {
        "temperature": 0,
        "messages":  [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the events and the relevant time information from an image into the following format:\n\"[event]: [dd/mm/yyyy]: [time start] to [time end]\"\n\nPlease be descriptive about the name of the 'event' and include specific time information if it is included in the image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        "model": "openai/gpt-4o",
        "stream": stream,
        "frequency_penalty":  0,
        "max_tokens": 729
    }
    response = requests.post(url, headers=headers, json=data)
    if stream:
        for line in response.iter_lines():
            if line:
                l = line[6:]
                if l != b'[DONE]':
                    pass
                    #print(json.loads(l))
    else:
        pass
        #print(response.json())

    #print(response.json())

    deadlines = response.json()['choices'][0]['message']['content'].split('\n')[0:-1]
    return deadlines


image_url = "https://d2e931syjhr5o9.cloudfront.net/playground_uploads/0193c73f-8e4c-4dfe-a940-14ba635c023b"
image_url = image_to_base64("pennapps_friday.png")
#print(image_url)
deadlines = image_to_text(image_url)
# Print the extracted deadlines
for deadline in deadlines:
    print(deadline)
#print(image_to_text("blackboard_2.jpg"))
#detect_text("Detailed_Schedule_COMP310-F2024-23-8.jpg")
