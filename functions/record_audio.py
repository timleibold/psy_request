import sounddevice as sd
import soundfile as sf

def record_memo(filename: str, duration: float = 300, samplerate: int = 16000):
    """
    Records audio from the default microphone and writes it to `filename`.
    If duration is None, it records until you hit Ctrl+C.
    """
    channels = 1
    try:
        if duration:
            print(f"Recording for {duration} seconds…")
            data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels)
            sd.wait()
        else:
            print("Recording… press Ctrl+C to stop.")
            # start an infinite stream that we append to a list
            frames = []
            def callback(indata, frames_count, time, status):
                if status:
                    print("⚠️", status)
                frames.append(indata.copy())
            with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
                while True:
                    pass
            data = b"".join(frames)
        sf.write(filename, data, samplerate)
        print(f"Saved recording to {filename}")
    except KeyboardInterrupt:
        # if user stopped early without a fixed duration
        if not duration:
            data = b"".join(frames)
            sf.write(filename, data, samplerate)
            print(f"\nStopped and saved recording to {filename}")
        else:
            raise

# Usage examples:
# 1) record a 30-second memo
#record_memo("memo.wav", duration=100)