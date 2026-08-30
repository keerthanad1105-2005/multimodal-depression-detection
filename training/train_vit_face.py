import os
import torch
import torch.nn as nn
import timm
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

print("Starting...")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Device:", device)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRAIN_DIR = os.path.join(BASE_DIR, "datasets", "FER2013", "train")
TEST_DIR = os.path.join(BASE_DIR, "datasets", "FER2013", "test")

transform = transforms.Compose([
transforms.Resize((224, 224)),
transforms.Grayscale(num_output_channels=3),
transforms.ToTensor()
])

print("Loading datasets...")

train_dataset = datasets.ImageFolder(
TRAIN_DIR,
transform=transform
)

test_dataset = datasets.ImageFolder(
TEST_DIR,
transform=transform
)

print("Train Images:", len(train_dataset))
print("Test Images:", len(test_dataset))

train_loader = DataLoader(
train_dataset,
batch_size=8,
shuffle=True,
num_workers=0
)

test_loader = DataLoader(
test_dataset,
batch_size=8,
shuffle=False,
num_workers=0
)

print("Loading MobileViT...")

model = timm.create_model(
"mobilevit_xxs",
pretrained=True,
num_classes=7
)

model = model.to(device)

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.AdamW(
model.parameters(),
lr=1e-4
)

epochs = 5

for epoch in range(epochs):

    model.train()

    running_loss = 0

    for batch_idx, (images, labels) in enumerate(train_loader):

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        running_loss += loss.item()

        if batch_idx % 100 == 0:
            print(
                f"Epoch {epoch+1}/{epochs} "
                f"Batch {batch_idx}/{len(train_loader)} "
                f"Loss {loss.item():.4f}"
            )

    print(
        f"Epoch {epoch+1}/{epochs} "
        f"Average Loss: {running_loss/len(train_loader):.4f}"
    )

MODEL_DIR = os.path.join(BASE_DIR, "training", "models")

os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(
MODEL_DIR,
"mobilevit_face.pth"
)

torch.save(
model.state_dict(),
MODEL_PATH
)

print("Model Saved:", MODEL_PATH)
