document.getElementById("loginBtn").addEventListener("click", function(){

    const username =
    document.getElementById("username").value.trim();

    const password =
    document.getElementById("password").value.trim();

    if(username==="" || password===""){

        alert("Please enter Username and Password");

        return;

    }

    localStorage.setItem("username",username);

    window.location.href="index.html";

});