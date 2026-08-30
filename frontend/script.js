/*=====================================================
        MULTIMODAL DEPRESSION DETECTION SYSTEM
======================================================*/

/*=====================================================
                API URL
======================================================*/

const API_URL = "http://127.0.0.1:8000";

/*=====================================================
                GLOBAL VARIABLES
======================================================*/
let latestResult = null;
let capturedImage = null;
let cameraStream = null;

let scoreChart = null;
let pieChart = null;


function showToast(message,type="success"){

    const toast=document.getElementById("toast");

    toast.innerText=message;

    toast.className="toast show "+type;

    setTimeout(()=>{

        toast.className="toast";

    },3000);

}
/*=====================================================
                SECTION NAVIGATION
======================================================*/
function showSection(sectionId){

    const sections = [
        "homeSection",
        "analysisSection",
        "historySection",
        "statisticsSection",
        "adminSection"
    ];

    sections.forEach(id=>{
        document.getElementById(id).style.display="none";
    });

    document.getElementById(sectionId).style.display="block";

    if(sectionId==="historySection"){
        loadHistory();
    }

    if(sectionId==="statisticsSection"){
        loadChart();
    }

    if(sectionId==="adminSection"){
        loadAdminDashboard();
    }

}

/*=====================================================
                DARK MODE
======================================================*/

function toggleTheme() {

    document.body.classList.toggle("dark");

    if (document.body.classList.contains("dark")) {

        localStorage.setItem("theme", "dark");

    }

    else {

        localStorage.setItem("theme", "light");

    }

}

function loadTheme() {

    const theme = localStorage.getItem("theme");

    if (theme === "dark") {

        document.body.classList.add("dark");

    }

}

/*=====================================================
                LOADING
======================================================*/

function showLoading() {

    const loading = document.getElementById("loading");

    if (!loading) return;

    loading.style.display = "block";

    loading.innerHTML = `

        <div class="loader"></div>

        <p>AI is analysing...</p>

    `;

}

function hideLoading() {

    const loading = document.getElementById("loading");

    if (!loading) return;

    loading.style.display = "none";

    loading.innerHTML = "";

}

/*=====================================================
                CAMERA
======================================================*/

async function startCamera(){

    try{

        const stream = await navigator.mediaDevices.getUserMedia({
            video:true
        });

        const video = document.getElementById("video");

        video.srcObject = stream;

        // ADD HERE
        showToast("Camera started.","success");

    }

    catch(error){

        console.log(error);

        showToast("Unable to access camera.","error");

    }


}



/*=====================================================
                CAPTURE FACE
======================================================*/

function captureImage() {

    const video = document.getElementById("video");

    const canvas = document.getElementById("canvas");

    const context = canvas.getContext("2d");

    context.drawImage(

        video,

        0,

        0,

        canvas.width,

        canvas.height

    );

    canvas.toBlob(function(blob){

         capturedImage = blob;

        const preview = document.getElementById("capturedPreview");

        preview.src = URL.createObjectURL(blob);

        preview.style.display = "block";

        showToast("Face captured successfully.","success");

        // Stop camera AFTER image is captured
        video.srcObject.getTracks().forEach(track => track.stop());

        showToast("Camera stopped.","info");

    },"image/jpeg");

    
}

function retakeImage(){

    capturedImage = null;

    document.getElementById("capturedPreview").style.display = "none";

    showToast("Capture another image.","info");

    startCamera();

}

/*=====================================================
                TAB SWITCHING
======================================================*/
function initializeTabs(){

    const textSection = document.getElementById("textSection");

    if(textSection){

        textSection.style.display = "block";

    }

} 

/*=====================================================
                INITIALIZATION
======================================================*/

document.addEventListener("DOMContentLoaded", function () {

    loadTheme();

    initializeTabs();

    showSection("homeSection");

    loadHistory();

    loadChart();

    loadAdminDashboard();

    document.getElementById("analyzeBtn")
        ?.addEventListener("click", analyzeMentalHealth);

    const downloadBtn = document.getElementById("downloadBtn");

    if (downloadBtn) {

    downloadBtn.addEventListener(
        "click",
        generatePDF
    );

}

    document.getElementById("exportExcelBtn")
        ?.addEventListener("click", exportHistory);

});

/*=====================================================
            ANALYZE MENTAL HEALTH
======================================================*/

async function analyzeMentalHealth(){

    const startTime = performance.now();
    
    
    const text=document.getElementById("text").value.trim();

    const uploadedFace=document.getElementById("face").files[0];

    const voice=document.getElementById("voice").files[0];

    if(text===""){

        showToast("Please enter your feelings.","error");

        return;

    }

    if(!capturedImage && !uploadedFace){

        alert("Please capture or upload a face image.");

        return;

    }

    if(!voice){

        showToast("Please upload a voice (.wav) file.","error");

        return;

    }

    const formData=new FormData();
    
    formData.append("patientName",
    document.getElementById("patientName").value.trim());

        formData.append("patientAge",
            document.getElementById("patientAge").value);

        formData.append("patientGender",
            document.getElementById("patientGender").value);

        formData.append("patientOccupation",
            document.getElementById("patientOccupation").value.trim());

        formData.append("patientSymptoms",
            document.getElementById("patientSymptoms").value.trim());

        formData.append("patientDuration",
            document.getElementById("patientDuration").value);

        formData.append("patientStarted",
            document.getElementById("patientStarted").value);    

            formData.append("text",text);

    if(capturedImage){

        formData.append(

            "image",

            capturedImage,

            "captured.jpg"

        );

    }

    else{

        formData.append(

            "image",

            uploadedFace

        );

    }

    formData.append(

        "audio",

        voice

    );

    console.log("Patient Data:");
    console.log("Name:", document.getElementById("patientName").value);
    console.log("Age:", document.getElementById("patientAge").value);
    console.log("Gender:", document.getElementById("patientGender").value);
    console.log("Occupation:", document.getElementById("patientOccupation").value);
    console.log("Symptoms:", document.getElementById("patientSymptoms").value);
    console.log("Duration:", document.getElementById("patientDuration").value);
    console.log("Started:", document.getElementById("patientStarted").value);

    showLoading();

    document.getElementById("result").style.display="none";

    try{

        const response=await fetch(

            API_URL+"/analyze",

            {

                method:"POST",

                body:formData

            }

        );

        if (!response.ok) {

            const errorText = await response.text();

            console.error("ANALYZE ERROR:", response.status, errorText);

            throw new Error(
                `Backend error ${response.status}: ${errorText}`
            );

        }

        const data=await response.json();

        const endTime = performance.now();

        data.processing_time = ((endTime - startTime) / 1000).toFixed(2);

        latestResult = data;

        hideLoading();

        displayResult(data);

        // ✅ Show success message here
        showToast("Analysis completed successfully.","success");

        loadHistory();

        loadChart();

        loadAdminDashboard();

    }

    catch(error){

        hideLoading();

        console.log(error);

        showToast("Unable to connect to backend.","error");

    }

}

/*=====================================================
                RESULT CARD
======================================================*/

function displayResult(data){

    console.log("displayResult() called");

    const result = document.getElementById("result");

    result.style.display = "block";

    let recommendation = "";

    if(data.level.toLowerCase().includes("high")){

        recommendation =
        "Seek immediate consultation with a mental health professional.";

    }

    else if(data.level.toLowerCase().includes("moderate")){

        recommendation =
        "Practice stress management and consider counselling if symptoms continue.";

    }

    else{

        recommendation =
        "Maintain a healthy lifestyle and continue positive daily activities.";

    }
    
    let explanation = "";

    if (data.level.toLowerCase().includes("high")) {

        explanation = `
        <ul>
            <li>Negative emotional language detected in text.</li>
            <li>Facial expression indicates sadness.</li>
            <li>Voice shows low emotional energy.</li>
            <li>All three modalities strongly indicate depression.</li>
        </ul>
        `;

    }

    else if (data.level.toLowerCase().includes("moderate")) {

        explanation = `
        <ul>
            <li>Some negative emotions detected in text.</li>
            <li>Face shows mild sadness.</li>
            <li>Voice indicates moderate emotional variation.</li>
            <li>Combined analysis suggests moderate depression risk.</li>
        </ul>
        `;

    }

    else {

        explanation = `
        <ul>
            <li>Positive language detected.</li>
            <li>Face appears emotionally stable.</li>
            <li>Voice sounds energetic.</li>
            <li>Overall analysis indicates low depression risk.</li>
        </ul>
        `;

    }

    result.innerHTML = `

         <h2 style="text-align:center;">
            DEPRESSION ANALYSIS REPORT
        </h2>

        <hr>

        <h3>Analysis Summary</h3>

        <p><strong>Face Emotion :</strong> ${data.face_emotion}</p>

        <p><strong>Voice Emotion :</strong> ${data.voice_emotion}</p>

        <p><strong>Text Score :</strong> ${Number(data.text_score).toFixed(2)}%</p>

        <p><strong>Overall Depression Score :</strong> ${(Number(data.final_score) * 100).toFixed(0)}%</p>

        <p><strong>Depression Level :</strong> ${data.level}</p>

        <h3>Explainable AI</h3>

        ${explanation}

        <h3>Recommendation</h3>

        <p>${recommendation}</p>

     `;

        document.getElementById("reportActions").style.display = "block";

}

/*=====================================================
                LOAD HISTORY
======================================================*/

async function loadHistory(){

    console.log("loadHistory called");

    try{

        const response = await fetch(API_URL + "/history");

        console.log(response);

        const history = await response.json();

        console.log(history);

        const tbody = document.querySelector("#historyTable tbody");

        console.log(tbody);

        tbody.innerHTML = "";

        history.forEach(item => {

            console.log(item);

            tbody.innerHTML += `
            <tr>
                <td>${item.username}</td>
                <td>${item.analysis_type}</td>
                <td>${(Number(item.score) * 100).toFixed(0)}%</td>
                <td>${item.level}</td>
                <td>${item.date}</td>
                <td>
                    <button onclick="deleteHistory(${item.id})">
                        Delete
                    </button>
                </td>
            </tr>`;
        });

        console.log("Rows added:", tbody.rows.length);

    }
    catch(error){

        console.log(error);

    }

}

/*=====================================================
                DELETE HISTORY
======================================================*/

async function deleteHistory(id){

    const ok = confirm(
        "Are you sure you want to permanently delete this history record?"
    );

    if(!ok) return;

    try{

        await fetch(API_URL + "/history/" + id,{
            method:"DELETE"
        });

        showToast("History deleted successfully.","success");

        loadHistory();

    }

    catch{

        alert("Unable to delete history.");

    }

}

/*=====================================================
                SEARCH HISTORY
======================================================*/

function searchHistory(){

    const input = document
        .getElementById("searchHistory")
        .value
        .toLowerCase();

    const rows = document.querySelectorAll("#historyTable tbody tr");

    rows.forEach(row=>{

        if(row.innerText.toLowerCase().includes(input)){

            row.style.display="";

        }

        else{

            row.style.display="none";

        }

    });

}

/*=====================================================
                FILTER HISTORY
======================================================*/

function filterHistory(){

    const filter = document.getElementById("historyFilter").value;

    const rows = document.querySelectorAll("#historyTable tbody tr");

    const today = new Date();

    rows.forEach(row=>{

        const dateText = row.cells[4].innerText;

        if(filter==="all"){

            row.style.display="";

            return;

        }

        if(filter==="today"){

            const current = today.toLocaleDateString("en-GB").replace(/\//g,"-");

            if(dateText.includes(current))

                row.style.display="";

            else

                row.style.display="none";

        }

        else{

            row.style.display="";

        }

    });

}

/*=====================================================
                LOAD STATISTICS
======================================================*/

async function loadChart(){

    try{

        const response = await fetch(API_URL + "/history");

        const history = await response.json();

        const labels = [];
        const scores = [];

        history.reverse().forEach(item=>{

            labels.push(item.date);

            scores.push(Number(item.score) * 100);

        });

        const ctx = document
            .getElementById("scoreChart")
            .getContext("2d");

        if(scoreChart){

            scoreChart.destroy();

        }

        scoreChart = new Chart(ctx,{

            type:"line",

            data:{

                labels:labels,

                datasets:[{

                    label:"Depression Score",

                    data:scores,

                    fill:false,

                    borderColor:"#4F46E5",

                    borderWidth:3,

                    tension:0.3

                }]

            },

            options:{

                responsive:true,

                maintainAspectRatio:false

            }

        });

        updateStatistics(history);

    }

    catch(error){

        console.log(error);

    }

}

/*=====================================================
            UPDATE STATISTICS
======================================================*/

function updateStatistics(history){

    document.getElementById("totalAnalysis").innerText=history.length;

    if(history.length===0){

        return;

    }

    const scores=history.map(x=>Number(x.score) * 100);

    const average=scores.reduce((a,b)=>a+b,0)/scores.length;

    document.getElementById("avgScore").innerText=

        average.toFixed(2)+"%";

    const high=

        history.filter(x=>x.level==="High Depression").length;

    document.getElementById("highCount").innerText=high;

    const levelCount={};

    history.forEach(item=>{

        levelCount[item.level]=(levelCount[item.level]||0)+1;

    });

    let common="-";

    let max=0;

    for(const level in levelCount){

        if(levelCount[level]>max){

            max=levelCount[level];

            common=level;

        }

    }

    document.getElementById("commonLevel").innerText=common;

}

/*=====================================================
            ADMIN DASHBOARD
======================================================*/

async function loadAdminDashboard(){

    try{

        const response = await fetch(API_URL + "/admin-dashboard");

        const data = await response.json();

        console.log(data);   // <-- add this

        document.getElementById("totalUsers").innerText = data.total_users;
        document.getElementById("adminTotalAnalysis").innerText = data.total_analyses;
        document.getElementById("todayAnalysis").innerText = data.today_analyses;
        document.getElementById("adminAvgScore").innerText =
            (Number(data.average_score) * 100).toFixed(0) + "%";
        document.getElementById("highRisk").innerText = data.high_risk;

    }
    catch(error){

        console.log(error);

    }

}

document.getElementById("logoutBtn").addEventListener("click", logout);

function logout() {

    const ok = confirm("Are you sure you want to logout?");

    if (!ok) return;

    localStorage.clear();

    sessionStorage.clear();

    window.location.href = "login.html";

}
/*=====================================================
                PDF REPORT
======================================================*/

async function generatePDF() {
    if (!latestResult) {
    alert("Please perform an analysis first.");
    return;
}

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    const name = document.getElementById("patientName").value || "N/A";
    const age = document.getElementById("patientAge").value || "N/A";
    const gender = document.getElementById("patientGender").value || "N/A";
    const occupation = document.getElementById("patientOccupation").value || "N/A";
    const symptoms = document.getElementById("patientSymptoms").value || "N/A";
    
    let y = 20;

    // ---------------- TITLE ----------------

    doc.setFont("helvetica","bold");
    doc.setFontSize(16);

    doc.text(
        "MULTIMODAL DEPRESSION DETECTION REPORT",
        105,
        y,
        {align:"center"}
    );

    y += 12;

    // ---------------- PATIENT INFO ----------------

    doc.setFontSize(13);
    doc.text("PATIENT INFORMATION",20,y);

    y += 8;

    doc.setFont("helvetica","normal");
    doc.setFontSize(11);

    const patientInfo = [

        ["Name",name],
        ["Age",age],
        ["Gender",gender],
        ["Occupation",occupation],
        ["Symptoms",symptoms],
        ["Report Date",new Date().toLocaleString()]

    ];

    patientInfo.forEach(item=>{

        doc.text(item[0],20,y);
        doc.text(":",65,y);
        doc.text(String(item[1]),70,y);

        y += 6;

    });

    y += 5;

    // ---------------- ANALYSIS ----------------

    doc.setFont("helvetica","bold");
    doc.setFontSize(13);

    doc.text("ANALYSIS RESULT",20,y);

    y += 8;

    doc.setFont("helvetica","normal");
    doc.setFontSize(11);

    doc.text("Overall Score",20,y);
    doc.text(":",65,y);
    doc.text((Number(latestResult.final_score) * 100).toFixed(0) + "%",70,y);

    y += 6;

    doc.text("Depression Level",20,y);
    doc.text(":",65,y);
    doc.text(latestResult.level,70,y);

    y += 6;

    doc.text("Face Emotion",20,y);
    doc.text(":",65,y);
    doc.text(latestResult.face_emotion,70,y);

    y += 6;

    doc.text("Voice Emotion",20,y);
    doc.text(":",65,y);
    doc.text(latestResult.voice_emotion,70,y);

    y += 10;

    // ---------------- STATISTICS ----------------

    doc.setFont("helvetica","bold");
    doc.setFontSize(13);

    doc.text("STATISTICS",20,y);

    y += 8;

    doc.setFont("helvetica","normal");
    doc.setFontSize(11);

    const stats=[

        ["Total Analyses",document.getElementById("totalAnalysis").innerText],
        ["Average Score",document.getElementById("avgScore").innerText],
        ["High Depression Cases",document.getElementById("highCount").innerText],
        ["Most Common Level",document.getElementById("commonLevel").innerText]

    ];

    stats.forEach(item=>{

        doc.text(item[0],20,y);
        doc.text(":",65,y);
        doc.text(String(item[1]),70,y);

        y += 6;

    });

    y += 8;

    // ---------------- RECOMMENDATIONS ----------------

    doc.setFont("helvetica","bold");
    doc.setFontSize(13);

    doc.text("RECOMMENDATIONS",20,y);

    y += 8;

    doc.setFont("helvetica","normal");
    doc.setFontSize(11);

    if(latestResult.level.toLowerCase().includes("high")){

        doc.text("• Immediate consultation with a psychologist.",20,y);
        y+=6;

        doc.text("• Maintain regular counselling sessions.",20,y);
        y+=6;

        doc.text("• Seek family and social support.",20,y);

    }

    else if(latestResult.level.toLowerCase().includes("moderate")){

        doc.text("• Practice stress management.",20,y);
        y+=6;

        doc.text("• Sleep at least 7-8 hours daily.",20,y);
        y+=6;

        doc.text("• Consider counselling if symptoms continue.",20,y);

    }

    else{

        doc.text("• Continue a healthy lifestyle.",20,y);
        y+=6;

        doc.text("• Exercise regularly.",20,y);
        y+=6;

        doc.text("• Maintain positive social interaction.",20,y);

    }

    // ---------------- FOOTER ----------------

    doc.setFont("helvetica","italic");
    doc.setFontSize(10);

    doc.text(
        "Generated by AI Mental Health Dashboard",
        105,
        285,
        {align:"center"}
    );

    doc.save("Depression_Report.pdf");

}

/*=====================================================
            EXPORT HISTORY
======================================================*/

function exportHistory(){

    const table=document.getElementById("historyTable");

    const workbook=XLSX.utils.table_to_book(table);

    XLSX.writeFile(

        workbook,

        "Depression_History.xlsx"

    );

}

async function loadHomeDashboard(){

    const response = await fetch("http://127.0.0.1:8000/admin-dashboard");

    const data = await response.json();

    document.getElementById("homeTotalUsers").innerText =
        data.total_users;

    document.getElementById("homeTotalAnalysis").innerText =
        data.total_analyses;

    document.getElementById("homeAverageScore").innerText =
    (Number(data.average_score) * 100).toFixed(0) + "%";

    document.getElementById("homeHighRisk").innerText =
        data.high_risk;

}
document.addEventListener("DOMContentLoaded",()=>{

    loadHomeDashboard();

});

function resetForm(){

    document.getElementById("patientName").value = "";
    document.getElementById("patientAge").value = "";
    document.getElementById("patientOccupation").value = "";
    document.getElementById("patientSymptoms").value = "";
    document.getElementById("patientDuration").value = "";
    document.getElementById("patientStarted").value = "";

    document.getElementById("text").value = "";

    document.getElementById("face").value = "";

    document.getElementById("voice").value = "";


    capturedImage = null;

    const preview = document.getElementById("capturedPreview");

    if(preview){

        preview.style.display = "none";

        preview.src = "";

    }

    document.getElementById("result").style.display = "none";

    document.getElementById("reportActions").style.display = "none";

    showToast("Form cleared successfully.","success");

}
 
/*=====================================================
        AUTO CALCULATE SYMPTOM DURATION
======================================================*/

document.addEventListener("DOMContentLoaded", function () {

    const startedInput = document.getElementById("patientStarted");
    const durationInput = document.getElementById("patientDuration");

    if (!startedInput || !durationInput) {
        console.log("Duration elements not found");
        return;
    }

    // Prevent selecting a future date
    const today = new Date();
    const todayString = today.toISOString().split("T")[0];

    startedInput.max = todayString;

    startedInput.addEventListener("change", function () {

        if (!this.value) {
            durationInput.value = "";
            return;
        }

        const startDate = new Date(this.value + "T00:00:00");
        const currentDate = new Date();

        currentDate.setHours(0, 0, 0, 0);

        // Future date check
        if (startDate > currentDate) {

            showToast(
                "Symptoms start date cannot be in the future.",
                "error"
            );

            this.value = "";
            durationInput.value = "";

            return;
        }

        // Calculate calendar difference
        let years =
            currentDate.getFullYear() - startDate.getFullYear();

        let months =
            currentDate.getMonth() - startDate.getMonth();

        let days =
            currentDate.getDate() - startDate.getDate();

        // Adjust days
        if (days < 0) {

            months--;

            const previousMonth =
                new Date(
                    currentDate.getFullYear(),
                    currentDate.getMonth(),
                    0
                );

            days += previousMonth.getDate();
        }

        // Adjust months
        if (months < 0) {

            years--;
            months += 12;
        }

        // Build duration text
        let duration = [];

        if (years > 0) {
            duration.push(
                years + (years === 1 ? " Year" : " Years")
            );
        }

        if (months > 0) {
            duration.push(
                months + (months === 1 ? " Month" : " Months")
            );
        }

        if (days > 0) {
            duration.push(
                days + (days === 1 ? " Day" : " Days")
            );
        }

        // Same-day selection
        if (duration.length === 0) {
            duration.push("0 Days");
        }

        durationInput.value = duration.join(" ");

        console.log("Symptoms started:", this.value);
        console.log("Calculated duration:", durationInput.value);

    });

});
