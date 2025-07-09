import sounddevice as sd
import soundfile as sf
import numpy as np

def record_audio(filename: str, duration: int, samplerate: int = 16000, channels: int = 1):
    """
    Record audio from the default microphone for a fixed duration and save it to a WAV file.

    Args:
        filename (str): The name of the file to save the recording to.
        duration (int): The duration of the recording in seconds.
        samplerate (int): The sample rate of the recording.
        channels (int): The number of channels for the recording.
    """
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='float64')
    sd.wait()  # Wait until recording is finished
    print("Recording finished.")

    sf.write(filename, recording, samplerate)
    print(f"✅ Saved recording to {filename}")
