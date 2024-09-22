
import speech_recognition as sr

#filename = "audio_test.wav"

def speech_to_txt(filename):
    r = sr.Recognizer()

    with sr.AudioFile(filename) as source:
        # load audio to memory
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data)
        return text

print(speech_to_txt("audio_test.wav"))




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
