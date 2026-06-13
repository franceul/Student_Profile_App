const API_URL = "http://127.0.0.1:8000";

async function checkAuth() {

    const token =
        localStorage.getItem("token");

    if (!token) {

        window.location.href =
            "frontend_main.html";

        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/me`,
            {
                headers: {
                    Authorization:
                        `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {

            localStorage.removeItem(
                "token"
            );

            window.location.href =
                "frontend_main.html";
        }

    } catch (error) {

        console.error(error);
    }
}

checkAuth();

function logout() {

    localStorage.removeItem(
        "token"
    );

    window.location.href =
        "frontend_main.html";
}


async function loadProfile() {

    const token =
        localStorage.getItem("token");

    const response = await fetch(
        `${API_URL}/me`,
        {
            headers: {
                Authorization:
                    `Bearer ${token}`
            }
        }
    );

    const data = await response.json();

    const usernameElement =
        document.getElementById(
            "username"
        );

    if (usernameElement) {

        usernameElement.innerText =
            `Welcome ${data.username}`;
    }
}

loadProfile();