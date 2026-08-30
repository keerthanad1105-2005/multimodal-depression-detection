import os
import cv2
import torch
import timm
from torchvision import transforms
from PIL import Image

device = torch.device("cpu")

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "training",
    "models",
    "mobilevit_face.pth"
)

emotion_labels = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "neutral",
    "sad",
    "surprise"
]

depression_emotions = [
    "sad",
    "fear"
]

model = timm.create_model(
    "mobilevit_xxs",
    pretrained=False,
    num_classes=7
)

model.load_state_dict(
    torch.load(
        MODEL_PATH,
        map_location=device
    )
)

model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])


def predict_face(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return {
            "emotion": "Unknown",
            "score": 0.2
        }

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    image = Image.fromarray(image)

    image = transform(image)

    image = image.unsqueeze(0).to(device)

    with torch.no_grad():

        output = model(image)

        prediction = torch.argmax(
            output,
            dim=1
        ).item()

    emotion = emotion_labels[prediction]


    if emotion in depression_emotions:
        score = 1.0
    else:
        score = 0.2
    
    return {
        "emotion": emotion,
        "score": score
    }