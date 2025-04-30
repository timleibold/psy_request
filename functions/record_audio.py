import io
import streamlit as st
import importlib

def audio_recorder():
    """
    Proxy to the external audio-recorder-streamlit component.
    Renders an in-browser recorder and returns raw audio bytes or None.
    """
    # Dynamically import the installed package to avoid shadowing
    pkg = importlib.import_module("audio_recorder_streamlit")
    audio_bytes = pkg.audio_recorder()
    return audio_bytes


def start_recording(filename: str):
    """Display an in-browser recorder, then save the result to `filename` and session state."""
    # audio_recorder() returns raw WAV/MP3 bytes after user stops recording
    audio_bytes = audio_recorder()
    if audio_bytes:
        # write to disk
        with open(filename, "wb") as f:
            f.write(audio_bytes)
        # save in session for downstream use
        st.session_state.audio_file = io.BytesIO(audio_bytes)
        st.session_state.memo_ready = True


def stop_recording():
    """No-op: recording and stopping are handled in start_recording()."""
    pass
