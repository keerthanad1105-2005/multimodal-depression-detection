import os
import librosa
import numpy as np

from datasets import Dataset
from transformers import (
    Wav2Vec2Processor,
    Wav2Vec2ForSequenceClassification,
    TrainingArguments,
    Trainer
)

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "datasets",
    "RAVDESS"
)

emotion_map = {
    "01": 0,
    "02": 1,
    "03": 2,
    "04": 3,
    "05": 4,
    "06": 5,
    "07": 6,
    "08": 7
}

print("Loading processor...")

processor = Wav2Vec2Processor.from_pretrained(
    "facebook/wav2vec2-base"
)

audio_paths = []
labels = []

print("Reading dataset...")

for root, dirs, files in os.walk(DATASET_PATH):

    for file in files:

        if file.endswith(".wav"):

            emotion_code = file.split("-")[2]

            audio_paths.append(
                os.path.join(root, file)
            )

            labels.append(
                emotion_map[emotion_code]
            )

print("Total Audio Files:", len(audio_paths))

dataset = Dataset.from_dict({
    "audio": audio_paths,
    "label": labels
})

MAX_LENGTH = 16000 * 4

def preprocess(example):

    speech, sr = librosa.load(
        example["audio"],
        sr=16000
    )

    if len(speech) > MAX_LENGTH:
        speech = speech[:MAX_LENGTH]

    else:
        padding = MAX_LENGTH - len(speech)

        speech = np.pad(
            speech,
            (0, padding)
        )

    inputs = processor(
        speech,
        sampling_rate=16000,
        return_tensors="pt"
    )

    example["input_values"] = (
        inputs.input_values[0].numpy()
    )

    return example

print("Processing audio...")

dataset = dataset.map(
    preprocess
)

dataset = dataset.train_test_split(
    test_size=0.2,
    seed=42
)

print("Loading model...")

model = Wav2Vec2ForSequenceClassification.from_pretrained(
    "facebook/wav2vec2-base",
    num_labels=8
)

training_args = TrainingArguments(
    output_dir="training/models/wav2vec2_voice",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=3,
    logging_steps=10,
    save_steps=500
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"]
)

print("Starting training...")

trainer.train()

print("Saving model...")

trainer.save_model(
    "training/models/wav2vec2_voice"
)

processor.save_pretrained(
    "training/models/wav2vec2_voice"
)

print("Wav2Vec2 Model Saved Successfully")