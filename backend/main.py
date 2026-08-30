from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi import Form
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import cv2

from backend.predict_text import predict_text
from backend.predict_face import predict_face
from backend.predict_voice import predict_voice
from backend.fusion import calculate_depression

from backend.database import conn, DB_PATH
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "Depression Detection API Running"
    }

import time

@app.post("/analyze")
async def analyze(
    text: str = Form(...),
    image: UploadFile = File(...),
    audio: UploadFile = File(...)
):
    print("========== REQUEST RECEIVED ==========")

    t = time.time()

    image_path = os.path.join(UPLOAD_DIR, image.filename)
    audio_path = os.path.join(UPLOAD_DIR, audio.filename)

    print("Saving files...")

    with open(image_path, "wb") as f:
        f.write(await image.read())

    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    print("Files Saved:", round(time.time()-t,2), "sec")

    t=time.time()
    print("Running Text Model...")
    text_result = predict_text(text)
    print("Text Done:", round(time.time()-t,2), "sec")

    t=time.time()
    print("Running Face Model...")
    face_result = predict_face(image_path)
    print("Face Done:", round(time.time()-t,2), "sec")

    t=time.time()
    print("Running Voice Model...")
    voice_result = predict_voice(audio_path)
    print("Voice Done:", round(time.time()-t,2), "sec")

    t=time.time()
    result = calculate_depression(
        face_result["score"],
        voice_result["score"],
        text_result["score"]
    )
    print("Fusion Done:", round(time.time()-t,2), "sec")

    print("========== FINISHED ==========")

    from datetime import datetime
    cursor = conn.cursor()
    cursor.execute(
    """
    INSERT INTO history
    (username, analysis_type, score, level, date)
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        "Keerthana",
        "Text + Face + Voice",
        result["score"],
        result["level"],
        datetime.now().strftime("%d-%m-%Y %H:%M")
    )
)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM history")
    print("Rows in history:", cursor.fetchone()[0])

    print("✅ Saved to database")
    
    os.remove(image_path)
    os.remove(audio_path)

    return {
        "text_score": round(text_result["score"],2),
        "face_emotion": face_result["emotion"],
        "voice_emotion": voice_result["emotion"],
        "final_score": result["score"],
        "level": result["level"]
    }

# Create uploads folder if it doesn't exist
os.makedirs("uploads", exist_ok=True)

@app.post("/analyze-video")
async def analyze_video(video: UploadFile = File(...)):

    filename = video.filename

    with open(filename, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    cap = cv2.VideoCapture(filename)

    frame_count = 0
    saved_frames = []

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        if frame_count % 30 == 0:

            image_path = f"temp_frame_{frame_count}.jpg"

            cv2.imwrite(image_path, frame)

            saved_frames.append(image_path)

        frame_count += 1

    cap.release()

    # -------------------------------
    # Analyze each extracted frame
    # -------------------------------

    emotions = []
    scores = []

    for frame in saved_frames:

        result = predict_face(frame)

        emotions.append(result["emotion"])
        scores.append(result["score"])

    # No frames found
    if len(scores) == 0:
        return {
            "emotion": "Unknown",
            "score": 0,
            "level": "Unable to Detect",
            "frames_used": 0
        }

    # -------------------------------
    # Calculate average score
    # -------------------------------

    average_score = sum(scores) / len(scores)

    final_score = average_score

    emotion = max(set(emotions), key=emotions.count)

    if final_score < 0.35:
        level = "Low Depression"
    elif final_score < 0.70:
        level = "Moderate Depression"
    else:
        level = "High Depression"

    cursor = conn.cursor()
    cursor.execute(
    """
    INSERT INTO history
    (username, analysis_type, score, level, date)
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        "Keerthana",
        "Video Analysis",
        final_score,
        level,
        datetime.now().strftime("%d-%m-%Y %H:%M")
    )
)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM history")
    print("Rows in history:", cursor.fetchone()[0])

    print("Video History Saved")

    # Delete extracted frames
    for frame in saved_frames:
        os.remove(frame)

    # Delete uploaded video
    os.remove(filename)

    return {
        "emotion": emotion,
        "score": round(final_score, 2),
        "level": level,
        "frames_used": len(saved_frames)
    }
      
@app.get("/history")
def get_history():
     
    cursor = conn.cursor() 

    print("Using cursor:", cursor)
    print("Using database:", DB_PATH)

    cursor.execute("""
        SELECT id, username, analysis_type, score, level, date
        FROM history
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    history = []

    for row in rows:

        history.append({

            "id": row[0],
            "username": row[1],
            "analysis_type": row[2],
            "score": row[3],
            "level": row[4],
            "date": row[5]

})

    return history  

@app.delete("/history/{history_id}")
def delete_history(history_id: int):

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM history WHERE id=?",
        (history_id,)
    )

    conn.commit()

    return {
        "message":"History deleted successfully"
    }

@app.get("/admin-dashboard")
def admin_dashboard():

    cursor = conn.cursor()

    # Total Users
    cursor.execute("SELECT COUNT(DISTINCT username) FROM history")
    total_users = cursor.fetchone()[0]

    # Total Analyses
    cursor.execute("SELECT COUNT(*) FROM history")
    total_analyses = cursor.fetchone()[0]

    # Average Score
    cursor.execute("""
        SELECT AVG(
            CASE
                WHEN score > 1 THEN score / 100.0
                ELSE score
            END
        )
        FROM history
    """)

    avg_score = cursor.fetchone()[0] or 0

    # High Risk Cases
    cursor.execute("""
        SELECT COUNT(*)
        FROM history
        WHERE level='High Depression'
    """)
    high_risk = cursor.fetchone()[0]

    # Today's Analyses
    from datetime import datetime

    today = datetime.now().strftime("%d-%m-%Y")

    cursor.execute("""
        SELECT COUNT(*)
        FROM history
        WHERE date LIKE ?
    """, (today + "%",))

    today_analysis = cursor.fetchone()[0]

    return {
        "total_users": total_users,
        "total_analyses": total_analyses,
        "today_analyses": today_analysis,
        "average_score": round(avg_score, 2),
        "high_risk": high_risk
    }