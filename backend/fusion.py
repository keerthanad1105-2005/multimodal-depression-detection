def calculate_depression(face_score, voice_score, text_score):

    final_score = (
    text_score * 0.5 +
    face_score * 0.25 +
    voice_score * 0.25
)

    if final_score < 0.3:
        level = "Minimal"

    elif final_score < 0.5:
        level = "Mild"

    elif final_score < 0.7:
        level = "Moderate"

    else:
        level = "Severe"

    return {
        "score": round(final_score, 2),
        "level": level
    }