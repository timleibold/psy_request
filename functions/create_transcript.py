from openai import OpenAI
import os
import pprint as pp

def create_transcript(audio_file):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    resp = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )

    transcript = resp
    return transcript