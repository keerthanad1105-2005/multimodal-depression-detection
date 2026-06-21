import os
import joblib
import librosa
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "training",
    "models",
    "voice_emotion_model.pkl"
)

model = joblib.load(MODEL_PATH)

depression_emotions = [
    "sad",
    "fearful"
]

def predict_voice(audio_path):

    audio, sr = librosa.load(audio_path, sr=22050)

    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sr,
        n_mfcc=40
    )

    mfcc_mean = np.mean(mfcc.T, axis=0)

    prediction = str(model.predict([mfcc_mean])[0])

    if prediction in depression_emotions:
        score = 1.0
    else:
        score = 0.2

    return {
        "emotion": prediction,
        "score": score
    }