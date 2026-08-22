document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector(".auth-form");
    const message = document.getElementById("message");

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const email = document.getElementById("login-id").value.trim();
            const password = document.getElementById("password").value;

            // Clear previous message
            message.innerText = "";
            message.style.display = "none";

            try {
                const response = await fetch(
                    "http://127.0.0.1:8000/api/v1/auth/login",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            edu_email: email,
                            password: password
                        })
                    }
                );

                const data = await response.json();

                // Error from backend
                if (!response.ok) {
                    message.innerText = data.detail || "Login failed.";
                    message.style.display = "block";
                    return;
                }

                // Successful login
                localStorage.setItem("user_id", data.user_id);
                localStorage.setItem("edu_email", data.edu_email);
                localStorage.setItem("full_name", data.full_name);

                // Go to home page
                window.location.href = "index.html";

            } catch (error) {
                console.error("Login error:", error);
                message.style.color = "red";
                message.innerText = "Could not connect to API.";
                message.style.display = "block";
            }
        });
    }
});