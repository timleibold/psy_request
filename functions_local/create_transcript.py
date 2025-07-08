#!/usr/bin/env python3
#Vorsicht: dieser Funktion muss der Dateipfad, nicht ie Datei selbst übergeben werden!!!

from faster_whisper import WhisperModel
import torch, gc

import torch
from faster_whisper import WhisperModel

def transcribe_full(path):
    model = WhisperModel(
        "large-v3-turbo",
        device="cuda",
        compute_type="float16",
        cpu_threads=4,
        num_workers=1,
    )

    segments, info = model.transcribe(path, word_timestamps=False, beam_size=5)

    # Volltext zusammensetzen
    full_text = " ".join(segment.text.strip() for segment in segments)

    # Ressourcen bereinigen
    del model, segments, info
    gc.collect()
    torch.cuda.empty_cache()

    return full_text
if __name__ == "__main__":
    print(transcribe_full("memo.wav"))
