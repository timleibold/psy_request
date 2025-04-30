import io
import streamlit as st
from audio_recorder_streamlit import audio_recorder


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