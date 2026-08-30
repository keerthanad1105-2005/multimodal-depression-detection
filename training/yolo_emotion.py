import cv2
import torch
import torch.nn as nn
from ultralytics import YOLO
from torchvision import transforms

# -----------------------
# Emotion Model (same as trained)
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
# Load models
# -----------------------
device = torch.device("cpu")

emotion_model = EmotionCNN()
emotion_model.load_state_dict(torch.load(
    "training/models/face_emotion_cnn.pth",
    map_location=device
))
emotion_model.eval()

yolo_model = YOLO("yolov8n.pt")

# -----------------------
# Labels
# -----------------------
labels = ['angry','disgust','fear','happy','neutral','sad','surprise']

# -----------------------
# Transform
# -----------------------
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Grayscale(),
    transforms.Resize((48, 48)),
    transforms.ToTensor()
])

# -----------------------
# Webcam
# -----------------------
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = yolo_model(frame)

    for r in results:
        for box in r.boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            face = frame[y1:y2, x1:x2]

            if face.size == 0:
                continue

            img = transform(face)
            img = img.unsqueeze(0)

            with torch.no_grad():
                output = emotion_model(img)
                pred = torch.argmax(output, dim=1).item()
                emotion = labels[pred]

            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
            cv2.putText(frame, emotion, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                        (0,255,0), 2)

    cv2.imshow("YOLO + Emotion Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()