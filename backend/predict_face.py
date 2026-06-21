import os
import cv2
import torch
import timm
from torchvision import transforms

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

model.eval()

labels = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "neutral",
    "sad",
    "surprise"
]

transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224,224)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor()
])

def predict_face(image_path):

    img = cv2.imread(image_path)

    if img is None:
        raise ValueError(
            f"Image not found: {image_path}"
        )

    img = transform(img)

    img = img.unsqueeze(0)

    with torch.no_grad():

        output = model(img)

        pred = torch.argmax(
            output,
            dim=1
        ).item()

    emotion = labels[pred]

    if emotion in [
        "sad",
        "fear",
        "angry"
    ]:
        score = 1.0
    else:
        score = 0.2

    return {
        "emotion": emotion,
        "score": score
    }