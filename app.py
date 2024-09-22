import base64
from io import BytesIO
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from fancy_ai import CalendarAssistant
from whispy import transcribe_audio
import os
from img_to_text import image_to_text, image_to_base64
from PIL import Image

app = Flask(__name__)

# Directory for uploaded images
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def hello_world():
    return render_template("index.html")


# Route for handling the form submission
@app.route("/submit", methods=["POST"])
def submit():
    uploaded_image = request.files.get("image", None)
    camera_image = request.form.get("camera_image", None)
    ocr_text = None
    if uploaded_image:
        # Handle image upload
        if uploaded_image.filename:
            filename = secure_filename(uploaded_image.filename)
        else:
            filename = f"image.{uploaded_image.content_type.split('/')[-1]}"
        # add random string to filename to avoid overwriting
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        uploaded_image.save(file_path)
        
        # Compress the image to avoid base64 url length issues
        with Image.open(file_path) as img:
            img = img.convert('RGB')
            img.save(file_path, format='JPEG', quality=50)  # Adjust quality as needed

        base64_img = image_to_base64(file_path)
        ocr_text = image_to_text(base64_img)
        print(f"OCR'd text: `{ocr_text}`")
    elif camera_image:
        # Decode the base64 image data
        header, encoded = camera_image.split(',', 1)  # Get rid of the data URL header
        image_data = base64.b64decode(encoded)

        # Save the image from camera
        filename = "camera_image.png"  # You can generate a unique filename here
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        with open(file_path, "wb") as f:
            f.write(image_data)

        # Compress and process the image
        with Image.open(file_path) as img:
            img = img.convert('RGB')
            img.save(file_path, format='JPEG', quality=50)  # Adjust quality as necessary

        base64_img = image_to_base64(file_path)
        ocr_text = image_to_text(base64_img)
        print(f"OCR'd text from camera: `{ocr_text}`")
        
    audio = request.files.get("audio", None)
    asr_text = None
    if audio:
        # Handle audio upload
        audio_filename = secure_filename(audio.filename)
        audio_path = os.path.join(app.config["UPLOAD_FOLDER"], audio_filename)
        audio.save(audio_path)
        print(f"Saved audio file to {audio_path}")
        asr_text = transcribe_audio(audio_path)
        print(f"asr_text: {asr_text}")

    # Get the optional prompt from the user
    user_prompt = request.form.get("prompt", "")

    if ocr_text:
        user_prompt += "\n"
        prompt = f"{user_prompt}Scanned text:\n{ocr_text}"
    else:
        prompt = user_prompt

    if asr_text:
        asr_text += "\n"
        prompt = f"{asr_text}Transcribed text:\n{asr_text}"
    else:
        prompt = user_prompt

    print(f"Prompt: `{prompt}`")

    # Use CalendarAssistant to convert text into a .ics file
    cal_assistant = CalendarAssistant()
    cal_assistant.handle_user_message(prompt)
    ics_file = BytesIO(cal_assistant.to_ical_bytes())
    calendar_name = cal_assistant.calendar_name

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{calendar_name}.ics")
    cal_assistant.write_calendar(save_path)
    
    # Send the .ics file back to the user for download
    response = send_file(
        path_or_file=ics_file, as_attachment=True, download_name=f"{calendar_name}.ics"
    )
    response.headers["X-Download-Name"] = f"{calendar_name}.ics"  # Custom header for JS to capture
    return response
