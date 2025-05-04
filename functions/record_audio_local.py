import threading
import numpy as np
import sounddevice as sd
import soundfile as sf

# Globals for the recording thread and control
_recording_thread = None
_stop_event = threading.Event()
_frames = []
_filename = None
_samplerate = 16000
_channels = 1

def start_recording(filename: str, samplerate: int = 16000):
    """
    Start recording audio from the default microphone into `filename`.
    Recording runs in a background thread until stop_recording() is called.
    """
    global _recording_thread, _stop_event, _frames, _filename, _samplerate

    if _recording_thread and _recording_thread.is_alive():
        print("⚠️  Recording already in progress.")
        return

    _filename = filename
    _samplerate = samplerate
    _frames = []
    _stop_event.clear()

    def _record_loop():
        def callback(indata, frames_count, time_info, status):
            if status:
                print("⚠️", status)
            _frames.append(indata.copy())

        with sd.InputStream(samplerate=_samplerate, channels=_channels, callback=callback):
            print(f"Recording... call stop_recording() to finish.")
            while not _stop_event.is_set():
                sd.sleep(100)

        # Once stopped, concatenate frames and write file
        data = np.concatenate(_frames, axis=0)
        sf.write(_filename, data, _samplerate)
        print(f"✅ Saved recording to {_filename}")

    _recording_thread = threading.Thread(target=_record_loop, daemon=True)
    _recording_thread.start()

def stop_recording():
    """
    Stop the background recording and write the WAV file.
    """
    global _recording_thread, _stop_event

    if not _recording_thread:
        print("⚠️  No active recording to stop.")
        return

    _stop_event.set()
    _recording_thread.join()
    print("⏹️  Recording stopped.")

# Usage examples:
# 1) record a 30-second memo
#record_memo("memo.wav", duration=100)