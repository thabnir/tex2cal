import json
import requests
import os

#Various uses: take a picture of a physical calendar and convert the picture to Google calendar events

# poppler_path = r"C:\Users\Reyna\Downloads\Release-24.07.0-0\poppler-24.07.0\Library\bin"
# #TODO: finetune the model

# # TODO: For any image, remove all irrelevant information and keep only the deadlines -> maybe help improve performance???

# pdf_path = "pdf"
# img_path = "images"

# def pdf_to_img(pdf_path, img_path):
#     if not os.path.exists(img_path):
#         os.makedirs(img_path)  

#     for filename in os.listdir(pdf_path):
#         if filename.endswith('.pdf'):
#             pdf_path = os.path.join(pdf_path, filename)  # Get the full path of the PDF file
#             output_path = os.path.join(img_path, f'{os.path.splitext(filename)[0]}.jpg')  # Construct the output image path

#             try:
#                 images = convert_from_path(pdf_path, poppler_path = poppler_path)
#                 for i, img in enumerate(images):
#                     img_path = f'{output_path[:-4]}_{i}.jpg' if i > 0 else output_path  # Add index to output image path if multiple pages
#                     img.save(img_path, 'JPEG')

#             except Exception as e:
#                 print(f'Error converting {pdf_path}: {e}')

#             else:
#                 print(f'Successfully converted {pdf_path} to {output_path}')

# # pdf_to_img(pdf_path, img_path)

# #TODO: make this accept local image paths
# #TODO: make this accept multiple images
url = "https://proxy.tune.app/chat/completions"
image_url = "https://d2e931syjhr5o9.cloudfront.net/playground_uploads/e172d34b-97ef-4499-8e43-5c6c18995ad4"

def image_to_text(image_url):
    headers = {
        "Authorization": "sk-tune-ihOAWpXjjsdEv4XeD6D6LA0joqJLU80SAEm",
        "Content-Type": "application/json",
        "X-Org-Id": "8dfdb00c-7f43-45fe-abf9-477b7089962b"
    }
    data = {
        "temperature": 0.9,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract all the deadlines from the provided image and turn them into a txt file of the format DATE - TASK. Do not include any fancy formatting."
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
        "model": "mistral/pixtral-12B-2409",
        "stream": False,
        "frequency_penalty": 0.2,
        "max_tokens": 200
    }

    response = requests.post(url, headers=headers, json=data)
    #print(response.json())
        
    deadlines = response.json()['choices'][0]['message']['content'].split('\n')[1:-1]
    return deadlines

# deadlines = image_to_text(image_url)
# # Print the extracted deadlines
# for deadline in deadlines:
#     print(deadline)
