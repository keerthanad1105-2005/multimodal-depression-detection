import os
import pandas as pd
import torch

from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)

print("Loading dataset...")

csv_path = r"datasets/reddit/depression_dataset.csv/depression_dataset_reddit_cleaned.csv"

df = pd.read_csv(csv_path)

df = df[["clean_text", "is_depression"]]

df = df.rename(
    columns={
        "clean_text": "text",
        "is_depression": "label"
    }
)

print("Dataset Shape:", df.shape)

train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df["label"]
)

train_dataset = Dataset.from_pandas(train_df)
test_dataset = Dataset.from_pandas(test_df)

print("Loading RoBERTa tokenizer...")

model_name = "roberta-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize(batch):
    return tokenizer(
        batch["text"],
        padding="max_length",
        truncation=True,
        max_length=128
    )

train_dataset = train_dataset.map(
    tokenize,
    batched=True
)

test_dataset = test_dataset.map(
    tokenize,
    batched=True
)

train_dataset.set_format(
    type="torch",
    columns=["input_ids", "attention_mask", "label"]
)

test_dataset.set_format(
    type="torch",
    columns=["input_ids", "attention_mask", "label"]
)

print("Loading RoBERTa model...")

model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=2
)

training_args = TrainingArguments(
    output_dir="training/models/roberta_depression",
    num_train_epochs=2,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    save_strategy="epoch",
    logging_steps=100,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset
)

print("Training started...")

trainer.train()

print("Saving model...")

trainer.save_model(
    "training/models/roberta_depression"
)

tokenizer.save_pretrained(
    "training/models/roberta_depression"
)

print("RoBERTa Model Saved Successfully!")