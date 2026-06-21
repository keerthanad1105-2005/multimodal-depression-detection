import os
import torch
import librosa

from transformers import (
    Wav2Vec2Processor,
    Wav2Vec2ForSequenceClassification
)

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "training",
    "models",
    "wav2vec2_voice"
)

processor = Wav2Vec2Processor.from_pretrained(
    MODEL_PATH
)

model = Wav2Vec2ForSequenceClassification.from_pretrained(
    MODEL_PATH
)

model.eval()

labels = [
    "neutral",
    "calm",
    "happy",
    "sad",
    "angry",
    "fearful",
    "disgust",
    "surprised"
]

def predict_voice(audio_path):

    speech, sr = librosa.load(
        audio_path,
        sr=16000
    )

    inputs = processor(
        speech,
        sampling_rate=16000,
        return_tensors="pt"
    )

    with torch.no_grad():

        logits = model(
            **inputs
        ).logits

    pred = torch.argmax(
        logits,
        dim=1
    ).item()

    emotion = labels[pred]

    if emotion in [
        "sad",
        "fearful",
        "angry"
    ]:
        score = 1.0
    else:
        score = 0.2

    return {
        "emotion": emotion,
        "score": score
    }