async function analyze() {

    document.getElementById("loading").innerHTML =
        "Analyzing... Please wait";

    const text =
        document.getElementById("text").value;

    const image =
        document.getElementById("image").files[0];

    const audio =
        document.getElementById("audio").files[0];

    const formData = new FormData();

    formData.append("text", text);
    formData.append("image", image);
    formData.append("audio", audio);

    const response = await fetch(
        "http://127.0.0.1:8000/analyze",
        {
            method:"POST",
            body:formData
        }
    );

    const data = await response.json();

    document.getElementById("loading").innerHTML = "";

    document.getElementById("result").style.display =
        "block";

    document.getElementById("result").innerHTML =

    `
    <h2 class="result-title">
        Analysis Result
    </h2>

    <div class="score">
        📝 Text Score:
        <b>${data.text_score}</b>
    </div>

    <div class="score">
        😀 Face Emotion:
        <b>${data.face_emotion}</b>
    </div>

    <div class="score">
        🎤 Voice Emotion:
        <b>${data.voice_emotion}</b>
    </div>

    <div class="score">
        📊 Depression Score:
        <b>${data.final_score}</b>
    </div>

    <div class="level">
        ${data.level}
    </div>
    `;
}