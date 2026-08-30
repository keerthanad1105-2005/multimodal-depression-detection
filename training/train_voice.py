import os
import librosa
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "datasets", "RAVDESS")

emotion_map = {
    "01": "neutral",
    "02": "calm",
    "03": "happy",
    "04": "sad",
    "05": "angry",
    "06": "fearful",
    "07": "disgust",
    "08": "surprised"
}

features = []
labels = []

print("Reading audio files...")

for root, dirs, files in os.walk(DATASET_PATH):

    for file in files:

        if file.endswith(".wav"):

            file_path = os.path.join(root, file)

            try:
                emotion_code = file.split("-")[2]
                emotion = emotion_map[emotion_code]

                audio, sr = librosa.load(file_path, sr=22050)

                mfcc = librosa.feature.mfcc(
                    y=audio,
                    sr=sr,
                    n_mfcc=40
                )

                mfcc_mean = np.mean(mfcc.T, axis=0)

                features.append(mfcc_mean)
                labels.append(emotion)

            except Exception as e:
                print("Error:", file_path)

print("Total Samples:", len(features))

X = np.array(features)
y = np.array(labels)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("Training model...")

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("Accuracy:", accuracy)

os.makedirs("training/models", exist_ok=True)

joblib.dump(
    model,
    "training/models/voice_emotion_model.pkl"
)

print("Voice Model Saved")