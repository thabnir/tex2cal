import json
import requests

#TODO have a thing that turns pdf into image
#TODO: finetune the model

url = "https://proxy.tune.app/chat/completions"
image_url = "https://d2e931syjhr5o9.cloudfront.net/playground_uploads/e172d34b-97ef-4499-8e43-5c6c18995ad4"

def image_to_text(image_url):
    headers = {
        #"Authorization": "sk-tune-ihOAWpXjjsdEv4XeD6D6LA0joqJLU80SAEm",
        "Authorization: sk-tune-Y9MwiV5Z1gjHPYlrqmDUHZt7GCSfgsxNsBd"
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

deadlines = image_to_text(image_url)
# Print the extracted deadlines
for deadline in deadlines:
    print(deadline)
