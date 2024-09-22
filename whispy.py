from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


def transcribe_audio(audio_file_path: str) -> str:
    audio_file = open(audio_file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file  # whisper-1
    )
    return transcription.text
