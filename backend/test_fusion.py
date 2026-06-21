from fusion import calculate_depression

result = calculate_depression(
    face_score=0.8,
    voice_score=0.7,
    text_score=0.9
)

print(result)