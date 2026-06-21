# backend/test_voice_wav2vec2.py

from predict_voice import predict_voice

print(
    predict_voice(
        r"datasets\RAVDESS\Actor_22\03-01-01-01-01-01-22.wav"
    )
)