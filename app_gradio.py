import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import gradio as gr
import os
from functions_local.create_transcript import transcribe_full
from functions_local.llm_call_local import LLMCall
from functions_local.create_docx import create_docx

# --- Core Processing Function ---
def process_audio(audio_path):
    if audio_path is None:
        return "No audio provided", None, None

    # 1. Transcription
    try:
        print(f"Starting transcription for {audio_path}...")
        transcript_text = transcribe_full(audio_path)
        print("Transcription finished.")
    except Exception as e:
        print(f"Error during transcription: {e}")
        return f"Error during transcription: {e}", None, None

    # 2. LLM Call
    try:
        print("Starting LLM call...")
        llm_output = LLMCall(transcript_text)
        print("LLM call finished.")
    except Exception as e:
        print(f"Error during LLM call: {e}")
        return transcript_text, f"Error during LLM call: {e}", None

    # 3. Create DOCX
    try:
        print("Creating DOCX file...")
        doc_path = "Psychotherapie_Antrag.docx"
        create_docx(llm_output, doc_path)
        print(f"DOCX file created at {doc_path}")
    except Exception as e:
        print(f"Error during DOCX creation: {e}")
        return transcript_text, llm_output, f"Error during DOCX creation: {e}"

    return transcript_text, llm_output, doc_path

# --- Gradio Interface Definition ---
with gr.Blocks() as demo:
    gr.Markdown("# Psychotherapie Antrag Assistent")
    gr.Markdown("Nehmen Sie ein Audio-Memo auf oder laden Sie eine Datei hoch, um automatisch einen Psychotherapie-Antrag zu erstellen.")

    with gr.Row():
        audio_input = gr.Audio(
            sources=["microphone", "upload"],
            type="filepath",
            label="Audio-Memo aufnehmen oder hochladen"
        )

    process_button = gr.Button("Antrag erstellen")

    with gr.Row():
        transcript_output = gr.Textbox(label="Transkript", lines=10)
    with gr.Row():
        llm_output_json = gr.JSON(label="Strukturierter Antrag")
    with gr.Row():
        docx_output_file = gr.File(label="Download DOCX")

    process_button.click(
        fn=process_audio,
        inputs=audio_input,
        outputs=[transcript_output, llm_output_json, docx_output_file]
    )

# --- Launch the App ---
if __name__ == "__main__":
    demo.launch()