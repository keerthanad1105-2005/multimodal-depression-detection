import cv2
import torch
import torch.nn as nn
import numpy as np
from torchvision import transforms

# -----------------------
# Model Architecture (MUST match training)
# -----------------------
class EmotionCNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        self.classifier = nn.Sequential(
            nn.Linear(128 * 6 * 6, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 7)
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)

# -----------------------
# Load trained model
# -----------------------
device = torch.device("cpu")

model = EmotionCNN()
model.load_state_dict(torch.load(
    "training/models/face_emotion_cnn.pth",
    map_location=device
))
model.eval()

# -----------------------
# Emotion labels
# -----------------------
labels = ['angry','disgust','fear','happy','neutral','sad','surprise']

# -----------------------
# Image transform
# -----------------------
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Grayscale(),
    transforms.Resize((48, 48)),
    transforms.ToTensor()
])

# -----------------------
# Face detector
# -----------------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(0)

print("Starting webcam... Press 'q' to exit")

# -----------------------
# Webcam loop
# -----------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 🔥 DEBUG: face detection
    faces = face_cascade.detectMultiScale(gray, 1.1, 3)
    print("Faces detected:", len(faces))

    for (x, y, w, h) in faces:

        print("Face loop entered")

        face = gray[y:y+h, x:x+w]

        img = transform(face)
        img = img.unsqueeze(0)

        print("Input shape:", img.shape)

        with torch.no_grad():
            output = model(img)
            pred = torch.argmax(output, dim=1).item()
            emotion = labels[pred]

        # Draw rectangle + label
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(
            frame,
            f"{emotion} ({pred})",
            (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2
        )

    cv2.imshow("Emotion Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()