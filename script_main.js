const API_URL = "http://127.0.0.1:8000";

function showRegister() {

    document.getElementById("registerForm")
        .classList.remove("hidden");

    document.getElementById("loginForm")
        .classList.add("hidden");
}

function showLogin() {

    document.getElementById("loginForm")
        .classList.remove("hidden");

    document.getElementById("registerForm")
        .classList.add("hidden");
}


async function register() {

    const username =
        document.getElementById("registerUsername").value;

    const password =
        document.getElementById("registerPassword").value;

    try {

        const response = await fetch(
            `${API_URL}/register`,
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

        document.getElementById("message")
            .innerText = data.message || data.detail;

    } catch (error) {

        document.getElementById("message")
            .innerText = "Connection Error";
    }
}


async function login() {

    const username =
        document.getElementById("loginUsername").value;

    const password =
        document.getElementById("loginPassword").value;

    try {

        const response = await fetch(
            `${API_URL}/login`,
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

        document.getElementById("message")
            .innerText = data.message || data.detail;

    } catch (error) {

        document.getElementById("message")
            .innerText = "Connection Error";
    }
}