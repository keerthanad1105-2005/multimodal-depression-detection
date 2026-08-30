import whisper

print("Loading Whisper model...")

model = whisper.load_model("base")

print("Model loaded successfully")

audio_file = "sample.wav"

result = model.transcribe(audio_file)

print("\nTranscription:")
print(result["text"])