import base64
from PIL import Image
import io
import json
import requests

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        # Read the image file in binary mode
        image_data = image_file.read()
        # Encode the binary data to base64
        base64_encoded_data = base64.b64encode(image_data)
        # Convert bytes to string
        base64_string = base64_encoded_data.decode('utf-8')
        return "data:image/png;base64,"+base64_string


def base64_to_text(image_url):
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

def image_to_text(img_path):
    img_64 = image_to_base64(img_path)
    deadlines = base64_to_text(img_64)

    # Print the extracted deadlines
    list_of_deadlines = []
    for deadline in deadlines:
        list_of_deadlines.append(deadline)
        print(deadline)

    return list_of_deadlines

image_to_text("Weixin Image_20240921170839.jpg")



