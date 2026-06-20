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


async function saveMotto() {

    const token =
        localStorage.getItem("token");

    const motto =
        document.getElementById(
            "mottoInput"
        ).value;

    const response = await fetch(
        `${API_URL}/save-motto`,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",

                Authorization:
                    `Bearer ${token}`
            },

            body: JSON.stringify({
                motto: motto
            })
        }
    );

    const data =
        await response.json();

    document.getElementById(
        "mottoMessage"
    ).innerText = data.message;
}


async function loadMottos() {

    const response =
        await fetch(
            `${API_URL}/users`
        );

    const users =
        await response.json();

    const container =
        document.getElementById(
            "mottoContainer"
        );

    if (!container) {
        return;
    }

    container.innerHTML = "";

    users.forEach(user => {

        const card =
            document.createElement("div");

        card.classList.add(
            "motto-card"
        );

        card.innerHTML = `
            <h3>${user.username}</h3>
            <p>${user.motto || ""}</p>
        `;

        container.appendChild(card);
    });
}


loadMottos();