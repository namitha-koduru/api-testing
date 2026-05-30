async function login() {

    const username =
        document.getElementById("username").value;

    const password =
        document.getElementById("password").value;

    const response = await fetch(
        "http://127.0.0.1:5000/api/auth/login",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                username,
                password
            })
        }
    );

    const data = await response.json();

    if (data.token) {

        localStorage.setItem(
            "token",
            data.token
        );

        window.location.href =
            "dashboard.html";
    }

    else {

        document.getElementById("message").innerText =
            data.message;
    }
}