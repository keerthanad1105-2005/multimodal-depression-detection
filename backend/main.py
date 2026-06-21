from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi import Form

from fastapi.middleware.cors import CORSMiddleware

import os

from backend.predict_text import predict_text
from backend.predict_face import predict_face
from backend.predict_voice import predict_voice
from backend.fusion import calculate_depression

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

@app.get("/")
def home():

    return {
        "message": "Depression Detection API Running"
    }

@app.post("/analyze")
async def analyze(

    text: str = Form(...),

    image: UploadFile = File(...),

    audio: UploadFile = File(...)
):

    image_path = os.path.join(
        UPLOAD_DIR,
        image.filename
    )

    audio_path = os.path.join(
        UPLOAD_DIR,
        audio.filename
    )

    with open(image_path, "wb") as f:
        f.write(
            await image.read()
        )

    with open(audio_path, "wb") as f:
        f.write(
            await audio.read()
        )

    text_result = predict_text(text)

    face_result = predict_face(
        image_path
    )

    voice_result = predict_voice(
        audio_path
    )

    result = calculate_depression(
        face_result["score"],
        voice_result["score"],
        text_result["score"]
    )

    return {

        "text_score":
            round(
                text_result["score"],
                2
            ),

        "face_emotion":
            face_result["emotion"],

        "voice_emotion":
            voice_result["emotion"],

        "final_score":
            result["score"],

        "level":
            result["level"]
    }